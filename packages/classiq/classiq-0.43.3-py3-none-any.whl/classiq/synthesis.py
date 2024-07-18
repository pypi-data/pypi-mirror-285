from typing import NewType

import pydantic

from classiq.interface.executor.execution_preferences import ExecutionPreferences
from classiq.interface.generator.model.constraints import Constraints
from classiq.interface.generator.model.preferences.preferences import Preferences
from classiq.interface.model.model import Model, SerializedModel

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import syncify_function

SerializedQuantumProgram = NewType("SerializedQuantumProgram", str)


async def synthesize_async(
    serialized_model: SerializedModel,
) -> SerializedQuantumProgram:
    model = pydantic.parse_raw_as(Model, serialized_model)
    quantum_program = await ApiWrapper.call_generation_task(model)
    return SerializedQuantumProgram(quantum_program.json(indent=2))


synthesize = syncify_function(synthesize_async)


def set_preferences(
    serialized_model: SerializedModel, preferences: Preferences
) -> SerializedModel:
    model = pydantic.parse_raw_as(Model, serialized_model)
    model.preferences = preferences
    return model.get_model()


def set_constraints(
    serialized_model: SerializedModel, constraints: Constraints
) -> SerializedModel:
    model = pydantic.parse_raw_as(Model, serialized_model)
    model.constraints = constraints
    return model.get_model()


def set_execution_preferences(
    serialized_model: SerializedModel, execution_preferences: ExecutionPreferences
) -> SerializedModel:
    model = pydantic.parse_raw_as(Model, serialized_model)
    model.execution_preferences = execution_preferences
    return model.get_model()


__all__ = [
    "SerializedModel",
    "SerializedQuantumProgram",
    "synthesize",
    "set_preferences",
    "set_constraints",
    "set_execution_preferences",
]
