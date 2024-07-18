from typing import List, Tuple

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.bind_operation import BindOperation
from classiq.interface.model.handle_binding import HandleBinding, SlicedHandleBinding
from classiq.interface.model.model import Model, SerializedModel
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_expressions.arithmetic_operation import (
    ArithmeticOperation,
)
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_lambda_function import QuantumLambdaFunction
from classiq.interface.model.quantum_type import QuantumBitvector, QuantumNumeric
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)

from classiq import RegisterUserInput

_OUTPUT_VARIABLE_NAME = "result"

_PREDICATE_FUNCTION_NAME = "expr_predicate"


def _arithmetic_oracle_ios(
    definitions: List[Tuple[str, RegisterUserInput]], handle_name: str
) -> List[HandleBinding]:
    cursor = 0
    ios: List[HandleBinding] = []
    for _, reg in definitions:
        ios.append(
            SlicedHandleBinding(
                name=handle_name,
                start=Expression(expr=f"{cursor}"),
                end=Expression(expr=f"{cursor + reg.size}"),
            )
        )
        cursor += reg.size
    return ios


def _construct_arithmetic_oracle(
    predicate_function: str,
    definitions: List[Tuple[str, RegisterUserInput]],
) -> QuantumFunctionCall:
    predicate_var_binding = _arithmetic_oracle_ios(definitions, "arg0")
    predicate_var_binding.append(HandleBinding(name="arg1"))
    return QuantumFunctionCall(
        function="phase_oracle",
        positional_args=[
            QuantumLambdaFunction(
                body=[
                    QuantumFunctionCall(
                        function=predicate_function,
                        positional_args=predicate_var_binding,
                    ),
                ],
            ),
            HandleBinding(name="arg0"),
        ],
    )


def grover_main_port_declarations(
    definitions: List[Tuple[str, RegisterUserInput]],
    direction: PortDeclarationDirection,
) -> List[PortDeclaration]:
    return [
        PortDeclaration(
            name=name,
            quantum_type=QuantumNumeric(
                size=Expression(expr=f"{reg.size}"),
                is_signed=Expression(expr=f"{reg.is_signed}"),
                fraction_digits=Expression(expr=f"{reg.fraction_places}"),
            ),
            direction=direction,
        )
        for name, reg in definitions
    ]


def construct_grover_model(
    definitions: List[Tuple[str, RegisterUserInput]],
    expression: str,
    num_reps: int = 1,
) -> SerializedModel:
    predicate_port_decls = grover_main_port_declarations(
        definitions, PortDeclarationDirection.Inout
    )
    predicate_port_decls.append(
        PortDeclaration(
            name="res",
            quantum_type=QuantumBitvector(length=Expression(expr="1")),
            direction=PortDeclarationDirection.Inout,
        )
    )
    num_qubits = sum(reg.size for _, reg in definitions)

    grover_model = Model(
        functions=[
            NativeFunctionDefinition(
                name=_PREDICATE_FUNCTION_NAME,
                positional_arg_declarations=predicate_port_decls,
                body=[
                    ArithmeticOperation(
                        expression=Expression(expr=expression),
                        result_var=HandleBinding(name="res"),
                        inplace_result=True,
                    ),
                ],
            ),
            NativeFunctionDefinition(
                name="main",
                positional_arg_declarations=grover_main_port_declarations(
                    definitions, PortDeclarationDirection.Output
                ),
                body=[
                    VariableDeclarationStatement(name="packed_vars"),
                    QuantumFunctionCall(
                        function="allocate",
                        positional_args=[
                            Expression(expr=f"{num_qubits}"),
                            HandleBinding(name="packed_vars"),
                        ],
                    ),
                    QuantumFunctionCall(
                        function="grover_search",
                        positional_args=[
                            Expression(expr=f"{num_reps}"),
                            QuantumLambdaFunction(
                                body=[
                                    _construct_arithmetic_oracle(
                                        _PREDICATE_FUNCTION_NAME,
                                        definitions,
                                    )
                                ]
                            ),
                            HandleBinding(name="packed_vars"),
                        ],
                    ),
                    BindOperation(
                        in_handles=[HandleBinding(name="packed_vars")],
                        out_handles=[
                            HandleBinding(name=name) for name, _ in definitions
                        ],
                    ),
                ],
            ),
        ],
    )
    return grover_model.get_model()
