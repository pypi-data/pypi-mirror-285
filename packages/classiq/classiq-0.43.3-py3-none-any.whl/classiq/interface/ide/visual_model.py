from typing import Dict, List, Optional, Tuple

import pydantic

from classiq.interface.generator.hardware.hardware_data import SynthesisHardwareData
from classiq.interface.helpers.versioned_model import VersionedModel

from classiq._internals.enum_utils import StrEnum


class OperationLevel(StrEnum):
    USER_DEFINED = "USER_DEFINED"
    ENGINE_GENERATED = "ENGINE_GENERATED"
    BASIS_GATE = "BASIS_GATE"
    UNKNOWN = "UNKNOWN"


class OperationType(StrEnum):
    REGULAR = "REGULAR"
    VAR_INITIALIZATION = "VAR_INITIALIZATION"
    BIND = "BIND"


class OperationData(pydantic.BaseModel):
    approximated_depth: Optional[int]
    width: int
    gate_count: Dict[str, int] = pydantic.Field(default_factory=dict)


class ProgramData(pydantic.BaseModel):
    hardware_data: SynthesisHardwareData


class OperationParameter(pydantic.BaseModel):
    label: str
    value: Optional[float]


class OperationLink(pydantic.BaseModel):
    label: str
    qubits: Tuple[int, ...]
    type: str


class OperationLinks(pydantic.BaseModel):
    inputs: List[OperationLink]
    outputs: List[OperationLink]


class Operation(pydantic.BaseModel):
    name: str
    children: List["Operation"]
    operation_data: Optional[OperationData]
    operation_links: OperationLinks
    control_qubits: Tuple[int, ...] = pydantic.Field(default_factory=tuple)
    auxiliary_qubits: Tuple[int, ...]
    target_qubits: Tuple[int, ...]
    parameters: List[OperationParameter] = pydantic.Field(default_factory=list)
    operation_level: OperationLevel
    # This field is meant to identify unique operations, such as variable initialization
    # These will be visualized differently. We don't identify them yet, though, so
    # we always set this field to be REGULAR
    operation_type: OperationType = pydantic.Field(default=OperationType.REGULAR)


class ProgramVisualModel(VersionedModel):
    main_operation: Operation
    program_data: ProgramData
