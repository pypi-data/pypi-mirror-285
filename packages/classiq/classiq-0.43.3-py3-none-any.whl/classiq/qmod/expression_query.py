from typing import TYPE_CHECKING, List, Tuple

from classiq.interface.generator.arith.arithmetic import compute_arithmetic_result_type
from classiq.interface.generator.arith.number_utils import MAXIMAL_MACHINE_PRECISION
from classiq.interface.model.quantum_type import QuantumNumeric

from classiq.qmod.qmod_variable import QNum
from classiq.qmod.symbolic_type import SymbolicTypes


def get_expression_numeric_attributes(
    vars: List[QNum],
    expr: SymbolicTypes,
    machine_precision: int = MAXIMAL_MACHINE_PRECISION,
) -> Tuple[int, bool, int]:
    res_type = compute_arithmetic_result_type(
        expr_str=str(expr),
        var_types={var._name: var.get_qmod_type() for var in vars},
        machine_precision=machine_precision,
    )
    if TYPE_CHECKING:
        assert isinstance(res_type, QuantumNumeric)
    return res_type.size_in_bits, res_type.sign_value, res_type.fraction_digits_value
