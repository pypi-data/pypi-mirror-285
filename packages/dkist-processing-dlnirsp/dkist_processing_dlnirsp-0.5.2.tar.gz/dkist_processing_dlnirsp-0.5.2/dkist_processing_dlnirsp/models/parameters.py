"""Machinery to access pipeline parameters served in input dataset document."""
from datetime import datetime
from functools import cached_property

import numpy as np
from dkist_processing_common.models.parameters import ParameterArmIdMixin
from dkist_processing_common.models.parameters import ParameterBase
from dkist_processing_common.models.parameters import ParameterWavelengthMixin


class DlnirspParsingParameters(ParameterBase):
    """
    Parameters specifically (and only) for the Parse task.

    Needed because the Parse task doesn't know what the wavelength is yet and therefore can't use the
    `ParameterWaveLengthMixin`.
    """

    @property
    def max_cs_step_time_sec(self) -> float:
        """Time window within which CS steps with identical GOS configurations are considered to be the same."""
        return self._find_most_recent_past_value(
            "dlnirsp_max_cs_step_time_sec", start_date=datetime.now()
        )


class DlnirspParameters(ParameterBase, ParameterWavelengthMixin, ParameterArmIdMixin):
    """Put all DLNIRSP parameters parsed from the input dataset document in a single property."""

    @cached_property
    def group_id_array(self) -> np.ndarray:
        """
        Return an array containing 'group ids' of each array pixel.

        The group id labels each IFU ribbon/mirror slice.
        """
        param_dict = self._find_parameter_for_arm("dlnirsp_group_id_file")
        return self._load_param_value_from_fits(param_dict)

    @property
    def group_id_rough_slit_separation_px(self) -> float:
        """
        Rough pixel distance between slits.

        This is NOT the pixel distance between both beams of the same slit.
        """
        return self._find_most_recent_past_value("dlnirsp_group_id_rough_slit_separation_px")

    @property
    def corrections_max_nan_frac(self) -> float:
        """
        Maximum allowable fraction of NaN in a shifted pixel before that pixel gets converted to NaN.

        Input NaN values are tracked and any shifted pixel that has a value made up of more than this fraction of NaN
        pixels will be set to NaN.
        """
        return self._find_most_recent_past_value("dlnirsp_corrections_max_nan_frac")

    @property
    def pac_remove_linear_I_trend(self) -> bool:
        """Flag that determines if a linear intensity trend is removed from the whole PolCal CS.

        The trend is fit using the average flux in the starting and ending clear steps.
        """
        return self._find_most_recent_past_value("dlnirsp_pac_remove_linear_I_trend")

    @property
    def pac_fit_mode(self) -> str:
        """Name of set of fitting flags to use during PAC Calibration Unit parameter fits."""
        return self._find_most_recent_past_value("dlnirsp_pac_fit_mode")

    @property
    def pac_init_set(self):
        """Name of set of initial values for Calibration Unit parameter fit."""
        return self._find_most_recent_past_value("dlnirsp_pac_init_set")

    @property
    def lamp_despike_kernel(self) -> (float, float):
        """Return the (x, y) stddev of the Gaussian kernel used for lamp despiking."""
        return self._find_most_recent_past_value("dlnirsp_lamp_despike_kernel")

    @property
    def lamp_despike_threshold(self) -> float:
        """Return the threhold value used to identify spikes in lamp gains."""
        return self._find_most_recent_past_value("dlnirsp_lamp_despike_threshold")

    @cached_property
    def geo_dispersion_array(self) -> np.ndarray:
        """Return an array that provides the dispersion (in Angstrom / px) for each group."""
        param_dict = self._find_parameter_for_arm("dlnirsp_geo_dispersion_file")
        return self._load_param_value_from_fits(param_dict)

    @property
    def geo_spectral_edge_trim(self) -> int:
        """Return the +/- number of pixels to remove from the ends of all spectra prior to fitting."""
        return self._find_most_recent_past_value("dlnirsp_geo_spectral_edge_trim")

    @property
    def geo_continuum_smoothing_sigma_px(self) -> float:
        """
        Return the Gaussian sigma used to smooth out spectral lines when estimating the continuum background.

        This should be roughly the width, in px, of typical spectral lines. Err on the side of too large.
        """
        return self._find_most_recent_past_value("dlnirsp_geo_continuum_smoothing_sigma_px")

    @property
    def geo_max_shift_px(self) -> float:
        """
        Return the maximum shift to consider when computing spectral curvature.

        This is an absolute value: negative and positive shifts are constrained to the same magnitude.
        """
        return self._find_most_recent_past_value("dlnirsp_geo_max_shift_px")

    @property
    def geo_shift_poly_fit_order(self) -> int:
        """Return the order of the polynomial used to fit spectral shifts as a function of slit position."""
        return self._find_most_recent_past_value("dlnirsp_geo_shift_poly_fit_order")

    @property
    def geo_bad_px_sigma_threshold(self) -> float:
        """Any pixels larger than this many stddevs from a difference between a filtered and raw spectrum will be removed."""
        return self._find_most_recent_past_value("dlnirsp_geo_bad_px_sigma_threshold")

    @property
    def geo_slitbeam_fit_sig_clip(self) -> int:
        """Plus/minus number of standard deviations away from the median used to reject outlier values when fitting along the slitbeams."""
        return self._find_most_recent_past_value("dlnirsp_geo_slitbeam_fit_sig_clip")

    @property
    def ifu_x_pos_array(self) -> np.ndarray:
        """Return the array mapping raw pixel position to an X coordinate in the IFU."""
        param_dict = self._find_parameter_for_arm("dlnirsp_ifu_x_pos_file")
        return self._load_param_value_from_fits(param_dict)

    @property
    def ifu_y_pos_array(self) -> np.ndarray:
        """Return the array mapping raw pixel position to an X coordinate in the IFU."""
        param_dict = self._find_parameter_for_arm("dlnirsp_ifu_y_pos_file")
        return self._load_param_value_from_fits(param_dict)
