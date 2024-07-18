from typing import Any, Dict, List, Literal, Union

import pydantic
from pydantic import Extra, Field
from sympy import IndexedBase, Symbol
from typing_extensions import Annotated

from classiq.interface.ast_node import HashableASTNode
from classiq.interface.generator.expressions.expression_types import RuntimeExpression
from classiq.interface.helpers.pydantic_model_helpers import values_with_discriminator

CLASSICAL_ATTRIBUTES = {"len", "size", "is_signed", "fraction_digits"}

NamedSymbol = Union[IndexedBase, Symbol]


class ClassicalType(HashableASTNode):
    def as_symbolic(self, name: str) -> Union[NamedSymbol, List[NamedSymbol]]:
        return Symbol(name)

    @property
    def qmod_type(self) -> type:
        raise NotImplementedError(
            f"{self.__class__.__name__!r} has no QMOD SDK equivalent"
        )

    class Config:
        extra = Extra.forbid

    def __str__(self) -> str:
        return str(type(self).__name__)


class Integer(ClassicalType):
    kind: Literal["int"]

    def as_symbolic(self, name: str) -> Symbol:
        return Symbol(name, integer=True)

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "int")

    @property
    def qmod_type(self) -> type:
        from classiq.qmod.qmod_parameter import CInt

        return CInt


class Real(ClassicalType):
    kind: Literal["real"]

    def as_symbolic(self, name: str) -> Symbol:
        return Symbol(name, real=True)

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "real")

    @property
    def qmod_type(self) -> type:
        from classiq.qmod.qmod_parameter import CReal

        return CReal


class Bool(ClassicalType):
    kind: Literal["bool"]

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "bool")

    @property
    def qmod_type(self) -> type:
        from classiq.qmod.qmod_parameter import CBool

        return CBool


class ClassicalList(ClassicalType):
    kind: Literal["list"]
    element_type: "ConcreteClassicalType"

    def as_symbolic(self, name: str) -> Symbol:
        return IndexedBase(name)

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "list")

    @property
    def qmod_type(self) -> type:
        from classiq.qmod.qmod_parameter import CArray

        return CArray[self.element_type.qmod_type]  # type:ignore[name-defined]


class Pauli(ClassicalType):
    kind: Literal["pauli"]

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "pauli")

    @property
    def qmod_type(self) -> type:
        from classiq.qmod.builtins.enums import Pauli

        return Pauli


class StructMetaType(ClassicalType):
    kind: Literal["type_proxy"]

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "type_proxy")


class TypeName(ClassicalType):
    kind: Literal["struct_instance"]
    name: str = pydantic.Field(description="The type name of the instance")

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "struct_instance")

    @property
    def qmod_type(self) -> type:
        return type(self.name, (TypeName,), dict())


class Enum(TypeName):
    pass


class Struct(TypeName):
    pass


class ClassicalArray(ClassicalType):
    kind: Literal["array"]
    element_type: "ConcreteClassicalType"
    size: pydantic.PositiveInt

    def as_symbolic(self, name: str) -> list:
        return [self.element_type.as_symbolic(f"{name}_{i}") for i in range(self.size)]

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "array")

    @property
    def qmod_type(self) -> type:
        from classiq.qmod.qmod_parameter import CArray

        return CArray[
            self.element_type.qmod_type, self.size  # type:ignore[name-defined]
        ]


class OpaqueHandle(ClassicalType):
    pass


class VQEResult(OpaqueHandle):
    kind: Literal["vqe_result"]

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "vqe_result")


class Histogram(OpaqueHandle):
    kind: Literal["histogram"]

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "histogram")


class Estimation(OpaqueHandle):
    kind: Literal["estimation_result"]

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "estimation_result")


class IQAERes(OpaqueHandle):
    kind: Literal["iqae_result"]

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "iqae_result")


class LadderOperator(ClassicalType):
    kind: Literal["ladder_operator"]

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "ladder_operator")

    @property
    def qmod_type(self) -> type:
        from classiq.qmod.builtins.enums import LadderOperator

        return LadderOperator


ConcreteClassicalType = Annotated[
    Union[
        Integer,
        Real,
        Bool,
        ClassicalList,
        Pauli,
        StructMetaType,
        TypeName,
        ClassicalArray,
        VQEResult,
        Histogram,
        Estimation,
        LadderOperator,
        IQAERes,
    ],
    Field(discriminator="kind"),
]
ClassicalList.update_forward_refs()
ClassicalArray.update_forward_refs()

PythonClassicalTypes = (int, float, bool, list, Enum)


def as_symbolic(symbols: Dict[str, ClassicalType]) -> Dict[str, RuntimeExpression]:
    return {
        param_name: param_type.as_symbolic(param_name)
        for param_name, param_type in symbols.items()
    }


class QmodPyObject:
    pass
