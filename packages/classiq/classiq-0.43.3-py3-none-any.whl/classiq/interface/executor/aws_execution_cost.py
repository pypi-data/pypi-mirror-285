from datetime import date
from typing import Any, Dict, List, Optional

import pydantic
from pydantic import validator

from classiq._internals.enum_utils import StrEnum
from classiq.exceptions import ClassiqValueError


class Granularity(StrEnum):
    monthly = "MONTHLY"
    daily = "DAILY"
    hourly = "HOURLY"


class CostScope(StrEnum):
    user = "user"
    organization = "organization"


class ExecutionCostForTimePeriod(pydantic.BaseModel):
    start: date = pydantic.Field(
        description="The beginning of the time period for tasks usage and cost ("
        "inclusive).",
    )
    end: date = pydantic.Field(
        description="The end of the time period for tasks usage and cost (exclusive).",
    )
    granularity: Granularity = pydantic.Field(
        description="Either MONTHLY or DAILY, or HOURLY.", default=Granularity.daily
    )
    cost_scope: CostScope = pydantic.Field(
        description="Either user or organization", default=CostScope.user
    )

    class Config:
        json_encoders = {date: lambda v: v.strftime("%Y-%m-%d")}

    @validator("end")
    def date_order(cls, v: date, values: Dict[str, Any], **kwargs: Any) -> date:
        if "start" in values and v <= values["start"]:
            raise ClassiqValueError('"end" date should be after "start" date')
        return v


"""The following models describe the aws response model and based on this schema:
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage"""


class TimePeriod(pydantic.BaseModel):
    Start: str
    End: str


class BlendedCost(pydantic.BaseModel):
    Amount: str
    Unit: str


class Total(pydantic.BaseModel):
    BlendedCost: BlendedCost


class ExecutedTaskForPeriodItem(pydantic.BaseModel):
    TimePeriod: TimePeriod
    Total: Total
    Groups: Optional[List]
    Estimated: Optional[bool]


class ExecutionCostForTimePeriodResponse(pydantic.BaseModel):
    executed_task_for_period: List[ExecutedTaskForPeriodItem]
