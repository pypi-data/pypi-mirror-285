# Basically copied from ViSP
import json
from uuid import uuid4

import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.codecs.quality import quality_data_encoder
from dkist_processing_common.codecs.str import str_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tests.conftest import FakeGQLClient
from pydantic import BaseModel

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.trial_output_data import TransferDlnirspTrialData


@pytest.fixture
def recipe_run_configuration(
    debug_switch,
    intermediate_switch,
    output_switch,
    dataset_inventory_switch,
    asdf_switch,
    quality_report_switch,
    quality_data_switch,
    tag_lists,
):
    """Mock Recipe Run endpoint for trial output configuration flags"""

    class GQLClientWithConfiguration(FakeGQLClient):
        def execute_gql_query(self, **kwargs):
            response = super().execute_gql_query(**kwargs)
            response[0].configuration = json.dumps(
                {
                    "trial_transfer_debug_frames": bool(debug_switch),
                    "trial_transfer_intermediate_frames": bool(intermediate_switch),
                    "trial_transfer_output_frames": bool(output_switch),
                    "trial_transfer_output_dataset_inventory": bool(dataset_inventory_switch),
                    "trial_transfer_output_asdf": bool(asdf_switch),
                    "trial_transfer_output_quality_report": bool(quality_report_switch),
                    "trial_transfer_output_quality_data": bool(quality_data_switch),
                    "trial_transfer_tag_lists": tag_lists,
                }
            )
            return response

    return GQLClientWithConfiguration


intermediate_task_names = [
    TaskName.dark.value,
    TaskName.lamp_gain.value,
    TaskName.geometric.value,
    TaskName.solar_gain.value,
    TaskName.demodulation_matrices.value,
]

tag_lists = [[DlnirspTag.movie()], ["FOO", "BAR"]]


def write_debug_frames_to_task(task: TransferDlnirspTrialData) -> int:
    num_debug = 3
    for _ in range(num_debug):
        task.write(data="123", encoder=str_encoder, tags=[DlnirspTag.frame(), DlnirspTag.debug()])

    return num_debug


def write_intermediate_frames_to_task(task: TransferDlnirspTrialData) -> int:
    for task_name in intermediate_task_names:
        task.write(
            data=task_name,
            encoder=str_encoder,
            tags=[DlnirspTag.frame(), DlnirspTag.intermediate(), DlnirspTag.task(task_name)],
        )

    return len(intermediate_task_names)


def write_dummy_output_frames_to_task(task: TransferDlnirspTrialData) -> int:
    num_output = 2
    for i in range(num_output):
        task.write(
            data=f"output_{i}", encoder=str_encoder, tags=[DlnirspTag.frame(), DlnirspTag.output()]
        )

    return num_output


def write_specific_tags_to_task(task: TransferDlnirspTrialData) -> int:
    for tags in tag_lists:
        task.write(data="foo", encoder=str_encoder, tags=tags)

    return len(tag_lists)


def write_dataset_inventory_to_task(task: TransferDlnirspTrialData) -> int:
    dataset_inventory_obj: dict = {f"dataset_inventory_key": uuid4().hex}
    task.write(
        data=dataset_inventory_obj,
        encoder=json_encoder,
        tags=[DlnirspTag.output(), DlnirspTag.dataset_inventory()],
    )
    return 1


def write_asdf_to_task(task: TransferDlnirspTrialData) -> int:
    asdf_obj = uuid4().hex
    task.write(data=asdf_obj, encoder=str_encoder, tags=[DlnirspTag.output(), DlnirspTag.asdf()])
    return 1


def write_quality_report_to_task(task: TransferDlnirspTrialData) -> int:
    quality_report_obj = uuid4().hex.encode("utf-8")
    task.write(data=quality_report_obj, tags=[DlnirspTag.output(), DlnirspTag.quality_report()])
    return 1


def write_quality_data_to_task(task: TransferDlnirspTrialData) -> int:
    quality_data_obj: list[dict] = [{f"quality_key": uuid4().hex}]
    task.write(data=quality_data_obj, encoder=quality_data_encoder, tags=DlnirspTag.quality_data())
    return 1


def write_unused_frame_to_task(task: TransferDlnirspTrialData) -> int:
    task.write(data="bad", encoder=str_encoder, tags=["FOO"])
    return 1


class AvailableOutputFiles(BaseModel):
    """Number of files of each type available for potential output"""

    num_debug: int
    num_intermediate: int
    num_output: int
    num_specific: int
    num_dataset_inventory: int
    num_asdf: int
    num_quality_report: int
    num_quality_data: int


@pytest.fixture
def transfer_task_with_files(recipe_run_id, recipe_run_configuration, tmp_path, mocker):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
        new=recipe_run_configuration,
    )
    proposal_id = "test_proposal_id"
    with TransferDlnirspTrialData(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.constants._update({"PROPOSAL_ID": proposal_id})
        try:
            write_unused_frame_to_task(task)
            available_output_files = AvailableOutputFiles(
                num_debug=write_debug_frames_to_task(task),
                num_intermediate=write_intermediate_frames_to_task(task),
                num_output=write_dummy_output_frames_to_task(task),
                num_specific=write_specific_tags_to_task(task),
                num_dataset_inventory=write_dataset_inventory_to_task(task),
                num_asdf=write_asdf_to_task(task),
                num_quality_report=write_quality_report_to_task(task),
                num_quality_data=write_quality_data_to_task(task),
            )
            yield task, available_output_files

        finally:
            task._purge()


@pytest.mark.parametrize(
    "debug_switch, intermediate_switch, output_switch, dataset_inventory_switch, asdf_switch, quality_report_switch, quality_data_switch, tag_lists",
    [
        pytest.param(0, 0, 0, 0, 0, 0, 0, [], id="none"),
        pytest.param(1, 0, 0, 0, 0, 0, 0, [], id="debug_only"),
        pytest.param(0, 1, 0, 0, 0, 0, 0, [], id="intermediate_only"),
        pytest.param(0, 0, 1, 0, 0, 0, 0, [], id="output_only"),
        pytest.param(0, 0, 0, 1, 0, 0, 0, [], id="dataset_inventory_only"),
        pytest.param(0, 0, 0, 0, 1, 0, 0, [], id="asdf_only"),
        pytest.param(0, 0, 0, 0, 0, 1, 0, [], id="quality_report_only"),
        pytest.param(0, 0, 0, 0, 0, 0, 1, [], id="quality_data_only"),
        pytest.param(0, 0, 0, 0, 0, 0, 0, tag_lists, id="specific_only"),
        pytest.param(1, 1, 1, 1, 1, 1, 1, tag_lists, id="all"),
        pytest.param(1, 1, 0, 0, 0, 0, 0, tag_lists, id="combo_debug_intermediate_specific"),
        pytest.param(1, 1, 1, 0, 0, 0, 0, [], id="combo_debug_intermediate_output"),
        pytest.param(0, 1, 1, 0, 0, 0, 0, tag_lists, id="combo_intermediate_output_specific"),
        pytest.param(1, 0, 1, 0, 0, 0, 0, tag_lists, id="combo_debug_output_specific"),
    ],
)
def test_build_transfer_list(
    transfer_task_with_files,
    debug_switch,
    intermediate_switch,
    output_switch,
    dataset_inventory_switch,
    asdf_switch,
    quality_report_switch,
    quality_data_switch,
    tag_lists,
):
    """
    Given: A TransferDlnirspTrialData task with a recipe run configuration (RRC) and a collection of frames
    When: Building the transfer list
    Then: Only the files requested by the RRC switches are collected for transfer
    """
    task, available_output_files = transfer_task_with_files

    expected_num = 0
    if debug_switch:
        expected_num += available_output_files.num_debug
    if intermediate_switch:
        expected_num += available_output_files.num_intermediate
    if output_switch:
        expected_num += available_output_files.num_output
    if dataset_inventory_switch:
        expected_num += available_output_files.num_dataset_inventory
    if asdf_switch:
        expected_num += available_output_files.num_asdf
    if quality_report_switch:
        expected_num += available_output_files.num_quality_report
    if quality_data_switch:
        expected_num += available_output_files.num_quality_data
    if tag_lists:
        expected_num += available_output_files.num_specific

    transfer_list = task.build_transfer_list()
    assert len(transfer_list) == expected_num
