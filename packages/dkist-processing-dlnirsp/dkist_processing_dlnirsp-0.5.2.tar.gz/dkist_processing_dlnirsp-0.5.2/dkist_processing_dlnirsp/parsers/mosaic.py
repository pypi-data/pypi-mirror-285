"""Bud to parse the number of subloops making up a mosaic."""
from collections import defaultdict
from collections import namedtuple
from typing import Literal
from typing import Type

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_dlnirsp.models.constants import DlnirspBudName
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspL0FitsAccess


class NumMosaicPieceBase(Stem):
    """
    Base class for identifying the number of mosaic repeats, X tiles, and Y tiles in a dataset.

    Header keys exist for all of these loop levels; this class exists to handle the logic of datasets that are aborted
    at different levels of the instrument loops.

    Each "piece" of the mosaic loop (mosaic repeats, X tiles, Y tiles) is recorded for all OBSERVE frames so that
    derived classes can use this information to figure out how many pieces there are.
    """

    MosaicPieces = namedtuple("MosaicPieces", ["mosaic_num", "X_tile", "Y_tile"])
    observe_task_name = TaskName.observe.value.casefold()

    # This only here so type-hinting of this complex dictionary will work.
    key_to_petal_dict: dict[str, MosaicPieces]

    def __init__(self, constant_name: str):
        super().__init__(stem_name=constant_name)

    def setter(self, fits_obj: DlnirspL0FitsAccess) -> Type[SpilledDirt] | tuple:
        """
        Extract the mosaic piece information from each frame and package in a tuple.

        Only OBSERVE frames are considered.
        """
        if fits_obj.ip_task_type.casefold() != TaskName.observe.value.casefold():
            return SpilledDirt

        mosaic_num = fits_obj.mosaic_num
        X_tile = fits_obj.X_tile_num
        Y_tile = fits_obj.Y_tile_num

        return self.MosaicPieces(mosaic_num=mosaic_num, X_tile=X_tile, Y_tile=Y_tile)

    def num_files_per_mosaic_piece(
        self, piece_name: Literal["mosaic_num", "X_tile", "Y_tile"]
    ) -> dict[int, int]:
        """
        Compute the number of files per each unique mosaic piece.

        For example, if each mosaic num usually has 4 files, but an abort resulted in the last one only having 2 then
        the output of this method would be `{0: 4, 1: 4, 2: 4, 3: 2}`.
        """
        num_files_per_piece = defaultdict(int)
        for mosaic_pieces in self.key_to_petal_dict.values():
            num_files_per_piece[getattr(mosaic_pieces, piece_name)] += 1

        return num_files_per_piece

    def complete_piece_list(self, num_files_per_piece_dict: dict[int, int]) -> list[int]:
        """
        Identify the index numbers of all complete mosaic pieces.

        "Completed" pieces are assumed to be those that have a number of files equal to the maximum number of files
        in any mosaic piece. This is a good assumption for now.
        """
        complete_piece_size = max(num_files_per_piece_dict.values())
        return [
            piece_num
            for piece_num, piece_size in num_files_per_piece_dict.items()
            if piece_size == complete_piece_size
        ]


class NumMosaicRepeatsBud(NumMosaicPieceBase):
    """
    Bud for determining the number of mosaic repeats.

    Only completed mosaics are completed.
    """

    def __init__(self):
        super().__init__(constant_name=DlnirspBudName.num_mosaic_repeats.value)

    def getter(self, key: str) -> int:
        """
        Return the number of *completed* mosaic repeats.

        A check is also made that the set of completed repeats is continuous from 0 to the number of completed repeats.
        """
        num_files_per_mosaic = self.num_files_per_mosaic_piece("mosaic_num")
        complete_mosaic_nums = self.complete_piece_list(num_files_per_mosaic)

        num_mosaics = len(complete_mosaic_nums)

        sorted_complete_mosaic_nums = sorted(complete_mosaic_nums)
        if sorted_complete_mosaic_nums != list(range(num_mosaics)):
            raise ValueError(
                f"Not all sequential mosaic repeats could be found. Found {sorted_complete_mosaic_nums}"
            )

        return num_mosaics


class NumXTilesBud(NumMosaicPieceBase):
    """
    Bud for determining the number of X tiles.

    If the dataset includes multiple complete mosaic repeats then all found X tiles are expected to be completed. If
    only a single mosaic repeat exists then the number of complete X tiles is returned. This allows for the case
    where the mosaic repeat loop was unused.
    """

    def __init__(self):
        super().__init__(constant_name=DlnirspBudName.num_spatial_steps_X.value)

    def getter(self, key: str) -> int:
        """
        Return the number of X tiles.

        If multiple mosaic repeats exist then all X tiles are required to be complete, but if only a single mosaic
        repeat exists then the total number of X tiles is considered to be the number of *completed* X tiles.

        A check is also made that the set of X tiles is continuous from 0 to the number of X tiles.
        """
        num_files_per_mosaic = self.num_files_per_mosaic_piece("mosaic_num")
        complete_mosaic_nums = self.complete_piece_list(num_files_per_mosaic)

        num_mosaics = len(complete_mosaic_nums)

        num_files_per_X_tile = self.num_files_per_mosaic_piece("X_tile")
        if num_mosaics > 1:
            all_X_tiles = sorted(list(num_files_per_X_tile.keys()))
            num_X_tiles = len(all_X_tiles)
            if all_X_tiles != list(range(num_X_tiles)):
                raise ValueError(
                    f"Whole X tiles are missing. This is extremely strange. Found {all_X_tiles}"
                )
            return num_X_tiles

        completed_X_tiles = self.complete_piece_list(num_files_per_X_tile)

        num_X_tiles = len(completed_X_tiles)
        sorted_complete_X_tiles = sorted(completed_X_tiles)
        if sorted_complete_X_tiles != list(range(num_X_tiles)):
            raise ValueError(
                f"Not all sequential X tiles could be found. Found {sorted_complete_X_tiles}"
            )

        return num_X_tiles


class NumYTilesBud(NumMosaicPieceBase):
    """
    Bud for determining the number of Y tiles.

    If the dataset includes multiple complete mosaic repeats and X tiles then all found Y tiles are expected to be
    completed. If only a single mosaic repeat AND X tile exists then the number of complete Y tiles is returned.
    This allows for the case where the mosaic repeat and X tile loops were unused.
    """

    def __init__(self):
        super().__init__(constant_name=DlnirspBudName.num_spatial_steps_Y.value)

    def getter(self, key: str) -> int:
        """
        Return the number of Y tiles.

        If multiple mosaic repeats and X tiles exist then all Y tiles are required to be complete, but if only a single
        mosaic repeat AND X tile exists then the total number of Y tiles is considered to be the number of *completed*
        Y tiles.

        A check is also made that the set of Y tiles is continuous from 0 to the number of Y tiles.
        """
        num_files_per_mosaic = self.num_files_per_mosaic_piece("mosaic_num")
        complete_mosaic_nums = self.complete_piece_list(num_files_per_mosaic)
        num_mosaics = len(complete_mosaic_nums)

        num_files_per_X_tile = self.num_files_per_mosaic_piece("X_tile")
        completed_X_tiles = self.complete_piece_list(num_files_per_X_tile)
        num_X_tiles = len(completed_X_tiles)

        num_files_per_Y_tile = self.num_files_per_mosaic_piece("Y_tile")
        if num_mosaics > 1 or num_X_tiles > 1:
            # The logic of this conditional is pretty subtle so here's an explanation:
            # If ANY higher-level loop has more than one iteration then ALL lower-level loops will be required
            # to be complete. This is why this is `or` instead of `and`. For example if num_mosaics = 3 but the X tile
            # loop was not used (num_X_tiles = 1) we still need all Y tiles.
            all_Y_tiles = sorted(list(num_files_per_Y_tile.keys()))
            num_Y_tiles = len(all_Y_tiles)
            if all_Y_tiles != list(range(num_Y_tiles)):
                raise ValueError(
                    f"Whole Y tiles are missing. This is extremely strange. Found {all_Y_tiles}"
                )
            return num_Y_tiles

        completed_Y_tiles = self.complete_piece_list(num_files_per_Y_tile)
        num_Y_tiles = len(completed_Y_tiles)
        sorted_complete_Y_tiles = sorted(completed_Y_tiles)
        if sorted_complete_Y_tiles != list(range(num_Y_tiles)):
            raise ValueError(
                f"Not all sequential Y tiles could be found. Found {sorted_complete_Y_tiles}"
            )

        return num_Y_tiles
