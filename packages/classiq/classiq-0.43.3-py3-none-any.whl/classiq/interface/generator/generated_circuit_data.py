from typing import Dict, List, Literal, Optional, Tuple, Union

import pydantic
from typing_extensions import TypeAlias

from classiq.interface.generator.control_state import ControlState
from classiq.interface.generator.register_role import RegisterRole
from classiq.interface.generator.synthesis_metadata.synthesis_execution_data import (
    ExecutionData,
)

ParameterName = str
IOQubitMapping: TypeAlias = Dict[str, Tuple[int, ...]]


CLASSIQ_HIERARCHY_SEPARATOR: Literal["."] = "."

VISUALIZATION_HIDE_LIST = [
    "apply_to_all",
    "repeat",
    "control",
    "mcx",
    "iteration",
    "operand",
]


def last_name_in_call_hierarchy(name: str) -> str:
    return name.split(CLASSIQ_HIERARCHY_SEPARATOR)[-1]


class QubitMapping(pydantic.BaseModel):
    logical_inputs: IOQubitMapping = pydantic.Field(default_factory=dict)
    logical_outputs: IOQubitMapping = pydantic.Field(default_factory=dict)
    physical_inputs: IOQubitMapping = pydantic.Field(default_factory=dict)
    physical_outputs: IOQubitMapping = pydantic.Field(default_factory=dict)


class GeneratedRegister(pydantic.BaseModel):
    name: str
    role: RegisterRole
    qubit_indexes_relative: List[int]
    qubit_indexes_absolute: List[int]

    def __len__(self) -> int:
        return self.qubit_indexes_relative.__len__()

    @property
    def width(self) -> int:
        return len(self)


class GeneratedFunction(pydantic.BaseModel):
    name: str
    control_states: List[ControlState]
    registers: List[GeneratedRegister] = list()
    depth: Optional[int]
    width: Optional[int]
    released_auxiliary_qubits: List[int] = list()
    dangling_inputs: Dict[str, GeneratedRegister] = dict()
    dangling_outputs: Dict[str, GeneratedRegister] = dict()

    def __getitem__(self, key: Union[int, str]) -> GeneratedRegister:
        if isinstance(key, int):
            return self.registers[key]
        if isinstance(key, str):
            for register in self.registers:
                if key == register.name:
                    return register
        raise KeyError(key)

    def get(self, key: Union[int, str]) -> Optional[GeneratedRegister]:
        try:
            return self.__getitem__(key)
        except KeyError:
            return None

    @property
    def should_appear_in_visualization(self) -> bool:
        return all(
            hide_regex not in last_name_in_call_hierarchy(self.name.lower())
            for hide_regex in VISUALIZATION_HIDE_LIST
        )


class GeneratedCircuitData(pydantic.BaseModel):
    width: int
    circuit_parameters: List[ParameterName] = pydantic.Field(default_factory=list)
    qubit_mapping: QubitMapping = pydantic.Field(default_factory=QubitMapping)
    execution_data: Optional[ExecutionData] = pydantic.Field(default=None)

    @classmethod
    def from_empty_logic_flow(cls) -> "GeneratedCircuitData":
        return cls(width=0)


class FunctionDebugInfo(pydantic.BaseModel):
    generated_function: Optional[GeneratedFunction]
    children: List["FunctionDebugInfo"]
    relative_qubits: Tuple[int, ...]
    absolute_qubits: Optional[Tuple[int, ...]]
    is_basis_gate: Optional[bool]

    @property
    def registers(self) -> List[GeneratedRegister]:
        if self.generated_function is None:
            return list()
        return self.generated_function.registers

    @property
    def is_controlled(self) -> bool:
        if self.generated_function is None:
            return False
        return len(self.generated_function.control_states) > 0

    @property
    def control_states(self) -> List[ControlState]:
        if self.generated_function is None:
            return list()
        return self.generated_function.control_states
