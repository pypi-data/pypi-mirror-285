from typing import List, Tuple

from pydantic import BaseModel

from classiq.interface.executor.result import ExecutionDetails
from classiq.interface.generator.functions.classical_type import QmodPyObject
from classiq.interface.helpers.versioned_model import VersionedModel


class IQAEIterationData(BaseModel):
    grover_iterations: int
    sample_results: ExecutionDetails


class IQAEResult(VersionedModel, QmodPyObject):
    estimation: float
    confidence_interval: Tuple[float, float]
    iterations_data: List[IQAEIterationData]
    warnings: List[str]
