import numpy as np
import pytest
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_header_validator.translator import translate_spec122_to_spec214_l0
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_dlnirsp.models.constants import DlnirspBudName
from dkist_processing_dlnirsp.models.parameters import DlnirspParsingParameters
from dkist_processing_dlnirsp.models.tags import DlnirspStemName
from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspRampFitsAccess
from dkist_processing_dlnirsp.tasks.parse import ParseL0DlnirspLinearizedData
from dkist_processing_dlnirsp.tasks.parse import ParseL0DlnirspRampData
from dkist_processing_dlnirsp.tests.conftest import _write_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import AbortedMosaicObserveHeaders
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import make_random_data
from dkist_processing_dlnirsp.tests.conftest import MissingMosaicStepObserveHeaders
from dkist_processing_dlnirsp.tests.conftest import MissingXStepObserveHeaders
from dkist_processing_dlnirsp.tests.conftest import MissingYStepObserveHeaders
from dkist_processing_dlnirsp.tests.conftest import RawRampHeaders
from dkist_processing_dlnirsp.tests.conftest import write_dark_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_lamp_gain_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_observe_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_polcal_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_solar_gain_frames_to_task


@pytest.fixture
def raw_ramp_parse_task(tmp_path, recipe_run_id, arm_id):
    num_ramps = 3
    num_NDR_per_ramp = 2
    start_date = "2023-01-01T01:23:45"
    ramp_length_sec = 1.0
    array_shape = (10, 10)
    with ParseL0DlnirspRampData(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        frame_generator = RawRampHeaders(
            array_shape=array_shape,
            num_ramps=num_ramps,
            num_NDR_per_ramp=num_NDR_per_ramp,
            start_date=start_date,
            ramp_length_sec=ramp_length_sec,
            arm_id=arm_id,
        )
        for frame in frame_generator:
            header = frame.header()
            data = np.random.randint(0, 4e5, array_shape).astype(np.int16)
            translated_header = fits.Header(translate_spec122_to_spec214_l0(header))
            hdul = fits.HDUList(
                [fits.PrimaryHDU(), fits.CompImageHDU(data=data, header=translated_header)]
            )
            task.write(
                data=hdul,
                tags=[DlnirspTag.input(), DlnirspTag.frame()],
                encoder=fits_hdulist_encoder,
            )

        yield task, num_ramps, num_NDR_per_ramp, start_date, ramp_length_sec
        task.scratch.purge()
        task.constants._purge()


@pytest.mark.parametrize("arm_id", [pytest.param("HBand", id="IR"), pytest.param("VIS", id="VIS")])
def test_parse_ramp_data(raw_ramp_parse_task, arm_id):
    """
    Given: A ParseL0DlnirspRampData task with raw ramp data
    When: Parsing the input frames
    Then: Constants and tags are updated/applied correctly
    """
    task, num_ramps, num_NDR_per_ramp, start_date, ramp_length_sec = raw_ramp_parse_task

    task()

    # Constants
    start_date_obj = Time(start_date)
    time_delta = TimeDelta(ramp_length_sec, format="sec")
    expected_obs_time_list = [(start_date_obj + time_delta * i).fits for i in range(num_ramps)]
    assert task.constants._db_dict[DlnirspBudName.arm_id.value] == arm_id
    if arm_id == "VIS":
        return

    assert task.constants._db_dict[DlnirspBudName.camera_readout_mode.value] == "UpTheRamp"
    assert task.constants._db_dict[DlnirspBudName.time_obs_list.value] == expected_obs_time_list

    # Tags
    for ramp_time in expected_obs_time_list:
        fits_obj_list = list(
            task.read(
                tags=[DlnirspTag.time_obs(ramp_time)],
                decoder=fits_access_decoder,
                fits_access_class=DlnirspRampFitsAccess,
            )
        )
        assert len(fits_obj_list) == num_NDR_per_ramp
        for fits_obj in fits_obj_list:
            header_curr_frame = fits_obj.header["DLCAMCUR"]
            tags = task.tags(fits_obj.name)
            tag_curr_frame = [
                int(t.split("_")[-1])
                for t in tags
                if DlnirspStemName.current_frame_in_ramp.value in t
            ][0]
            assert header_curr_frame == tag_curr_frame


@pytest.fixture
def linearized_parse_task(tmp_path, recipe_run_id, assign_input_dataset_doc_to_task):
    with ParseL0DlnirspLinearizedData(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task=task,
            parameters=DlnirspTestingParameters(),
            parameter_class=DlnirspParsingParameters,
            obs_ip_start_time=None,
        )

        yield task
        task.constants._purge()
        task.scratch.purge()


def test_parse_linearized_data(linearized_parse_task):
    """
    Given: A set of LINEARIZED frames and a Parse task
    When: Parsing the frames
    Then: The frames are tagged correctly and constants are populated correctly
    """

    task = linearized_parse_task

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    num_mod = 8
    num_mosaic = 4
    num_X_tile = 3
    num_Y_tile = 2
    num_data_cycles = 2
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, polcal_exp_time, unused_exp_time]

    num_dark = 0
    lin_tag = [DlnirspTag.linearized()]
    for exp_time in dark_exp_times:
        num_dark += write_dark_frames_to_task(task, exp_time_ms=exp_time, tags=lin_tag)
    num_lamp = write_lamp_gain_frames_to_task(task, tags=lin_tag)
    num_solar = write_solar_gain_frames_to_task(task, tags=lin_tag)
    num_polcal = write_polcal_frames_to_task(task, tags=lin_tag)
    num_obs = write_observe_frames_to_task(
        task,
        num_modstates=num_mod,
        num_mosaics=num_mosaic,
        num_X_tiles=num_X_tile,
        num_Y_tiles=num_Y_tile,
        num_data_cycles=num_data_cycles,
        tags=lin_tag,
    )

    task()

    # Tags applied correctly
    assert len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_dark()]))) == num_dark
    assert (
        len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_lamp_gain()])))
        == num_lamp
    )
    assert (
        len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_solar_gain()])))
        == num_solar
    )
    assert (
        len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_polcal()]))) == num_polcal
    )
    assert (
        len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_observe()]))) == num_obs
    )

    for task_name, exp_times in zip(
        [
            TaskName.dark.value,
            TaskName.lamp_gain.value,
            TaskName.solar_gain.value,
            TaskName.polcal.value,
        ],
        [dark_exp_times, [lamp_exp_time], [solar_exp_time], [polcal_exp_time]],
    ):
        for exp in exp_times:
            for modstate in range(1, num_mod + 1):
                tags = [
                    DlnirspTag.frame(),
                    DlnirspTag.linearized(),
                    DlnirspTag.task(task_name),
                    DlnirspTag.exposure_time(exp),
                    DlnirspTag.modstate(modstate),
                ]
                assert len(list(task.read(tags=tags))) == 1

    # Observe frames are special because we want to check for mosaic stuff
    for mosaic in range(num_mosaic):
        for X_tile in range(num_X_tile):
            for Y_tile in range(num_Y_tile):
                for modstate in range(1, num_mod + 1):
                    tags = [
                        DlnirspTag.frame(),
                        DlnirspTag.linearized(),
                        DlnirspTag.task_observe(),
                        DlnirspTag.exposure_time(obs_exp_time),
                        DlnirspTag.mosaic_num(mosaic),
                        DlnirspTag.tile_X_num(X_tile),
                        DlnirspTag.tile_Y_num(Y_tile),
                        DlnirspTag.modstate(modstate),
                    ]
                    assert len(list(task.read(tags=tags))) == num_data_cycles

    # Constants loaded correctly
    assert task.constants._db_dict[DlnirspBudName.wavelength] == 1565.0
    assert task.constants._db_dict[DlnirspBudName.polarimeter_mode] == "Full Stokes"
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_mod
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_repeats] == num_mosaic
    assert task.constants._db_dict[DlnirspBudName.num_spatial_steps_X] == num_X_tile
    assert task.constants._db_dict[DlnirspBudName.num_spatial_steps_Y] == num_Y_tile
    assert task.constants._db_dict[DlnirspBudName.lamp_gain_exposure_times] == [lamp_exp_time]
    assert task.constants._db_dict[DlnirspBudName.solar_gain_exposure_times] == [solar_exp_time]
    assert task.constants._db_dict[DlnirspBudName.observe_exposure_times] == [obs_exp_time]
    assert task.constants._db_dict[DlnirspBudName.polcal_exposure_times] == [polcal_exp_time]


@pytest.mark.parametrize(
    "abort_loop",
    [
        pytest.param("mosaic"),
        pytest.param("X_tile"),
        pytest.param("Y_tile"),
        pytest.param("data_cycle"),
        pytest.param("modstate"),
    ],
)
def test_parse_aborted_mosaic(linearized_parse_task, abort_loop):
    """
    Given: A Parse task and a set of data with multiple mosaics and the last mosaic aborted at various loop levels
    When: Parsing the data
    Then: The number of mosaics is correctly set to the number of *completed* mosaics
    """
    task = linearized_parse_task

    num_mosaics = 3
    num_X_tiles = 3
    num_Y_tiles = 2
    num_data_cycles = 3
    num_modstates = 2

    frame_generator = AbortedMosaicObserveHeaders(
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        num_data_cycles=num_data_cycles,
        num_modstates=num_modstates,
        aborted_loop_level=abort_loop,
        array_shape=(10, 10),
    )

    _write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    expected_num_mosaics = num_mosaics - 1

    task()
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_repeats] == expected_num_mosaics
    assert task.constants._db_dict[DlnirspBudName.num_spatial_steps_X] == num_X_tiles
    assert task.constants._db_dict[DlnirspBudName.num_spatial_steps_Y] == num_Y_tiles
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_modstates


@pytest.mark.parametrize(
    "abort_loop",
    [
        pytest.param("X_tile"),
        pytest.param("Y_tile"),
        pytest.param("data_cycle"),
        pytest.param("modstate"),
    ],
)
def test_parse_aborted_single_mosaic(linearized_parse_task, abort_loop):
    """
    Given: A Parse task and a set of data with a single mosaic and the last X tile aborted at various loop levels
    When: Parsing the data
    Then: The number of X tiles is correctly set to the number of *completed* X tiles
    """
    task = linearized_parse_task

    num_mosaics = 1
    num_X_tiles = 3
    num_Y_tiles = 2
    num_data_cycles = 3
    num_modstates = 2

    frame_generator = AbortedMosaicObserveHeaders(
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        num_data_cycles=num_data_cycles,
        num_modstates=num_modstates,
        aborted_loop_level=abort_loop,
        array_shape=(10, 10),
    )

    _write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    expected_X_tiles = num_X_tiles - 1

    task()
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_repeats] == 1
    assert task.constants._db_dict[DlnirspBudName.num_spatial_steps_X] == expected_X_tiles
    assert task.constants._db_dict[DlnirspBudName.num_spatial_steps_Y] == num_Y_tiles
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_modstates


@pytest.mark.parametrize(
    "abort_loop", [pytest.param("Y_tile"), pytest.param("data_cycle"), pytest.param("modstate")]
)
def test_parse_aborted_single_X_tile(linearized_parse_task, abort_loop):
    """
    Given: A Parse task and a set of data with a single mosaic and X tile and the last Y tile aborted at various loop levels
    When: Parsing the data
    Then: The number of Y tiles is correctly set to the number of *completed* Y tiles
    """
    task = linearized_parse_task

    num_mosaics = 1
    num_X_tiles = 1
    num_Y_tiles = 2
    num_data_cycles = 3
    num_modstates = 2

    frame_generator = AbortedMosaicObserveHeaders(
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        num_data_cycles=num_data_cycles,
        num_modstates=num_modstates,
        aborted_loop_level=abort_loop,
        array_shape=(10, 10),
    )

    _write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    expected_Y_tiles = num_Y_tiles - 1

    task()
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_repeats] == 1
    assert task.constants._db_dict[DlnirspBudName.num_spatial_steps_X] == 1
    assert task.constants._db_dict[DlnirspBudName.num_spatial_steps_Y] == expected_Y_tiles
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_modstates


@pytest.mark.parametrize(
    "frame_generator_class, error_name",
    [
        pytest.param(
            MissingMosaicStepObserveHeaders,
            "mosaic repeats",
            id="Mosaic",
        ),
        pytest.param(
            MissingXStepObserveHeaders,
            "X tiles",
            id="X_tile",
        ),
        pytest.param(
            MissingYStepObserveHeaders,
            "Y tiles",
            id="Y_tile",
        ),
    ],
)
def test_parse_aborted_single_loop_failures(
    linearized_parse_task, frame_generator_class, error_name
):
    """
    Given: A Parse task and a set of data where all three of mosaic, X_tile, and Y_tile loops contain missing data
    When: Parsing the data
    Then: The correct error is raised
    """
    task = linearized_parse_task

    frame_generator = frame_generator_class(array_shape=(10, 10))

    _write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    with pytest.raises(
        ValueError,
        match=f"Not all sequential {error_name} could be found.",
    ):
        task()


@pytest.mark.parametrize(
    "frame_generator, error_name",
    [
        pytest.param(
            MissingXStepObserveHeaders(array_shape=(3, 3), num_mosaics=2),
            "X tiles",
            id="X_tile",
        ),
        pytest.param(
            MissingYStepObserveHeaders(array_shape=(3, 3), num_X_tiles=2),
            "Y tiles",
            id="Y_tile",
        ),
    ],
)
def test_parse_missing_loop_failures(linearized_parse_task, frame_generator, error_name):
    """
    Given: A Parse task and a set of data where all three of mosaic, X_tile, and Y_tile loops contain missing data
    When: Parsing the data
    Then: The correct error is raised
    """
    task = linearized_parse_task

    _write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    with pytest.raises(
        ValueError,
        match=f"Whole {error_name} are missing. This is extremely strange.",
    ):
        task()
