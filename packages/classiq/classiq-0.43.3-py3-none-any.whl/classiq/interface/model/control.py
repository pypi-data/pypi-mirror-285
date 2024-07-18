from typing import TYPE_CHECKING, Literal

import pydantic

from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumExpressionOperation,
)

if TYPE_CHECKING:
    from classiq.interface.model.statement_block import StatementBlock


class Control(QuantumExpressionOperation):
    kind: Literal["Control"]
    body: "StatementBlock"

    _ctrl_state: str = pydantic.PrivateAttr(default="")

    @property
    def ctrl_state(self) -> str:
        return self._ctrl_state

    def set_ctrl_state(self, ctrl_state: str) -> None:
        self._ctrl_state = ctrl_state
