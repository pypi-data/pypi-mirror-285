import itertools
from collections import defaultdict
from typing import Any, Dict, List, MutableSet, Optional

import pydantic

from classiq.interface.backend.backend_preferences import BackendPreferences
from classiq.interface.generator.transpiler_basis_gates import (
    DEFAULT_BASIS_GATES,
    DEFAULT_ROUTING_BASIS_GATES,
    ROUTING_TWO_QUBIT_BASIS_GATES,
    TWO_QUBIT_GATES,
    TranspilerBasisGates,
)
from classiq.interface.helpers.custom_pydantic_types import PydanticNonNegIntTuple

from classiq.exceptions import ClassiqValueError

ConnectivityMap = List[PydanticNonNegIntTuple]
BACKEND_VALIDATION_ERROR_MESSAGE = (
    "Backend service provider and backend name should be specified together."
)


class HardwareData(pydantic.BaseModel):
    basis_gates: List[str] = pydantic.Field(
        default=list(),
        description="The basis gates of the hardware. "
        "This set will be used during the model optimization. "
        "If none given, use default values: "
        f"If no connectivity map is given or the connectivity map is symmetric - {sorted(DEFAULT_BASIS_GATES)}. "
        f"If a non-symmetric connectivity map is given - {sorted(DEFAULT_ROUTING_BASIS_GATES)}. ",
    )
    connectivity_map: Optional[ConnectivityMap] = pydantic.Field(
        default=None,
        description="Qubit connectivity map, in the form [ [q0, q1], [q1, q2],...]. "
        "If none given, assume the hardware is fully connected",
    )
    is_symmetric_connectivity: bool = pydantic.Field(
        default=True,
        description="Assumes that the coupling map forms an undirected graph, "
        "so for every qubit pair [q0, q1], both qubits can act as control and target. "
        "If false, the first / second qubit denotes the control / target, respectively",
    )

    @pydantic.validator("connectivity_map")
    def _validate_connectivity_map(
        cls, connectivity_map: Optional[ConnectivityMap]
    ) -> Optional[ConnectivityMap]:
        if connectivity_map is None:
            return connectivity_map
        if not connectivity_map:
            raise ClassiqValueError("Connectivity map cannot be empty")
        connectivity_map = _reindex_qubits(connectivity_map)
        return connectivity_map

    @pydantic.root_validator()
    def _symmetrize_connectivity_map(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        connectivity_map = values.get("connectivity_map")
        if connectivity_map is None:
            return values

        is_symmetric = values.get("is_symmetric_connectivity")
        if is_symmetric:
            connectivity_map = _symmetrize_connectivity_map(connectivity_map)
            values["connectivity_map"] = connectivity_map

        if not _is_connected_map(connectivity_map):
            raise ClassiqValueError(
                f"Connectivity map must be connected: {connectivity_map} is not connected."
            )
        return values

    @pydantic.root_validator()
    def _validate_basis_gates(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        connectivity_map = values.get("connectivity_map")
        specified_basis_gates = values.get("basis_gates", [])
        if connectivity_map is None:
            values["basis_gates"] = specified_basis_gates or list(DEFAULT_BASIS_GATES)
            return values

        is_symmetric_connectivity = values.get("is_symmetric")
        if is_symmetric_connectivity or _check_symmetry(connectivity_map):
            values["basis_gates"] = specified_basis_gates or list(DEFAULT_BASIS_GATES)
            return values

        values["basis_gates"] = specified_basis_gates or list(
            DEFAULT_ROUTING_BASIS_GATES
        )
        invalid_gates = [
            gate
            for gate in specified_basis_gates
            if gate in TWO_QUBIT_GATES and gate not in ROUTING_TWO_QUBIT_BASIS_GATES
        ]
        if invalid_gates:
            raise ClassiqValueError(
                "Connectivity-aware synthesis with non-symmetric coupling map "
                "is currently supported for the following two-qubit gates only: cx, ecr, rzx."
            )

        return values


class CustomHardwareSettings(HardwareData):
    _width: Optional[int] = pydantic.PrivateAttr(default=None)

    @pydantic.validator("basis_gates")
    def validate_basis_gates(cls, basis_gates: List[str]) -> List[TranspilerBasisGates]:
        valid_gates = list(TranspilerBasisGates)
        invalid_gates = [gate for gate in basis_gates if gate not in valid_gates]
        if invalid_gates:
            raise ClassiqValueError(
                "Invalid gates for hardware-aware synthesis: " + str(invalid_gates)
            )

        return [TranspilerBasisGates(gate) for gate in basis_gates]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._width: Optional[int] = (
            len(set(itertools.chain.from_iterable(self.connectivity_map)))
            if self.connectivity_map
            else None
        )

    @property
    def width(self) -> Optional[int]:
        return self._width


def _is_connected_map(connectivity_map: ConnectivityMap) -> bool:
    nodes: MutableSet[int] = set()
    node_to_neighbors: Dict[int, MutableSet[int]] = defaultdict(set)
    for edge in connectivity_map:
        nodes.add(edge[0])
        nodes.add(edge[1])
        node_to_neighbors[edge[0]].add(edge[1])
        node_to_neighbors[edge[1]].add(edge[0])
    visited: MutableSet[int] = set()
    starting_node = list(nodes)[0]
    _node_dfs(starting_node, node_to_neighbors, visited)
    return len(visited) == len(nodes)


def _node_dfs(
    node: int, node_to_neighbors: Dict[int, MutableSet[int]], visited: MutableSet[int]
) -> None:
    visited.add(node)
    neighbors = node_to_neighbors[node]
    for neighbor in neighbors:
        if neighbor in visited:
            continue
        _node_dfs(neighbor, node_to_neighbors, visited)
    return


def _reindex_qubits(connectivity_map: ConnectivityMap) -> ConnectivityMap:
    qubits = sorted({q for pair in connectivity_map for q in pair})
    return [(qubits.index(pair[0]), qubits.index(pair[1])) for pair in connectivity_map]


def _check_symmetry(connectivity_map: ConnectivityMap) -> bool:
    undirected_edges = {tuple(sorted(edge)) for edge in connectivity_map}
    return len(undirected_edges) == len(connectivity_map) / 2


def _symmetrize_connectivity_map(connectivity_map: ConnectivityMap) -> ConnectivityMap:
    # A more complicated implementation than using set to maintain the order
    connectivity_map_no_duplicates = []
    for edge in connectivity_map:
        reversed_edge = (edge[1], edge[0])
        if (
            edge not in connectivity_map_no_duplicates
            and reversed_edge not in connectivity_map_no_duplicates
        ):
            connectivity_map_no_duplicates.append(edge)
    reversed_connectivity_map = [
        (edge[1], edge[0]) for edge in connectivity_map_no_duplicates
    ]
    return connectivity_map_no_duplicates + reversed_connectivity_map


class SynthesisHardwareData(HardwareData):
    backend_data: Optional[BackendPreferences]
