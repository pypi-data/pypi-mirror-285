import itertools
from typing import Any, Dict, List, Literal, Mapping, Optional, Type, Union

import pydantic

from classiq.interface.ast_node import ASTNode
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.function_declaration import (
    FunctionDeclaration,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.handle_binding import (
    HandleBinding,
    SlicedHandleBinding,
    SubscriptHandleBinding,
)
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)
from classiq.interface.model.quantum_lambda_function import (
    QuantumOperand,
)
from classiq.interface.model.quantum_statement import QuantumOperation
from classiq.interface.model.validation_handle import get_unique_handle_names

from classiq.exceptions import ClassiqError, ClassiqValueError


def _validate_no_duplicated_ports(
    inputs: Mapping[str, HandleBinding],
    outputs: Mapping[str, HandleBinding],
    inouts: Mapping[str, HandleBinding],
) -> None:
    inputs_and_inouts = inputs.keys() & inouts.keys()
    if inputs_and_inouts:
        raise ClassiqValueError(
            f"{inputs_and_inouts} are used as ports in both inputs and inouts"
        )

    outputs_and_inouts = outputs.keys() & inouts.keys()
    if outputs_and_inouts:
        raise ClassiqValueError(
            f"{outputs_and_inouts} are used as ports in both outputs and inouts"
        )


def _validate_no_duplicated_handles(
    inputs: Mapping[str, HandleBinding],
    outputs: Mapping[str, HandleBinding],
    inouts: Mapping[str, HandleBinding],
) -> None:
    inputs_and_inouts = get_unique_handle_names(inputs) & get_unique_handle_names(
        inouts
    )
    if inputs_and_inouts:
        raise ClassiqValueError(
            f"{inputs_and_inouts} are used as handles in both inputs and inouts"
        )

    outputs_and_inouts = get_unique_handle_names(outputs) & get_unique_handle_names(
        inouts
    )
    if outputs_and_inouts:
        raise ClassiqValueError(
            f"{outputs_and_inouts} are used as handles in both outputs and inouts"
        )


def _validate_no_mixing_sliced_and_whole_handles(
    inouts: Mapping[str, HandleBinding],
) -> None:
    def _treat_subscript_as_slice(type_: Type[HandleBinding]) -> Type[HandleBinding]:
        if type_ == SubscriptHandleBinding:
            return SlicedHandleBinding
        return type_

    inout_handle_names_to_types = {
        handle_name: {_treat_subscript_as_slice(type(handle)) for handle in handles}
        for handle_name, handles in itertools.groupby(
            inouts.values(), lambda handle: handle.name
        )
    }
    invalid_handles = [
        handle
        for handle, types in inout_handle_names_to_types.items()
        if len(types) > 1
    ]
    if invalid_handles:
        raise ClassiqValueError(
            f"Inout handles {', '.join(invalid_handles)} mix sliced and whole handles"
        )


ArgValue = Union[
    Expression,
    QuantumOperand,
    SlicedHandleBinding,
    SubscriptHandleBinding,
    HandleBinding,
]


class OperandIdentifier(ASTNode):
    name: str
    index: Expression


class QuantumFunctionCall(QuantumOperation):
    kind: Literal["QuantumFunctionCall"]

    function: Union[str, OperandIdentifier] = pydantic.Field(
        description="The function that is called"
    )
    designated_params: Dict[str, Expression] = pydantic.Field(default_factory=dict)
    designated_inputs: Dict[str, HandleBinding] = pydantic.Field(
        default_factory=dict,
        description="A mapping from the input name to the wire it connects to",
    )
    designated_inouts: Dict[
        str, Union[SlicedHandleBinding, SubscriptHandleBinding, HandleBinding]
    ] = pydantic.Field(
        default_factory=dict,
        description="A mapping from in/out name to the wires that connect to it",
    )
    designated_outputs: Dict[str, HandleBinding] = pydantic.Field(
        default_factory=dict,
        description="A mapping from the output name to the wire it connects to",
    )
    designated_operands: Dict[str, QuantumOperand] = pydantic.Field(
        description="Function calls passed to the operator",
        default_factory=dict,
    )
    positional_args: List[ArgValue] = pydantic.Field(default_factory=list)

    _func_decl: Optional[QuantumFunctionDeclaration] = pydantic.PrivateAttr(
        default=None
    )

    @property
    def func_decl(self) -> QuantumFunctionDeclaration:
        if self._func_decl is None:
            raise ClassiqError("Accessing an unresolved quantum function call")

        return self._func_decl

    def set_func_decl(self, fd: Optional[FunctionDeclaration]) -> None:
        if fd is not None and not isinstance(fd, QuantumFunctionDeclaration):
            raise ClassiqValueError(
                "the declaration of a quantum function call cannot be set to a non-quantum function declaration."
            )
        self._func_decl = fd

    @property
    def func_name(self) -> str:
        if isinstance(self.function, OperandIdentifier):
            return self.function.name
        return self.function

    @property
    def wiring_inputs(self) -> Mapping[str, HandleBinding]:
        return self.inputs

    @property
    def wiring_inouts(
        self,
    ) -> Mapping[
        str, Union[SlicedHandleBinding, SubscriptHandleBinding, HandleBinding]
    ]:
        return self.inouts

    @property
    def wiring_outputs(self) -> Mapping[str, HandleBinding]:
        return self.outputs

    def get_positional_args(self) -> List[ArgValue]:
        result: List[ArgValue] = self.positional_args
        if not result:
            result = list(self.designated_params.values())
            result.extend(self.designated_operands.values())
            result.extend(self.designated_inputs.values())
            result.extend(self.designated_inouts.values())
            result.extend(self.designated_outputs.values())
        return result

    @property
    def positional_params(self) -> Dict[str, Expression]:
        return dict(
            zip(
                self.func_decl.param_decls.keys(),
                (
                    param
                    for param in self.positional_args
                    if isinstance(param, Expression)
                ),
            )
        )

    @property
    def params(self) -> Dict[str, Expression]:
        return self.positional_params or self.designated_params

    @property
    def positional_operands(self) -> Dict[str, "QuantumOperand"]:
        return dict(
            zip(
                self.func_decl.operand_declarations.keys(),
                (
                    param
                    for param in self.positional_args
                    if not isinstance(param, (Expression, HandleBinding))
                ),
            )
        )

    @property
    def operands(self) -> Dict[str, "QuantumOperand"]:
        return self.positional_operands or self.designated_operands

    @property
    def pos_port_args(self) -> Dict[str, HandleBinding]:
        return dict(
            zip(
                self.func_decl.port_declarations.keys(),
                (
                    param
                    for param in self.positional_args
                    if isinstance(param, HandleBinding)
                ),
            )
        )

    def _get_pos_port_args_by_direction(
        self, direction: PortDeclarationDirection
    ) -> Dict[str, HandleBinding]:
        # This is a hack for handles to wires reduction tests,
        # that initialize function definitions or calls not in the scope of a model,
        # so there is no function resolution annotation.
        if self._func_decl is None:
            return dict()
        return {
            port_decl.name: port
            for port_decl, port in zip(
                self.func_decl.port_declarations.values(),
                (
                    param
                    for param in self.positional_args
                    if isinstance(param, HandleBinding)
                ),
            )
            if direction == port_decl.direction
        }

    @property
    def inputs(self) -> Dict[str, HandleBinding]:
        return (
            self._get_pos_port_args_by_direction(PortDeclarationDirection.Input)
            or self.designated_inputs
        )

    @property
    def inouts(
        self,
    ) -> Dict[str, Union[SlicedHandleBinding, SubscriptHandleBinding, HandleBinding]]:
        return (
            self._get_pos_port_args_by_direction(PortDeclarationDirection.Inout)
            or self.designated_inouts
        )

    @property
    def outputs(self) -> Dict[str, HandleBinding]:
        return (
            self._get_pos_port_args_by_direction(PortDeclarationDirection.Output)
            or self.designated_outputs
        )

    @pydantic.root_validator()
    def validate_handles(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        inputs = values.get("designated_inputs", dict())
        outputs = values.get("designated_outputs", dict())
        inouts = values.get("designated_inouts", dict())

        _validate_no_duplicated_ports(inputs, outputs, inouts)
        _validate_no_duplicated_handles(inputs, outputs, inouts)
        _validate_no_mixing_sliced_and_whole_handles(inouts)

        return values
