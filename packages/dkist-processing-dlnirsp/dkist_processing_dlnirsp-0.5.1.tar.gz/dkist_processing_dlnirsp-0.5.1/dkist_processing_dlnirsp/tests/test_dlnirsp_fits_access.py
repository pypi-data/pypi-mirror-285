import pytest
from astropy.io import fits
from dkist_header_validator.translator import translate_spec122_to_spec214_l0

from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspRampFitsAccess
from dkist_processing_dlnirsp.tests.conftest import DlnirspHeaders


@pytest.fixture
def header(arm_id, tmp_path):
    dataset = DlnirspHeaders(
        dataset_shape=(2, 2, 2), array_shape=(1, 2, 2), time_delta=1.0, arm_id=arm_id
    )
    translated_header = fits.Header(translate_spec122_to_spec214_l0(dataset.header()))
    return translated_header


@pytest.mark.parametrize(
    "arm_id", [pytest.param("JBand"), pytest.param("HBand"), pytest.param("VIS")]
)
def test_dlnirsp_ramp_fits_access(header, arm_id):
    """
    Given: A header that may or may not contain IR camera-specific header keys
    When: Parsing the header with `DlnirspRampFitsAccess`
    Then: If the data are IR then the header values are parsed, and if the data are VIS then dummy values are returned
          for the IR-only keys.
    """
    fits_obj = DlnirspRampFitsAccess.from_header(header)

    assert fits_obj.arm_id == arm_id
    if arm_id == "VIS":
        assert fits_obj.camera_readout_mode == "DEFAULT_VISIBLE_CAMERA"
        assert fits_obj.num_frames_in_ramp == -99
        assert fits_obj.current_frame_in_ramp == -88

    else:
        assert fits_obj.camera_readout_mode == header["DLCAMSMD"]
        assert fits_obj.num_frames_in_ramp == header["DLCAMNS"]
        assert fits_obj.current_frame_in_ramp == header["DLCAMCUR"]
