from datetime import datetime
from typing import List, Literal, Optional, Union

import pydantic
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from classiq.interface.executor.estimation import OperatorsEstimation
from classiq.interface.executor.execution_preferences import ExecutionPreferences
from classiq.interface.executor.quantum_code import QuantumCode
from classiq.interface.generator.quantum_program import QuantumProgram
from classiq.interface.helpers.custom_encoders import CUSTOM_ENCODERS
from classiq.interface.helpers.versioned_model import VersionedModel
from classiq.interface.jobs import JobStatus


class QuantumProgramExecution(QuantumProgram):
    execution_type: Literal["quantum_program2"] = "quantum_program2"


class QuantumCodeExecution(QuantumCode):
    execution_type: Literal["quantum_code"] = "quantum_code"


class EstimateOperatorsExecution(OperatorsEstimation):
    execution_type: Literal["estimate_operators"] = "estimate_operators"


ExecutionPayloads = Annotated[
    Union[QuantumProgramExecution, QuantumCodeExecution, EstimateOperatorsExecution],
    Field(discriminator="execution_type"),
]


class ExecutionRequest(BaseModel, json_encoders=CUSTOM_ENCODERS):
    execution_payload: ExecutionPayloads
    preferences: ExecutionPreferences = pydantic.Field(
        default_factory=ExecutionPreferences,
        description="preferences for the execution",
    )


class QuantumProgramExecutionRequest(ExecutionRequest):
    execution_payload: QuantumCodeExecution


class ExecutionJobDetails(VersionedModel):
    id: str

    name: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]

    provider: Optional[str]
    backend_name: Optional[str]

    status: JobStatus

    num_shots: Optional[int]
    program_id: Optional[str]

    error: Optional[str]


class ExecutionJobsQueryResults(VersionedModel):
    results: List[ExecutionJobDetails]
