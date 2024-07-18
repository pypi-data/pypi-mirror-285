from datetime import timedelta
from typing import Any, Dict, Optional

import pydantic

from classiq.interface.backend.backend_preferences import (
    AWS_DEFAULT_JOB_TIMEOUT_SECONDS,
    AwsBackendPreferences,
    BackendPreferencesTypes,
    backend_preferences_field,
)
from classiq.interface.backend.pydantic_backend import MAX_EXECUTION_TIMEOUT_SECONDS
from classiq.interface.backend.quantum_backend_providers import (
    ClassiqSimulatorBackendNames,
)
from classiq.interface.executor.optimizer_preferences import OptimizerType
from classiq.interface.generator.model.preferences.preferences import (
    TranspilationOption,
)
from classiq.interface.generator.model.preferences.randomness import create_random_seed
from classiq.interface.generator.noise_properties import NoiseProperties

from classiq._internals.enum_utils import ReprEnum
from classiq.exceptions import ClassiqValueError

DIFFERENT_TIMEOUT_MSG = (
    "Timeout is defined differently in the execution preferences and the "
    "AWS Backend Preferences."
)

TIMEOUT_LARGE_FOR_AWS_MSG = (
    "Timeout is larger than the current allowed limit of "
    f"{timedelta(MAX_EXECUTION_TIMEOUT_SECONDS)}"
)


class QaeWithQpeEstimationMethod(int, ReprEnum):
    MAXIMUM_LIKELIHOOD = 0
    BEST_FIT = 1


class ExecutionPreferences(pydantic.BaseModel):
    timeout_sec: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None,
        description="If set, limits the execution runtime. Value is in seconds. "
        "Not supported on all platforms.",
    )
    noise_properties: Optional[NoiseProperties] = pydantic.Field(
        default=None, description="Properties of the noise in the circuit"
    )
    random_seed: int = pydantic.Field(
        default_factory=create_random_seed,
        description="The random seed used for the execution",
    )
    backend_preferences: BackendPreferencesTypes = backend_preferences_field(
        backend_name=ClassiqSimulatorBackendNames.SIMULATOR
    )
    num_shots: Optional[pydantic.PositiveInt] = pydantic.Field(default=None)
    transpile_to_hardware: TranspilationOption = pydantic.Field(
        default=TranspilationOption.DECOMPOSE,
        description="Transpile the circuit to the hardware basis gates before execution",
        title="Transpilation Option",
    )
    job_name: Optional[str] = pydantic.Field(
        min_length=1,
        description="The job name",
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @pydantic.validator("backend_preferences", always=True)
    def validate_timeout_for_aws(
        cls, backend_preferences: BackendPreferencesTypes, values: Dict[str, Any]
    ) -> BackendPreferencesTypes:
        timeout = values.get("timeout_sec", None)
        if (
            not isinstance(backend_preferences, AwsBackendPreferences)
            or timeout is None
        ):
            return backend_preferences
        if (
            timeout != backend_preferences.job_timeout
            and backend_preferences.job_timeout != AWS_DEFAULT_JOB_TIMEOUT_SECONDS
        ):
            raise ClassiqValueError(DIFFERENT_TIMEOUT_MSG)
        if timeout > MAX_EXECUTION_TIMEOUT_SECONDS:
            raise ClassiqValueError(TIMEOUT_LARGE_FOR_AWS_MSG)

        backend_preferences.job_timeout = timeout
        return backend_preferences


__all__ = [
    "ExecutionPreferences",
    "OptimizerType",
    "NoiseProperties",
    "QaeWithQpeEstimationMethod",
]
