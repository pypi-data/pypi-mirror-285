from typing import List, Mapping

from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)
from classiq.interface.model.quantum_lambda_function import (
    QuantumCallable,
    QuantumLambdaFunction,
    QuantumOperand,
)

from classiq.exceptions import ClassiqError


def annotate_function_call_decl(
    fc: QuantumFunctionCall,
    function_dict: Mapping[str, QuantumFunctionDeclaration],
) -> None:
    if fc._func_decl is None:
        func_decl = function_dict.get(fc.func_name)
        if func_decl is None:
            raise ClassiqError(
                f"Error resolving function {fc.func_name}, the function is not found in included library."
            )
        fc.set_func_decl(func_decl)

    for name, op in fc.operands.items():
        op_decl = fc.func_decl.operand_declarations[name]
        for qlambda in _get_lambda_defs(op):
            if isinstance(qlambda, QuantumLambdaFunction):
                qlambda.set_op_decl(op_decl)


def _get_lambda_defs(operand: QuantumOperand) -> List[QuantumCallable]:
    if isinstance(operand, list):
        return operand
    return [operand]
