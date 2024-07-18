from typing import Callable, Dict, List, Tuple, Union

import torch
from torch import Tensor

from classiq.interface.executor.execution_result import ResultsCollection, SavedResult

from classiq import QuantumProgram
from classiq.synthesis import SerializedQuantumProgram

Arguments = Dict[str, float]
MultipleArguments = Tuple[Arguments, ...]

Circuit = QuantumProgram
ExecuteFunction = Callable[
    [SerializedQuantumProgram, MultipleArguments], ResultsCollection
]
ExecuteFuncitonOnlyArguments = Callable[[MultipleArguments], ResultsCollection]
PostProcessFunction = Callable[[SavedResult], Tensor]
TensorToArgumentsCallable = Callable[[Tensor, Tensor], MultipleArguments]

Shape = Union[torch.Size, Tuple[int, ...]]

GradientFunction = Callable[[Tensor, Tensor], Tensor]
SimulateFunction = Callable[[Tensor, Tensor], Tensor]

DataAndLabel = Tuple[List[int], Union[List[int], int]]
Transform = Callable[[Tensor], Tensor]
