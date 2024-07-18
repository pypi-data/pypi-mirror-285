from typing import TYPE_CHECKING, Final, Iterable, Optional

import pydantic

from classiq.interface.generator.arith import argument_utils, number_utils
from classiq.interface.generator.arith.arithmetic_operations import (
    ArithmeticOperationParams,
)
from classiq.interface.generator.arith.register_user_input import RegisterArithmeticInfo
from classiq.interface.generator.function_params import get_zero_input_name

from classiq.exceptions import ClassiqValueError

UNARY_ARG_NAME: Final[str] = "arg"


class UnaryOpParams(ArithmeticOperationParams):
    arg: RegisterArithmeticInfo
    inplace: bool = False

    def garbage_output_size(self) -> pydantic.NonNegativeInt:
        return int(self.is_inplaced()) * (
            max(self.arg.integer_part_size - self.result_register.integer_part_size, 0)
            + max(self.arg.fraction_places - self.result_register.fraction_places, 0)
        )

    def should_add_zero_inputs(self) -> bool:
        return not self.is_inplaced() or self.zero_input_for_extension() > 0

    def zero_input_for_extension(self) -> pydantic.NonNegativeInt:
        return max(0, self.result_register.size - self.arg.size)

    def _create_ios(self) -> None:
        self._inputs = {UNARY_ARG_NAME: self.arg}
        self._outputs = {self.output_name: self.result_register}

        zero_input_name = get_zero_input_name(self.output_name)
        if not self.is_inplaced():
            self._outputs[UNARY_ARG_NAME] = self.arg
            zero_input_register = self.result_register
            self._zero_inputs = {zero_input_name: zero_input_register}
            return
        if self.zero_input_for_extension() > 0:
            output_extension_size = self.zero_input_for_extension()
            self._create_zero_input_registers({zero_input_name: output_extension_size})
        if self.garbage_output_size() > 0:
            self._outputs[self.garbage_output_name] = RegisterArithmeticInfo(
                size=self.garbage_output_size()
            )

    def is_inplaced(self) -> bool:
        return self.inplace

    def get_params_inplace_options(self) -> Iterable["UnaryOpParams"]:
        params_kwargs = self.copy().__dict__
        params_kwargs["inplace"] = True
        yield self.__class__(**params_kwargs)

    class Config:
        arbitrary_types_allowed = True


class BitwiseInvert(UnaryOpParams):
    output_name = "inverted"

    def _get_result_register(self) -> RegisterArithmeticInfo:
        eff_arg = argument_utils.limit_fraction_places(self.arg, self.machine_precision)
        if TYPE_CHECKING:
            assert isinstance(eff_arg, RegisterArithmeticInfo)
        return RegisterArithmeticInfo(
            size=self.output_size or eff_arg.size,
            fraction_places=eff_arg.fraction_places,
            is_signed=eff_arg.is_signed and self._include_sign,
        )


class Negation(UnaryOpParams):
    output_name = "negated"

    @staticmethod
    def _expected_result_size(arg: RegisterArithmeticInfo) -> pydantic.PositiveInt:
        if arg.size == 1:
            return 1
        return arg.fraction_places + number_utils.bounds_to_integer_part_size(
            *(-bound for bound in arg.bounds)
        )

    def _get_result_register(self) -> RegisterArithmeticInfo:
        eff_arg = self.arg.limit_fraction_places(self.machine_precision)
        is_signed = max(eff_arg.bounds) > 0 and self._include_sign
        bounds = (-max(eff_arg.bounds), -min(eff_arg.bounds))
        return RegisterArithmeticInfo(
            size=self.output_size or self._expected_result_size(eff_arg),
            fraction_places=eff_arg.fraction_places,
            is_signed=is_signed,
            bounds=bounds if (is_signed or min(bounds) >= 0) else None,
        )

    def zero_input_for_extension(self) -> pydantic.NonNegativeInt:
        eff_arg = self.arg.limit_fraction_places(self.machine_precision)
        if (self.output_size or eff_arg.size) == 1:
            return 0
        return (
            self.output_size or self._expected_result_size(self.arg)
        ) - self.arg.size


class Sign(UnaryOpParams):
    output_name = "sign"

    @pydantic.validator("output_size")
    def _validate_output_size(
        cls, output_size: Optional[pydantic.PositiveInt]
    ) -> pydantic.PositiveInt:
        if output_size is not None and output_size != 1:
            raise ClassiqValueError("Sign output size must be 1")
        return 1

    def _get_result_register(self) -> RegisterArithmeticInfo:
        return RegisterArithmeticInfo(size=1, fraction_places=0, is_signed=False)

    def is_inplaced(self) -> bool:
        return self.inplace and self.arg.is_signed
