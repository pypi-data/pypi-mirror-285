import ast
import functools
from dataclasses import is_dataclass
from enum import EnumMeta
from inspect import isclass
from typing import Any, Callable, Dict, List, Optional, Tuple, get_origin

from classiq.interface.executor.execution_preferences import ExecutionPreferences
from classiq.interface.generator.model.constraints import Constraints
from classiq.interface.generator.model.preferences.preferences import Preferences
from classiq.interface.model.model import Model, SerializedModel
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)

from classiq.exceptions import ClassiqError
from classiq.qmod.classical_function import CFunc
from classiq.qmod.declaration_inferrer import infer_func_decl
from classiq.qmod.qmod_constant import QConstant
from classiq.qmod.qmod_parameter import CArray, CParam
from classiq.qmod.qmod_variable import QVar
from classiq.qmod.quantum_callable import QCallable, QCallableList
from classiq.qmod.quantum_expandable import QExpandable, QTerminalCallable
from classiq.qmod.utilities import mangle_keyword, unmangle_keyword


def _lookup_qfunc(name: str) -> Optional[QuantumFunctionDeclaration]:
    # FIXME: to be generalized to existing user-defined functions
    return QuantumFunctionDeclaration.BUILTIN_FUNCTION_DECLARATIONS.get(name)


def create_model(
    entry_point: "QFunc",
    constraints: Optional[Constraints] = None,
    execution_preferences: Optional[ExecutionPreferences] = None,
    preferences: Optional[Preferences] = None,
    classical_execution_function: Optional[CFunc] = None,
) -> SerializedModel:
    if entry_point.func_decl.name != "main":
        raise ClassiqError(
            f"The entry point function must be named 'main', got '{entry_point.func_decl.name}'"
        )
    return entry_point.create_model(
        constraints, execution_preferences, preferences, classical_execution_function
    ).get_model()


class QFunc(QExpandable):
    FRAME_DEPTH = 2

    def __init__(self, py_callable: Callable) -> None:
        _validate_no_gen_params(py_callable.__annotations__)
        super().__init__(py_callable)
        functools.update_wrapper(self, py_callable)

    @property
    def func_decl(self) -> QuantumFunctionDeclaration:
        return self._qmodule.native_defs.get(
            self._py_callable.__name__,
            infer_func_decl(self._py_callable, qmodule=self._qmodule),
        )

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        super().__call__(*args, **kwargs)
        self.expand()

    def create_model(
        self,
        constraints: Optional[Constraints] = None,
        execution_preferences: Optional[ExecutionPreferences] = None,
        preferences: Optional[Preferences] = None,
        classical_execution_function: Optional[CFunc] = None,
    ) -> Model:
        self._qmodule.enum_decls = dict()
        self._qmodule.type_decls = dict()
        self._qmodule.native_defs = dict()
        self._qmodule.constants = dict()
        QConstant.set_current_model(self._qmodule)
        self.expand()
        model_extra_settings: List[Tuple[str, Any]] = [
            ("constraints", constraints),
            ("execution_preferences", execution_preferences),
            ("preferences", preferences),
        ]
        if classical_execution_function is not None:
            self._add_constants_from_classical_code(classical_execution_function)
            model_extra_settings.append(
                ("classical_execution_code", classical_execution_function.code)
            )
        return Model(
            constants=list(self._qmodule.constants.values()),
            functions=list(self._qmodule.native_defs.values()),
            enums=list(self._qmodule.enum_decls.values()),
            types=list(self._qmodule.type_decls.values()),
            **{key: value for key, value in model_extra_settings if value},
        )

    def expand(self) -> None:
        if self.func_decl.name in self._qmodule.native_defs:
            return
        super().expand()
        self._qmodule.native_defs[self.func_decl.name] = NativeFunctionDefinition(
            **{**self.func_decl.dict(), **{"body": self.body}}
        )

    def _add_constants_from_classical_code(
        self, classical_execution_function: CFunc
    ) -> None:
        # FIXME: https://classiq.atlassian.net/browse/CAD-18050
        # We use this visitor to add the constants that were used in the classical
        # execution code to the model. In the future, if we will have a better notion
        # of "QModule" and a "QConstant" will be a part of it then we may be able to
        # remove the handling of the QConstants from this visitor, but I think we will
        # need similar logic to allow using python variables in the classical execution
        # code
        class IdentifierVisitor(ast.NodeVisitor):
            def visit_Name(self, node: ast.Name) -> None:
                if (
                    node.id in classical_execution_function._caller_constants
                    and isinstance(
                        classical_execution_function._caller_constants[node.id],
                        QConstant,
                    )
                ):
                    classical_execution_function._caller_constants[
                        node.id
                    ].add_to_model()

        IdentifierVisitor().visit(ast.parse(classical_execution_function.code))


class ExternalQFunc(QTerminalCallable):
    def __init__(self, py_callable: Callable) -> None:
        decl = _lookup_qfunc(unmangle_keyword(py_callable.__name__))
        if decl is None:
            raise ClassiqError(f"Definition of {py_callable.__name__!r} not found")

        py_callable.__annotations__.pop("return", None)
        if py_callable.__annotations__.keys() != {
            mangle_keyword(arg.name) for arg in decl.get_positional_arg_decls()
        }:
            raise ClassiqError(
                f"Parameter type hints for {py_callable.__name__!r} do not match imported declaration"
            )
        super().__init__(decl)
        functools.update_wrapper(self, py_callable)


ILLEGAL_PARAM_ERROR = "Unsupported type hint '{annotation}' for argument '{name}'."


class IllegalParamsError(ClassiqError):
    _HINT = (
        "\nNote - QMOD functions can declare classical parameters using the type hints "
        "'CInt', 'CReal', 'CBool', and 'CArray'."
    )

    def __init__(self, message: str) -> None:
        super().__init__(message + self._HINT)


def _validate_no_gen_params(annotations: Dict[str, Any]) -> None:
    _illegal_params = {
        name: annotation
        for name, annotation in annotations.items()
        if not (
            name == "return"
            or isclass(annotation)
            and issubclass(annotation, CParam)
            or isclass(annotation)
            and is_dataclass(annotation)
            or isclass(annotation)
            and isinstance(annotation, EnumMeta)
            or get_origin(annotation) is CArray
            or (get_origin(annotation) or annotation) is QCallable
            or (get_origin(annotation) or annotation) is QCallableList
            or QVar.from_type_hint(annotation) is not None
        )
    }
    if _illegal_params:
        raise IllegalParamsError(
            "\n".join(
                ILLEGAL_PARAM_ERROR.format(name=name, annotation=annotation)
                for name, annotation in _illegal_params.items()
            )
        )
