import re
from typing import Mapping, Set

from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
    QuantumOperandDeclaration,
)
from classiq.interface.model.quantum_lambda_function import (
    QuantumLambdaFunction,
    QuantumOperand,
)

from classiq.exceptions import ClassiqError
from classiq.qmod.semantics.error_manager import ErrorManager


def validate_call_arguments(
    fc: QuantumFunctionCall,
    function_dict: Mapping[str, QuantumFunctionDeclaration],
) -> None:
    _check_params_against_declaration(
        set(fc.params.keys()),
        set(fc.func_decl.param_decls.keys()),
        fc.func_decl.name,
    )
    _check_ports_against_declaration(fc, fc.func_decl)
    _check_params_against_declaration(
        set(fc.operands.keys()),
        set(fc.func_decl.operand_declarations.keys()),
        fc.func_name,
    )
    _check_operands_against_declaration(fc, fc.func_decl, function_dict)


def _check_ports_against_declaration(
    call: QuantumFunctionCall, decl: QuantumFunctionDeclaration
) -> None:
    call_input_names = set(call.inputs.keys())

    _check_params_against_declaration(
        call_input_names,
        decl.ports_by_declaration_direction(PortDeclarationDirection.Input),
        call.func_name,
    )

    call_output_names = set(call.outputs.keys())

    _check_params_against_declaration(
        call_output_names,
        decl.ports_by_declaration_direction(PortDeclarationDirection.Output),
        call.func_name,
    )

    inout_params = set(call.inouts.keys())

    _check_params_against_declaration(
        inout_params,
        decl.ports_by_declaration_direction(PortDeclarationDirection.Inout),
        call.func_name,
    )


def _check_operand_against_declaration(
    call: QuantumFunctionCall,
    operand_decl: QuantumOperandDeclaration,
    operand_argument: QuantumOperand,
    function_dict: Mapping[str, QuantumFunctionDeclaration],
    in_list: bool = False,
) -> None:
    if isinstance(operand_argument, list):
        if in_list:
            ErrorManager().add_error(
                f"{str(operand_argument)!r} argument to {call.func_decl.name!r} is not "
                f"a valid operand. Nested operand lists are not permitted"
            )
            return
        for arg in operand_argument:
            _check_operand_against_declaration(
                call, operand_decl, arg, function_dict, in_list=True
            )
        return
    operand_arg_decl: QuantumFunctionDeclaration
    if isinstance(operand_argument, str):
        if operand_argument not in function_dict:
            ErrorManager().add_error(
                f"{operand_argument!r} argument to {call.func_decl.name!r} is not a "
                f"registered function"
            )
            return
        operand_arg_decl = function_dict[operand_argument]
    elif isinstance(operand_argument, QuantumLambdaFunction):
        if operand_argument.func_decl is None:
            return
        operand_arg_decl = operand_argument.func_decl
    else:
        raise ClassiqError(
            f"{str(operand_argument)!r} argument to {call.func_decl.name!r} is not a "
            f"valid operand"
        )
    num_arg_parameters = len(operand_arg_decl.get_positional_arg_decls())
    num_decl_parameters = len(operand_decl.get_positional_arg_decls())
    if num_arg_parameters != num_decl_parameters:
        ErrorManager().add_error(
            f"Signature of argument {operand_argument!r} to {call.func_decl.name!r} "
            f"does not match the signature of parameter {operand_decl.name!r}. "
            f"{operand_decl.name!r} accepts {num_decl_parameters} parameters but "
            f"{operand_argument!r} accepts {num_arg_parameters} parameters"
        )


def _check_operands_against_declaration(
    call: QuantumFunctionCall,
    decl: QuantumFunctionDeclaration,
    function_dict: Mapping[str, QuantumFunctionDeclaration],
) -> None:
    for operand_parameter, operand_argument in call.operands.items():
        _check_operand_against_declaration(
            call,
            decl.operand_declarations[operand_parameter],
            operand_argument,
            function_dict,
        )


def _check_params_against_declaration(
    call_params: Set[str],
    param_decls: Set[str],
    callee_name: str,
) -> None:
    unknown_params = call_params - param_decls
    if any(re.match(r"arg\d+", param) for param in unknown_params):
        error_msg = (
            f"Unsupported passing of named function {callee_name!r} as an operand."
            "\nSuggestion: replace the named function with lambda function."
        )
    else:
        error_msg = f"Unknown parameters {unknown_params} in call to {callee_name!r}."
    if unknown_params:
        ErrorManager().add_error(error_msg)

    missing_params = param_decls - call_params
    if missing_params:
        ErrorManager().add_error(
            f"Missing parameters {missing_params} in call to {callee_name!r}."
        )
