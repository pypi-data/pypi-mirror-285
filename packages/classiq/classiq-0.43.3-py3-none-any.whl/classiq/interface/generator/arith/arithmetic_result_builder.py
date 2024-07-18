from typing import Any, Dict, List, Optional, Set

import networkx as nx

from classiq.interface.generator.arith import arithmetic_param_getters, number_utils
from classiq.interface.generator.arith.argument_utils import RegisterOrConst
from classiq.interface.generator.arith.ast_node_rewrite import OUTPUT_SIZE
from classiq.interface.generator.arith.register_user_input import RegisterArithmeticInfo

from classiq.exceptions import ClassiqArithmeticError

ArithmeticDefinitions = Dict[str, RegisterOrConst]


class ArithmeticResultBuilder:
    def __init__(
        self,
        *,
        graph: nx.DiGraph,
        definitions: ArithmeticDefinitions,
        machine_precision: int,
    ) -> None:
        self.result = self._fill_operation_results(
            graph=graph,
            result_definitions=definitions,
            machine_precision=machine_precision,
        )

    @staticmethod
    def convert_result_definition(
        node: Any, definition: Optional[RegisterOrConst], machine_precision: int
    ) -> RegisterOrConst:
        if definition:
            return definition
        elif isinstance(node, int):
            return float(node)
        elif isinstance(node, float):
            return number_utils.limit_fraction_places(
                node, machine_precision=machine_precision
            )
        raise ClassiqArithmeticError("Incompatible argument definition type")

    @classmethod
    def _compute_inputs_data(
        cls,
        *,
        inputs_node_set: Set[Any],
        result_definitions: ArithmeticDefinitions,
        machine_precision: int,
    ) -> Dict[str, RegisterOrConst]:
        return {
            cls._convert_int_to_float_str(node): cls.convert_result_definition(
                node, result_definitions.get(node), machine_precision
            )
            for node in inputs_node_set
        }

    @classmethod
    def _fill_operation_results(
        cls,
        *,
        graph: nx.DiGraph,
        result_definitions: ArithmeticDefinitions,
        machine_precision: int,
    ) -> RegisterArithmeticInfo:
        inputs_node_set: Set[str] = {
            vertex for vertex, deg in graph.in_degree if deg == 0
        }
        node_results: Dict[str, RegisterOrConst] = cls._compute_inputs_data(
            inputs_node_set=inputs_node_set,
            result_definitions=result_definitions,
            machine_precision=machine_precision,
        )
        for node in nx.topological_sort(graph):
            if node in inputs_node_set:
                continue

            args = [
                node_results[cls._convert_int_to_float_str(predecessor_node)]
                for predecessor_node in graph.predecessors(node)
            ]
            if graph.out_degree(node) == 0:
                return cls._get_node_result(
                    graph, args, node, machine_precision=machine_precision
                )
            node_results[node] = cls._get_node_result(
                graph, args, node, machine_precision=machine_precision
            )
        raise ClassiqArithmeticError("Expression has no result")

    @classmethod
    def _get_node_result(
        cls,
        graph: nx.DiGraph,
        args: List[RegisterOrConst],
        node: str,
        *,
        machine_precision: int,
    ) -> RegisterArithmeticInfo:
        return arithmetic_param_getters.get_params(
            node_id=node,
            args=args,
            output_size=graph.nodes[node].get(OUTPUT_SIZE, None),
            machine_precision=machine_precision,
        ).result_register

    @staticmethod
    def _convert_int_to_float_str(node: Any) -> str:
        return str(float(node)) if isinstance(node, int) else str(node)


def validate_arithmetic_result_type(
    graph: nx.DiGraph, definitions: ArithmeticDefinitions, machine_precision: int
) -> None:
    ArithmeticResultBuilder(
        graph=graph, definitions=definitions, machine_precision=machine_precision
    )
