import inspect
from abc import ABC
from dataclasses import is_dataclass
from enum import Enum as PythonEnum
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Optional,
    Type,
    Union,
    cast,
    overload,
)

from sympy import Basic
from typing_extensions import Self

from classiq.interface.ast_node import SourceReference
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import (
    PythonClassicalTypes,
)
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_call import (
    ArgValue,
    OperandIdentifier,
    QuantumFunctionCall,
)
from classiq.interface.model.quantum_function_declaration import (
    PositionalArg,
    QuantumFunctionDeclaration,
    QuantumOperandDeclaration,
)
from classiq.interface.model.quantum_lambda_function import QuantumLambdaFunction
from classiq.interface.model.quantum_statement import QuantumStatement
from classiq.interface.model.quantum_type import QuantumType
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)

from classiq.exceptions import ClassiqValueError
from classiq.qmod.model_state_container import QMODULE, ModelStateContainer
from classiq.qmod.qmod_constant import QConstant
from classiq.qmod.qmod_parameter import CInt, CParam, CParamScalar, create_param
from classiq.qmod.qmod_variable import QVar, create_qvar_for_port_decl
from classiq.qmod.quantum_callable import QCallable, QExpandableInterface
from classiq.qmod.symbolic_expr import SymbolicExpr
from classiq.qmod.utilities import mangle_keyword, qmod_val_to_expr_str

ArgType = Union[CParam, QVar, QCallable]


class QExpandable(QCallable, QExpandableInterface, ABC):
    STACK: ClassVar[List["QExpandable"]] = list()

    def __init__(self, py_callable: Callable) -> None:
        self._qmodule: ModelStateContainer = QMODULE
        self._py_callable: Callable = py_callable
        self._body: List[QuantumStatement] = list()

    @property
    def body(self) -> List[QuantumStatement]:
        return self._body

    def __enter__(self) -> Self:
        QExpandable.STACK.append(self)
        QCallable.CURRENT_EXPANDABLE = self
        self._body.clear()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        assert QExpandable.STACK.pop() is self
        QCallable.CURRENT_EXPANDABLE = (
            QExpandable.STACK[-1] if QExpandable.STACK else None
        )

    def expand(self) -> None:
        if self not in QExpandable.STACK:
            with self:
                self._py_callable(*self._get_positional_args())

    def infer_rename_params(self) -> Dict[str, str]:
        return {}

    def add_local_handle(
        self,
        name: str,
        qtype: QuantumType,
        source_ref: Optional[SourceReference] = None,
    ) -> None:
        self._body.append(
            VariableDeclarationStatement(
                name=name, quantum_type=qtype, source_ref=source_ref
            )
        )

    def append_statement_to_body(self, stmt: QuantumStatement) -> None:
        self._body.append(stmt)

    def _get_positional_args(self) -> List[ArgType]:
        result: List[ArgType] = []
        for arg in self.func_decl.get_positional_arg_decls():
            rename_dict = self.infer_rename_params()
            actual_name = rename_dict.get(arg.name, arg.name)
            if isinstance(arg, ClassicalParameterDeclaration):
                result.append(
                    create_param(actual_name, arg.classical_type, self._qmodule)
                )
            elif isinstance(arg, PortDeclaration):
                result.append(create_qvar_for_port_decl(arg, actual_name))
            else:
                assert isinstance(arg, QuantumOperandDeclaration)
                result.append(QTerminalCallable(arg))
        return result

    def create_quantum_function_call(
        self, source_ref_: SourceReference, *args: Any, **kwargs: Any
    ) -> QuantumFunctionCall:
        return _create_quantum_function_call(
            self.func_decl, None, source_ref_, *args, **kwargs
        )


class QLambdaFunction(QExpandable):
    def __init__(self, decl: QuantumFunctionDeclaration, py_callable: Callable) -> None:
        py_callable.__annotations__.pop("return", None)
        super().__init__(py_callable)
        self._decl = decl

    @property
    def func_decl(self) -> QuantumFunctionDeclaration:
        return self._decl

    def infer_rename_params(self) -> Dict[str, str]:
        py_params = inspect.getfullargspec(self._py_callable)
        decl_params = self.func_decl.get_positional_arg_decls()
        return {
            decl_param.name: py_param
            for decl_param, py_param in zip(decl_params, py_params.args)
            if decl_param.name != py_param
        }


class QTerminalCallable(QCallable):
    def __init__(
        self,
        decl: QuantumFunctionDeclaration,
        index_: Optional[Union[int, CParamScalar]] = None,
    ) -> None:
        self._decl = decl
        self._index = index_

    @property
    def is_list(self) -> bool:
        return isinstance(self._decl, QuantumOperandDeclaration) and self._decl.is_list

    def __getitem__(self, key: Union[slice, int, CInt]) -> "QTerminalCallable":
        if not self.is_list:
            raise ClassiqValueError("Cannot index a non-list operand")
        if isinstance(key, slice):
            raise NotImplementedError("Operand lists don't support slicing")
        if isinstance(key, CParam) and not isinstance(key, CParamScalar):
            raise ClassiqValueError("Non-classical parameter for slicing")
        return QTerminalCallable(self._decl, key)

    def __len__(self) -> int:
        raise ClassiqValueError(
            "len(<func>) is not supported for quantum callables - use <func>.len instead (Only if it is an operand list)"
        )

    if TYPE_CHECKING:

        @property
        def len(self) -> int: ...

    else:

        @property
        def len(self) -> CParamScalar:
            if not self.is_list:
                raise ClassiqValueError("Cannot get length of a non-list operand")
            return CParamScalar(f"get_field({self.func_decl.name}, 'len')")

    @property
    def func_decl(self) -> QuantumFunctionDeclaration:
        return self._decl

    def create_quantum_function_call(
        self, source_ref_: SourceReference, *args: Any, **kwargs: Any
    ) -> QuantumFunctionCall:
        if self.is_list and self._index is None:
            raise ClassiqValueError(
                f"Quantum operand {self.func_decl.name!r} is a list and must be indexed"
            )
        return _create_quantum_function_call(
            self.func_decl, self._index, source_ref_, *args, **kwargs
        )


@overload
def prepare_arg(
    arg_decl: PositionalArg, val: Union[QCallable, Callable[..., None]], func_name: str
) -> QuantumLambdaFunction: ...


@overload
def prepare_arg(arg_decl: PositionalArg, val: Any, func_name: str) -> ArgValue: ...


def prepare_arg(arg_decl: PositionalArg, val: Any, func_name: str) -> ArgValue:
    if isinstance(val, QConstant):
        val.add_to_model()
        return Expression(expr=str(val.name))
    if isinstance(arg_decl, ClassicalParameterDeclaration):
        _validate_classical_arg(val, arg_decl, func_name)
        return Expression(expr=qmod_val_to_expr_str(val))
    elif isinstance(arg_decl, PortDeclaration):
        if not isinstance(val, QVar):
            raise ClassiqValueError(
                f"Argument {str(val)!r} to parameter {arg_decl.name!r} of function "
                f"{func_name!r} has incompatible type; expected quantum variable"
            )
        return val.get_handle_binding()
    else:
        if isinstance(val, list):
            if not all(isinstance(v, QCallable) or callable(v) for v in val):
                raise ClassiqValueError(
                    f"Quantum operand {arg_decl.name!r} cannot be initialized with a "
                    f"list of non-callables"
                )
            val = cast(List[Union[QCallable, Callable[[Any], None]]], val)
            return [prepare_arg(arg_decl, v, func_name) for v in val]

        if not isinstance(val, QCallable):
            val = QLambdaFunction(arg_decl, val)
            val.expand()
            return QuantumLambdaFunction(
                rename_params=val.infer_rename_params(),
                body=val.body,
            )

        if isinstance(val, QExpandable):
            val.expand()
        return val.func_decl.name


def _validate_classical_arg(
    arg: Any, arg_decl: ClassicalParameterDeclaration, func_name: str
) -> None:
    if (
        not isinstance(
            arg, (*PythonClassicalTypes, CParam, SymbolicExpr, Basic, PythonEnum)
        )
        and not is_dataclass(arg)  # type:ignore[unreachable]
        or isinstance(arg, SymbolicExpr)
        and arg.is_quantum
    ):
        raise ClassiqValueError(
            f"Argument {str(arg)!r} to parameter {arg_decl.name!r} of function "
            f"{func_name!r} has incompatible type; expected "
            f"{arg_decl.classical_type.qmod_type.__name__}"
        )


def _get_operand_hint_args(
    func: QuantumFunctionDeclaration, param: PositionalArg, param_value: str
) -> str:
    return ", ".join(
        [
            (
                f"{decl.name}={param_value}"
                if decl.name == param.name
                else f"{decl.name}=..."
            )
            for decl in func.get_positional_arg_decls()
        ]
    )


def _get_operand_hint(func: QuantumFunctionDeclaration, param: PositionalArg) -> str:
    return (
        f"\nHint: To create an operand, do not call quantum gates directly "
        f"`{func.name}({_get_operand_hint_args(func, param, 'H(q)')})`. "
        f"Instead, use a lambda function "
        f"`{func.name}({_get_operand_hint_args(func, param, 'lambda: H(q)')})` "
        f"or a quantum function "
        f"`{func.name}({_get_operand_hint_args(func, param, 'my_func')})`"
    )


def _prepare_args(
    decl: QuantumFunctionDeclaration, arg_list: List[Any], kwargs: Dict[str, Any]
) -> List[ArgValue]:
    result = []
    for arg_decl in decl.get_positional_arg_decls():
        if arg_list:
            arg = arg_list.pop(0)
        else:
            arg = kwargs.pop(mangle_keyword(arg_decl.name), None)
        if arg is None:
            error_message = (
                f"{decl.name!r} is missing required argument for {arg_decl.name!r}"
            )
            if isinstance(arg_decl, QuantumOperandDeclaration):
                error_message += _get_operand_hint(decl, arg_decl)
            raise ClassiqValueError(error_message)
        result.append(prepare_arg(arg_decl, arg, decl.name))

    return result


def _create_quantum_function_call(
    decl_: QuantumFunctionDeclaration,
    index_: Optional[Union[CParamScalar, int]] = None,
    source_ref_: Optional[SourceReference] = None,
    *args: Any,
    **kwargs: Any,
) -> QuantumFunctionCall:
    arg_decls = decl_.get_positional_arg_decls()
    arg_list = list(args)
    prepared_args = _prepare_args(decl_, arg_list, kwargs)

    if kwargs:
        bad_kwarg = next(iter(kwargs))
        if not all(arg_decl.name == bad_kwarg for arg_decl in arg_decls):
            raise ClassiqValueError(
                f"{decl_.name}() got an unexpected keyword argument {bad_kwarg!r}"
            )
        else:
            raise ClassiqValueError(
                f"{decl_.name}() got multiple values for argument {bad_kwarg!r}"
            )
    if arg_list:
        raise ClassiqValueError(
            f"{decl_.name}() takes {len(arg_decls)} arguments but {len(args)} were given"
        )
    function_ident: Union[str, OperandIdentifier] = decl_.name
    if index_ is not None:
        function_ident = OperandIdentifier(
            index=Expression(expr=str(index_)), name=function_ident
        )

    return QuantumFunctionCall(
        function=function_ident, positional_args=prepared_args, source_ref=source_ref_
    )
