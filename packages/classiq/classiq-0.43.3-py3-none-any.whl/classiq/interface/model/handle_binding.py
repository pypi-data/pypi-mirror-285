from typing import Union

from pydantic import Extra

from classiq.interface.ast_node import ASTNode
from classiq.interface.generator.expressions.expression import Expression


class HandleBinding(ASTNode):
    name: str

    class Config:
        frozen = True
        extra = Extra.forbid

    def __str__(self) -> str:
        return self.name

    def is_bindable(self) -> bool:
        return True


class SubscriptHandleBinding(HandleBinding):
    index: Expression

    class Config:
        frozen = True
        extra = Extra.forbid

    def __str__(self) -> str:
        return f"{self.name}[{self.index}]"

    def is_bindable(self) -> bool:
        return False


class SlicedHandleBinding(HandleBinding):
    start: Expression
    end: Expression

    class Config:
        frozen = True
        extra = Extra.forbid

    def __str__(self) -> str:
        return f"{self.name}[{self.start}:{self.end}]"

    def is_bindable(self) -> bool:
        return False


ConcreteHandleBinding = Union[
    HandleBinding, SubscriptHandleBinding, SlicedHandleBinding
]
