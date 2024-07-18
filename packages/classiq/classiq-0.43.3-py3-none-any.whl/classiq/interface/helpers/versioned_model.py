import pydantic

from classiq.interface._version import VERSION
from classiq.interface.helpers.custom_encoders import CUSTOM_ENCODERS


class VersionedModel(
    pydantic.BaseModel, extra=pydantic.Extra.forbid, json_encoders=CUSTOM_ENCODERS
):
    version: str = pydantic.Field(default=VERSION)
