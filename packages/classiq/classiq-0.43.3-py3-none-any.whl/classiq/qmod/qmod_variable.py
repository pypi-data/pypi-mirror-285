import abc
import sys
from contextlib import contextmanager
from typing import (  # type: ignore[attr-defined]
    TYPE_CHECKING,
    Any,
    ForwardRef,
    Generic,
    Iterator,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    _GenericAlias,
    get_args,
    get_origin,
    overload,
)

from typing_extensions import Annotated, ParamSpec, Self, _AnnotatedAlias

from classiq.interface.ast_node import SourceReference
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.handle_binding import (
    HandleBinding,
    SlicedHandleBinding,
    SubscriptHandleBinding,
)
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_expressions.amplitude_loading_operation import (
    AmplitudeLoadingOperation,
)
from classiq.interface.model.quantum_expressions.arithmetic_operation import (
    ArithmeticOperation,
)
from classiq.interface.model.quantum_type import (
    QuantumBit,
    QuantumBitvector,
    QuantumNumeric,
    QuantumType,
)

from classiq.exceptions import ClassiqValueError
from classiq.qmod.qmod_parameter import ArrayBase, CBool, CInt, CParam, CParamScalar
from classiq.qmod.quantum_callable import QCallable
from classiq.qmod.symbolic_expr import Symbolic, SymbolicExpr
from classiq.qmod.symbolic_type import SymbolicTypes
from classiq.qmod.utilities import get_source_ref, version_portable_get_args

ILLEGAL_SLICING_STEP_MSG = "Slicing with a step of a quantum variable is not supported"
SLICE_OUT_OF_BOUNDS_MSG = "Slice end index out of bounds"
UNSUPPORTED_ELEMENT_TYPE = "Only QBit and QNum are supported as element type for QArray"
QARRAY_ELEMENT_NOT_SUBSCRIPTABLE = "Subscripting an element in QArray is illegal"


def _is_input_output_typehint(type_hint: Any) -> bool:
    return isinstance(type_hint, _AnnotatedAlias) and isinstance(
        type_hint.__metadata__[0], PortDeclarationDirection
    )


def get_type_hint_expr(type_hint: Any) -> str:
    if isinstance(type_hint, ForwardRef):  # expression in string literal
        return str(type_hint.__forward_arg__)
    if get_origin(type_hint) == Literal:  # explicit numeric literal
        return str(get_args(type_hint)[0])
    else:
        return str(type_hint)  # implicit numeric literal


@contextmanager
def _no_current_expandable() -> Iterator[None]:
    current_expandable = QCallable.CURRENT_EXPANDABLE
    QCallable.CURRENT_EXPANDABLE = None
    try:
        yield
    finally:
        QCallable.CURRENT_EXPANDABLE = current_expandable


class QVar(Symbolic):
    def __init__(self, name: str, depth: int = 2) -> None:
        super().__init__(name, True)
        self._name = name
        source_ref = get_source_ref(sys._getframe(depth))
        if QCallable.CURRENT_EXPANDABLE is not None:
            QCallable.CURRENT_EXPANDABLE.add_local_handle(
                self._name, self.get_qmod_type(), source_ref
            )

    @abc.abstractmethod
    def get_handle_binding(self) -> HandleBinding:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_qmod_type(self) -> QuantumType:
        raise NotImplementedError()

    @staticmethod
    def from_type_hint(type_hint: Any) -> Optional[Type["QVar"]]:
        if _is_input_output_typehint(type_hint):
            return QVar.from_type_hint(type_hint.__args__[0])
        type_ = get_origin(type_hint) or type_hint
        if issubclass(type_, QVar):
            return type_
        return None

    @classmethod
    @abc.abstractmethod
    def to_qmod_quantum_type(cls, type_hint: Any) -> QuantumType:
        raise NotImplementedError()

    @classmethod
    def port_direction(cls, type_hint: Any) -> PortDeclarationDirection:
        if _is_input_output_typehint(type_hint):
            assert len(type_hint.__metadata__) >= 1
            return type_hint.__metadata__[0]
        assert type_hint == cls or get_origin(type_hint) == cls
        return PortDeclarationDirection.Inout

    def __str__(self) -> str:
        return str(self.get_handle_binding())


_Q = TypeVar("_Q", bound=QVar)
Output = Annotated[_Q, PortDeclarationDirection.Output]
Input = Annotated[_Q, PortDeclarationDirection.Input]


class QScalar(QVar, SymbolicExpr):
    def __init__(self, name: str, depth: int = 2) -> None:
        QVar.__init__(self, name, depth)
        SymbolicExpr.__init__(self, name, True)

    def _insert_arith_operation(
        self, expr: SymbolicTypes, inplace: bool, source_ref: SourceReference
    ) -> None:
        # Fixme: Arithmetic operations are not yet supported on slices (see CAD-12670)
        if TYPE_CHECKING:
            assert QCallable.CURRENT_EXPANDABLE is not None
        QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
            ArithmeticOperation(
                expression=Expression(expr=str(expr)),
                result_var=self.get_handle_binding(),
                inplace_result=inplace,
                source_ref=source_ref,
            )
        )

    def _insert_amplitude_loading(
        self, expr: SymbolicTypes, source_ref: SourceReference
    ) -> None:
        if TYPE_CHECKING:
            assert QCallable.CURRENT_EXPANDABLE is not None
        QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
            AmplitudeLoadingOperation(
                expression=Expression(expr=str(expr)),
                result_var=self.get_handle_binding(),
                source_ref=source_ref,
            )
        )

    def get_handle_binding(self) -> HandleBinding:
        return HandleBinding(name=self._name)

    def __ior__(self, other: Any) -> Self:
        if not isinstance(other, get_args(SymbolicTypes)):
            raise TypeError(
                f"Invalid argument {other!r} for out-of-place arithmetic operation"
            )

        self._insert_arith_operation(other, False, get_source_ref(sys._getframe(1)))
        return self

    def __ixor__(self, other: Any) -> Self:
        if not isinstance(other, get_args(SymbolicTypes)):
            raise TypeError(
                f"Invalid argument {other!r} for in-place arithmetic operation"
            )

        self._insert_arith_operation(other, True, get_source_ref(sys._getframe(1)))
        return self

    def __imul__(self, other: Any) -> Self:
        if not isinstance(other, get_args(SymbolicTypes)):
            raise TypeError(
                f"Invalid argument {other!r} for out of ampltiude encoding operation"
            )

        self._insert_amplitude_loading(other, get_source_ref(sys._getframe(1)))
        return self


class QBit(QScalar):
    @classmethod
    def to_qmod_quantum_type(cls, type_hint: Any) -> QuantumType:
        return QuantumBit()

    def get_qmod_type(self) -> QuantumType:
        return QuantumBit()


_P = ParamSpec("_P")


class QNum(Generic[_P], QScalar):
    QMOD_TYPE = QuantumNumeric

    @overload
    def __init__(self, name: str):
        pass

    @overload
    def __init__(
        self,
        name: str,
        size: Union[int, CInt],
        is_signed: Union[bool, CBool],
        fraction_digits: Union[int, CInt],
    ):
        pass

    def __init__(
        self,
        name: str,
        size: Union[int, CInt, None] = None,
        is_signed: Union[bool, CBool, None] = None,
        fraction_digits: Union[int, CInt, None] = None,
    ):
        if (
            size is None
            and (is_signed is not None or fraction_digits is not None)
            or size is not None
            and (is_signed is None or fraction_digits is None)
        ):
            raise ClassiqValueError(
                "Assign none or all of size, is_signed, and fraction_digits"
            )
        self._size = None if size is None else Expression(expr=str(size))
        self._is_signed = None if is_signed is None else Expression(expr=str(is_signed))
        self._fraction_digits = (
            None if fraction_digits is None else Expression(expr=str(fraction_digits))
        )
        super().__init__(name, 3)

    @classmethod
    def to_qmod_quantum_type(cls, type_hint: Any) -> QuantumType:
        type_args = get_args(type_hint)
        if len(type_args) == 0:
            return cls.QMOD_TYPE()
        type_args = type_args[0]
        if len(type_args) != 3:
            raise ClassiqValueError(
                "QNum receives three type arguments: QNum[size: int | CInt, "
                "is_signed: bool | CBool, fraction_digits: int | CInt]"
            )
        return cls.QMOD_TYPE(
            size=Expression(expr=get_type_hint_expr(type_args[0])),
            is_signed=Expression(expr=get_type_hint_expr(type_args[1])),
            fraction_digits=Expression(expr=get_type_hint_expr(type_args[2])),
        )

    def get_qmod_type(self) -> QuantumType:
        return self.QMOD_TYPE(
            size=self._size,
            is_signed=self._is_signed,
            fraction_digits=self._fraction_digits,
        )

    @property
    def size(self) -> CParamScalar:
        return CParamScalar(f"get_field({self._name}, 'size')")

    @property
    def fraction_digits(self) -> CParamScalar:
        return CParamScalar(f"get_field({self._name}, 'fraction_digits')")

    @property
    def is_signed(self) -> CParamScalar:
        return CParamScalar(f"get_field({self._name}, 'is_signed')")

    # Support comma-separated generic args in older Python versions
    if sys.version_info[0:2] < (3, 10):

        def __class_getitem__(cls, args) -> _GenericAlias:
            return _GenericAlias(cls, args)


class QArray(ArrayBase[_P], QVar):
    def __init__(
        self,
        name: str,
        element_type: _GenericAlias = QBit,
        length: Optional[Union[int, CInt]] = None,
        # TODO [CAD-18620]: improve type hints
        slice_: Optional[Tuple[int, int]] = None,
        index_: Optional[Union[int, CInt]] = None,
    ) -> None:
        if not issubclass(get_origin(element_type) or element_type, (QBit, QNum)):
            raise ClassiqValueError(UNSUPPORTED_ELEMENT_TYPE)
        self._element_type = element_type
        self._length = length
        self._slice = slice_
        self._index = index_
        super().__init__(name)

    def get_handle_binding(self) -> HandleBinding:
        if self._index is not None:
            return SubscriptHandleBinding(
                name=self._name,
                index=Expression(expr=str(self._index)),
            )

        if self._slice is not None:
            return SlicedHandleBinding(
                name=self._name,
                start=Expression(expr=str(self._slice[0])),
                end=Expression(expr=str(self._slice[1])),
            )

        return HandleBinding(name=self._name)

    def __getitem__(self, key: Union[slice, int, CInt]) -> Any:
        if self._index is not None:
            raise ClassiqValueError(QARRAY_ELEMENT_NOT_SUBSCRIPTABLE)

        # TODO [CAD-18620]: improve type hints
        new_index: Optional[Any] = None

        if isinstance(key, slice):
            if key.step is not None:
                raise ClassiqValueError(ILLEGAL_SLICING_STEP_MSG)
            new_slice = self._get_new_slice(key.start, key.stop)

        else:
            if isinstance(key, CParam) and not isinstance(key, CParamScalar):
                raise ClassiqValueError("Non-classical parameter for slicing")
            new_slice = self._get_new_slice(key, key + 1)
            new_index = new_slice[0]

        if (
            self._slice is not None
            and not isinstance(new_slice[1], Symbolic)
            and not isinstance(self._slice[1], Symbolic)
            and new_slice[1] > self._slice[1]
        ) or (
            self._length is not None
            and not isinstance(new_slice[1], Symbolic)
            and not isinstance(self._length, Symbolic)
            and new_slice[1] > self._length
        ):
            raise ClassiqValueError(SLICE_OUT_OF_BOUNDS_MSG)
        # prevent addition to local handles, since this is used for slicing existing local handles
        with _no_current_expandable():
            if new_index is None:
                array_class = QArray
            else:
                array_class = QArraySubscript
            return array_class(
                self._name, length=self._length, slice_=new_slice, index_=new_index
            )

    # TODO [CAD-18620]: improve type hints
    def _get_new_slice(self, start: Any, end: Any) -> Tuple[Any, Any]:
        if self._slice is not None:
            return (self._slice[0] + start, self._slice[0] + end)
        return (start, end)

    def __len__(self) -> int:
        raise ClassiqValueError(
            "len(<var>) is not supported for quantum variables - use <var>.len instead"
        )

    if TYPE_CHECKING:

        @property
        def len(self) -> int: ...

    else:

        @property
        def len(self) -> CParamScalar:
            if self._length is not None:
                return CParamScalar(f"{self._length}")
            return CParamScalar(f"get_field({self._name}, 'len')")

    @classmethod
    def to_qmod_quantum_type(cls, type_hint: Any) -> QuantumType:
        type_args = version_portable_get_args(type_hint)
        if len(type_args) == 1 and isinstance(type_args[0], (str, int)):
            type_args = (QBit, type_args[0])

        api_element_type = QBit if len(type_args) == 0 else type_args[0]
        api_element_class = get_origin(api_element_type) or api_element_type
        element_type = api_element_class.to_qmod_quantum_type(api_element_type)

        length_expr: Optional[Expression] = None
        if len(type_args) == 2:
            length_expr = Expression(expr=get_type_hint_expr(type_args[1]))

        return QuantumBitvector(element_type=element_type, length=length_expr)

    def get_qmod_type(self) -> QuantumType:
        element_class = get_origin(self._element_type) or self._element_type
        length = None
        if self._length is not None:
            length = Expression(expr=str(self._length))
        return QuantumBitvector(
            element_type=element_class.to_qmod_quantum_type(self._element_type),
            length=length,
        )


class QArraySubscript(QArray, QScalar):
    @property
    def size(self) -> CParamScalar:
        return CParamScalar(f"get_field({self.get_handle_binding()}, 'size')")

    @property
    def fraction_digits(self) -> CParamScalar:
        return CParamScalar(
            f"get_field({self.get_handle_binding()}, 'fraction_digits')"
        )

    @property
    def is_signed(self) -> CParamScalar:
        return CParamScalar(f"get_field({self.get_handle_binding()}, 'is_signed')")


def create_qvar_for_port_decl(port: PortDeclaration, name: str) -> QVar:
    # prevent addition to local handles, since this is used for ports
    with _no_current_expandable():
        if _is_single_qbit_vector(port):
            return QBit(name)
        elif isinstance(port.quantum_type, QuantumNumeric):
            return QNum(name)
        return QArray(name)


def _is_single_qbit_vector(port: PortDeclaration) -> bool:
    return (
        isinstance(port.quantum_type, QuantumBit)
        or isinstance(port.quantum_type, QuantumBitvector)
        and port.size is not None
        and port.size.is_evaluated()
        and port.size.to_int_value() == 1
    )
