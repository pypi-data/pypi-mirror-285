from classiq.interface.ast_node import ASTNode
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import ConcreteClassicalType


class Constant(ASTNode):
    name: str
    const_type: ConcreteClassicalType
    value: Expression
