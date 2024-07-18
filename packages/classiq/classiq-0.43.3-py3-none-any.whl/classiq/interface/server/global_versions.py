from datetime import datetime
from typing import Any, Dict

import pydantic
from pydantic import BaseModel


class DeprecationInfo(BaseModel):
    deprecation_date: datetime = pydantic.Field()
    removal_date: datetime = pydantic.Field()


class GlobalVersions(BaseModel):
    deprecated: Dict[str, DeprecationInfo] = pydantic.Field()
    deployed: Dict[str, Any] = pydantic.Field()
