from typing import List, Union

from pydantic import Field
from typing_extensions import Annotated

from classiq.interface.model.bind_operation import BindOperation
from classiq.interface.model.classical_if import ClassicalIf
from classiq.interface.model.control import Control
from classiq.interface.model.inplace_binary_operation import InplaceBinaryOperation
from classiq.interface.model.invert import Invert
from classiq.interface.model.power import Power
from classiq.interface.model.quantum_expressions.amplitude_loading_operation import (
    AmplitudeLoadingOperation,
)
from classiq.interface.model.quantum_expressions.arithmetic_operation import (
    ArithmeticOperation,
)
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_lambda_function import QuantumLambdaFunction
from classiq.interface.model.repeat import Repeat
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)
from classiq.interface.model.within_apply_operation import WithinApply

ConcreteQuantumStatement = Annotated[
    Union[
        QuantumFunctionCall,
        ArithmeticOperation,
        AmplitudeLoadingOperation,
        VariableDeclarationStatement,
        BindOperation,
        InplaceBinaryOperation,
        Repeat,
        Power,
        Invert,
        ClassicalIf,
        Control,
        WithinApply,
    ],
    Field(..., discriminator="kind"),
]

StatementBlock = List[ConcreteQuantumStatement]

Control.update_forward_refs(StatementBlock=StatementBlock)
QuantumLambdaFunction.update_forward_refs(StatementBlock=StatementBlock)
Repeat.update_forward_refs(StatementBlock=StatementBlock)
Power.update_forward_refs(StatementBlock=StatementBlock)
Invert.update_forward_refs(StatementBlock=StatementBlock)
WithinApply.update_forward_refs(StatementBlock=StatementBlock)
ClassicalIf.update_forward_refs(StatementBlock=StatementBlock)
