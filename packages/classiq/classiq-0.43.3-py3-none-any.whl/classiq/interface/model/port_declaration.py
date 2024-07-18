from typing import Any, Dict, Literal, Mapping

import pydantic

from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.helpers.pydantic_model_helpers import values_with_discriminator
from classiq.interface.model.quantum_variable_declaration import (
    QuantumVariableDeclaration,
)

from classiq.exceptions import ClassiqValueError


class PortDeclaration(QuantumVariableDeclaration):
    kind: Literal["PortDeclaration"]

    direction: PortDeclarationDirection

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "PortDeclaration")

    @pydantic.validator("direction")
    def _direction_validator(
        cls, direction: PortDeclarationDirection, values: Mapping[str, Any]
    ) -> PortDeclarationDirection:
        if direction is PortDeclarationDirection.Output:
            quantum_type = values.get("quantum_type")
            if quantum_type is None:
                raise ClassiqValueError("Port declaration is missing a type")

        return direction
