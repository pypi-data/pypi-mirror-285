import functools
import operator
from collections import defaultdict
from typing import (
    Any,
    DefaultDict,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)

import pydantic
from pydantic import BaseModel
from typing_extensions import TypeAlias

from classiq.interface.executor.quantum_code import OutputQubitsMap, Qubits
from classiq.interface.generator.arith import number_utils
from classiq.interface.generator.complex_type import Complex
from classiq.interface.generator.functions.classical_type import QmodPyObject
from classiq.interface.helpers.custom_pydantic_types import PydanticNonNegIntTuple
from classiq.interface.helpers.versioned_model import VersionedModel

from classiq.exceptions import ClassiqError

_ILLEGAL_QUBIT_ERROR_MSG: str = "Illegal qubit index requested"
_REPEATED_QUBIT_ERROR_MSG: str = "Requested a qubit more than once"
_UNAVAILABLE_OUTPUT_ERROR_MSG: str = "Requested output doesn't exist in the circuit"

State: TypeAlias = str
Name: TypeAlias = str
RegisterValue: TypeAlias = Union[float, int]
MeasuredShots: TypeAlias = pydantic.NonNegativeInt
ParsedState: TypeAlias = Mapping[Name, RegisterValue]
ParsedStates: TypeAlias = Mapping[State, ParsedState]
Counts: TypeAlias = Dict[State, MeasuredShots]
StateVector: TypeAlias = Optional[Dict[str, Any]]


class SampledState(BaseModel):
    state: ParsedState
    shots: MeasuredShots

    def __repr__(self) -> str:
        return f"{self.state}: {self.shots}"


ParsedCounts: TypeAlias = List[SampledState]


class SimulatedState(BaseModel):
    state: ParsedState
    bitstring: State
    amplitude: Complex

    def __getitem__(self, item: Name) -> RegisterValue:
        return self.state[item]


ParsedStateVector: TypeAlias = List[SimulatedState]


class VaRResult(BaseModel):
    var: Optional[float] = None
    alpha: Optional[float] = None


class GroverSimulationResults(VersionedModel):
    result: Dict[str, Any]


def _validate_qubit_indices(counts: Counts, indices: Tuple[int, ...]) -> None:
    if not indices:
        raise ClassiqError(_ILLEGAL_QUBIT_ERROR_MSG)

    if max(indices) >= len(list(counts.keys())[0]):
        raise ClassiqError(_ILLEGAL_QUBIT_ERROR_MSG)

    if len(set(indices)) < len(indices):
        raise ClassiqError(_REPEATED_QUBIT_ERROR_MSG)


def _slice_str(s: str, indices: Tuple[int, ...]) -> str:
    return "".join(s[i] for i in indices)


def flip_counts_qubit_order(counts: Counts) -> Counts:
    return {key[::-1]: value for key, value in counts.items()}


def get_sampled_state(
    parsed_counts: ParsedCounts, state: ParsedState
) -> Optional[SampledState]:
    for sampled_state in parsed_counts:
        if sampled_state.state == state:
            return sampled_state
    return None


def reduce_parsed_states(
    parsed_states: ParsedStates, outputs: Tuple[Name, ...]
) -> ParsedStates:
    return {
        state: {
            output: value for output, value in parsed_state.items() if output in outputs
        }
        for state, parsed_state in parsed_states.items()
    }


def get_parsed_counts(counts: Counts, parsed_states: ParsedStates) -> ParsedCounts:
    parsed_counts: ParsedCounts = []
    for bitstring, count in counts.items():
        parsed_state = parsed_states[bitstring]
        if sampled_state := get_sampled_state(parsed_counts, parsed_state):
            sampled_state.shots += count
        else:
            parsed_counts.append(SampledState(state=parsed_state, shots=count))
    return sorted(parsed_counts, key=lambda k: k.shots, reverse=True)


class ExecutionDetails(BaseModel, QmodPyObject):
    vendor_format_result: Dict[str, Any] = pydantic.Field(
        ..., description="Result in proprietary vendor format"
    )
    counts: Counts = pydantic.Field(
        default_factory=dict, description="Number of counts per state"
    )
    counts_lsb_right: bool = pydantic.Field(
        True,
        description="Is the qubit order of counts field such that the LSB is right?",
    )
    parsed_states: ParsedStates = pydantic.Field(
        default_factory=dict,
        description="A mapping between the raw states of counts (bitstrings) to their parsed states (registers' values)",
    )
    histogram: Optional[Dict[State, pydantic.NonNegativeFloat]] = pydantic.Field(
        None,
        description="Histogram of probability per state (an alternative to counts)",
    )
    output_qubits_map: OutputQubitsMap = pydantic.Field(
        default_factory=dict,
        description="The map of outputs (measured registers) to their qubits in the circuit.",
    )
    state_vector: StateVector = pydantic.Field(
        default=None,
        description="The state vector when executed on a simulator, with LSB right qubit order",
    )
    parsed_state_vector_states: ParsedStates = pydantic.Field(
        default=None,
        description="A mapping between the raw states of the state vector (bitstrings) to their parsed states (registers' values)",
    )
    physical_qubits_map: Optional[OutputQubitsMap] = pydantic.Field(
        default=None,
        description="The map of all registers (also non measured) to their qubits in the circuit. Used for state_vector which represent also the non-measured qubits.",
    )
    num_shots: Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=None, description="The total number of shots the circuit was executed"
    )

    @pydantic.validator("counts", pre=True)
    def _clean_spaces_from_counts_keys(cls, v: Counts) -> Counts:
        if not v or " " not in list(v.keys())[0]:
            return v
        return {state.replace(" ", ""): v[state] for state in v}

    @pydantic.validator("num_shots", always=True)
    def _validate_num_shots(
        cls, num_shots: Optional[int], values: Dict[str, Any]
    ) -> Optional[int]:
        if num_shots is not None:
            return num_shots
        counts = values.get("counts")
        if not counts:
            return None
        return sum(shots for _, shots in counts.items())

    @property
    def parsed_counts(self) -> ParsedCounts:
        return get_parsed_counts(self.counts, self.parsed_states)

    @property
    def parsed_state_vector(self) -> Optional[ParsedStateVector]:
        if not self.state_vector:
            return None
        parsed_state_vector = [
            SimulatedState(
                state=self.parsed_state_vector_states[bitstring],
                bitstring=bitstring,
                amplitude=complex(amplitude_str),
            )
            for bitstring, amplitude_str in self.state_vector.items()
        ]
        return sorted(parsed_state_vector, key=lambda k: abs(k.amplitude), reverse=True)

    def flip_execution_counts_bitstring(self) -> None:
        """Backends should return result count bitstring in right to left form"""
        self.counts = flip_counts_qubit_order(self.counts)
        self.counts_lsb_right = not self.counts_lsb_right

    def counts_by_qubit_order(self, lsb_right: bool) -> Counts:
        if self.counts_lsb_right != lsb_right:
            return flip_counts_qubit_order(self.counts)
        else:
            return self.counts

    def counts_of_qubits(self, *qubits: int) -> Counts:
        _validate_qubit_indices(self.counts, qubits)

        reduced_counts: DefaultDict[State, int] = defaultdict(int)
        for state_str, state_count in self.counts_by_qubit_order(
            lsb_right=False
        ).items():
            reduced_counts[_slice_str(state_str, qubits)] += state_count

        return dict(reduced_counts)

    def counts_of_output(self, output_name: Name) -> Counts:
        if output_name not in self.output_qubits_map:
            raise ClassiqError(_UNAVAILABLE_OUTPUT_ERROR_MSG)

        return self.counts_of_qubits(*self.output_qubits_map[output_name])

    def counts_of_multiple_outputs(
        self, output_names: Tuple[Name, ...]
    ) -> Dict[Tuple[State, ...], pydantic.NonNegativeInt]:
        if any(name not in self.output_qubits_map for name in output_names):
            raise ClassiqError(_UNAVAILABLE_OUTPUT_ERROR_MSG)

        output_regs: Tuple[Qubits, ...] = tuple(
            self.output_qubits_map[name] for name in output_names
        )
        reduced_counts: DefaultDict[Tuple[State, ...], int] = defaultdict(int)
        for state_str, state_count in self.counts_by_qubit_order(
            lsb_right=False
        ).items():
            reduced_strs = tuple(_slice_str(state_str, reg) for reg in output_regs)
            reduced_counts[reduced_strs] += state_count
        return dict(reduced_counts)

    def parsed_counts_of_outputs(
        self, output_names: Union[Name, Tuple[Name, ...]]
    ) -> ParsedCounts:
        if isinstance(output_names, Name):
            output_names = (output_names,)
        if any(name not in self.output_qubits_map for name in output_names):
            raise ClassiqError(_UNAVAILABLE_OUTPUT_ERROR_MSG)

        reduced_parsed_states = reduce_parsed_states(self.parsed_states, output_names)
        return get_parsed_counts(self.counts, reduced_parsed_states)

    def register_output_from_qubits(self, qubits: Tuple[int, ...]) -> Dict[float, int]:
        register_output: Dict[float, int] = {}
        value_from_str_bin = functools.partial(
            self._get_register_value_from_binary_string_results, register_qubits=qubits
        )
        for results_binary_key, counts in self.counts_by_qubit_order(
            lsb_right=False
        ).items():
            value = value_from_str_bin(binary_string=results_binary_key)
            register_output[value] = register_output.get(value, 0) + counts

        return register_output

    @staticmethod
    def _get_register_value_from_binary_string_results(
        binary_string: str, register_qubits: List[int]
    ) -> RegisterValue:
        register_binary_string = "".join(
            operator.itemgetter(*register_qubits)(binary_string)
        )[::-1]
        return number_utils.binary_to_float_or_int(bin_rep=register_binary_string)


class MultipleExecutionDetails(VersionedModel):
    details: List[ExecutionDetails]

    def __getitem__(self, index: int) -> ExecutionDetails:
        return self.details[index]


class EstimationMetadata(BaseModel, extra=pydantic.Extra.allow):
    shots: Optional[pydantic.NonNegativeInt] = None
    remapped_qubits: bool = False
    input_qubit_map: Optional[List[PydanticNonNegIntTuple]] = None


class EstimationResult(BaseModel, QmodPyObject):
    value: Complex = pydantic.Field(..., description="Estimation for the operator")
    variance: Complex = pydantic.Field(..., description="Variance of the estimation")
    metadata: EstimationMetadata = pydantic.Field(
        ..., description="Metadata for the estimation"
    )


class EstimationResults(VersionedModel):
    results: List[EstimationResult]

    def __len__(self) -> int:
        return len(self.results)

    def __iter__(self) -> Iterator[EstimationResult]:  # type: ignore[override]
        # TODO This is a bug waiting to happen. We change the meaning of
        # __iter__ in a derived class.
        return iter(self.results)

    def __getitem__(self, index: int) -> EstimationResult:
        return self.results[index]
