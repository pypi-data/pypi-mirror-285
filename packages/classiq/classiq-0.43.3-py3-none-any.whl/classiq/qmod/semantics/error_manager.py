from contextlib import contextmanager
from typing import Iterator, List, Type

from classiq.interface.ast_node import ASTNode


class ErrorManager:
    def __new__(cls) -> "ErrorManager":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_instantiated"):
            return
        self._instantiated = True
        self._errors: List[str] = []
        self._current_nodes_stack: List[ASTNode] = []

    def add_error(self, error: str) -> None:
        source_referenced_error = (
            f"{error}\n\t\tat {self._current_nodes_stack[-1].source_ref}"
            if self._current_nodes_stack
            and self._current_nodes_stack[-1].source_ref is not None
            else error
        )
        self._errors.append(source_referenced_error)

    def get_errors(self) -> List[str]:
        return self._errors

    def clear(self) -> None:
        self._current_nodes_stack = []
        self._errors = []

    def has_errors(self) -> bool:
        return len(self._errors) > 0

    def report_errors(self, error_type: Type[Exception]) -> None:
        if self.has_errors():
            errors = self._errors
            self.clear()
            raise error_type("\n\t" + "\n\t".join(errors))

    @contextmanager
    def node_context(self, node: ASTNode) -> Iterator[None]:
        self._current_nodes_stack.append(node)
        yield
        self._current_nodes_stack.pop()
