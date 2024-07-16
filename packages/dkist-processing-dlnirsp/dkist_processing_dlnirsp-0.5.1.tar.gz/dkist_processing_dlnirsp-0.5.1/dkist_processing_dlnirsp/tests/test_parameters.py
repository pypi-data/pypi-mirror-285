from dataclasses import asdict
from dataclasses import dataclass

import numpy as np
import pytest

from dkist_processing_dlnirsp.models.parameters import DlnirspParameters
from dkist_processing_dlnirsp.models.parameters import DlnirspParsingParameters
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters

# The property names of all parameters on `DlnirspParsingParameters`
PARSE_PARAMETER_NAMES = [
    k for k, v in vars(DlnirspParsingParameters).items() if isinstance(v, property)
]


class Task(DlnirspTaskBase):
    def run(self):
        pass


@pytest.fixture
def task_with_parameters(
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    link_constants_db,
    arm_id,
    default_obs_ip_start_time,
    vis_group_id_file_parameter,
    vis_dispersion_file_parameter,
    vis_ifu_x_pos_file_parameter,
    vis_ifu_y_pos_file_parameter,
    jband_group_id_file_parameter,
    jband_dispersion_file_parameter,
    jband_ifu_x_pos_file_parameter,
    jband_ifu_y_pos_file_parameter,
    hband_group_id_file_parameter,
    hband_dispersion_file_parameter,
    hband_ifu_x_pos_file_parameter,
    hband_ifu_y_pos_file_parameter,
):
    def make_task(parameter_class=DlnirspParameters, obs_ip_start_time=default_obs_ip_start_time):
        link_constants_db(
            recipe_run_id=recipe_run_id,
            constants_obj=DlnirspTestingConstants(),
        )
        with Task(
            recipe_run_id=recipe_run_id,
            workflow_name="workflow_name",
            workflow_version="workflow_version",
        ) as task:

            parameters = DlnirspTestingParameters(
                dlnirsp_group_id_file_vis=vis_group_id_file_parameter,
                dlnirsp_geo_dispersion_file_vis=vis_dispersion_file_parameter,
                dlnirsp_ifu_x_pos_file_vis=vis_ifu_x_pos_file_parameter,
                dlnirsp_ifu_y_pos_file_vis=vis_ifu_y_pos_file_parameter,
                dlnirsp_group_id_file_jband=jband_group_id_file_parameter,
                dlnirsp_geo_dispersion_file_jband=jband_dispersion_file_parameter,
                dlnirsp_ifu_x_pos_file_jband=jband_ifu_x_pos_file_parameter,
                dlnirsp_ifu_y_pos_file_jband=jband_ifu_y_pos_file_parameter,
                dlnirsp_group_id_file_hband=hband_group_id_file_parameter,
                dlnirsp_geo_dispersion_file_hband=hband_dispersion_file_parameter,
                dlnirsp_ifu_x_pos_file_hband=hband_ifu_x_pos_file_parameter,
                dlnirsp_ifu_y_pos_file_hband=hband_ifu_y_pos_file_parameter,
            )
            assign_input_dataset_doc_to_task(
                task=task,
                parameters=parameters,
                parameter_class=parameter_class,
                arm_id=arm_id,
                obs_ip_start_time=obs_ip_start_time,
            )

            yield task, parameters
            task.constants._purge()
            task.scratch.purge()

    return make_task


# These params are capitalized on purpose
@pytest.mark.parametrize(
    "arm_id", [pytest.param("VIS"), pytest.param("JBand"), pytest.param("HBand")]
)
def test_files_parameters(task_with_parameters, request, arm_id):
    """
    Given: A task with parameters
    When: Accessing the group_id parameter
    Then: The correct array is returned
    """
    # This might just be a test of the fixturization of our test environment. But it's still useful for that.
    cased_arm_id = arm_id.casefold()
    expected_group_id_array = request.getfixturevalue(f"{cased_arm_id}_group_id_array")
    expcted_dispersion_array = request.getfixturevalue(f"{cased_arm_id}_dispersion_array")
    expected_ifu_x_pos_array = request.getfixturevalue(f"{cased_arm_id}_ifu_x_pos_array")
    expected_ifu_y_pos_array = request.getfixturevalue(f"{cased_arm_id}_ifu_y_pos_array")

    task, _ = next(task_with_parameters(parameter_class=DlnirspParameters))
    assert np.array_equal(task.parameters.group_id_array, expected_group_id_array, equal_nan=True)
    assert np.array_equal(
        task.parameters.geo_dispersion_array,
        expcted_dispersion_array,
        equal_nan=True,
    )
    assert np.array_equal(task.parameters.ifu_x_pos_array, expected_ifu_x_pos_array, equal_nan=True)
    assert np.array_equal(task.parameters.ifu_y_pos_array, expected_ifu_y_pos_array, equal_nan=True)


@pytest.mark.parametrize("arm_id", [pytest.param("VIS")])
def test_parse_parameters(task_with_parameters):
    """
    Given: A Science task with Parsing parameters
    When: Accessing properties for Parse parameters
    Then: The correct value is returned
    """
    task, expected = next(
        task_with_parameters(
            parameter_class=DlnirspParsingParameters,
            obs_ip_start_time=None,
        )
    )
    task_param_attr = task.parameters
    for pn, pv in asdict(expected).items():
        property_name = pn.removeprefix("dlnirsp_")
        if property_name in PARSE_PARAMETER_NAMES and type(pv) is not dict:
            assert getattr(task_param_attr, property_name) == pv
