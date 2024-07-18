import dataclasses
import inspect
from enum import EnumMeta
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    get_args,
    get_origin,
)

from typing_extensions import _AnnotatedAlias

from classiq.interface.generator.functions.classical_type import (
    Bool,
    ClassicalArray,
    ClassicalList,
    ConcreteClassicalType,
    Enum,
    Integer,
    Real,
    Struct,
)
from classiq.interface.generator.types.enum_declaration import (
    EnumDeclaration,
    declaration_from_enum,
)
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_declaration import (
    PositionalArg,
    QuantumFunctionDeclaration,
    QuantumOperandDeclaration,
)

from classiq import StructDeclaration
from classiq.exceptions import ClassiqValueError
from classiq.qmod.model_state_container import ModelStateContainer
from classiq.qmod.qmod_parameter import CArray, CBool, CInt, CParam, CReal
from classiq.qmod.qmod_variable import QVar, get_type_hint_expr
from classiq.qmod.quantum_callable import QCallable, QCallableList
from classiq.qmod.utilities import unmangle_keyword, version_portable_get_args

OPERAND_ARG_NAME = "arg{i}"


def python_type_to_qmod(
    py_type: type, *, qmodule: ModelStateContainer
) -> Optional[ConcreteClassicalType]:
    if py_type == int or py_type is CInt:
        return Integer()
    elif py_type == float or py_type is CReal:
        return Real()
    elif py_type == bool or py_type is CBool:
        return Bool()
    elif get_origin(py_type) == list:
        return ClassicalList(
            element_type=python_type_to_qmod(get_args(py_type)[0], qmodule=qmodule)
        )
    elif get_origin(py_type) == CArray:
        array_args = version_portable_get_args(py_type)
        if len(array_args) == 1:
            return ClassicalList(
                element_type=python_type_to_qmod(array_args[0], qmodule=qmodule)
            )
        elif len(array_args) == 2:
            return ClassicalArray(
                element_type=python_type_to_qmod(array_args[0], qmodule=qmodule),
                size=get_type_hint_expr(array_args[1]),
            )
        raise ClassiqValueError(
            "CArray accepts one or two generic parameters in the form "
            "`CArray[<element-type>]` or `CArray[<element-type>, <size>]`"
        )
    elif inspect.isclass(py_type) and dataclasses.is_dataclass(py_type):
        _add_qmod_struct(py_type, qmodule=qmodule)
        return Struct(name=py_type.__name__)
    elif inspect.isclass(py_type) and isinstance(py_type, EnumMeta):
        _add_qmod_enum(py_type, qmodule=qmodule)
        return Enum(name=py_type.__name__)
    return None


def _add_qmod_enum(py_type: EnumMeta, *, qmodule: ModelStateContainer) -> None:
    if (
        py_type.__name__ in EnumDeclaration.BUILTIN_ENUM_DECLARATIONS
        or py_type.__name__ in qmodule.enum_decls
    ):
        return

    qmodule.enum_decls[py_type.__name__] = declaration_from_enum(py_type)


def _add_qmod_struct(py_type: Type, *, qmodule: ModelStateContainer) -> None:
    if (
        py_type.__name__ in StructDeclaration.BUILTIN_STRUCT_DECLARATIONS
        or py_type.__name__ in qmodule.type_decls
    ):
        return

    qmodule.type_decls[py_type.__name__] = StructDeclaration(
        name=py_type.__name__,
        variables={
            f.name: python_type_to_qmod(f.type, qmodule=qmodule)
            for f in dataclasses.fields(py_type)
        },
    )


def _extract_port_decl(name: str, py_type: Any) -> PortDeclaration:
    # FIXME: CAD-13409
    qtype: Type[QVar] = QVar.from_type_hint(py_type)  # type:ignore[assignment]
    direction = qtype.port_direction(py_type)
    if isinstance(py_type, _AnnotatedAlias):
        py_type = py_type.__args__[0]
    return PortDeclaration(
        name=name,
        direction=direction,
        quantum_type=qtype.to_qmod_quantum_type(py_type),
    )


def _extract_operand_decl(
    name: str, py_type: Any, qmodule: ModelStateContainer
) -> QuantumOperandDeclaration:
    qc_args = version_portable_get_args(py_type)
    arg_dict = {
        OPERAND_ARG_NAME.format(i=i): arg_type for i, arg_type in enumerate(qc_args)
    }
    return QuantumOperandDeclaration(
        name=name,
        positional_arg_declarations=_extract_positional_args(arg_dict, qmodule=qmodule),
        is_list=(get_origin(py_type) or py_type) is QCallableList,
    )


def _extract_positional_args(
    args: Dict[str, Any], qmodule: ModelStateContainer
) -> List[PositionalArg]:
    result: List[PositionalArg] = []
    for name, py_type in args.items():
        if name == "return":
            continue
        name = unmangle_keyword(name)
        if (
            inspect.isclass(py_type)
            and (
                issubclass(py_type, CParam)
                or dataclasses.is_dataclass(py_type)
                or isinstance(py_type, EnumMeta)
            )
            or get_origin(py_type) == CArray
        ):
            result.append(
                ClassicalParameterDeclaration(
                    name=name,
                    classical_type=python_type_to_qmod(py_type, qmodule=qmodule),
                )
            )
        elif QVar.from_type_hint(py_type) is not None:
            result.append(_extract_port_decl(name, py_type))
        else:
            assert (get_origin(py_type) or py_type) is QCallable or (
                get_origin(py_type) or py_type
            ) is QCallableList
            result.append(_extract_operand_decl(name, py_type, qmodule=qmodule))
    return result


def infer_func_decl(
    py_func: Callable, qmodule: ModelStateContainer
) -> QuantumFunctionDeclaration:
    return QuantumFunctionDeclaration(
        name=unmangle_keyword(py_func.__name__),
        positional_arg_declarations=_extract_positional_args(
            py_func.__annotations__, qmodule=qmodule
        ),
    )
