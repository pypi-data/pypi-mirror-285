from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Iterable, List, Optional, Union

import pydantic
from pydantic import BaseModel, PrivateAttr, validator

from classiq.interface.backend import pydantic_backend
from classiq.interface.backend.quantum_backend_providers import (
    EXACT_SIMULATORS,
    AliceBobBackendNames,
    AmazonBraketBackendNames,
    AzureQuantumBackendNames,
    ClassiqNvidiaBackendNames,
    ClassiqSimulatorBackendNames,
    IonqBackendNames,
    OQCBackendNames,
    ProviderTypeVendor,
    ProviderVendor,
)
from classiq.interface.hardware import Provider
from classiq.interface.helpers.pydantic_model_helpers import values_with_discriminator

from classiq.exceptions import ClassiqValueError


class BackendPreferences(BaseModel):
    # Due to the way the field is currently implemented, i.e. it redefined with different types
    # in the subclass, it shouldn't be dumped with exclude_unset. This causes this field not to appear.
    # For example: don't use obj.dict(exclude_unset=True).
    backend_service_provider: str = pydantic.Field(
        ..., description="Provider company or cloud for the requested backend."
    )
    backend_name: str = pydantic.Field(
        ..., description="Name of the requested backend or target."
    )

    @property
    def hw_provider(self) -> Provider:
        return Provider(self.backend_service_provider)

    @pydantic.validator("backend_service_provider", pre=True)
    def validate_backend_service_provider(
        cls, backend_service_provider: Any
    ) -> Provider:
        return validate_backend_service_provider(backend_service_provider)

    @classmethod
    def batch_preferences(
        cls, *, backend_names: Iterable[str], **kwargs: Any
    ) -> List[BackendPreferences]:
        return [cls(backend_name=name, **kwargs) for name in backend_names]

    def is_nvidia_backend(self) -> bool:
        return False


AWS_DEFAULT_JOB_TIMEOUT_SECONDS = int(timedelta(minutes=240).total_seconds())


class AliceBobBackendPreferences(BackendPreferences):
    backend_service_provider: ProviderTypeVendor.ALICE_BOB
    distance: Optional[int] = pydantic.Field(
        default=None, description="Repetition code distance"
    )
    kappa_1: Optional[float] = pydantic.Field(
        default=None, description="One-photon dissipation rate (Hz)"
    )
    kappa_2: Optional[float] = pydantic.Field(
        default=None, description="Two-photon dissipation rate (Hz)"
    )
    average_nb_photons: Optional[float] = pydantic.Field(
        default=None, description="Average number of photons"
    )
    api_key: pydantic_backend.PydanticAliceBobApiKeyType = pydantic.Field(
        ..., description="AliceBob API key"
    )
    _parameters: Dict[str, Any] = PrivateAttr(default_factory=dict)

    @pydantic.root_validator(pre=True)
    def _set_backend_service_provider(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(
            values, "backend_service_provider", ProviderVendor.ALICE_AND_BOB
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        self._parameters = {
            "distance": self.distance,
            "kappa_1": self.kappa_1,
            "kappa_2": self.kappa_2,
            "average_nb_photons": self.average_nb_photons,
        }
        self._parameters = {k: v for k, v in self._parameters.items() if v is not None}
        return self._parameters


class ClassiqBackendPreferences(BackendPreferences):
    backend_service_provider: ProviderTypeVendor.CLASSIQ

    @pydantic.root_validator(pre=True)
    def _set_backend_service_provider(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(
            values, "backend_service_provider", ProviderVendor.CLASSIQ
        )

    def is_nvidia_backend(self) -> bool:
        return self.backend_name in list(ClassiqNvidiaBackendNames)


class AwsBackendPreferences(BackendPreferences):
    backend_service_provider: ProviderTypeVendor.AMAZON_BRAKET
    aws_role_arn: pydantic_backend.PydanticAwsRoleArn = pydantic.Field(
        description="ARN of the role to be assumed for execution on your Braket account."
    )
    s3_bucket_name: str = pydantic.Field(description="S3 Bucket Name")
    s3_folder: pydantic_backend.PydanticS3BucketKey = pydantic.Field(
        description="S3 Folder Path Within The S3 Bucket"
    )
    job_timeout: pydantic_backend.PydanticExecutionTimeout = pydantic.Field(
        description="Timeout for Jobs sent for execution in seconds.",
        default=AWS_DEFAULT_JOB_TIMEOUT_SECONDS,
    )

    @validator("s3_bucket_name")
    def _validate_s3_bucket_name(
        cls, s3_bucket_name: str, values: Dict[str, Any]
    ) -> str:
        s3_bucket_name = s3_bucket_name.strip()
        if not s3_bucket_name.startswith("amazon-braket-"):
            raise ClassiqValueError('S3 bucket name should start with "amazon-braket-"')
        return s3_bucket_name

    @pydantic.root_validator(pre=True)
    def _set_backend_service_provider(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(
            values, "backend_service_provider", ProviderVendor.AMAZON_BRAKET
        )


class IBMBackendProvider(BaseModel):
    hub: str = "ibm-q"
    group: str = "open"
    project: str = "main"


class IBMBackendPreferences(BackendPreferences):
    backend_service_provider: ProviderTypeVendor.IBM_QUANTUM
    access_token: Optional[str] = pydantic.Field(
        default=None,
        description="IBM Quantum access token to be used"
        " with IBM Quantum hosted backends",
    )
    provider: IBMBackendProvider = pydantic.Field(
        default_factory=IBMBackendProvider,
        description="Provider specs. for identifying a single IBM Quantum provider.",
    )

    @pydantic.root_validator(pre=True)
    def _set_backend_service_provider(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(
            values, "backend_service_provider", ProviderVendor.IBM_QUANTUM
        )


class AzureCredential(pydantic.BaseSettings):
    tenant_id: str = pydantic.Field(description="Azure Tenant ID")
    client_id: str = pydantic.Field(description="Azure Client ID")
    client_secret: str = pydantic.Field(description="Azure Client Secret")
    resource_id: pydantic_backend.PydanticAzureResourceIDType = pydantic.Field(
        description="Azure Resource ID (including Azure subscription ID, resource "
        "group and workspace), for personal resource",
    )

    class Config:
        title = "Azure Service Principal Credential"
        env_prefix = "AZURE_"
        case_sensitive = False


class AzureBackendPreferences(BackendPreferences):
    backend_service_provider: ProviderTypeVendor.AZURE_QUANTUM

    location: str = pydantic.Field(
        default="East US", description="Azure personal resource region"
    )

    credentials: Optional[AzureCredential] = pydantic.Field(
        default=None,
        description="The service principal credential to access personal quantum workspace",
    )

    ionq_error_mitigation_flag: Optional[bool] = pydantic.Field(
        default=False,
        description="Error mitigation configuration upon running on IonQ through Azure.",
    )

    @property
    def run_through_classiq(self) -> bool:
        return self.credentials is None

    @pydantic.root_validator(pre=True)
    def _set_backend_service_provider(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(
            values, "backend_service_provider", ProviderVendor.AZURE_QUANTUM
        )


class IonqBackendPreferences(BackendPreferences):
    backend_service_provider: ProviderTypeVendor.IONQ
    api_key: pydantic_backend.PydanticIonQApiKeyType = pydantic.Field(
        ..., description="IonQ API key"
    )

    @pydantic.root_validator(pre=True)
    def _set_backend_service_provider(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(
            values, "backend_service_provider", ProviderVendor.IONQ
        )


class GCPBackendPreferences(BackendPreferences):
    backend_service_provider: ProviderTypeVendor.GOOGLE

    @pydantic.root_validator(pre=True)
    def _set_backend_service_provider(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(
            values, "backend_service_provider", ProviderVendor.GOOGLE
        )

    def is_nvidia_backend(self) -> bool:
        return True


class OQCBackendPreferences(BackendPreferences):
    backend_service_provider: ProviderTypeVendor.OQC
    username: str = pydantic.Field(description="OQC username")
    password: str = pydantic.Field(description="OQC password")

    @pydantic.root_validator(pre=True)
    def _set_backend_service_provider(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(
            values, "backend_service_provider", ProviderVendor.OQC
        )


def is_exact_simulator(backend_preferences: BackendPreferences) -> bool:
    return backend_preferences.backend_name in EXACT_SIMULATORS


def default_backend_preferences(
    backend_name: str = ClassiqSimulatorBackendNames.SIMULATOR,
) -> BackendPreferences:
    return ClassiqBackendPreferences(backend_name=backend_name)


def backend_preferences_field(
    backend_name: str = ClassiqSimulatorBackendNames.SIMULATOR,
) -> Any:
    return pydantic.Field(
        default_factory=lambda: default_backend_preferences(backend_name),
        description="Preferences for the requested backend to run the quantum circuit.",
        discriminator="backend_service_provider",
    )


BackendPreferencesTypes = Union[
    AzureBackendPreferences,
    ClassiqBackendPreferences,
    IBMBackendPreferences,
    AwsBackendPreferences,
    IonqBackendPreferences,
    GCPBackendPreferences,
    AliceBobBackendPreferences,
    OQCBackendPreferences,
]

__all__ = [
    "AzureBackendPreferences",
    "AzureCredential",
    "AzureQuantumBackendNames",
    "ClassiqBackendPreferences",
    "ClassiqSimulatorBackendNames",
    "IBMBackendPreferences",
    "IBMBackendProvider",
    "AwsBackendPreferences",
    "AmazonBraketBackendNames",
    "IonqBackendPreferences",
    "IonqBackendNames",
    "ClassiqNvidiaBackendNames",
    "GCPBackendPreferences",
    "AliceBobBackendPreferences",
    "AliceBobBackendNames",
    "OQCBackendPreferences",
    "OQCBackendNames",
]


def validate_backend_service_provider(backend_service_provider: Any) -> Provider:
    if isinstance(backend_service_provider, Provider):
        return backend_service_provider
    if isinstance(backend_service_provider, str):
        for member in Provider:
            if member.lower() == backend_service_provider.lower():
                return Provider(member)
    raise ClassiqValueError(
        f"""Vendor {backend_service_provider} is not supported.
    The supported providers are {', '.join(Provider)}."""
    )
