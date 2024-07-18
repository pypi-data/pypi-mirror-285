from typing import Tuple, Union

from classiq.qmod.symbolic_expr import SymbolicExpr

SymbolicTypes = Union[SymbolicExpr, int, float, bool, Tuple["SymbolicTypes", ...]]
