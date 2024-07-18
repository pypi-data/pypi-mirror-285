"""Executor module, implementing facilities for executing quantum programs using Classiq platform."""

from typing import Tuple, Union

from typing_extensions import TypeAlias

from classiq.interface.backend.backend_preferences import BackendPreferencesTypes
from classiq.interface.executor.estimation import OperatorsEstimation
from classiq.interface.executor.execution_preferences import ExecutionPreferences
from classiq.interface.executor.quantum_code import QuantumCode
from classiq.interface.executor.quantum_instruction_set import QuantumInstructionSet
from classiq.interface.executor.result import ExecutionDetails
from classiq.interface.generator.quantum_program import QuantumProgram

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import syncify_function
from classiq.execution.jobs import ExecutionJob
from classiq.synthesis import SerializedQuantumProgram

BatchExecutionResult: TypeAlias = Union[ExecutionDetails, BaseException]
ProgramAndResult: TypeAlias = Tuple[QuantumCode, BatchExecutionResult]
BackendPreferencesAndResult: TypeAlias = Tuple[
    BackendPreferencesTypes, int, BatchExecutionResult
]


def _parse_serialized_qprog(
    quantum_program: SerializedQuantumProgram,
) -> QuantumProgram:
    return QuantumProgram.parse_raw(quantum_program)


async def execute_async(quantum_program: SerializedQuantumProgram) -> ExecutionJob:
    circuit = _parse_serialized_qprog(quantum_program)
    result = await ApiWrapper.call_execute_generated_circuit(circuit)
    return ExecutionJob(details=result)


execute = syncify_function(execute_async)


def set_quantum_program_execution_preferences(
    quantum_program: SerializedQuantumProgram,
    preferences: ExecutionPreferences,
) -> SerializedQuantumProgram:
    circuit = _parse_serialized_qprog(quantum_program)
    circuit.model.execution_preferences = preferences
    return SerializedQuantumProgram(circuit.json())


__all__ = [
    "QuantumCode",
    "QuantumInstructionSet",
    "OperatorsEstimation",
    "set_quantum_program_execution_preferences",
]
