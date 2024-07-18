import abc
from typing import Tuple

from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)


class FinanceModelInput(HashablePydanticBaseModel):
    kind: str

    @property
    def num_output_qubits(self) -> int:
        return 0

    class Config:
        frozen = True

    @property
    @abc.abstractmethod
    def distribution_range(self) -> Tuple[float, float]:
        pass
