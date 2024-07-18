from typing import Any, Dict, Generic, Optional, TypeVar, Union

import pydantic
from pydantic import BaseModel
from pydantic.generics import GenericModel

from classiq.interface.helpers.custom_encoders import CUSTOM_ENCODERS

from classiq._internals.enum_utils import StrEnum
from classiq.exceptions import ClassiqAPIError

JSONObject = Dict[str, Any]
T = TypeVar("T", bound=Union[pydantic.BaseModel, JSONObject])
AUTH_HEADER = "Classiq-BE-Auth"
INVALID_RESPONSE_ERROR_MSG = "Invalid response from Classiq API"


class JobID(BaseModel):
    job_id: str


class JobStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    READY = "READY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"

    def is_final(self) -> bool:
        return self in (self.COMPLETED, self.FAILED, self.CANCELLED)


"""
A job can be in either of 3 states: ongoing, completed successfully or completed
unsuccessfully. Each job status belongs to one of the 3 states
For ongoing jobs, we expect both the failure_details and result to be None
For successful jobs, we expect failure_details to be None and result to be an instance of T
For unsuccessful jobs, we expect failure_details to be a string and result to be None
"""


class JobDescription(GenericModel, Generic[T], json_encoders=CUSTOM_ENCODERS):
    status: JobStatus
    failure_details: Optional[str]
    result: Optional[T]

    @pydantic.root_validator
    def validate_status_and_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        status: Optional[JobStatus] = values.get("status")
        if status is None or "result" not in values or "failure_details" not in values:
            # If any of the fields doesn't exist, then previous validations failed
            # result and failure_details are Optional, so we explicitly check if they
            # exist in the values dictionary
            return values

        result = values["result"]
        failure_details = values["failure_details"]

        if status is JobStatus.COMPLETED:
            # Completed job must return result and not have an error
            if result is None or failure_details is not None:
                raise ClassiqAPIError(INVALID_RESPONSE_ERROR_MSG)
        elif status in (JobStatus.FAILED, JobStatus.CANCELLED):
            # Failed job must return error and not have result
            if result is not None or failure_details is None:
                raise ClassiqAPIError(INVALID_RESPONSE_ERROR_MSG)
        elif result is not None or failure_details is not None:
            # Pending job must have no result and no error
            raise ClassiqAPIError(INVALID_RESPONSE_ERROR_MSG)

        return values
