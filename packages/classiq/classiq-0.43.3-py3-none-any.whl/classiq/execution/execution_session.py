import json
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from classiq.interface.executor.execution_preferences import ExecutionPreferences
from classiq.interface.executor.execution_result import ResultsCollection
from classiq.interface.executor.result import (
    EstimationResult,
    EstimationResults,
    ExecutionDetails,
    MultipleExecutionDetails,
)
from classiq.interface.generator.functions.qmod_python_interface import QmodPyStruct
from classiq.interface.generator.quantum_program import QuantumProgram

from classiq.applications.combinatorial_helpers.pauli_helpers.pauli_utils import (
    _pauli_dict_to_str,
    _pauli_terms_to_qmod,
)
from classiq.exceptions import ClassiqValueError
from classiq.executor import execute
from classiq.qmod.builtins import PauliTerm
from classiq.qmod.builtins.classical_execution_primitives import (
    CARRAY_SEPARATOR,
    ExecutionParams,
)
from classiq.synthesis import SerializedQuantumProgram

Hamiltonian = Union[List[QmodPyStruct], List[PauliTerm]]
Program = Union[SerializedQuantumProgram, QuantumProgram]
ParsedExecutionParams = Dict[str, Union[float, int]]
ExecutionParameters = Optional[Union[ExecutionParams, List[ExecutionParams]]]
ParsedExecutionParameters = Optional[
    Union[ParsedExecutionParams, List[ParsedExecutionParams]]
]


SAVE_RESULT = "\nsave({'result': result})\n"


class SupportedPrimitives:
    SAMPLE = "sample"
    BATCH_SAMPLE = "batch_sample"
    ESTIMATE = "estimate"
    BATCH_ESTIMATE = "batch_estimate"


def _deserialize_program(program: Program) -> QuantumProgram:
    return (
        program
        if isinstance(program, QuantumProgram)
        else QuantumProgram.parse_obj(json.loads(program))
    )


def to_hamiltonian_str(hamiltonian: Hamiltonian) -> str:
    return (
        _pauli_terms_to_qmod(cast(List[PauliTerm], hamiltonian))
        if isinstance(hamiltonian[0], PauliTerm)
        else _pauli_dict_to_str(cast(List[QmodPyStruct], hamiltonian))
    )


def serialize(
    item: Union[float, int, Tuple[int, ...], Tuple[float, ...]]
) -> Union[str, List]:
    if isinstance(item, tuple):
        return list(item)
    return str(item)


def parse_params(params: ExecutionParams) -> ParsedExecutionParams:
    result = {}
    for key, values in params.items():
        if isinstance(values, list):
            for index, value in enumerate(values):
                new_key = f"{key}{CARRAY_SEPARATOR}{index}"
                result[new_key] = value
        elif isinstance(values, (int, float)):
            result[key] = values
        else:
            raise TypeError("Parameters were provided in un-supported format")
    return result


def format_parameters(execution_params: ExecutionParameters) -> str:
    parsed_parameters: ParsedExecutionParameters = None
    if execution_params is None:
        return ""
    if isinstance(execution_params, dict):
        parsed_parameters = parse_params(execution_params)

    elif isinstance(execution_params, list):
        parsed_parameters = [
            parse_params(ep) if isinstance(ep, dict) else ep for ep in execution_params
        ]

    execution_params = cast(ExecutionParams, parsed_parameters)
    return json.dumps(execution_params, default=serialize, indent=2)


def create_estimate_execution_code(operation: str, **kwargs: Any) -> str:
    hamiltonian = kwargs.get("hamiltonian", "")
    parameters = kwargs.get("parameters", "")
    return f"\nresult = {operation}([{hamiltonian}], {parameters})" + SAVE_RESULT


def create_sample_execution_code(operation: str, **kwargs: Any) -> str:
    parameters = kwargs.get("parameters", "")
    return f"\nresult = {operation}({parameters})" + SAVE_RESULT


operation_handlers: Dict[str, Callable[[str], str]] = {
    "estimate": create_estimate_execution_code,
    "batch_estimate": create_estimate_execution_code,
    "sample": create_sample_execution_code,
    "batch_sample": create_sample_execution_code,
}


def generate_code_snippet(operation: str, **kwargs: Any) -> str:
    handler = operation_handlers.get(operation)
    if handler:
        return handler(operation, **kwargs)
    raise ClassiqValueError(f"Unsupported operation type: {operation}")


class ExecutionSession:
    def __init__(
        self,
        quantum_program: Program,
        execution_preferences: Optional[ExecutionPreferences] = None,
    ):
        self.program: QuantumProgram = _deserialize_program(quantum_program)
        self.update_execution_preferences(execution_preferences)

    @property
    def qprog(self) -> str:
        return SerializedQuantumProgram(self.program.json(indent=2))

    def update_execution_preferences(
        self, execution_preferences: Optional[ExecutionPreferences]
    ) -> None:
        if execution_preferences is not None:
            self.program.model.execution_preferences = execution_preferences

    def execute_quantum_program(
        self, operation: str, **kwargs: Any
    ) -> ResultsCollection:
        self.program.model.classical_execution_code = generate_code_snippet(
            operation, **kwargs
        )
        return execute(self.qprog).result()

    def sample(self, parameters: Optional[ExecutionParams] = None) -> ExecutionDetails:
        return cast(
            ExecutionDetails,
            self.execute_quantum_program(
                SupportedPrimitives.SAMPLE, parameters=format_parameters(parameters)
            )[0].value,
        )

    def batch_sample(self, parameters: List[ExecutionParams]) -> List[ExecutionDetails]:
        return cast(
            MultipleExecutionDetails,
            self.execute_quantum_program(
                SupportedPrimitives.BATCH_SAMPLE,
                parameters=format_parameters(parameters),
            )[0].value,
        ).details

    def estimate(
        self, hamiltonian: Hamiltonian, parameters: Optional[ExecutionParams] = None
    ) -> EstimationResult:
        return cast(
            EstimationResult,
            self.execute_quantum_program(
                SupportedPrimitives.ESTIMATE,
                parameters=format_parameters(parameters),
                hamiltonian=to_hamiltonian_str(hamiltonian),
            )[0].value,
        )

    def batch_estimate(
        self, hamiltonian: Hamiltonian, parameters: List[ExecutionParams]
    ) -> List[EstimationResult]:
        return cast(
            EstimationResults,
            self.execute_quantum_program(
                SupportedPrimitives.BATCH_ESTIMATE,
                parameters=format_parameters(parameters),
                hamiltonian=to_hamiltonian_str(hamiltonian),
            )[0].value,
        ).results
