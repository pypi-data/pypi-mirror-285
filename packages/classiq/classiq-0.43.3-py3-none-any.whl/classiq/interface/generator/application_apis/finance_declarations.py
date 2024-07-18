from enum import Enum
from typing import TYPE_CHECKING, Callable, Mapping

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_function_declaration import (
    ClassicalFunctionDeclaration,
)
from classiq.interface.generator.functions.classical_type import (
    Bool,
    ClassicalList,
    Integer,
    Real,
    Struct,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.types.struct_declaration import StructDeclaration
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)

if TYPE_CHECKING:
    from classiq.qmod.builtins.structs import GaussianModel
    from classiq.qmod.symbolic_expr import SymbolicExpr

FUNCTION_PORT_NAME = "func_port"
OBJECTIVE_PORT_NAME = "obj_port"


class FinanceModelType(Enum):
    LogNormal = "log_normal"
    Gaussian = "gaussian"


FINANCE_FUNCTION_PORT_SIZE_MAPPING: Mapping[FinanceModelType, str] = {
    FinanceModelType.Gaussian: "get_field(finance_model, 'num_qubits') + get_field(get_field(finance_model, 'rhos'), 'len') + floor(log(sum(get_field(finance_model, 'loss')), 2)) + 1",
    FinanceModelType.LogNormal: "get_field(finance_model, 'num_qubits')",
}


def _get_gaussian_size(finance_model: "GaussianModel") -> "SymbolicExpr":
    from classiq.qmod.symbolic import floor, log, sum as sym_sum

    return (
        finance_model.num_qubits
        + finance_model.rhos.len
        + floor(log(sym_sum(finance_model.loss), 2))
        + 1
    )


FINANCE_FUNCTION_PORT_SIZE_FUNCTION_MAPPING: Mapping[FinanceModelType, Callable] = {
    FinanceModelType.Gaussian: _get_gaussian_size,
    FinanceModelType.LogNormal: lambda finance_model: finance_model.num_qubits,
}


def _generate_finance_function(
    finance_model: FinanceModelType,
) -> QuantumFunctionDeclaration:
    return QuantumFunctionDeclaration(
        name=f"{finance_model.value}_finance",
        param_decls={
            "finance_model": Struct(name=f"{finance_model.name}Model"),
            "finance_function": Struct(name="FinanceFunction"),
        },
        port_declarations={
            FUNCTION_PORT_NAME: PortDeclaration(
                name=FUNCTION_PORT_NAME,
                direction=PortDeclarationDirection.Inout,
                size=Expression(expr=FINANCE_FUNCTION_PORT_SIZE_MAPPING[finance_model]),
            ),
            OBJECTIVE_PORT_NAME: PortDeclaration(
                name=OBJECTIVE_PORT_NAME,
                direction=PortDeclarationDirection.Inout,
                size=Expression(expr="1"),
            ),
        },
    )


LOG_NORMAL_FINANCE_FUNCTION = _generate_finance_function(FinanceModelType.LogNormal)

GAUSSIAN_FINANCE_FUNCTION = _generate_finance_function(FinanceModelType.Gaussian)

GAUSSIAN_MODEL = StructDeclaration(
    name="GaussianModel",
    variables={
        "num_qubits": Integer(),
        "normal_max_value": Real(),
        "default_probabilities": ClassicalList(element_type=Real()),
        "rhos": ClassicalList(element_type=Real()),
        "loss": ClassicalList(element_type=Integer()),
        "min_loss": Integer(),
    },
)


LOG_NORMAL_MODEL = StructDeclaration(
    name="LogNormalModel",
    variables={"num_qubits": Integer(), "mu": Real(), "sigma": Real()},
)


FINANCE_FUNCTION = StructDeclaration(
    name="FinanceFunction",
    variables={
        "f": Integer(),
        "threshold": Real(),
        "larger": Bool(),
        "polynomial_degree": Integer(),
        "use_chebyshev_polynomial_approximation": Bool(),
        "tail_probability": Real(),
    },
)

LOG_NORMAL_FINANCE_POST_PROCESS = ClassicalFunctionDeclaration(
    name="log_normal_finance_post_process",
    param_decls={
        "finance_model": Struct(name="LogNormalModel"),
        "estimation_method": Struct(name="FinanceFunction"),
        "probability": Real(),
    },
    return_type=Real(),
)

GAUSSIAN_FINANCE_POST_PROCESS = ClassicalFunctionDeclaration(
    name="gaussian_finance_post_process",
    param_decls={
        "finance_model": Struct(name="GaussianModel"),
        "estimation_method": Struct(name="FinanceFunction"),
        "probability": Real(),
    },
    return_type=Real(),
)

__all__ = [
    "LOG_NORMAL_FINANCE_FUNCTION",
    "GAUSSIAN_FINANCE_FUNCTION",
    "GAUSSIAN_MODEL",
    "LOG_NORMAL_MODEL",
    "FINANCE_FUNCTION",
    "LOG_NORMAL_FINANCE_POST_PROCESS",
    "GAUSSIAN_FINANCE_POST_PROCESS",
]
