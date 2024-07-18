import json
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

import pydantic
import pyomo.core.expr.numeric_expr as pyo_expr
import pyomo.environ as pyo
import sympy
from pyomo.core import ConcreteModel, Constraint, Objective, Var, maximize
from pyomo.core.base import _GeneralVarData
from pyomo.core.base.component import ComponentData
from pyomo.core.base.constraint import _GeneralConstraintData
from pyomo.core.base.indexed_component import IndexedComponent
from pyomo.core.base.objective import ScalarObjective
from pyomo.core.expr.sympy_tools import (
    Pyomo2SympyVisitor,
    PyomoSympyBimap,
    Sympy2PyomoVisitor,
)

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.types.struct_declaration import StructDeclaration

from classiq.exceptions import ClassiqValueError

ListVars = List[_GeneralVarData]


class ObjectiveType(Enum):
    Min = "Min"
    Max = "Max"


class CombinatorialOptimizationStructDeclaration(StructDeclaration):
    variable_lower_bound: int = pydantic.Field(default=0)
    variable_upper_bound: int = pydantic.Field(default=1)
    constraints: List[Expression] = pydantic.Field(
        default_factory=list, description="List of constraint expressions"
    )
    objective_type: ObjectiveType = pydantic.Field(
        description="Specify whether the optimization problem is Min or Max"
    )
    objective_function: Expression = pydantic.Field(
        description="The expression to optimize, according to the objective type"
    )


def contains(var_data: _GeneralVarData, vars_data: ListVars) -> bool:
    # HACK: standard "__containts__ (in)" method doesn't work, because pyomo overrode the __eq__ method (IMO)
    return any(var_data is var_data_temp for var_data_temp in vars_data)


def remove(var_data: _GeneralVarData, vars_data: ListVars) -> ListVars:
    # HACK: standard "list method remove" method doesn't work, because pyomo overrode the __eq__ method (IMO)
    assert contains(var_data, vars_data), "var not in list"
    vars_data = vars_data.copy()
    for idx, var_data_temp in enumerate(vars_data):
        if var_data_temp is var_data:
            del vars_data[idx]
            break
    return vars_data


def index(var_data: _GeneralVarData, vars_data: ListVars) -> int:
    # HACK: standard "index method" doesn't work.
    assert contains(var_data, vars_data), "var not in list"
    idxs = [
        idx for idx, var_data_temp in enumerate(vars_data) if var_data is var_data_temp
    ]
    return idxs[0]


T = TypeVar("T")


def extract(model: ConcreteModel, type_: Type[T]) -> List[T]:
    if type_ == _GeneralVarData:
        type_ = Var

    elif type_ == _GeneralConstraintData:
        type_ = Constraint

    components = model.component_objects(type_)
    return [
        component[component_idx]
        for component in components
        for component_idx in component
    ]


def delete_component(model: ConcreteModel, component: ComponentData) -> None:
    parent_ref = component._component

    if parent_ref is None:
        return

    parent_component = parent_ref()

    if component is parent_component:
        model.del_component(component)
    else:
        _delete_element_by_value(parent_component, component)

        if not parent_component:
            model.del_component(parent_component)


def _delete_element_by_value(dict_: Dict, value: Any) -> None:
    iter_dict = {**dict_}
    for k, v in iter_dict.items():
        if v is value and k in dict_:
            del dict_[k]


def get_name(component: Union[IndexedComponent, ComponentData]) -> str:
    if isinstance(component, IndexedComponent):
        return component._name  # constraint.name returns "'{name}'"
    else:
        return component.name


class FixedSympy2PyomoVisitor(Sympy2PyomoVisitor):
    def beforeChild(  # noqa: N802
        self, node: Optional[sympy.Expr], child: sympy.Expr, child_idx: Optional[int]
    ) -> Tuple[bool, Union[int, float, None]]:
        if not child._args:
            item = self.object_map.getPyomoSymbol(child, None)
            if item is None:
                if isinstance(child, sympy.Integer):  # addition to base implementation
                    item = int(child.evalf())
                else:
                    item = float(child.evalf())
            return False, item
        return True, None


def sympy2pyomo_expression(
    expr: sympy.core.Basic, object_map: PyomoSympyBimap
) -> pyo_expr.ExpressionBase:
    return FixedSympy2PyomoVisitor(object_map).walk_expression(expr)


def convert_pyomo_to_global_presentation(
    pyo_model: pyo.ConcreteModel,
) -> pyo.ConcreteModel:
    pyo_model_str = pyomo2qmod("nativePyoModel", pyo_model)
    problem_struct = CombinatorialOptimizationStructDeclaration.parse_raw(pyo_model_str)

    pyomo_model = pyo.ConcreteModel()

    var_names = list(problem_struct.variables.keys())
    pyomo_model.var_set = pyo.Var(
        var_names,
        domain=pyo.NonNegativeIntegers,
        bounds=(
            problem_struct.variable_lower_bound,
            problem_struct.variable_upper_bound,
        ),
    )
    obj_map = PyomoSympyBimap()
    var_dict = {
        var_name: obj_map.getSympySymbol(pyomo_model.var_set[var_name])
        for var_name in var_names
    }

    def expr2pyomo(expr: Expression) -> pyo_expr.ExpressionBase:
        sp_expr = sympy.sympify(expr.expr, locals=var_dict)
        if isinstance(sp_expr, sympy.core.relational.Equality):
            return sympy2pyomo_expression(
                sp_expr.args[0], obj_map
            ) == sympy2pyomo_expression(sp_expr.args[1], obj_map)

        # Note that strict greater/less than are not supported by Pyomo
        return sympy2pyomo_expression(sp_expr, obj_map)

    pyomo_model.constraints = pyo.Constraint(
        pyo.RangeSet(0, len(problem_struct.constraints) - 1),
        rule=lambda model, i: expr2pyomo(problem_struct.constraints[i]),
    )
    pyomo_model.objective = pyo.Objective(
        expr=expr2pyomo(problem_struct.objective_function),
        sense=(
            pyo.maximize
            if problem_struct.objective_type == ObjectiveType.Max
            else pyo.minimize
        ),
    )

    return pyomo_model


def pyomo2qmod(struct_name: str, pyo_model: ConcreteModel) -> str:
    symbols_map = PyomoSympyBimap()

    variables: List[sympy.Symbol] = []

    bounds_set = False
    lower_bound = None
    upper_bound = None

    for var_dict in pyo_model.component_objects(Var):
        for key in var_dict:
            var = Pyomo2SympyVisitor(symbols_map).walk_expression(var_dict[key])
            var.name = var.name.replace(",", "_")
            variables.append(var)
            if bounds_set:
                if lower_bound != var_dict[key].lb:
                    raise ClassiqValueError(
                        "All problem variables must agree on lower bound"
                    )
                if upper_bound != var_dict[key].ub:
                    raise ClassiqValueError(
                        "All problem variables must agree on upper bound"
                    )
            else:
                lower_bound = var_dict[key].lb
                upper_bound = var_dict[key].ub
                bounds_set = True

    constraint_exprs: List[sympy.Expr] = []

    constraint_exprs.extend(
        Pyomo2SympyVisitor(symbols_map).walk_expression(constraint_dict[key].expr)
        for constraint_dict in pyo_model.component_objects(Constraint)
        for key in constraint_dict
    )

    pyo_objective: ScalarObjective = next(pyo_model.component_objects(Objective))
    objective_type_str = "Max" if pyo_objective.sense == maximize else "Min"
    objective_expr: sympy.Expr = Pyomo2SympyVisitor(symbols_map).walk_expression(
        pyo_objective
    )

    combi_struct_decl = {
        "name": struct_name,
        "variables": {str(variable): {"kind": "int"} for variable in variables},
        "variable_lower_bound": lower_bound,
        "variable_upper_bound": upper_bound,
        "constraints": [
            {"expr": str(constraint_expr)} for constraint_expr in constraint_exprs
        ],
        "objective_type": objective_type_str,
        "objective_function": {"expr": str(objective_expr)},
    }
    return json.dumps(combi_struct_decl, indent=2)
