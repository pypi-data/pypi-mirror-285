import abc
import ast
import re
from typing import Any, Dict, Optional, Set, Tuple, Union

import networkx as nx
import pydantic
from typing_extensions import TypeAlias

from classiq.interface.generator.arith import number_utils
from classiq.interface.generator.arith.arithmetic_expression_parser import (
    parse_expression,
)
from classiq.interface.generator.arith.arithmetic_expression_validator import (
    validate_expression,
)
from classiq.interface.generator.arith.arithmetic_result_builder import (
    validate_arithmetic_result_type,
)
from classiq.interface.generator.arith.machine_precision import (
    DEFAULT_MACHINE_PRECISION,
)
from classiq.interface.generator.arith.register_user_input import RegisterArithmeticInfo
from classiq.interface.generator.arith.uncomputation_methods import UncomputationMethods
from classiq.interface.generator.expressions.expression_constants import (
    FORBIDDEN_LITERALS,
    SUPPORTED_FUNC_NAMES,
    SUPPORTED_VAR_NAMES_REG,
)
from classiq.interface.generator.function_params import FunctionParams
from classiq.interface.helpers.custom_pydantic_types import PydanticExpressionStr

from classiq.exceptions import ClassiqValueError

ValidDefinitions: TypeAlias = Union[
    pydantic.StrictInt, pydantic.StrictFloat, RegisterArithmeticInfo
]


class ArithmeticExpressionABC(abc.ABC, FunctionParams):
    uncomputation_method: UncomputationMethods = UncomputationMethods.optimized
    machine_precision: pydantic.NonNegativeInt = DEFAULT_MACHINE_PRECISION
    expression: PydanticExpressionStr
    definitions: Dict[str, ValidDefinitions]
    qubit_count: Optional[pydantic.NonNegativeInt] = None

    def _get_literal_set(self) -> Set[str]:
        return _extract_literals(self.expression)

    @pydantic.validator("definitions")
    def _validate_expression_literals_and_definitions(
        cls, definitions: Dict[str, ValidDefinitions], values: Dict[str, Any]
    ) -> Dict[str, ValidDefinitions]:
        expression = values.get("expression")
        if expression is None:
            return definitions

        literals = _extract_literals(expression)

        forbidden = literals.intersection(FORBIDDEN_LITERALS)
        if forbidden:
            raise ClassiqValueError(f"The following names are forbidden: {forbidden}")

        defined = set(definitions.keys())
        unused = defined.difference(literals)
        if unused:
            raise ClassiqValueError(f"The following registers are unused: {unused}")

        undefined = literals.difference(defined)
        if undefined:
            raise ClassiqValueError(f"The following names are undefined: {undefined}")
        return definitions

    @pydantic.root_validator
    def _validate_expression(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        expression: Optional[str] = values.get("expression")
        definitions: Optional[Dict[str, ValidDefinitions]] = values.get("definitions")
        machine_precision: Optional[int] = values.get("machine_precision")
        if expression is None or definitions is None or machine_precision is None:
            return values

        try:
            ast_obj = validate_expression(expression, mode="eval")
        except SyntaxError:
            raise ClassiqValueError(
                f"Failed to parse expression {expression!r}"
            ) from None
        cls._validate_ast_obj(ast_obj)

        graph = parse_expression(expression)
        cls._validate_expression_graph(graph, values)
        validate_arithmetic_result_type(
            graph=graph,
            definitions=definitions,
            machine_precision=machine_precision,
        )

        new_expr, new_defs = cls._replace_const_definitions_in_expression(
            expression, definitions, machine_precision
        )
        values["expression"] = new_expr
        values["definitions"] = new_defs
        return values

    @staticmethod
    def _validate_ast_obj(ast_obj: ast.AST) -> None:
        pass

    @staticmethod
    def _validate_expression_graph(graph: nx.DiGraph, values: Dict[str, Any]) -> None:
        pass

    @classmethod
    def _replace_const_definitions_in_expression(
        cls,
        expression: str,
        definitions: Dict[str, ValidDefinitions],
        machine_precision: int,
    ) -> Tuple[str, Dict[str, RegisterArithmeticInfo]]:
        new_definitions = dict()
        for var_name, value in definitions.items():
            if isinstance(value, RegisterArithmeticInfo):
                new_definitions[var_name] = value
            elif isinstance(value, (int, float)):
                expression = cls._replace_numeric_value_in_expression(
                    expression, var_name, value, machine_precision
                )
            else:
                raise ClassiqValueError(f"{type(value)} type ({var_name}) is illegal")

        return expression, new_definitions

    @staticmethod
    def _replace_numeric_value_in_expression(
        expression: str, var: str, value: Union[int, float], machine_precision: int
    ) -> str:
        if isinstance(value, float):
            value = number_utils.limit_fraction_places(
                value, machine_precision=machine_precision
            )
        return re.sub(r"\b" + var + r"\b", str(value), expression)


def _extract_literals(expression: str) -> Set[str]:
    return set(re.findall(SUPPORTED_VAR_NAMES_REG, expression)) - SUPPORTED_FUNC_NAMES
