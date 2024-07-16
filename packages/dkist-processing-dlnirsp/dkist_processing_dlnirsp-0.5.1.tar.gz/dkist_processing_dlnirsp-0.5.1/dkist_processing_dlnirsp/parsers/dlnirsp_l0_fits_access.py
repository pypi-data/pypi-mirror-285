"""DLNIRSP FitsAccess classes for raw and linearized data."""
from astropy.io import fits
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess


class DlnirspRampFitsAccess(L0FitsAccess):
    """
    Class to provide easy access to L0 headers for non-linearized (raw) DLNIRSP data.

    i.e. instead of <DlnirspL0FitsAccess>.header['weird_key'] this class lets us use <DlnirspL0FitsAccess>.nice_key instead

    Parameters
    ----------
    hdu :
        Fits L0 header object

    name : str
        The name of the file that was loaded into this FitsAccess object

    auto_squeeze : bool
        When set to True, dimensions of length 1 will be removed from the array
    """

    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | None = None,
        auto_squeeze: bool = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.camera_readout_mode: str = self.header.get("DLCAMSMD", "DEFAULT_VISIBLE_CAMERA")
        self.num_frames_in_ramp: int = self.header.get("DLCAMNS", -99)
        self.current_frame_in_ramp: int = self.header.get("DLCAMCUR", -88)
        self.arm_id: str = self.header["DLARMID"]


class DlnirspL0FitsAccess(L0FitsAccess):
    """
    Class to provide easy access to L0 headers for linearized (ready for processing) DLNIRSP data.

    i.e. instead of <DlnirspL0FitsAccess>.header['weird_key'] this class lets us use <DlnirspL0FitsAccess>.nice_key instead

    Parameters
    ----------
    hdu :
        Fits L0 header object

    name : str
        The name of the file that was loaded into this FitsAccess object

    auto_squeeze : bool
        When set to True, dimensions of length 1 will be removed from the array
    """

    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | None = None,
        auto_squeeze: bool = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.arm_id: str = self.header["DLARMID"]
        self.polarimeter_mode: str = self.header["DLPOLMD"]
        self.number_of_modulator_states: int = self.header["DLNUMST"]
        self.modulator_state: int = self.header["DLSTNUM"]
        self.num_mosaic_repeats: int = self.header["DLMOSNRP"]
        self.mosaic_num: int = self.header["DLCURMOS"]
        self.num_X_tiles: int = self.header["DLNSSTPX"]
        self.X_tile_num: int = self.header["DLCSTPX"]
        self.num_Y_tiles: int = self.header["DLNSSTPY"]
        self.Y_tile_num: int = self.header["DLCSTPY"]
