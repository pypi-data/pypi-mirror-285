from collections import defaultdict
from typing import Dict, Optional, Union

import pydantic
from pydantic import BaseModel, Extra

from classiq.interface.generator.transpiler_basis_gates import TranspilerBasisGates

from classiq._internals.enum_utils import StrEnum
from classiq.exceptions import ClassiqValueError

UNCONSTRAINED = -1


class OptimizationParameter(StrEnum):
    WIDTH = "width"
    DEPTH = "depth"
    NO_OPTIMIZATION = "no_opt"


OptimizationParameterType = Union[OptimizationParameter, TranspilerBasisGates]


def optimization_parameter_type_from_string(param: str) -> OptimizationParameterType:
    for enum_ in (OptimizationParameter, TranspilerBasisGates):
        try:
            return enum_(param)  # type: ignore[return-value]
        except ValueError:
            pass
    raise ClassiqValueError(f"Invalid OptimizationParameterType {param}")


class Constraints(BaseModel, extra=Extra.forbid):
    """
    Input constraints for the generated quantum circuit.
    """

    max_width: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None,
        description="Maximum number of qubits in generated quantum circuit",
    )
    max_depth: Optional[pydantic.PositiveInt] = None

    max_gate_count: Dict[TranspilerBasisGates, pydantic.NonNegativeInt] = (
        pydantic.Field(default_factory=lambda: defaultdict(int))
    )

    optimization_parameter: OptimizationParameterType = pydantic.Field(
        default=OptimizationParameter.NO_OPTIMIZATION,
        description="If set, the synthesis engine optimizes the solution"
        " according to that chosen parameter",
    )
