import pydantic

from classiq.interface.chemistry import operator
from classiq.interface.chemistry.operator import PauliOperator
from classiq.interface.generator.hamiltonian_evolution.hamiltonian_evolution import (
    HamiltonianEvolution,
)
from classiq.interface.generator.parameters import ParameterFloatType

from classiq.exceptions import ClassiqValueError


class SuzukiParameters(pydantic.BaseModel):
    order: pydantic.PositiveInt = pydantic.Field(
        default=1,
        description="The order of the Suzuki-Trotter. Supports only order equals to 1 or an even number",
    )
    repetitions: pydantic.NonNegativeInt = pydantic.Field(
        default=1, description="The number of repetitions in the Suzuki-Trotter"
    )

    @pydantic.validator("order")
    def _validate_order(cls, order: int) -> int:
        if order != 1 and order % 2:
            raise ClassiqValueError(
                f"Odd order greater than 1 is not supported. Got {order}"
            )
        return order

    class Config:
        frozen = True


class SuzukiTrotter(HamiltonianEvolution):
    """
    Suzuki trotterization of a Hermitian operator
    """

    evolution_coefficient: ParameterFloatType = pydantic.Field(
        default=1.0,
        description="A global coefficient multiplying the operator.",
        is_exec_param=True,
    )
    suzuki_parameters: SuzukiParameters = pydantic.Field(
        default_factory=SuzukiParameters, description="The Suziki parameters."
    )
    disable_scheduling: bool = pydantic.Field(
        default=False, description="Whether to disable the reordering of Pauli terms."
    )

    @pydantic.validator("pauli_operator")
    def _validate_no_complex_coefficients(
        cls, pauli_operator: PauliOperator
    ) -> PauliOperator:
        return operator.validate_operator_has_no_complex_coefficients(pauli_operator)
