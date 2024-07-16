from functools import partial

import numpy as np
import pytest
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tests.conftest import FakeGQLClient

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks import LinearityCorrection
from dkist_processing_dlnirsp.tests.conftest import _write_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import AbortedRampHeaders
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import RawRampHeaders
from dkist_processing_dlnirsp.tests.conftest import SimpleModulatedHeaders


@pytest.fixture
def linearity_correction_task(recipe_run_id, tmp_path):
    with LinearityCorrection(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(recipe_run_id=recipe_run_id, scratch_base_path=tmp_path)

        yield task

        task._purge()


def write_ramps_to_task(task, num_ramps: int, arm_id: str):
    start_date = "2024-04-20T16:20:00.00"
    ramp_length_sec = 3.0
    bias_value = 5.0
    num_NDR_per_ramp = 5

    start_date_obj = Time(start_date)
    time_delta = TimeDelta(ramp_length_sec, format="sec")
    expected_obs_time_list = [(start_date_obj + time_delta * i).fits for i in range(num_ramps)]

    ramp_data_func = partial(make_ramp_data, bias=bias_value)

    dataset = RawRampHeaders(
        array_shape=(1, 10, 10),
        num_ramps=num_ramps,
        num_NDR_per_ramp=num_NDR_per_ramp,
        ramp_length_sec=ramp_length_sec,
        start_date=start_date,
        arm_id=arm_id,
    )

    _write_frames_to_task(
        task=task,
        frame_generator=dataset,
        data_func=ramp_data_func,
        extra_tags=[DlnirspTag.input()],
        tag_func=tag_on_time_obs,
    )

    return expected_obs_time_list, bias_value, num_NDR_per_ramp


def write_skipable_ramps_to_task(task):

    # Write one good frame
    good_start_date = write_ramps_to_task(task, num_ramps=1, arm_id="JBand")[0][0]

    ramp_data_func = partial(make_ramp_data, bias=1.0)

    # Write one aborted ramp
    aborted_start_date = "2024-06-28T11:55:30.230"  # Needs to be different than the start_date in `write_ramps_to_task`
    aborted_generator = AbortedRampHeaders(
        array_shape=(1, 10, 10), num_NDR_per_ramp=5, start_date=aborted_start_date
    )

    _write_frames_to_task(
        task,
        frame_generator=aborted_generator,
        data_func=ramp_data_func,
        extra_tags=[DlnirspTag.input()],
        tag_func=tag_on_time_obs,
    )

    # Write one ramp with weird header values
    bad_ramp_start_date = "2024-03-14T15:55:30.231"  # Needs to be different than the start_date in `write_ramps_to_task`
    bad_ramp_generator = AbortedRampHeaders(
        array_shape=(1, 10, 10), num_NDR_per_ramp=5, start_date=bad_ramp_start_date
    )

    _write_frames_to_task(
        task,
        frame_generator=bad_ramp_generator,
        data_func=ramp_data_func,
        extra_tags=[DlnirspTag.input()],
        tag_func=tag_on_time_obs,
    )

    return good_start_date, aborted_start_date, bad_ramp_start_date


def make_ramp_data(dataset: RawRampHeaders, bias: float):
    shape = dataset.array_shape

    if dataset.frame_in_ramp("") == 1:
        # Bias
        value = bias

    else:
        value = (dataset.current_ramp + 1) * 100.0 + dataset.frame_in_ramp("") * 10

    return np.ones(shape) * value


def write_vis_inputs_to_task(task, num_frames):
    dataset = SimpleModulatedHeaders(
        num_modstates=num_frames,
        array_shape=(1, 10, 10),
        task=TaskName.dark.value,
        exp_time_ms=10.0,
        arm_id="VIS",
    )

    _write_frames_to_task(
        task=task,
        frame_generator=dataset,
        data_func=make_vis_data,
        extra_tags=[DlnirspTag.input()],
        tag_func=tag_on_time_obs,
    )


def make_vis_data(frame: SimpleModulatedHeaders):
    modstate = frame.header()["DLN__015"]
    return np.ones(frame.array_shape) * modstate


def tag_on_time_obs(frame: RawRampHeaders):
    time_obs = frame.header()["DATE-OBS"]
    return [DlnirspTag.time_obs(time_obs)]


@pytest.mark.parametrize("arm_id", [pytest.param("JBand"), pytest.param("HBand")])
def test_linearity_correction(linearity_correction_task, link_constants_db, arm_id, mocker):
    """
    Given: A `LinearityCorrection` task and some raw INPUT frames
    When: Linearizing the data
    Then: The correct number of frames are produced and they have the expected linearized values
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    num_ramps = 3
    task = linearity_correction_task
    expected_time_obs_list, bias_value, num_NDR_per_ramp = write_ramps_to_task(
        task, num_ramps=num_ramps, arm_id=arm_id
    )

    link_constants_db(
        task.recipe_run_id,
        DlnirspTestingConstants(TIME_OBS_LIST=tuple(expected_time_obs_list), ARM_ID=arm_id),
    )

    task()

    assert len(list(task.read([DlnirspTag.frame(), DlnirspTag.linearized()]))) == num_ramps
    for ramp_num, time_obs in enumerate(expected_time_obs_list, start=1):
        files = list(
            task.read([DlnirspTag.frame(), DlnirspTag.linearized(), DlnirspTag.time_obs(time_obs)])
        )
        assert len(files) == 1
        # See `make_ramp_data` for where this comes from
        expected_value = ramp_num * 100 + num_NDR_per_ramp * 10 - bias_value
        data = fits.getdata(files[0])
        np.testing.assert_array_equal(data, expected_value)


def test_VIS_linearity_correction(linearity_correction_task, link_constants_db, mocker):
    """
    Given: A `LinearityCorrection` task and some raw visible INPUT frames
    When: Linearizing the data
    Then: The visible frames are re-tagged as LINEARIZED and their data are un-changed
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    num_frames = 3
    task = linearity_correction_task
    write_vis_inputs_to_task(task, num_frames=num_frames)

    link_constants_db(task.recipe_run_id, DlnirspTestingConstants(ARM_ID="VIS"))
    task()

    linearized_frame_list = list(task.read([DlnirspTag.frame(), DlnirspTag.linearized()]))
    assert len(linearized_frame_list) == num_frames

    # All INPUT frames should be retagged as LINEARIZED
    assert len(list(task.read([DlnirspTag.frame(), DlnirspTag.input()]))) == 0

    for path in linearized_frame_list:
        hdu = fits.open(path)[0]
        modstate = hdu.header["DLN__015"]  # See `make_vis_data`
        np.testing.assert_array_equal(hdu.data, modstate)


def test_linearity_correction_with_invalid_ramps(
    linearity_correction_task, link_constants_db, mocker
):
    """
    Given: A `LinearityCorrection` task and raw INPUT frames that include 2 invalid ramps
    When: Linearizing the data
    Then: The invalid ramps are not linearized
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    task = linearity_correction_task
    good_time, aborted_time, bad_time = write_skipable_ramps_to_task(task)
    time_obs_list = [good_time, aborted_time, bad_time]
    link_constants_db(
        task.recipe_run_id, DlnirspTestingConstants(TIME_OBS_LIST=tuple(time_obs_list))
    )

    task()

    assert len(list(task.read([DlnirspTag.frame(), DlnirspTag.linearized()]))) == 1
    assert (
        len(
            list(
                task.read(
                    [DlnirspTag.frame(), DlnirspTag.linearized(), DlnirspTag.time_obs(good_time)]
                )
            )
        )
        == 1
    )
    assert (
        len(
            list(
                task.read(
                    [DlnirspTag.frame(), DlnirspTag.linearized(), DlnirspTag.time_obs(aborted_time)]
                )
            )
        )
        == 0
    )
    assert (
        len(
            list(
                task.read(
                    [DlnirspTag.frame(), DlnirspTag.linearized(), DlnirspTag.time_obs(bad_time)]
                )
            )
        )
        == 0
    )
