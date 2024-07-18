from typing import Dict, Final, List, Optional, Union

from classiq.interface.executor.execution_preferences import QaeWithQpeEstimationMethod
from classiq.interface.executor.iqae_result import IQAEResult
from classiq.interface.executor.result import (
    EstimationResult,
    EstimationResults,
    ExecutionDetails,
    MultipleExecutionDetails,
)
from classiq.interface.executor.vqe_result import VQESolverResult
from classiq.interface.generator.functions.qmod_python_interface import QmodPyStruct

from classiq.applications.qsvm.qsvm import Data, Labels
from classiq.exceptions import ClassiqError
from classiq.qmod.builtins.enums import Optimizer

ExecutionParams = Dict[str, Union[float, int, List[int], List[float]]]

_CALL_IN_QFUNC_ERROR = (
    'Cannot call "{}" in a quantum context. "{}" is a classical execution primitive.'
)

CARRAY_SEPARATOR: Final[str] = "_"


def _raise_error(primitive_name: str) -> None:
    raise ClassiqError(_CALL_IN_QFUNC_ERROR.format(primitive_name, primitive_name))


def save(values_to_save: dict) -> None:
    _raise_error("save")


def sample(  # type: ignore[return]
    execution_params: Optional[ExecutionParams] = None,
) -> ExecutionDetails:
    _raise_error("sample")


def batch_sample(  # type: ignore[return]
    batch_execution_params: List[ExecutionParams],
) -> MultipleExecutionDetails:
    _raise_error("batch_sample")


def estimate(  # type: ignore[return]
    hamiltonian: List[QmodPyStruct], execution_params: Optional[ExecutionParams] = None
) -> EstimationResult:
    _raise_error("estimate")


def batch_estimate(  # type: ignore[return]
    hamiltonian: List[QmodPyStruct],
    batch_execution_params: List[ExecutionParams],
) -> EstimationResults:
    _raise_error("batch_estimate")


def vqe(  # type: ignore[return]
    hamiltonian: List[QmodPyStruct],
    maximize: bool,
    initial_point: List[float],
    optimizer: Optimizer,
    max_iteration: int,
    tolerance: float,
    step_size: float,
    skip_compute_variance: bool,
    alpha_cvar: float,
) -> VQESolverResult:
    _raise_error("vqe")


def qae_with_qpe_result_post_processing(  # type: ignore[return]
    estimation_register_size: int,
    estimation_method: QaeWithQpeEstimationMethod,
    result: ExecutionDetails,
) -> float:
    _raise_error("qae_with_qpe_result_post_processing")


def qsvm_full_run(  # type: ignore[return]
    train_data: Data,
    train_labels: Labels,
    test_data: Data,
    test_labels: Labels,
    predict_data: Data,
) -> QmodPyStruct:
    _raise_error("qsvm_full_run")


def iqae(  # type: ignore[return]
    epsilon: float,
    alpha: float,
    execution_params: Optional[ExecutionParams] = None,
) -> IQAEResult:
    _raise_error("iqae")


def molecule_ground_state_solution_post_process(  # type: ignore[return]
    problem: QmodPyStruct, vqe_result: VQESolverResult
) -> QmodPyStruct:
    _raise_error("molecule_ground_state_solution_post_process")


__all__ = [
    "ExecutionParams",
    "save",
    "sample",
    "batch_sample",
    "estimate",
    "batch_estimate",
    "vqe",
    "qae_with_qpe_result_post_processing",
    "qsvm_full_run",
    "iqae",
    "molecule_ground_state_solution_post_process",
]


def __dir__() -> List[str]:
    return __all__
