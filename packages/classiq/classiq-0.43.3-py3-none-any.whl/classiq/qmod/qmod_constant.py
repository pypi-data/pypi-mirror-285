import inspect
from dataclasses import is_dataclass
from typing import Any, Optional

from classiq.interface.generator.constant import Constant
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import (
    ClassicalArray,
    ClassicalList,
)

from classiq.exceptions import ClassiqError
from classiq.qmod.declaration_inferrer import python_type_to_qmod
from classiq.qmod.model_state_container import ModelStateContainer
from classiq.qmod.qmod_parameter import CParam, CParamList, CParamStruct
from classiq.qmod.symbolic_expr import SymbolicExpr
from classiq.qmod.utilities import qmod_val_to_expr_str


class QConstant(SymbolicExpr):
    CURRENT_QMODULE: Optional[ModelStateContainer] = None

    def __init__(self, name: str, py_type: type, value: Any) -> None:
        self.name = name
        self._py_type = py_type
        self._value = value

    @staticmethod
    def set_current_model(qmodule: ModelStateContainer) -> None:
        QConstant.CURRENT_QMODULE = qmodule

    def add_to_model(self) -> None:
        if QConstant.CURRENT_QMODULE is None:
            raise ClassiqError(
                "Error trying to add a constant to a model without a current QModule."
            )

        expr = qmod_val_to_expr_str(self._value)
        if (
            self.name in QConstant.CURRENT_QMODULE.constants
            and expr != QConstant.CURRENT_QMODULE.constants[self.name].value.expr
        ):
            raise ClassiqError(f"Constant {self.name} is already defined in the model")

        if isinstance(self._value, QConstant):
            QConstant.CURRENT_QMODULE.constants[self.name] = Constant(
                name=self.name,
                const_type=QConstant.CURRENT_QMODULE.constants[
                    self._value.name
                ].const_type,
                value=Expression(expr=self._value.name),
            )
        else:
            qmod_type = python_type_to_qmod(
                self._py_type, qmodule=QConstant.CURRENT_QMODULE
            )
            if qmod_type is None:
                raise ClassiqError("Invalid QMOD type")

            QConstant.CURRENT_QMODULE.constants[self.name] = Constant(
                name=self.name,
                const_type=qmod_type,
                value=Expression(expr=expr),
            )

    def __getattr__(self, name: str) -> CParam:
        self.add_to_model()

        if name == "is_quantum":
            return False  # type:ignore[return-value]

        py_type = type(self._value)
        if (
            QConstant.CURRENT_QMODULE is None
            or not inspect.isclass(py_type)
            or not is_dataclass(py_type)
        ):
            return self.__getattribute__(name)

        return CParamStruct.get_field(
            QConstant.CURRENT_QMODULE, self.name, py_type.__name__, name
        )

    def __getitem__(self, item: Any) -> CParam:
        self.add_to_model()

        assert QConstant.CURRENT_QMODULE is not None

        qmod_type = python_type_to_qmod(
            self._py_type, qmodule=QConstant.CURRENT_QMODULE
        )
        if qmod_type is None:
            raise ClassiqError("Invalid QMOD type")

        if not isinstance(qmod_type, (ClassicalList, ClassicalArray)):
            raise ClassiqError("Invalid subscript to non-list constant")

        return CParamList(
            self.name,
            qmod_type,
            QConstant.CURRENT_QMODULE,
        )[item]

    def __str__(self) -> str:
        return self.name
