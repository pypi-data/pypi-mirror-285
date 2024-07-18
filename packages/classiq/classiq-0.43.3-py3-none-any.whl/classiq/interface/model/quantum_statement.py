from typing import Any, Dict, Mapping, Union

from pydantic import Extra, root_validator

from classiq.interface.ast_node import ASTNode
from classiq.interface.helpers.pydantic_model_helpers import values_with_discriminator
from classiq.interface.model.handle_binding import (
    HandleBinding,
    SlicedHandleBinding,
    SubscriptHandleBinding,
)


class QuantumStatement(ASTNode):
    kind: str

    class Config:
        extra = Extra.forbid

    @root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", cls.__name__)  # type: ignore[attr-defined]


class QuantumOperation(QuantumStatement):
    @property
    def wiring_inputs(self) -> Mapping[str, HandleBinding]:
        return dict()

    @property
    def wiring_inouts(
        self,
    ) -> Mapping[
        str, Union[SlicedHandleBinding, SubscriptHandleBinding, HandleBinding]
    ]:
        return dict()

    @property
    def wiring_outputs(self) -> Mapping[str, HandleBinding]:
        return dict()
