from enum import IntEnum
from typing import Dict, List, Optional, Union

import pydantic

from classiq.interface.generator.generated_circuit_data import GeneratedFunction
from classiq.interface.generator.hardware.hardware_data import SynthesisHardwareData
from classiq.interface.helpers.versioned_model import VersionedModel

GateCount = Dict[str, int]
Depth = int


class IDEDataQubit(pydantic.BaseModel):
    id: int
    numChildren: Optional[int]
    name: Optional[str]


class IDEQubitDef(pydantic.BaseModel):
    qId: int


class RegisterType(IntEnum):
    QUBIT = 0
    CLASSICAL = 1


class IDEClassicalBitDef(pydantic.BaseModel):
    type: RegisterType
    qId: int
    cId: int


class DataAttributes(pydantic.BaseModel):
    tooltip: Optional[GeneratedFunction] = None
    expanded: str = ""
    controlStates: str = ""
    id: str = ""
    zoom_out: str = ""
    zoom_in: str = ""


class ConditionalRender(IntEnum):
    ALWAYS = 0
    ON_ZERO = 1
    ON_ONE = 2
    AS_GROUP = 3


class IDEDataOperation(pydantic.BaseModel):
    gate: str
    displayName: str
    children: List["IDEDataOperation"]
    depth: Depth
    width: int
    gate_count: GateCount
    _qubits: list = pydantic.PrivateAttr()  # list[Qubit]

    displayArgs: str = ""
    targets: Union[List[IDEQubitDef], List[IDEClassicalBitDef]] = pydantic.Field(
        default_factory=list
    )
    controls: List[IDEQubitDef] = list()
    dataAttributes: DataAttributes = pydantic.Field(default_factory=DataAttributes)
    isControlled: bool = False
    isMeasurement: bool = False
    isConditional: bool = False
    isAdjoint: bool = False
    conditional_render: Optional[ConditionalRender] = None

    @property
    def qubits(self) -> list:  # list[Qubit]
        return self._qubits


class IDEDataProperties(pydantic.BaseModel):
    color: Optional[str]
    rightLabel: Optional[str]
    leftLabel: Optional[str]


class RegisterData(pydantic.BaseModel):
    segmentIds: List[str]
    properties: IDEDataProperties
    registerId: str


class InterfaceSegmentData(pydantic.BaseModel):
    segmentId: str
    properties: IDEDataProperties


class CircuitMetrics(pydantic.BaseModel):
    depth: int
    count_ops: Dict[str, int]


class IDEData(VersionedModel):
    qubits: List[IDEDataQubit]
    operations: List[IDEDataOperation]
    register_data: List[RegisterData]
    segment_data: List[InterfaceSegmentData]
    circuit_metrics: Optional[CircuitMetrics]
    hardware_data: SynthesisHardwareData
    creation_time: str
