from typing import Dict, Optional

import pydantic

from classiq.interface.executor.quantum_instruction_set import QuantumInstructionSet
from classiq.interface.generator.circuit_code.types_and_constants import (
    INSTRUCTION_SET_TO_FORMAT,
    Code,
    CodeAndSyntax,
    LongStr,
    QasmVersion,
)
from classiq.interface.generator.model.preferences.preferences import QuantumFormat

from classiq.exceptions import ClassiqMissingOutputFormatError


class CircuitCodeInterface(pydantic.BaseModel):
    outputs: Dict[QuantumFormat, Code]
    qasm_version: QasmVersion

    @pydantic.validator("outputs")
    def reformat_long_string_output_formats(
        cls, outputs: Dict[QuantumFormat, str]
    ) -> Dict[QuantumFormat, LongStr]:
        return {key: LongStr(value) for key, value in outputs.items()}

    @property
    def qasm(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.QASM)

    @property
    def qsharp(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.QSHARP)

    @property
    def qir(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.QIR)

    @property
    def ionq(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.IONQ)

    @property
    def cirq_json(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.CIRQ_JSON)

    @property
    def qasm_cirq_compatible(self) -> Optional[Code]:
        return self.outputs.get(QuantumFormat.QASM_CIRQ_COMPATIBLE)

    def get_code(self, instruction_set: QuantumInstructionSet) -> Code:
        quantum_format: QuantumFormat = INSTRUCTION_SET_TO_FORMAT[instruction_set]
        code = self.outputs.get(quantum_format)
        if code is None:
            raise ClassiqMissingOutputFormatError(missing_formats=[quantum_format])
        return code

    def get_code_by_priority(self) -> Optional[CodeAndSyntax]:
        for instruction_set, quantum_format in INSTRUCTION_SET_TO_FORMAT.items():
            code = self.outputs.get(quantum_format)
            if code is not None:
                return code, instruction_set

        return None
