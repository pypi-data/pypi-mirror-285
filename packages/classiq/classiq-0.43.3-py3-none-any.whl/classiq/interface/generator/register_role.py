from typing import Set

from classiq._internals.enum_utils import StrEnum


class RegisterRole(StrEnum):
    INPUT = "input"
    OUTPUT = "output"
    AUXILIARY = "auxiliary"
    ZERO_INPUT = "zero_input"
    ZERO_OUTPUT = "zero_output"
    GARBAGE_OUTPUT = "garbage_output"

    @staticmethod
    def output_roles(include_garbage: bool = False) -> Set["RegisterRole"]:
        roles = {
            RegisterRole.OUTPUT,
            RegisterRole.ZERO_OUTPUT,
            RegisterRole.AUXILIARY,
        }
        if include_garbage:
            roles.add(RegisterRole.GARBAGE_OUTPUT)
        return roles

    @staticmethod
    def input_roles() -> Set["RegisterRole"]:
        return {RegisterRole.INPUT, RegisterRole.ZERO_INPUT, RegisterRole.AUXILIARY}
