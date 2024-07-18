from typing import Any

from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
    QuantumOperandDeclaration,
)


def get_single_empty_operand_operator(
    operator_name: str, **kwargs: Any
) -> QuantumFunctionDeclaration:
    operand_field_name = "operand"
    return QuantumFunctionDeclaration(
        name=operator_name,
        operand_declarations={
            operand_field_name: QuantumOperandDeclaration(name=operand_field_name)
        },
        **kwargs,
    )


PERMUTE_OPERATOR = QuantumFunctionDeclaration(
    name="permute",
    operand_declarations={
        "functions": QuantumOperandDeclaration(
            name="functions",
            is_list=True,
        )
    },
)

APPLY_OPERATOR = get_single_empty_operand_operator(operator_name="apply")

STD_QMOD_OPERATORS = [
    PERMUTE_OPERATOR,
    APPLY_OPERATOR,
]
