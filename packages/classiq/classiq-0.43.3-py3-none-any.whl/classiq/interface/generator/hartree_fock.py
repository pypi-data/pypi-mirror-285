from typing import Any, Union

import pydantic

from classiq.interface.chemistry.ground_state_problem import (
    CHEMISTRY_PROBLEMS,
    HamiltonianProblem,
    MoleculeProblem,
)
from classiq.interface.generator.chemistry_function_params import (
    ChemistryFunctionParams,
)

from classiq.exceptions import ClassiqValueError


class HartreeFock(ChemistryFunctionParams):
    @pydantic.validator("gs_problem")
    def validate_gs_problem(
        cls, gs_problem: Any
    ) -> Union[MoleculeProblem, HamiltonianProblem]:
        if not isinstance(gs_problem, CHEMISTRY_PROBLEMS):
            raise ClassiqValueError(
                f"ground state problem must be of type {CHEMISTRY_PROBLEMS}"
            )
        return gs_problem
