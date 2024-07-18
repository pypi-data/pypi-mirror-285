import os
from typing import Optional

import pydantic

from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)


class SourceReference(HashablePydanticBaseModel):
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    file_name: Optional[str] = pydantic.Field(default=None)

    def __str__(self) -> str:
        file_string = (
            f"file {os.path.basename(self.file_name)} " if self.file_name else ""
        )
        start_character_string = (
            f" character {self.start_column + 1}" if self.start_column > 0 else ""
        )
        return f"{file_string}line {self.start_line + 1}{start_character_string}"


class ASTNode(HashablePydanticBaseModel):
    source_ref: Optional[SourceReference] = pydantic.Field(default=None)


class HashableASTNode(ASTNode, HashablePydanticBaseModel):
    pass
