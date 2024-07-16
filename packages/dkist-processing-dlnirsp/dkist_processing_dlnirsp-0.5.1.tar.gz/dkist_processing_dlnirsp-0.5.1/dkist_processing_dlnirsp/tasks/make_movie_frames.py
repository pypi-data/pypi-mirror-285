"""Task for turning output science frames into movie frames."""
import numpy as np
from astropy.io import fits
from astropy.visualization import ZScaleInterval
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdu_decoder
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase

__all__ = ["MakeDlnirspMovieFrames"]


class MakeDlnirspMovieFrames(DlnirspTaskBase):
    """Task class for making individual movie frames that will be used for the browse movie."""

    def run(self) -> None:
        """
        Construct movie frames from the set of output science frames.

        For now just make a single movie frame for every output frame. If the data are polarimetric then all 4
        Stokes images will be put together in a grid.
        """
        if self.constants.correct_for_polarization:
            logger.info("Making polarimetric movie frames")
        else:
            logger.info("Making spectrographic movie frames")

        self.make_movie_frames()

    def make_movie_frames(self):
        """Make a movie frame for every output frame."""
        for mosaic_num in range(self.constants.num_mosaic_repeats):
            for tile_X_num in range(self.constants.num_spatial_steps_X):
                for tile_Y_num in range(self.constants.num_spatial_steps_Y):
                    if self.constants.correct_for_polarization:
                        data, header = self.make_single_polarimetric_frame(
                            mosaic_num=mosaic_num, tile_X_num=tile_X_num, tile_Y_num=tile_Y_num
                        )
                    else:
                        data, header = self.make_single_spectrographic_frame(
                            mosaic_num=mosaic_num, tile_X_num=tile_X_num, tile_Y_num=tile_Y_num
                        )

                    self.write(
                        data=data,
                        header=header,
                        tags=[
                            DlnirspTag.movie_frame(),
                            DlnirspTag.mosaic_num(mosaic_num),
                            DlnirspTag.tile_X_num(tile_X_num),
                            DlnirspTag.tile_Y_num(tile_Y_num),
                        ],
                        encoder=fits_array_encoder,
                    )

    def make_single_polarimetric_frame(
        self, mosaic_num: int, tile_X_num: int, tile_Y_num: int
    ) -> tuple[np.ndarray, fits.Header]:
        """
        Extract and grid together all 4 Stokes frames for a given instrument loop tuple.

        The data are also scaled for visual appeal.
        """
        stokes_dict = dict()
        for stokes in self.constants.stokes_params:
            tags = [
                DlnirspTag.frame(),
                DlnirspTag.output(),
                DlnirspTag.mosaic_num(mosaic_num),
                DlnirspTag.tile_X_num(tile_X_num),
                DlnirspTag.tile_Y_num(tile_Y_num),
            ]
            hdu = next(self.read(tags=tags, decoder=fits_hdu_decoder))
            data_2D = self.grab_wavelength_slice(hdu.data)
            stokes_dict[stokes] = self.scale_for_rendering(data_2D)

        # Don't care which hdu we get
        header = hdu.header
        movie_array = self.grid_movie_frame(
            top_left=stokes_dict["I"],
            top_right=stokes_dict["Q"],
            bottom_left=stokes_dict["U"],
            bottom_right=stokes_dict["V"],
        )
        return movie_array, header

    def make_single_spectrographic_frame(
        self, mosaic_num: int, tile_X_num: int, tile_Y_num: int
    ) -> tuple[np.ndarray, fits.Header]:
        """Load a output spectrographic frame, extract a single wavelength, and scale for visual appeal."""
        tags = [
            DlnirspTag.frame(),
            DlnirspTag.output(),
            DlnirspTag.mosaic_num(mosaic_num),
            DlnirspTag.tile_X_num(tile_X_num),
            DlnirspTag.tile_Y_num(tile_Y_num),
        ]
        hdu = next(self.read(tags=tags, decoder=fits_hdu_decoder))

        data_2D = self.grab_wavelength_slice(hdu.data)
        scaled_data = self.scale_for_rendering(data_2D)

        movie_array = self.scale_for_rendering(scaled_data)

        return movie_array, hdu.header

    @staticmethod
    def grab_wavelength_slice(data: np.ndarray):
        """Convert a 3D IFU image into a 2D movie frame by extracting a certain wavelength region."""
        wavelength_dim_size = data.shape[0]
        middle_index = int(np.mean(range(wavelength_dim_size)))
        return data[middle_index, :, :]

    @staticmethod
    def scale_for_rendering(data: np.ndarray):
        """
        Scale the output frame data using a normalization function to facilitate display as a movie frame.

        Non-number pixels (nan, inf, -inf) are set to black.
        """
        bad_idx = ~np.isfinite(data)
        data[bad_idx] = np.nanmedian(data)
        zscale = ZScaleInterval()
        scaled_data = zscale(data)
        scaled_data[bad_idx] = 0.0
        return scaled_data

    @staticmethod
    def grid_movie_frame(
        top_left: np.ndarray,
        top_right: np.ndarray,
        bottom_left: np.ndarray,
        bottom_right: np.ndarray,
    ) -> np.ndarray:
        """Combine multiple arrays into a 2x2 grid."""
        result = np.concatenate(
            (
                np.concatenate((top_left, top_right), axis=1),
                np.concatenate((bottom_left, bottom_right), axis=1),
            ),
            axis=0,
        )
        return result
