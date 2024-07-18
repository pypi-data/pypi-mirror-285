import inspect
import sys
from types import FrameType
from typing import Any, Callable, Final, List, Mapping, Union, overload

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.builtins.internal_operators import (
    REPEAT_OPERATOR_NAME,
)
from classiq.interface.model.bind_operation import BindOperation
from classiq.interface.model.classical_if import ClassicalIf
from classiq.interface.model.control import Control
from classiq.interface.model.inplace_binary_operation import (
    BinaryOperation,
    InplaceBinaryOperation,
)
from classiq.interface.model.invert import Invert
from classiq.interface.model.power import Power
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    QuantumOperandDeclaration,
)
from classiq.interface.model.quantum_lambda_function import QuantumLambdaFunction
from classiq.interface.model.repeat import Repeat
from classiq.interface.model.statement_block import StatementBlock
from classiq.interface.model.within_apply_operation import WithinApply

from classiq import Integer
from classiq.exceptions import ClassiqValueError
from classiq.qmod.qmod_variable import Input, Output, QArray, QBit, QNum, QVar
from classiq.qmod.quantum_callable import QCallable
from classiq.qmod.quantum_expandable import prepare_arg
from classiq.qmod.symbolic_expr import SymbolicExpr
from classiq.qmod.utilities import get_source_ref

_MISSING_VALUE: Final[int] = -1


def bind(
    source: Union[Input[QVar], List[Input[QVar]]],
    destination: Union[Output[QVar], List[Output[QVar]]],
) -> None:
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    if not isinstance(source, list):
        source = [source]
    if not isinstance(destination, list):
        destination = [destination]
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        BindOperation(
            in_handles=[src_var.get_handle_binding() for src_var in source],
            out_handles=[dst_var.get_handle_binding() for dst_var in destination],
            source_ref=source_ref,
        )
    )


def if_(
    condition: Union[SymbolicExpr, bool],
    then: Union[QCallable, Callable[[], None]],
    else_: Union[QCallable, Callable[[], None], int] = _MISSING_VALUE,
) -> None:
    _validate_operand(then)
    if else_ != _MISSING_VALUE:
        _validate_operand(else_)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        ClassicalIf(
            condition=Expression(expr=str(condition)),
            then=_operand_to_body(then),
            else_=_operand_to_body(else_) if else_ != _MISSING_VALUE else [],  # type: ignore[arg-type]
            source_ref=source_ref,
        )
    )


@overload
def control(
    ctrl: Union[QBit, QArray[QBit]], operand: Union[QCallable, Callable[[], None]]
) -> None:
    pass


@overload
def control(ctrl: SymbolicExpr, operand: Union[QCallable, Callable[[], None]]) -> None:
    pass


def control(
    ctrl: Union[SymbolicExpr, QBit, QArray[QBit]],
    operand: Union[QCallable, Callable[[], None]],
) -> None:
    _validate_operand(operand)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        Control(
            expression=Expression(expr=str(ctrl)),
            body=_operand_to_body(operand),
            source_ref=source_ref,
        )
    )


def inplace_add(
    value: QNum,
    target: QNum,
) -> None:
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        InplaceBinaryOperation(
            target=target.get_handle_binding(),
            value=value.get_handle_binding(),
            operation=BinaryOperation.Addition,
            source_ref=source_ref,
        )
    )


def inplace_xor(
    value: QNum,
    target: QNum,
) -> None:
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        InplaceBinaryOperation(
            target=target.get_handle_binding(),
            value=value.get_handle_binding(),
            operation=BinaryOperation.Xor,
            source_ref=source_ref,
        )
    )


def within_apply(
    compute: Callable[[], None],
    action: Callable[[], None],
) -> None:
    _validate_operand(compute)
    _validate_operand(action)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        WithinApply(
            compute=_operand_to_body(compute),
            action=_operand_to_body(action),
            source_ref=source_ref,
        )
    )


def repeat(count: Union[SymbolicExpr, int], iteration: Callable[[int], None]) -> None:
    _validate_operand(iteration)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    iteration_operand = prepare_arg(
        QuantumOperandDeclaration(
            name=REPEAT_OPERATOR_NAME, param_decls={"index": Integer()}
        ),
        iteration,
        repeat.__name__,
    )
    if not isinstance(iteration_operand, QuantumLambdaFunction):
        raise ClassiqValueError("`repeat`'s `iteration` argument must be a callable.")
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        Repeat(
            iter_var=inspect.getfullargspec(iteration).args[0],
            count=Expression(expr=str(count)),
            body=iteration_operand.body,
            source_ref=source_ref,
        )
    )


def power(
    power: Union[SymbolicExpr, int],
    operand: Union[QCallable, Callable[[], None]],
) -> None:
    _validate_operand(operand)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        Power(
            power=Expression(expr=str(power)),
            body=_operand_to_body(operand),
            source_ref=source_ref,
        )
    )


def invert(
    operand: Union[QCallable, Callable[[], None]],
) -> None:
    _validate_operand(operand)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        Invert(body=_operand_to_body(operand), source_ref=source_ref)
    )


def _validate_operand(operand: Any) -> None:
    if operand is not None:
        return
    currentframe: FrameType = inspect.currentframe()  # type: ignore[assignment]
    operation_frame: FrameType = currentframe.f_back  # type: ignore[assignment]
    operation_frame_info: inspect.Traceback = inspect.getframeinfo(operation_frame)
    operation_name: str = operation_frame_info.function

    context = operation_frame_info.code_context
    assert context is not None
    operand_arg_name = context[0].split("_validate_operand(")[1].split(")")[0]

    error_message = (
        f"{operation_name} is missing required argument for {operand_arg_name}"
    )
    error_message += _get_operand_hint(
        operation_name=operation_name,
        operand_arg_name=operand_arg_name,
        params=inspect.signature(operation_frame.f_globals[operation_name]).parameters,
    )
    raise ClassiqValueError(error_message)


def _get_operand_hint_args(
    params: Mapping[str, inspect.Parameter], operand_arg_name: str, operand_value: str
) -> str:
    return ", ".join(
        [
            (
                f"{param.name}={operand_value}"
                if param.name == operand_arg_name
                else f"{param.name}=..."
            )
            for param in params.values()
        ]
    )


def _get_operand_hint(
    operation_name: str, operand_arg_name: str, params: Mapping[str, inspect.Parameter]
) -> str:
    return (
        f"\nHint: To create an operand, do not call quantum gates directly "
        f"`{operation_name}({_get_operand_hint_args(params, operand_arg_name, 'H(q)')})`. "
        f"Instead, use a lambda function "
        f"`{operation_name}({_get_operand_hint_args(params, operand_arg_name, 'lambda: H(q)')})` "
        f"or a quantum function "
        f"`{operation_name}({_get_operand_hint_args(params, operand_arg_name, 'my_func')})`"
    )


def _operand_to_body(callable_: Union[QCallable, Callable[[], None]]) -> StatementBlock:
    op_name = sys._getframe(1).f_code.co_name
    if (
        isinstance(callable_, QCallable)
        and len(callable_.func_decl.positional_arg_declarations) > 0
    ):
        raise ClassiqValueError(
            f"Operand argument {callable_.func_decl.name!r} to {op_name!r} should "
            f"receive 0 parameters, not "
            f"{len(callable_.func_decl.positional_arg_declarations)}"
        )
    to_operand = prepare_arg(QuantumOperandDeclaration(name=""), callable_, op_name)
    if isinstance(to_operand, str):
        return [QuantumFunctionCall(function=to_operand)]
    elif isinstance(to_operand, QuantumLambdaFunction):
        return to_operand.body
    else:
        raise ValueError(f"Unexpected operand type: {type(to_operand)}")


__all__ = [
    "bind",
    "control",
    "invert",
    "if_",
    "inplace_add",
    "inplace_xor",
    "power",
    "within_apply",
    "repeat",
]


def __dir__() -> List[str]:
    return __all__
