"""Task to linearize raw input data."""
import numpy as np
from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspRampFitsAccess
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspLinearityTaskBase
from dkist_processing_dlnirsp.tasks.mixin.input_frame_loaders import InputFrameLoadersMixin

__all__ = ["LinearityCorrection"]


class LinearityCorrection(DlnirspLinearityTaskBase, InputFrameLoadersMixin):
    """Task class for performing linearity correction on all input frames, regardless of task type."""

    record_provenance = True

    def run(self):
        """
        Run method for this task.

        Steps to be performed:
            - Gather all input frames
            - Iterate through frames
                - Perform linearity correction for this frame (algorithm is TBD)
                - Get list of all tags for this frame
                - Remove input tag and add linearity_corrected tag
                - Write linearity corrected frame with updated tag list
                - Delete original frame

        Returns
        -------
        None
        """
        if self.constants.is_ir_data:
            with self.apm_task_step("Linearizing input IR frames"):
                self.linearize_IR_data()
                return

        with self.apm_task_step("Tagging non-IR frames as LINEARIZED"):
            self.tag_VIS_data_as_linearized()

    def tag_VIS_data_as_linearized(self):
        """Tag all INPUT frames as LINEARIZED."""
        for path in self.read(tags=[DlnirspTag.frame(), DlnirspTag.input()]):
            self.remove_tags(path, DlnirspTag.input())
            self.tag(path, tags=DlnirspTag.linearized())

    def linearize_IR_data(self):
        """
        Linearize data from IR cameras.

        Steps to be performed:
            - Gather all input frames
            - Iterate through frames
                - Perform linearity correction for this frame (algorithm is TBD)
                - Get list of all tags for this frame
                - Remove input tag and add linearity_corrected tag
                - Write linearity corrected frame with updated tag list
        """
        num_frames = len(self.constants.time_obs_list)
        for frame_num, time_obs in enumerate(self.constants.time_obs_list, start=1):
            logger.info(f"Processing frames from {time_obs} ({frame_num}/{num_frames})")
            input_objects = list(self.input_frame_loaders_fits_access_generator(time_obs=time_obs))

            if not self.is_ramp_valid(input_objects):
                continue

            lin_obj = self.perform_linearity_correction(input_objects)
            self.write_and_tag_linearized_frame(lin_obj, time_obs)
        logger.info(f"Processed {frame_num} frames")

    def is_ramp_valid(self, ramp_object_list: list[DlnirspRampFitsAccess]) -> bool:
        """
        Check if a given ramp is valid.

        Current validity checks are:

          1. All frames in the ramp have the same value for NUM_FRAMES_IN_RAMP
          2. The value of NUM_FRAMES_IN_RAMP equals the length of actual frames found

        If a ramp is not valid then warnings are logged and `False` is returned.
        """
        frames_in_ramp_set = {o.num_frames_in_ramp for o in ramp_object_list}

        if len(frames_in_ramp_set) > 1:
            logger.warning(
                f"Not all frames have the same FRAMES_IN_RAMP value. Set is {frames_in_ramp_set}. Skipping ramp."
            )
            return False

        num_frames_in_ramp = frames_in_ramp_set.pop()
        num_ramp_objects = len(ramp_object_list)
        if num_ramp_objects != num_frames_in_ramp:
            logger.warning(
                f"Missing some ramp frames. Expected {num_frames_in_ramp} but only have {num_ramp_objects}. Skipping ramp."
            )
            return False

        return True

    def perform_linearity_correction(
        self, input_objects: list[DlnirspRampFitsAccess]
    ) -> fits.PrimaryHDU:
        """
        Create a linearity corrected fits object from a series of input frames (ramp).

        Parameters
        ----------
        time_obs
            The common timestamp for all frames in the series (ramp)

        Returns
        -------
        None

        """
        # Now sort them based on frame in ramp
        sorted_input_objects = sorted(input_objects, key=lambda x: x.current_frame_in_ramp)
        output_array = self.linearize_single_ramp(sorted_input_objects)

        last_header = sorted_input_objects[-1].header
        hdu = fits.PrimaryHDU(data=output_array, header=last_header)

        return hdu

    def linearize_single_ramp(self, ramp_obj_list: [DlnirspRampFitsAccess]) -> np.ndarray:
        """Convert a group of exposures from the same ramp into a single, linearized array.

        Right now this just does the last NDR minus the first (bias NDR). It will probably get more complicated.
        """
        # Need to cast as float because raw are uint16 and will thus explode for values below 0
        bias = ramp_obj_list[0].data.astype(float)

        return ramp_obj_list[-1].data.astype(float) - bias

    def write_and_tag_linearized_frame(self, hdu: fits.PrimaryHDU, time_obs: str) -> None:
        """Write a linearized HDU and tag with LINEARIZED and FRAME."""
        hdu_list = fits.HDUList([hdu])

        tags = [DlnirspTag.linearized(), DlnirspTag.frame(), DlnirspTag.time_obs(time_obs)]
        self.write(data=hdu_list, tags=tags, encoder=fits_hdulist_encoder)
