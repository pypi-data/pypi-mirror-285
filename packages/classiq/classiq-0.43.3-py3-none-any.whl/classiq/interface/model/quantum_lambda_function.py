from typing import TYPE_CHECKING, Dict, List, Optional, Union

import pydantic

from classiq.interface.ast_node import ASTNode
from classiq.interface.model.quantum_function_declaration import (
    QuantumOperandDeclaration,
)

if TYPE_CHECKING:
    from classiq.interface.model.statement_block import StatementBlock


class QuantumLambdaFunction(ASTNode):
    """
    The definition of an anonymous function passed as operand to higher-level functions
    """

    rename_params: Dict[str, str] = pydantic.Field(
        default_factory=dict,
        description="Mapping of the declared param to the actual variable name used ",
    )

    body: "StatementBlock" = pydantic.Field(
        description="A list of function calls passed to the operator"
    )

    _func_decl: Optional[QuantumOperandDeclaration] = pydantic.PrivateAttr(default=None)

    @property
    def func_decl(self) -> Optional[QuantumOperandDeclaration]:
        return self._func_decl

    def set_op_decl(self, fd: QuantumOperandDeclaration) -> None:
        self._func_decl = fd


QuantumCallable = Union[str, QuantumLambdaFunction]
QuantumOperand = Union[QuantumCallable, List[QuantumCallable]]
