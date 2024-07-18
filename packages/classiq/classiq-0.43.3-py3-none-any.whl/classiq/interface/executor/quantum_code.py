from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import pydantic
from pydantic import BaseModel

from classiq.interface.backend.ionq.ionq_quantum_program import IonqQuantumCircuit
from classiq.interface.backend.pydantic_backend import PydanticArgumentNameType
from classiq.interface.executor.quantum_instruction_set import QuantumInstructionSet
from classiq.interface.executor.register_initialization import RegisterInitialization
from classiq.interface.generator.synthesis_metadata.synthesis_execution_data import (
    ExecutionData,
)

from classiq.exceptions import ClassiqValueError

Arguments = Dict[PydanticArgumentNameType, Any]
MultipleArguments = Tuple[Arguments, ...]
CodeType = str
RegistersInitialization = Dict[str, RegisterInitialization]
Qubits = Tuple[int, ...]
OutputQubitsMap = Dict[str, Qubits]


class QuantumBaseCode(BaseModel):
    syntax: QuantumInstructionSet = pydantic.Field(
        default=QuantumInstructionSet.QASM, description="The syntax of the program."
    )
    code: CodeType = pydantic.Field(
        ..., description="The textual representation of the program"
    )

    @pydantic.validator("code")
    def load_quantum_program(
        cls, code: Union[CodeType, IonqQuantumCircuit], values: Dict[str, Any]
    ) -> CodeType:
        syntax = values.get("syntax")
        if isinstance(code, IonqQuantumCircuit):
            if syntax != QuantumInstructionSet.IONQ:
                raise ClassiqValueError(
                    f"Invalid code type {type(code)} for syntax: {syntax}"
                )
            return code.json()

        return code


class QuantumCode(QuantumBaseCode):
    arguments: MultipleArguments = pydantic.Field(
        default=(),
        description="The parameters dictionary for a parametrized quantum program.",
    )
    output_qubits_map: OutputQubitsMap = pydantic.Field(
        default_factory=dict,
        description="The map of outputs to their qubits in the circuit.",
    )
    registers_initialization: Optional[RegistersInitialization] = pydantic.Field(
        default_factory=None,
        description="Initial conditions for the different registers in the circuit.",
    )
    synthesis_execution_data: Optional[ExecutionData] = pydantic.Field(default=None)
    synthesis_execution_arguments: Arguments = pydantic.Field(default_factory=dict)

    class Config:
        validate_assignment = True

    @pydantic.validator("arguments")
    def validate_arguments(
        cls, arguments: MultipleArguments, values: Dict[str, Any]
    ) -> MultipleArguments:
        if arguments and values.get("syntax") not in (
            QuantumInstructionSet.QSHARP,
            QuantumInstructionSet.QASM,
        ):
            raise ClassiqValueError("Only QASM or Q# programs support arguments")

        if values.get("syntax") == QuantumInstructionSet.QSHARP and len(arguments) > 1:
            raise ClassiqValueError(
                f"Q# programs supports only one group of arguments. {len(arguments)} given"
            )

        return arguments

    @pydantic.validator("synthesis_execution_data")
    def validate_synthesis_execution_data(
        cls,
        synthesis_execution_data: Optional[ExecutionData],
        values: Dict[str, Any],
    ) -> Optional[ExecutionData]:
        if (
            synthesis_execution_data is not None
            and values.get("syntax") is not QuantumInstructionSet.QASM
        ):
            raise ClassiqValueError("Only QASM supports the requested configuration")

        return synthesis_execution_data

    @staticmethod
    def from_file(
        file_path: Union[str, Path],
        syntax: Optional[Union[str, QuantumInstructionSet]] = None,
        arguments: MultipleArguments = (),
    ) -> QuantumCode:
        path = Path(file_path)
        code = path.read_text()
        if syntax is None:
            syntax = QuantumInstructionSet.from_suffix(path.suffix.lstrip("."))
        return QuantumCode(syntax=syntax, code=code, arguments=arguments)
