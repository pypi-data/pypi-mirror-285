from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Mapping, Type, Union

from classiq.interface.generator.function_params import PortDirection
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.visitor import Visitor
from classiq.interface.model.handle_binding import (
    HandleBinding,
    SlicedHandleBinding,
    SubscriptHandleBinding,
)
from classiq.interface.model.model import Model
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
    QuantumOperandDeclaration,
)
from classiq.interface.model.quantum_lambda_function import (
    QuantumLambdaFunction,
)
from classiq.interface.model.quantum_statement import QuantumOperation
from classiq.interface.model.validation_handle import HandleState
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)
from classiq.interface.model.within_apply_operation import WithinApply

from classiq.exceptions import ClassiqSemanticError
from classiq.qmod.semantics.annotation import annotate_function_call_decl
from classiq.qmod.semantics.error_manager import ErrorManager
from classiq.qmod.semantics.validation.func_call_validation import (
    validate_call_arguments,
)
from classiq.qmod.semantics.validation.types_validation import check_duplicate_types


class StaticScope:

    def __init__(
        self,
        parameters: List[str],
        operands: Dict[str, QuantumOperandDeclaration],
        variables_to_states: Dict[str, HandleState],
    ) -> None:
        self.parameters = parameters
        self.operands = operands
        self.variable_states = variables_to_states


class StaticSemanticsVisitor(Visitor):
    def __init__(
        self,
        functions_dict: Dict[str, QuantumFunctionDeclaration],
        constants: List[str],
    ) -> None:
        self._scope: List[StaticScope] = []
        self._error_manager = ErrorManager()
        self._functions_dict = functions_dict
        self._constants = constants

    @property
    def current_scope(self) -> StaticScope:
        return self._scope[-1]

    @contextmanager
    def scoped_visit(self, scope: StaticScope) -> Iterator[None]:
        self._scope.append(scope)
        yield
        self._scope.pop()

    def visit_Model(self, model: Model) -> None:
        check_duplicate_types([*model.enums, *model.types])
        self.visit_BaseModel(model)

    def visit_NativeFunctionDefinition(
        self, func_def: NativeFunctionDefinition
    ) -> None:
        if len(func_def.body) == 0:
            return
        scope = StaticScope(
            parameters=list(func_def.param_decls.keys()) + self._constants,
            operands=dict(func_def.operand_declarations),
            variables_to_states=initialize_variables_to_state(
                list(func_def.port_declarations.values())
            ),
        )
        with self.scoped_visit(scope):
            self.visit(func_def.body)
            with self._error_manager.node_context(func_def.body[-1]):
                for port_decl in func_def.port_declarations.values():
                    handle_state = self.current_scope.variable_states[port_decl.name]
                    expected_terminal_state = EXPECTED_TERMINAL_STATES.get(
                        port_decl.direction
                    )
                    if (
                        expected_terminal_state is not None
                        and handle_state is not expected_terminal_state
                    ):
                        self._error_manager.add_error(
                            f"At the end of the function, port `{port_decl.name}` is expected to be {expected_terminal_state.name.lower()} but it isn't"
                        )

    def visit_WithinApply(self, within_apply: WithinApply) -> None:
        initial_variables_to_state = self.current_scope.variable_states.copy()
        scope = StaticScope(
            parameters=self.current_scope.parameters,
            operands=self.current_scope.operands,
            variables_to_states=self.current_scope.variable_states.copy(),
        )
        with self.scoped_visit(scope):
            self.visit(within_apply.compute)
            compute_captured_variables = {
                var
                for var, state in self.current_scope.variable_states.items()
                if var in initial_variables_to_state
                and state != initial_variables_to_state[var]
            }
            self.visit(within_apply.action)
            variables_to_state = self.current_scope.variable_states.copy()
        self.current_scope.variable_states.update(
            {
                var: state
                for var, state in variables_to_state.items()
                if var in self.current_scope.variable_states
                and var not in compute_captured_variables
            }
        )

    def visit_QuantumOperation(self, op: QuantumOperation) -> None:
        with self._error_manager.node_context(op):
            if isinstance(op, QuantumFunctionCall):
                annotate_function_call_decl(
                    op,
                    {
                        **self._functions_dict,
                        **self.current_scope.operands,
                    },
                )
                validate_call_arguments(
                    op,
                    {
                        **self._functions_dict,
                        **self.current_scope.operands,
                    },
                )
            self._handle_inputs(op.wiring_inputs)
            self._handle_outputs(op.wiring_outputs)
            self._handle_inouts(op.wiring_inouts)
            self.generic_visit(op)

    def visit_VariableDeclarationStatement(
        self, declaration: VariableDeclarationStatement
    ) -> None:
        handle_wiring_state = self.current_scope.variable_states.get(declaration.name)
        if handle_wiring_state is not None:
            self._error_manager.add_error(
                f"Trying to declare a variable of the same name as previously declared variable {declaration.name}"
            )
            return

        self.current_scope.variable_states[declaration.name] = HandleState.UNINITIALIZED

    def visit_QuantumLambdaFunction(self, lambda_func: QuantumLambdaFunction) -> None:
        assert lambda_func.func_decl is not None
        renamed_parameters = [
            lambda_func.rename_params.get(param, param)
            for param in self.current_scope.parameters
            + list(lambda_func.func_decl.param_decls.keys())
        ]
        ports = list(lambda_func.func_decl.port_declarations.values())
        for i, port in enumerate(ports):
            ports[i] = port.copy(
                update={"name": lambda_func.rename_params.get(port.name, port.name)}
            )
        variables_to_states = self.current_scope.variable_states.copy()
        original_operands = {
            **dict(lambda_func.func_decl.operand_declarations),
            **self.current_scope.operands,
        }
        renamed_operands: Dict[str, QuantumOperandDeclaration] = {}
        for operand_name, operand_decl in original_operands.items():
            renamed_name = lambda_func.rename_params.get(operand_name, operand_name)
            renamed_operands[renamed_name] = operand_decl.copy(
                update={"name": renamed_name}
            )
        scope = StaticScope(
            parameters=renamed_parameters,
            operands=renamed_operands,
            variables_to_states={
                **variables_to_states,
                **initialize_variables_to_state(ports),
            },
        )
        with self.scoped_visit(scope):
            self.generic_visit(lambda_func)

    def _handle_inputs(self, inputs: Mapping[str, HandleBinding]) -> None:
        for handle_binding in inputs.values():
            handle_wiring_state = self.current_scope.variable_states[
                handle_binding.name
            ]
            if handle_wiring_state is not HandleState.INITIALIZED:
                self._error_manager.add_error(
                    f"Trying to access handle {handle_binding.name!r} as input but it is in incorrect state"
                )
                continue

            self.current_scope.variable_states[handle_binding.name] = (
                HandleState.UNINITIALIZED
            )

    def _handle_outputs(self, outputs: Mapping[str, HandleBinding]) -> None:
        for handle_binding in outputs.values():
            handle_wiring_state = self.current_scope.variable_states[
                handle_binding.name
            ]

            if handle_wiring_state is not HandleState.UNINITIALIZED:
                self._error_manager.add_error(
                    f"Trying to access handle {handle_binding.name!r} as output but it is in incorrect state"
                )
                continue

            self.current_scope.variable_states[handle_binding.name] = (
                HandleState.INITIALIZED
            )

    def _handle_inouts(
        self,
        inouts: Mapping[
            str, Union[SlicedHandleBinding, SubscriptHandleBinding, HandleBinding]
        ],
    ) -> None:
        sliced_handles = set()
        whole_handles = set()

        for handle_binding in inouts.values():
            handle_wiring_state = self.current_scope.variable_states[
                handle_binding.name
            ]

            if handle_wiring_state is not HandleState.INITIALIZED:
                self._error_manager.add_error(
                    f"Trying to access handle {handle_binding.name!r} as inout but it is in incorrect state"
                )

            if isinstance(
                handle_binding, (SlicedHandleBinding, SubscriptHandleBinding)
            ):
                sliced_handles.add(handle_binding.name)
            else:
                whole_handles.add(handle_binding.name)

        for handle in sliced_handles & whole_handles:
            self._error_manager.add_error(
                f"Invalid use of inout handle {handle!r}, used both in slice or subscript and whole"
            )


def resolve_function_calls(
    root: Any,
    quantum_function_dict: Mapping[str, QuantumFunctionDeclaration],
) -> None:
    StaticSemanticsVisitor(
        {
            **QuantumFunctionDeclaration.BUILTIN_FUNCTION_DECLARATIONS,
            **quantum_function_dict,
        },
        [],
    ).visit(root)


def static_semantics_analysis_pass(
    model: Model, error_type: Type[Exception] = ClassiqSemanticError
) -> None:
    StaticSemanticsVisitor(
        {
            **QuantumFunctionDeclaration.BUILTIN_FUNCTION_DECLARATIONS,
            **model.function_dict,
        },
        [const.name for const in model.constants],
    ).visit(model)
    ErrorManager().report_errors(error_type)


EXPECTED_TERMINAL_STATES: Dict[PortDeclarationDirection, HandleState] = {
    PortDeclarationDirection.Output: HandleState.INITIALIZED,
    PortDeclarationDirection.Inout: HandleState.INITIALIZED,
}


def initialize_variables_to_state(
    port_declarations: List[PortDeclaration],
) -> Dict[str, HandleState]:
    variables_to_state: Dict[str, HandleState] = dict()

    for port_decl in port_declarations:
        variables_to_state[port_decl.name] = (
            HandleState.INITIALIZED
            if port_decl.direction.includes_port_direction(PortDirection.Input)
            else HandleState.UNINITIALIZED
        )

    return variables_to_state
