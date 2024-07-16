"""
Workflow for trial runs.

These runs send their outputs (as well as intermediate files) to a special location that isn't published. This
allows the DC to coordinate with, e.g., instrument scientists to assess the performance of the pipeline (when
comissioning new modes, for example).
"""
from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialDatasetInventory
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TrialTeardown
from dkist_processing_core import Workflow

from dkist_processing_dlnirsp.tasks import AssembleDlnirspMovie
from dkist_processing_dlnirsp.tasks import DarkCalibration
from dkist_processing_dlnirsp.tasks import DlnirspAssembleQualityData
from dkist_processing_dlnirsp.tasks import DlnirspL0QualityMetrics
from dkist_processing_dlnirsp.tasks import DlnirspL1QualityMetrics
from dkist_processing_dlnirsp.tasks import DlnirspWriteL1Frame
from dkist_processing_dlnirsp.tasks import GeometricCalibration
from dkist_processing_dlnirsp.tasks import InstrumentPolarizationCalibration
from dkist_processing_dlnirsp.tasks import LampCalibration
from dkist_processing_dlnirsp.tasks import LinearityCorrection
from dkist_processing_dlnirsp.tasks import MakeDlnirspMovieFrames
from dkist_processing_dlnirsp.tasks import ParseL0DlnirspLinearizedData
from dkist_processing_dlnirsp.tasks import ParseL0DlnirspRampData
from dkist_processing_dlnirsp.tasks import ScienceCalibration
from dkist_processing_dlnirsp.tasks import SolarCalibration
from dkist_processing_dlnirsp.tasks.trial_output_data import TransferDlnirspTrialData

trial_pipeline = Workflow(
    category="dlnirsp",
    input_data="l0",
    output_data="l1",
    detail="full-trial",
    workflow_package=__package__,
)

trial_pipeline.add_node(task=TransferL0Data, upstreams=None)

# Science flow
trial_pipeline.add_node(task=ParseL0DlnirspRampData, upstreams=TransferL0Data)
trial_pipeline.add_node(task=LinearityCorrection, upstreams=ParseL0DlnirspRampData)
trial_pipeline.add_node(task=ParseL0DlnirspLinearizedData, upstreams=LinearityCorrection)
trial_pipeline.add_node(task=DarkCalibration, upstreams=ParseL0DlnirspLinearizedData)
trial_pipeline.add_node(task=LampCalibration, upstreams=DarkCalibration)
trial_pipeline.add_node(task=GeometricCalibration, upstreams=LampCalibration)
trial_pipeline.add_node(task=SolarCalibration, upstreams=GeometricCalibration)
trial_pipeline.add_node(
    task=InstrumentPolarizationCalibration, upstreams=ParseL0DlnirspLinearizedData
)
trial_pipeline.add_node(
    task=ScienceCalibration, upstreams=[InstrumentPolarizationCalibration, SolarCalibration]
)
trial_pipeline.add_node(task=DlnirspWriteL1Frame, upstreams=ScienceCalibration)

# Movie flow
trial_pipeline.add_node(task=MakeDlnirspMovieFrames, upstreams=DlnirspWriteL1Frame)
trial_pipeline.add_node(task=AssembleDlnirspMovie, upstreams=MakeDlnirspMovieFrames)

# Quality flow
trial_pipeline.add_node(task=DlnirspL0QualityMetrics, upstreams=ParseL0DlnirspLinearizedData)
trial_pipeline.add_node(task=DlnirspL1QualityMetrics, upstreams=DlnirspWriteL1Frame)
trial_pipeline.add_node(task=QualityL1Metrics, upstreams=DlnirspWriteL1Frame)
trial_pipeline.add_node(
    task=DlnirspAssembleQualityData,
    upstreams=[DlnirspL0QualityMetrics, DlnirspL1QualityMetrics, QualityL1Metrics],
)

# Trial Data Generation
trial_pipeline.add_node(
    task=CreateTrialDatasetInventory, upstreams=DlnirspWriteL1Frame, pip_extras=["inventory"]
)
trial_pipeline.add_node(task=CreateTrialAsdf, upstreams=DlnirspWriteL1Frame, pip_extras=["asdf"])
trial_pipeline.add_node(
    task=CreateTrialQualityReport, upstreams=DlnirspAssembleQualityData, pip_extras=["quality"]
)

# Output
trial_pipeline.add_node(
    task=TransferDlnirspTrialData,
    upstreams=[
        AssembleDlnirspMovie,
        CreateTrialDatasetInventory,
        CreateTrialAsdf,
        CreateTrialQualityReport,
    ],
)

trial_pipeline.add_node(task=TrialTeardown, upstreams=TransferDlnirspTrialData)
