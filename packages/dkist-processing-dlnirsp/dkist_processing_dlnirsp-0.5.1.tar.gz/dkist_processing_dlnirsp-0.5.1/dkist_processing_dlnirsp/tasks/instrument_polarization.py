"""Create demodulation matrices."""
from collections import defaultdict
from itertools import chain

import numpy as np
from astropy.io import fits
from dkist_processing_common.codecs.asdf import asdf_encoder
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_pac.fitter.fitting_core import fill_modulation_matrix
from dkist_processing_pac.fitter.fitting_core import generate_model_I
from dkist_processing_pac.fitter.fitting_core import generate_S
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from dkist_processing_pac.input_data.drawer import Drawer
from dkist_processing_pac.input_data.dresser import Dresser
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspL0FitsAccess
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tasks.mixin.intermediate_frame_helpers import (
    IntermediateFrameHelpersMixin,
)

__all__ = ["InstrumentPolarizationCalibration"]


class InstrumentPolarizationCalibration(
    DlnirspTaskBase, QualityMixin, IntermediateFrameHelpersMixin
):
    """
    Task class for computing "instrument polarization calibration" objects.

    AKA demodulation matrices.
    """

    record_provenance = True

    def run(self) -> None:
        """
        Create demodulation matrices.

        1. Create polcal dark and gain calibration objects

        2. Apply dark and gain calibration objects to all POLCAL frames (including dark and clear steps)

        3. Downsample full frame by binning each group

        4. Send data to `dkist-processing-pac` for demodulation calculation

        4. Resample demodulation matrices to full-frame size

        5. Write full demodulation matrices
        """
        if not self.constants.correct_for_polarization:
            return

        polcal_exposure_times = self.constants.polcal_exposure_times
        if len(polcal_exposure_times) > 1:
            logger.info(
                "WARNING: More than one polcal exposure time detected. "
                "Everything *should* still work, but this is a weird condition that may produce "
                "strange results."
            )
        logger.info(f"{polcal_exposure_times = }")

        with self.apm_processing_step("Generate polcal DARK frame"):
            logger.info("Generating polcal dark frame")
            self.generate_polcal_dark_calibration(exp_times=polcal_exposure_times)

        with self.apm_processing_step("Generate polcal GAIN frame"):
            logger.info("Generating polcal gain frame")
            self.generate_polcal_gain_calibration(exp_times=polcal_exposure_times)

        with self.apm_task_step("Process CS steps"):
            logger.info("Processing CS steps")
            local_data, global_data = self.process_cs_steps()

        with self.apm_processing_step("Fit CU parameters"):
            logger.info("Fitting CU parameters")

            remove_I_trend = self.parameters.pac_remove_linear_I_trend
            local_dresser = Dresser()
            local_dresser.add_drawer(Drawer(local_data, remove_I_trend=remove_I_trend))
            global_dresser = Dresser()
            global_dresser.add_drawer(Drawer(global_data, remove_I_trend=remove_I_trend))
            pac_fitter = PolcalFitter(
                local_dresser=local_dresser,
                global_dresser=global_dresser,
                fit_mode=self.parameters.pac_fit_mode,
                init_set=self.parameters.pac_init_set,
                # TODO: Check that we want to leave this as True for DL
                inherit_global_vary_in_local_fit=True,
                suppress_local_starting_values=True,
                fit_TM=False,
            )

        self.save_intermediate_polcal_files(polcal_fitter=pac_fitter)

        with self.apm_processing_step("Reample demodulation matrices"):
            logger.info("Resampling demodulation matrices to full frame")
            binned_demod = pac_fitter.demodulation_matrices
            full_array_shape = self.get_full_array_shape()

            final_demod = self.reshape_demodulation_matrices(binned_demod, full_array_shape)

        with self.apm_writing_step("Write full-frame demodulation matrices"):
            logger.info("Writing full-frame demodulation matrices")
            self.write(
                data=final_demod,
                encoder=fits_array_encoder,
                tags=[
                    DlnirspTag.intermediate(),
                    DlnirspTag.frame(),
                    DlnirspTag.task_demodulation_matrices(),
                ],
            )

        with self.apm_processing_step("Computing and recording polcal quality metrics"):
            self.record_polcal_quality_metrics(polcal_fitter=pac_fitter)

        with self.apm_processing_step("Computing and recording frame count quality metrics"):
            no_of_raw_lamp_frames: int = self.scratch.count_all(
                tags=[DlnirspTag.linearized(), DlnirspTag.frame(), DlnirspTag.task_polcal()],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.polcal.value, total_frames=no_of_raw_lamp_frames
            )

    def generate_polcal_dark_calibration(self, exp_times: list[float] | tuple[float]) -> None:
        """Compute an average polcal dark array for all polcal exposure times."""
        for exp_time in exp_times:
            logger.info(f"Computing polcal dark for  {exp_time = }")

            dark_arrays = self.read(
                tags=[
                    DlnirspTag.linearized(),
                    DlnirspTag.frame(),
                    DlnirspTag.task_polcal_dark(),
                    DlnirspTag.exposure_time(exp_time),
                ],
                decoder=fits_array_decoder,
            )

            avg_array = average_numpy_arrays(dark_arrays)
            self.intermediate_frame_helpers_write_arrays(
                arrays=avg_array, task=TaskName.polcal_dark.value, exposure_time=exp_time
            )

    def generate_polcal_gain_calibration(self, exp_times: list[float] | tuple[float]) -> None:
        """
        Average 'clear' polcal frames to produce a polcal gain calibration.

        The polcal dark calibration is applied prior to averaging.
        """
        for exp_time in exp_times:
            logger.info(f"Computing polcal gain for {exp_time = }")

            dark_array = next(
                self.intermediate_frame_helpers_load_arrays(
                    tags=[DlnirspTag.task_polcal_dark(), DlnirspTag.exposure_time(exp_time)]
                )
            )

            gain_arrays = self.read(
                tags=[
                    DlnirspTag.linearized(),
                    DlnirspTag.frame(),
                    DlnirspTag.task_polcal_gain(),
                    DlnirspTag.exposure_time(exp_time),
                ],
                decoder=fits_array_decoder,
            )

            dark_corrected_arrays = subtract_array_from_arrays(
                arrays=gain_arrays, array_to_subtract=dark_array
            )

            avg_array = average_numpy_arrays(dark_corrected_arrays)
            self.intermediate_frame_helpers_write_arrays(
                arrays=avg_array, task=TaskName.polcal_gain.value, exposure_time=exp_time
            )

    def process_cs_steps(
        self,
    ) -> tuple[dict[int, list[DlnirspL0FitsAccess]], dict[int, list[DlnirspL0FitsAccess]]]:
        """
        Start with raw, linearized POLCAL frames and produce data to be sent to `dkist-processing-pac`.

        Namely, the linearized frames first have dark and gain/clear corrections applied. They are then binned into
        a "global" and "local" set of data (see `dkist-processing-pac` for more information on the difference between
        these two data).
        """
        global_dict = defaultdict(list)
        local_dict = defaultdict(list)

        with self.apm_task_step("Collect dark and gain arrays"):
            dark_array_dict = self._collect_polcal_calibrations_by_exp_time(
                TaskName.polcal_dark.value
            )
            gain_array_dict = self._collect_polcal_calibrations_by_exp_time(
                TaskName.polcal_gain.value
            )

        with self.apm_processing_step("Correct and extract polcal data"):
            for cs_step in range(self.constants.num_cs_steps):
                for modstate in range(1, self.constants.num_modstates + 1):
                    log_str = f"{cs_step = }, {modstate = }"
                    logger.info(f"Applying basic corrections to {log_str}")
                    data, header = self.apply_basic_corrections(
                        cs_step=cs_step,
                        modstate=modstate,
                        dark_array_dict=dark_array_dict,
                        gain_array_dict=gain_array_dict,
                    )

                    logger.info(f"Extracting bins from {log_str}")
                    global_binned_data = self._bin_global_data(data)
                    global_hdu = fits.PrimaryHDU(data=global_binned_data, header=header)
                    global_obj = DlnirspL0FitsAccess(hdu=global_hdu)
                    global_dict[cs_step].append(global_obj)

                    local_binned_data = self._bin_local_data(data)
                    local_hdu = fits.PrimaryHDU(data=local_binned_data, header=header)
                    local_obj = DlnirspL0FitsAccess(hdu=local_hdu)
                    local_dict[cs_step].append(local_obj)

        return local_dict, global_dict

    def apply_basic_corrections(
        self,
        cs_step: int,
        modstate: int,
        dark_array_dict: dict[float, np.ndarray],
        gain_array_dict: dict[float, np.ndarray],
    ) -> tuple[np.ndarray, fits.Header]:
        """Apply polcal dark and gain/clear corrections to all POLCAL data."""
        # Grab ANY header. We only care about the modstate and GOS configuration (CS Step)
        tags = [
            DlnirspTag.linearized(),
            DlnirspTag.frame(),
            DlnirspTag.task_polcal(),
            DlnirspTag.modstate(modstate),
            DlnirspTag.cs_step(cs_step),
        ]
        any_access_obj = next(
            self.read(
                tags=tags,
                decoder=fits_access_decoder,
                fits_access_class=DlnirspL0FitsAccess,
            )
        )
        header = any_access_obj.header

        exp_time_corrected_list = []
        for exp_time in self.constants.polcal_exposure_times:
            cs_step_arrays = self.read(
                tags=tags + [DlnirspTag.exposure_time(exp_time)], decoder=fits_array_decoder
            )
            dark_corrected_arrays = subtract_array_from_arrays(
                arrays=cs_step_arrays, array_to_subtract=dark_array_dict[exp_time]
            )

            gain_corrected_arrays = divide_arrays_by_array(
                arrays=dark_corrected_arrays, array_to_divide_by=gain_array_dict[exp_time]
            )
            exp_time_corrected_list.append(gain_corrected_arrays)

        all_corrected_arrays = chain(*exp_time_corrected_list)
        avg_array = average_numpy_arrays(all_corrected_arrays)

        return avg_array, header

    def _collect_polcal_calibrations_by_exp_time(self, task: str) -> dict[float, np.ndarray]:
        """Pre-load a dictionary of calibration frames organized by exposure time."""
        cal_dict = dict()
        for exp_time in self.constants.polcal_exposure_times:
            tags = [DlnirspTag.task(task), DlnirspTag.exposure_time(exp_time)]
            cal_array = next(self.intermediate_frame_helpers_load_arrays(tags=tags))
            cal_dict[exp_time] = cal_array

        return cal_dict

    def _bin_local_data(self, data: np.ndarray) -> np.ndarray:
        """Convert full array into "local" polcal data by binning each group."""
        binned_group_arrays = []
        for group in range(self.group_id_num_groups):
            group_array = self._bin_single_group(data, group)
            binned_group_arrays.append(group_array)

        return np.stack(binned_group_arrays)

    def _bin_global_data(self, data: np.ndarray) -> np.ndarray:
        """Convert full array into "global" polcal data by averaging the entire frame."""
        global_data = np.nanmedian(data[self.group_id_illuminated_idx])[None]
        return global_data

    def _bin_single_group(self, data: np.ndarray, group_id: int) -> np.ndarray:
        """Bin a single IFU group."""
        group_data = self.group_id_get_data(data=data, group_id=group_id)
        return np.nanmedian(group_data)

    def get_full_array_shape(self) -> tuple[int, ...]:
        """Return the shape of the full DL-NIRSP frame."""
        return self._unrectified_array_shape

    def reshape_demodulation_matrices(
        self, binned_demod_matrices: np.ndarray, final_shape: tuple[int, ...]
    ) -> np.ndarray:
        """Populate a full frame from a set of demodulation matrices that are organized by binned IFU group."""
        # The non-demodulation matrix part of the larger array
        data_shape = binned_demod_matrices.shape[:-2]
        demod_shape = binned_demod_matrices.shape[-2:]  # The shape of a single demodulation matrix
        logger.info(f"Demodulation FOV sampling shape: {data_shape}")
        logger.info(f"Demodulation matrix shape: {demod_shape}")
        if np.prod(data_shape) == 1:
            # A single modulation matrix can be used directly, so just return it after removing extraneous dimensions
            logger.info(f"Single demodulation matrix detected")
            return np.squeeze(binned_demod_matrices)

        full_demod_matrices = np.zeros(final_shape + demod_shape)
        for group in range(self.group_id_num_groups):
            group_demod = binned_demod_matrices[group]
            self._place_group_in_full_array(
                group_data=group_demod, group_id=group, full_array=full_demod_matrices
            )

        return full_demod_matrices

    def _place_group_in_full_array(
        self, group_data: np.ndarray, group_id: int, full_array: np.ndarray
    ) -> None:
        """Upsample a single IFU group into the full DL-NIRSP array."""
        if len(group_data.shape) - 2:  # -2 for the actual demodulation matrix shape
            raise ValueError("Only a single value per group is currently supported")

        group_idx = self.group_id_get_idx(group_id=group_id, rectified=False)
        full_array[group_idx] = group_data

    def save_intermediate_polcal_files(
        self,
        polcal_fitter: PolcalFitter,
    ) -> None:
        """Save intermediate files for science-team analysis.

        THIS FUNCTION IS ONLY TEMPORARY. It should probably be removed prior to production.
        """
        dresser = polcal_fitter.local_objects.dresser
        ## Input flux
        #############
        input_flux_tags = [
            DlnirspTag.frame(),
            DlnirspTag.debug(),
            DlnirspTag.task("INPUT_FLUX"),
        ]

        # Put all flux into a single array
        fov_shape = dresser.shape
        socc_shape = (dresser.numdrawers, dresser.drawer_step_list[0], self.constants.num_modstates)
        flux_shape = fov_shape + socc_shape
        input_flux = np.zeros(flux_shape, dtype=np.float64)
        for i in range(np.prod(fov_shape)):
            idx = np.unravel_index(i, fov_shape)
            I_cal, _ = dresser[idx]
            input_flux[idx] = I_cal.T.reshape(socc_shape)

        with self.apm_writing_step("Writing input flux"):
            path = self.write(data=input_flux, tags=input_flux_tags, encoder=fits_array_encoder)
            logger.info(f"Wrote input flux with tags {input_flux_tags = } to {str(path)}")

        ## Calibration Unit best fit parameters
        #######################################
        cmp_tags = [
            DlnirspTag.frame(),
            DlnirspTag.debug(),
            DlnirspTag.task("CU_FIT_PARS"),
        ]
        with self.apm_writing_step("Writing CU fit parameters"):
            cu_dict = defaultdict(lambda: np.zeros(fov_shape) * np.nan)
            for i in range(np.prod(fov_shape)):
                idx = np.unravel_index(i, fov_shape)
                values_dict = polcal_fitter.fit_parameters[idx].valuesdict()
                for k, v in values_dict.items():
                    cu_dict[k][idx] = v

            path = self.write(data=cu_dict, tags=cmp_tags, encoder=asdf_encoder)
            logger.info(f"Wrote CU fits with {cmp_tags = } to {str(path)}")

        ## Best-fix flux
        ################
        fit_flux_tags = [DlnirspTag.frame(), DlnirspTag.debug(), DlnirspTag.task("BEST_FIT_FLUX")]
        with self.apm_processing_step("Computing best-fit flux"):
            best_fit_flux = self._compute_best_fit_flux(polcal_fitter)

        with self.apm_writing_step("Writing best-fit flux"):
            path = self.write(data=best_fit_flux, tags=fit_flux_tags, encoder=fits_array_encoder)
            logger.info(f"Wrote best-fit flux with {fit_flux_tags = } to {str(path)}")

    def _compute_best_fit_flux(self, polcal_fitter: PolcalFitter) -> np.ndarray:
        """Calculate the best-fit SoCC flux from a set of fit parameters.

        The output array has shape (1, num_spectral_bins, num_spatial_bins, 1, 4, num_modstate)
        """
        dresser = polcal_fitter.local_objects.dresser
        fov_shape = dresser.shape
        socc_shape = (dresser.numdrawers, dresser.drawer_step_list[0], self.constants.num_modstates)
        flux_shape = fov_shape + socc_shape
        best_fit_flux = np.zeros(flux_shape, dtype=np.float64)
        num_points = np.prod(fov_shape)
        for i in range(num_points):
            idx = np.unravel_index(i, fov_shape)
            I_cal, _ = dresser[idx]
            CM = polcal_fitter.local_objects.calibration_unit
            TM = polcal_fitter.local_objects.telescope
            par_vals = polcal_fitter.fit_parameters[idx].valuesdict()
            CM.load_pars_from_dict(par_vals)
            TM.load_pars_from_dict(par_vals)
            S = generate_S(TM=TM, CM=CM, use_M12=True)
            O = fill_modulation_matrix(par_vals, np.zeros((dresser.nummod, 4)))
            I_mod = generate_model_I(O, S)

            # Save all data to associated arrays
            best_fit_flux[idx] = I_mod.T.reshape(socc_shape)

        return best_fit_flux

    def record_polcal_quality_metrics(self, polcal_fitter: PolcalFitter):
        """Record various quality metrics from PolCal fits."""
        self.quality_store_polcal_results(
            polcal_fitter=polcal_fitter,
            label=f"IFU",
            bins_1=self.group_id_num_groups,
            bins_2=1,
            bin_1_type="IFU group",
            bin_2_type="dummy",
            skip_recording_constant_pars=False,
        )
