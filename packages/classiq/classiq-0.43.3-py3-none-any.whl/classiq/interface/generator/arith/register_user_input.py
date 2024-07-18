from typing import Any, Dict, Optional

import pydantic

from classiq.interface.generator.arith import number_utils
from classiq.interface.helpers.custom_pydantic_types import PydanticFloatTuple
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)

from classiq.exceptions import ClassiqValueError


class RegisterArithmeticInfo(HashablePydanticBaseModel):
    size: pydantic.PositiveInt
    is_signed: bool = pydantic.Field(default=False)
    fraction_places: pydantic.NonNegativeInt = pydantic.Field(default=0)
    bounds: PydanticFloatTuple = pydantic.Field(default=None)

    @pydantic.root_validator(pre=True)
    def _remove_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "name" in values:
            values.pop("name")
        return values

    @pydantic.validator("bounds", always=True)
    def _validate_bounds(
        cls, bounds: Optional[PydanticFloatTuple], values: Dict[str, Any]
    ) -> PydanticFloatTuple:
        if bounds is not None:
            if min(bounds) < 0:
                assert values.get("is_signed")
            fraction_places = values.get("fraction_places")
            if not isinstance(fraction_places, int):
                raise ClassiqValueError(
                    "RegisterUserInput must have an integer fraction_places"
                )
            return number_utils.limit_fraction_places(
                min(bounds), machine_precision=fraction_places
            ), number_utils.limit_fraction_places(
                max(bounds), machine_precision=fraction_places
            )

        size = values.get("size")
        if not isinstance(size, int):
            raise ClassiqValueError("RegisterUserInput must have an integer size")
        is_signed: bool = values.get("is_signed", False)
        lb = 0 if not is_signed else -(2 ** (size - 1))
        ub = 2**size - 1 if not is_signed else 2 ** (size - 1) - 1
        fraction_factor = float(2 ** -values.get("fraction_places", 0))
        return (lb * fraction_factor, ub * fraction_factor)

    def limit_fraction_places(self, machine_precision: int) -> "RegisterArithmeticInfo":
        truncated_bits: int = max(self.fraction_places - machine_precision, 0)
        return RegisterArithmeticInfo(
            size=self.size - truncated_bits,
            is_signed=self.is_signed,
            fraction_places=self.fraction_places - truncated_bits,
            bounds=self.bounds,
        )

    @property
    def is_boolean_register(self) -> bool:
        return (not self.is_signed) and (self.size == 1) and (self.fraction_places == 0)

    @property
    def is_frac(self) -> bool:
        return self.fraction_places > 0

    @property
    def integer_part_size(self) -> pydantic.NonNegativeInt:
        return self.size - self.fraction_places

    class Config:
        frozen = True


class RegisterUserInput(RegisterArithmeticInfo):
    name: str = pydantic.Field(default="")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._fields_to_skip_in_hash = frozenset({"name"})

    @pydantic.root_validator(pre=True)
    def _remove_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values

    def revalued(self, **kwargs: Any) -> "RegisterUserInput":
        return self.copy(update=kwargs)

    @classmethod
    def from_arithmetic_info(
        cls, info: RegisterArithmeticInfo, name: str = ""
    ) -> "RegisterUserInput":
        return RegisterUserInput(
            name=name,
            size=info.size,
            is_signed=info.is_signed,
            fraction_places=info.fraction_places,
            bounds=info.bounds,
        )
