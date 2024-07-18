import sys
from typing import (  # type: ignore[attr-defined]
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
    Union,
    _GenericAlias,
)

from typing_extensions import ParamSpec

from classiq.interface.generator.functions.classical_type import (
    ClassicalArray,
    ClassicalList,
    ClassicalType,
    Struct,
)

from classiq import StructDeclaration
from classiq.exceptions import ClassiqValueError
from classiq.qmod.model_state_container import ModelStateContainer
from classiq.qmod.symbolic_expr import Symbolic, SymbolicExpr

_T = TypeVar("_T")


if TYPE_CHECKING:
    from classiq.qmod.qmod_variable import QNum

    SymbolicSuperclass = SymbolicExpr
else:
    SymbolicSuperclass = Symbolic


class CParam(SymbolicSuperclass):
    def __init__(self, expr: str) -> None:
        super().__init__(expr, False)


class CInt(CParam):
    pass


class CReal(CParam):
    pass


class CBool(CParam):
    pass


_P = ParamSpec("_P")


class ArrayBase(Generic[_P]):
    # Support comma-separated generic args in older Python versions
    if sys.version_info[0:2] < (3, 10):

        def __class_getitem__(cls, args) -> _GenericAlias:
            return _GenericAlias(cls, args)


class CArray(CParam, ArrayBase[_P]):
    if TYPE_CHECKING:

        @property
        def len(self) -> int: ...

        def __getitem__(self, idx: Union[int, CInt, slice, "QNum"]) -> Any: ...


class CParamScalar(CParam, SymbolicExpr):

    def __hash__(self) -> int:
        return hash(str(self))


class CParamList(CParam):
    def __init__(
        self,
        expr: str,
        list_type: Union[ClassicalList, ClassicalArray],
        qmodule: ModelStateContainer,
    ) -> None:
        super().__init__(expr)
        self._qmodule = qmodule
        self._list_type = list_type

    def __getitem__(self, key: Any) -> CParam:
        if isinstance(key, slice):
            start = key.start if key.start is not None else ""
            stop = key.stop if key.stop is not None else ""
            if key.step is not None:
                key = f"{start}:{key.step}:{stop}"
            else:
                key = f"{start}:{stop}"
        return create_param(
            f"({self})[{key}]",
            self._list_type.element_type,
            qmodule=self._qmodule,
        )

    def __len__(self) -> int:
        raise ClassiqValueError(
            "len(<expr>) is not supported for QMod lists - use <expr>.len instead"
        )

    @property
    def len(self) -> CParamScalar:
        return CParamScalar(f"get_field({self}, 'len')")


class CParamStruct(CParam):
    def __init__(
        self, expr: str, struct_type: Struct, *, qmodule: ModelStateContainer
    ) -> None:
        super().__init__(expr)
        self._qmodule = qmodule
        self._struct_type = struct_type

    def __getattr__(self, field_name: str) -> CParam:
        return CParamStruct.get_field(
            self._qmodule, str(self), self._struct_type.name, field_name
        )

    @staticmethod
    def get_field(
        qmodule: ModelStateContainer,
        variable_name: str,
        struct_name: str,
        field_name: str,
    ) -> CParam:
        struct_decl = StructDeclaration.BUILTIN_STRUCT_DECLARATIONS.get(
            struct_name, qmodule.type_decls.get(struct_name)
        )
        assert struct_decl is not None
        field_type = struct_decl.variables.get(field_name)
        if field_type is None:
            raise ClassiqValueError(
                f"{struct_name} {variable_name!r} has no field {field_name!r}. "
                f"Available fields: {', '.join(struct_decl.variables.keys())}"
            )

        return create_param(
            f"get_field({variable_name},{field_name!r})",
            field_type,
            qmodule=qmodule,
        )


def create_param(
    expr_str: str, ctype: ClassicalType, qmodule: ModelStateContainer
) -> CParam:
    if isinstance(ctype, (ClassicalList, ClassicalArray)):
        return CParamList(expr_str, ctype, qmodule=qmodule)
    elif isinstance(ctype, Struct):
        return CParamStruct(expr_str, ctype, qmodule=qmodule)
    else:
        return CParamScalar(expr_str)


Array = CArray
