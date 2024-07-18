import re

import pydantic

from classiq.interface.analyzer.result import QasmCode

from classiq import QuantumProgram
from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import syncify_function
from classiq.exceptions import ClassiqValueError
from classiq.synthesis import SerializedQuantumProgram

QASM_VERSION_REGEX = re.compile("OPENQASM (\\d*.\\d*);")


async def qasm_show_interactive_async(qasm_code: str) -> None:
    circuit = await ApiWrapper.get_generated_circuit_from_qasm(QasmCode(code=qasm_code))
    circuit.show()  # type: ignore[attr-defined]


qasm_show_interactive = syncify_function(qasm_show_interactive_async)


CANT_PARSE_QUANTUM_PROGRAM_MSG = (
    "Can not parse quantum_program into GeneratedCircuit, \n"
)


def show(quantum_program: SerializedQuantumProgram) -> None:
    try:
        circuit = QuantumProgram.parse_raw(quantum_program)
    except pydantic.error_wrappers.ValidationError as exc:
        raise ClassiqValueError(CANT_PARSE_QUANTUM_PROGRAM_MSG) from exc
    circuit.show()  # type: ignore[attr-defined]
