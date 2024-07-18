import dataclasses
from enum import Enum
from typing import List, Mapping, Optional, Set

from classiq.interface.model.handle_binding import HandleBinding

from classiq.exceptions import ClassiqError


class HandleState(Enum):
    INITIALIZED = 0
    UNINITIALIZED = 1
    ERRORED = 2


@dataclasses.dataclass
class ValidationHandle:
    _state: HandleState
    errors: List[str] = dataclasses.field(default_factory=list)

    def __init__(
        self,
        initial_state: Optional[HandleState] = None,
        errors: Optional[List[str]] = None,
    ) -> None:
        if initial_state is None and not errors:
            raise ClassiqError("Missing initial state for ValidationHandle")

        self._state = initial_state or HandleState.ERRORED
        self.errors = errors or []

    @property
    def state(self) -> HandleState:
        return self._state

    def append_error(self, error: str) -> None:
        self.errors.append(error)
        self._state = HandleState.ERRORED

    def initialize(self) -> None:
        self._state = HandleState.INITIALIZED

    def uninitialize(self) -> None:
        self._state = HandleState.UNINITIALIZED


def get_unique_handle_names(io_dict: Mapping[str, HandleBinding]) -> Set[str]:
    return {handle_binding.name for handle_binding in io_dict.values()}
