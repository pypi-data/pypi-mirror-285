from typing import Any, Dict, List

import pydantic

from classiq.interface.generator.arith import number_utils

from classiq.exceptions import ClassiqStateInitializationError

_NON_INTEGER_INITIALIZATION_ERROR_MSG: str = (
    "Only natural numbers are supported as initial conditions"
)


class RegisterInitialization(pydantic.BaseModel):
    name: str
    qubits: List[int]
    initial_condition: pydantic.NonNegativeInt

    @pydantic.validator("initial_condition", pre=True)
    def _validate_initial_condition(cls, value: int) -> int:
        if not isinstance(value, int) or value < 0:
            raise ClassiqStateInitializationError(_NON_INTEGER_INITIALIZATION_ERROR_MSG)
        return value

    @pydantic.root_validator()
    def _validate_register_initialization(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        qubits: List[int] = values.get("qubits", list())
        initial_condition: int = values.get("initial_condition", 0)
        name: str = values.get("name", "")

        initial_condition_length = number_utils.size(initial_condition)
        register_length = len(qubits)
        if initial_condition_length > register_length:
            raise ClassiqStateInitializationError(
                f"Register {name} has {register_length} qubits, which is not enough to represent the number {initial_condition}."
            )
        return values
