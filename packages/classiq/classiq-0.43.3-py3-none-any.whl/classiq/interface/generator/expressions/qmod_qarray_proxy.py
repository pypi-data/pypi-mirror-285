from typing import Any, Callable, Mapping, Optional, Tuple, Union

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.expressions.non_symbolic_expr import NonSymbolicExpr
from classiq.interface.generator.expressions.qmod_sized_proxy import QmodSizedProxy
from classiq.interface.model.handle_binding import (
    HandleBinding,
    SlicedHandleBinding,
    SubscriptHandleBinding,
)

from classiq.exceptions import ClassiqValueError

ILLEGAL_SLICING_STEP_MSG = "Slicing with a step of a quantum variable is not supported"
SLICE_OUT_OF_BOUNDS_MSG = "Slice end index out of bounds"
QARRAY_ELEMENT_NOT_SUBSCRIPTABLE = "Subscripting an element in QArray is illegal"


class QmodQArrayProxy(NonSymbolicExpr, QmodSizedProxy):
    def __init__(
        self,
        handle: HandleBinding,
        element_proxy: Callable[[HandleBinding], QmodSizedProxy],
        element_size: int,
        length: int,
    ) -> None:
        super().__init__(handle, element_size * length)
        self._length = length
        self._element_proxy = element_proxy
        self._element_size = element_size

    def __getitem__(self, key: Union[slice, int]) -> "QmodSizedProxy":
        if self._index is not None:
            raise TypeError(QARRAY_ELEMENT_NOT_SUBSCRIPTABLE)

        new_index: Optional[int] = None

        if isinstance(key, slice):
            if key.step is not None:
                raise ClassiqValueError(ILLEGAL_SLICING_STEP_MSG)
            new_slice = self._get_new_slice(key.start, key.stop)
        else:
            new_slice = self._get_new_slice(key, key + 1)
            new_index = new_slice[0]

        if (self._slice is not None and new_slice[1] > self._slice[1]) or new_slice[
            1
        ] > self._size:
            raise ClassiqValueError(SLICE_OUT_OF_BOUNDS_MSG)

        new_handle = self._get_new_handle(new_index, new_slice)
        if new_index is not None:
            return self._element_proxy(new_handle)
        return QmodQArrayProxy(
            new_handle,
            self._element_proxy,
            self._element_size,
            self._length,
        )

    def _get_new_slice(self, start: int, end: int) -> Tuple[int, int]:
        if self._slice is not None:
            return self._slice[0] + start, self._slice[0] + end
        return start, end

    @property
    def type_name(self) -> str:
        return "Quantum array"

    @property
    def _index(self) -> Optional[int]:
        if not isinstance(self._handle, SubscriptHandleBinding):
            return None
        return self._handle.index.to_int_value()

    @property
    def _slice(self) -> Optional[Tuple[int, int]]:
        if not isinstance(self._handle, SlicedHandleBinding):
            return None
        return self._handle.start.to_int_value(), self._handle.end.to_int_value()

    def _get_new_handle(
        self, new_index: Optional[int], new_slice: Tuple[int, int]
    ) -> HandleBinding:
        if new_index is not None:
            return SubscriptHandleBinding(
                name=self.handle.name,
                index=Expression(expr=str(new_index)),
            )
        return SlicedHandleBinding(
            name=self.handle.name,
            start=Expression(expr=str(new_slice[0])),
            end=Expression(expr=str(new_slice[1])),
        )

    @property
    def len(self) -> int:
        return self._length

    @property
    def fields(self) -> Mapping[str, Any]:
        return {
            "len": self.len,
        }

    @property
    def size(self) -> int:
        if (slice_ := self._slice) is not None:
            length = slice_[1] - slice_[0]
        elif self._index is not None:
            length = 1
        else:
            length = self._length
        return length * self._element_size

    def __str__(self) -> str:
        return str(self.handle)
