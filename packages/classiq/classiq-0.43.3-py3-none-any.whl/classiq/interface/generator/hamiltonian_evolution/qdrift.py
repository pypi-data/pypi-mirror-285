import pydantic

from classiq.interface.chemistry import operator
from classiq.interface.chemistry.operator import PauliOperator
from classiq.interface.generator.hamiltonian_evolution.hamiltonian_evolution import (
    HamiltonianEvolution,
)
from classiq.interface.generator.parameters import ParameterFloatType


class QDrift(HamiltonianEvolution):
    """
    qDrift trotterization of a Hermitian operator; see https://arxiv.org/abs/1811.08017
    """

    evolution_coefficient: ParameterFloatType = pydantic.Field(
        default=1.0,
        description="A global coefficient multiplying the operator.",
        is_exec_param=True,
    )
    num_qdrift: pydantic.PositiveInt = pydantic.Field(
        description="The number of elements in the qDrift product.",
    )

    @pydantic.validator("pauli_operator")
    def _validate_is_hermitian(cls, pauli_operator: PauliOperator) -> PauliOperator:
        return operator.validate_operator_is_hermitian(pauli_operator)
