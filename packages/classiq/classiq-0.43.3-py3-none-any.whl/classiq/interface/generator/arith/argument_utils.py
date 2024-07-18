from typing import Tuple, Union

from classiq.interface.generator.arith import number_utils
from classiq.interface.generator.arith.register_user_input import RegisterArithmeticInfo

RegisterOrConst = Union[RegisterArithmeticInfo, float]


def fraction_places(argument: RegisterOrConst) -> int:
    if isinstance(argument, RegisterArithmeticInfo):
        return argument.fraction_places
    return number_utils.fraction_places(argument)


def integer_part_size(argument: RegisterOrConst) -> int:
    if isinstance(argument, RegisterArithmeticInfo):
        return argument.integer_part_size
    return number_utils.integer_part_size(argument)


def size(argument: RegisterOrConst) -> int:
    if isinstance(argument, RegisterArithmeticInfo):
        return argument.size
    return number_utils.size(argument)


def is_signed(argument: RegisterOrConst) -> bool:
    if isinstance(argument, RegisterArithmeticInfo):
        return argument.is_signed
    return argument < 0


def upper_bound(argument: RegisterOrConst) -> float:
    if isinstance(argument, RegisterArithmeticInfo):
        return max(argument.bounds)
    return argument


def lower_bound(argument: RegisterOrConst) -> float:
    if isinstance(argument, RegisterArithmeticInfo):
        return min(argument.bounds)
    return argument


def bounds(argument: RegisterOrConst) -> Tuple[float, float]:
    if isinstance(argument, RegisterArithmeticInfo):
        return argument.bounds
    return argument, argument


def limit_fraction_places(
    argument: RegisterOrConst, machine_precision: int
) -> RegisterOrConst:
    if isinstance(argument, RegisterArithmeticInfo):
        return argument.limit_fraction_places(machine_precision)
    return number_utils.limit_fraction_places(argument, machine_precision)


def arg_bounds_overlap(args: Tuple[RegisterOrConst, RegisterOrConst]) -> bool:
    return (max(bounds(args[0])) - min(bounds(args[1]))) * (
        min(bounds(args[0])) - max(bounds(args[1]))
    ) < 0


def as_arithmetic_info(
    arg: RegisterOrConst, with_bounds: bool = True
) -> RegisterArithmeticInfo:
    if isinstance(arg, RegisterArithmeticInfo):
        return arg
    return RegisterArithmeticInfo(
        size=number_utils.size(arg),
        is_signed=arg < 0,
        fraction_places=number_utils.fraction_places(arg),
        bounds=(arg, arg) if with_bounds else None,
    )
