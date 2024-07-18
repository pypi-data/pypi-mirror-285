from typing import Any, Mapping, Optional

import pydantic

from classiq.interface.ast_node import ASTNode
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.model.quantum_type import (
    ConcreteQuantumType,
    QuantumBitvector,
    QuantumNumeric,
)


class QuantumVariableDeclaration(ASTNode):
    name: str
    quantum_type: ConcreteQuantumType
    size: Optional[Expression] = pydantic.Field(default=None)

    @pydantic.validator("size")
    def _propagate_size_to_type(
        cls, size: Optional[Expression], values: Mapping[str, Any]
    ) -> Optional[Expression]:
        if size is not None:
            quantum_type = values.get("quantum_type")
            if isinstance(quantum_type, QuantumBitvector):
                quantum_type.length = size
            elif isinstance(quantum_type, QuantumNumeric):
                quantum_type.size = size
        return size
