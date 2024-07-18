from typing import Any, Dict, Literal

import pydantic

from classiq.interface.ast_node import ASTNode
from classiq.interface.generator.functions.classical_type import ConcreteClassicalType
from classiq.interface.helpers.pydantic_model_helpers import values_with_discriminator


class ClassicalParameterDeclaration(ASTNode):
    kind: Literal["ClassicalParameterDeclaration"]

    name: str
    classical_type: ConcreteClassicalType

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(
            values, "kind", "ClassicalParameterDeclaration"
        )

    def rename(self, new_name: str) -> "ClassicalParameterDeclaration":
        return self.copy(update=dict(name=new_name))
