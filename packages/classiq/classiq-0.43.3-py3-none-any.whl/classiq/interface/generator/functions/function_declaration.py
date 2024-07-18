import abc
from typing import Dict

import pydantic

from classiq.interface.ast_node import ASTNode
from classiq.interface.generator.functions.classical_type import ConcreteClassicalType


class FunctionDeclaration(ASTNode, abc.ABC):
    """
    Facilitates the creation of a common function interface object.
    """

    name: str = pydantic.Field(description="The name of the function")

    param_decls: Dict[str, ConcreteClassicalType] = pydantic.Field(
        description="The expected interface of the functions parameters",
        default_factory=dict,
    )

    class Config:
        extra = pydantic.Extra.forbid


FunctionDeclaration.update_forward_refs()
