from typing import Any, Mapping

from sympy import Symbol

from classiq.interface.generator.expressions.qmod_sized_proxy import QmodSizedProxy
from classiq.interface.model.handle_binding import HandleBinding

from classiq.exceptions import ClassiqValueError


class QmodQScalarProxy(Symbol, QmodSizedProxy):
    def __new__(cls, handle: HandleBinding, **assumptions: bool) -> "QmodQScalarProxy":
        return super().__new__(cls, str(handle), **assumptions)

    def __init__(self, handle: HandleBinding, size: int) -> None:
        super().__init__(handle, size)


class QmodQBitProxy(QmodQScalarProxy):
    def __init__(self, handle: HandleBinding) -> None:
        super().__init__(handle, 1)

    @property
    def type_name(self) -> str:
        return "Quantum bit"


class QmodQNumProxy(QmodQScalarProxy):
    def __init__(
        self, handle: HandleBinding, size: int, fraction_digits: int, is_signed: bool
    ) -> None:
        super().__init__(handle, size)
        if fraction_digits + is_signed > size:
            raise ClassiqValueError(
                f"{'Signed' if is_signed else 'Unsigned'} quantum numeric of size "
                f"{size} cannot have {fraction_digits} fraction digits"
            )
        self._fraction_digits = fraction_digits
        self._is_signed = is_signed

    @property
    def type_name(self) -> str:
        return "Quantum numeric"

    @property
    def size(self) -> int:
        return self._size

    @property
    def fraction_digits(self) -> int:
        return self._fraction_digits

    @property
    def is_signed(self) -> bool:
        return self._is_signed

    @property
    def fields(self) -> Mapping[str, Any]:
        return {
            "size": self.size,
            "is_signed": self.is_signed,
            "fraction_digits": self.fraction_digits,
        }
