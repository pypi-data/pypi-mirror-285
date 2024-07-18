from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import pydantic

from classiq.interface.generator.expressions.enums.finance_functions import (
    get_finance_function_dict,
)
from classiq.interface.helpers.custom_pydantic_types import (
    PydanticNonZeroProbabilityFloat,
)

from classiq.exceptions import ClassiqValueError

if TYPE_CHECKING:
    from classiq.qmod.builtins.enums import FinanceFunctionType


class FunctionCondition(pydantic.BaseModel):
    threshold: float
    larger: bool = pydantic.Field(
        default=False,
        description="When true, function is set when input is larger to threshold and otherwise 0. Default is False.",
    )

    class Config:
        frozen = True


class FinanceFunctionInput(pydantic.BaseModel):
    f: "FinanceFunctionType" = pydantic.Field(
        description="An enumeration of the wanted financial function: VaR, expected "
        "shortfall, European call options or x^2"
    )
    variable: str = pydantic.Field(
        default="x", description="Variable/s of the function"
    )
    condition: FunctionCondition = pydantic.Field(
        description="The condition for the function"
    )
    polynomial_degree: Optional[int] = pydantic.Field(
        default=None,
        description="The polynomial degree of approximation, uses linear approximation by default",
    )
    use_chebyshev_polynomial_approximation: bool = pydantic.Field(
        default=False,
        description="Flag if to use chebyshev polynomial approximation for target function",
    )

    tail_probability: Optional[PydanticNonZeroProbabilityFloat] = pydantic.Field(
        default=None,
        description="The required probability on the tail of the distribution (1 - percentile)",
    )

    @pydantic.validator("f", pre=True)
    def _convert_f_if_str(cls, f: Any) -> "FinanceFunctionType":
        # Keep this for backwards-compatible string support
        if f in get_finance_function_dict():
            return get_finance_function_dict()[f]
        return f

    @pydantic.validator("use_chebyshev_polynomial_approximation")
    def _validate_polynomial_flag(
        cls, use_chebyshev_flag: bool, values: Dict[str, Any]
    ) -> bool:
        if use_chebyshev_flag ^ (values.get("polynomial_degree") is None):
            return use_chebyshev_flag
        raise ClassiqValueError(
            "Degree must be positive and use_chebyshev_polynomial_approximation set to True"
        )

    @pydantic.validator("f")
    def _validate_finance_function(
        cls, f: Union[int, str, "FinanceFunctionType"]
    ) -> "FinanceFunctionType":
        from classiq.qmod.builtins.enums import FinanceFunctionType

        if isinstance(f, FinanceFunctionType):
            return f
        if isinstance(f, int):
            return FinanceFunctionType(f)
        return get_finance_function_dict()[f]

    @pydantic.validator("tail_probability", always=True)
    def _validate_tail_probability_assignment_for_shortfall(
        cls,
        tail_probability: Optional[PydanticNonZeroProbabilityFloat],
        values: Dict[str, Any],
    ) -> Optional[PydanticNonZeroProbabilityFloat]:
        from classiq.qmod.builtins.enums import FinanceFunctionType

        if values.get("f") == FinanceFunctionType.SHORTFALL and not tail_probability:
            raise ClassiqValueError(
                "Tail probability must be set for expected shortfall"
            )
        return tail_probability

    class Config:
        frozen = True
