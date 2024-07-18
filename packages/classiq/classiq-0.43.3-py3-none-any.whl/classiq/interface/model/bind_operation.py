from typing import List, Literal, Mapping

import pydantic

from classiq.interface.model.handle_binding import HandleBinding
from classiq.interface.model.quantum_statement import QuantumOperation

from classiq.exceptions import ClassiqValueError

BIND_INPUT_NAME = "bind_input"
BIND_OUTPUT_NAME = "bind_output"


class BindOperation(QuantumOperation):
    kind: Literal["BindOperation"]

    in_handles: List[HandleBinding]
    out_handles: List[HandleBinding]

    @property
    def wiring_inputs(self) -> Mapping[str, HandleBinding]:
        return {
            f"{BIND_INPUT_NAME}_{i}": handle for i, handle in enumerate(self.in_handles)
        }

    @property
    def wiring_outputs(self) -> Mapping[str, HandleBinding]:
        return {
            f"{BIND_OUTPUT_NAME}_{i}": handle
            for i, handle in enumerate(self.out_handles)
        }

    @pydantic.validator("in_handles", "out_handles")
    def validate_handle(cls, handles: List[HandleBinding]) -> List[HandleBinding]:
        for handle in handles:
            if not handle.is_bindable():
                raise ClassiqValueError(f"Cannot bind '{handle}'")

        return handles

    def reversed(self) -> "BindOperation":
        return BindOperation(in_handles=self.out_handles, out_handles=self.in_handles)
