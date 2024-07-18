from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Mapping,
    Sequence,
    Set,
    Type,
    Union,
)

import pydantic
from typing_extensions import Annotated

from classiq.interface.generator.function_params import ArithmeticIODict, PortDirection
from classiq.interface.generator.functions.function_declaration import (
    FunctionDeclaration,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.helpers.pydantic_model_helpers import (
    Nameable,
    values_with_discriminator,
)
from classiq.interface.helpers.validation_helpers import (
    validate_nameables_mapping,
    validate_nameables_no_overlap,
)
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_type import quantum_var_to_register

from classiq.exceptions import ClassiqValueError


def _is_equiv_kw_and_pos_decl(kw_decl: Nameable, pos_decl: Nameable) -> bool:
    if isinstance(pos_decl, ClassicalParameterDeclaration):
        return pos_decl.classical_type == kw_decl
    return pos_decl == kw_decl


def _populate_declaration_dicts_with_positional_lists(
    pos_decls: Sequence[Nameable],
    kw_decls: Dict[str, Nameable],
    param_type: Type[Nameable],
) -> None:
    for pos_decl in pos_decls:
        if not isinstance(pos_decl, param_type):
            continue
        kw_decl = kw_decls.get(pos_decl.name)
        if kw_decl is not None and not _is_equiv_kw_and_pos_decl(kw_decl, pos_decl):
            raise ClassiqValueError(
                f"{param_type.__name__} parameter with name {pos_decl.name} already declared"
            )
        kw_decls[pos_decl.name] = (
            pos_decl.classical_type  # type:ignore[assignment]
            if isinstance(pos_decl, ClassicalParameterDeclaration)
            else pos_decl
        )


PositionalArg = Annotated[
    Union[ClassicalParameterDeclaration, "QuantumOperandDeclaration", PortDeclaration],
    pydantic.Field(..., discriminator="kind"),
]


def _ports_to_registers(
    port_declarations: Dict[str, PortDeclaration], direction: PortDirection
) -> ArithmeticIODict:
    return {
        name: quantum_var_to_register(name, port_decl.quantum_type)
        for name, port_decl in port_declarations.items()
        if port_decl.direction.includes_port_direction(direction)
    }


class QuantumFunctionDeclaration(FunctionDeclaration):
    """
    Facilitates the creation of a common quantum function interface object.
    """

    port_declarations: Dict[str, PortDeclaration] = pydantic.Field(
        description="The input and output ports of the function.",
        default_factory=dict,
    )

    operand_declarations: Mapping[str, "QuantumOperandDeclaration"] = pydantic.Field(
        description="The expected interface of the quantum function operands",
        default_factory=dict,
    )

    positional_arg_declarations: List[PositionalArg] = pydantic.Field(
        default_factory=list
    )

    BUILTIN_FUNCTION_DECLARATIONS: ClassVar[Dict[str, "QuantumFunctionDeclaration"]] = (
        {}
    )

    @property
    def input_set(self) -> Set[str]:
        return set(self.inputs.keys())

    @property
    def output_set(self) -> Set[str]:
        return set(self.outputs.keys())

    @property
    def inputs(self) -> ArithmeticIODict:
        return _ports_to_registers(self.port_declarations, PortDirection.Input)

    @property
    def outputs(self) -> ArithmeticIODict:
        return _ports_to_registers(self.port_declarations, PortDirection.Output)

    def update_logic_flow(
        self, function_dict: Mapping[str, "QuantumFunctionDeclaration"]
    ) -> None:
        pass

    @property
    def port_names(self) -> List[str]:
        return list(self.port_declarations.keys())

    @property
    def operand_names(self) -> List[str]:
        return list(self.operand_declarations.keys())

    def ports_by_direction(
        self, direction: PortDirection
    ) -> Mapping[str, PortDeclaration]:
        return {
            name: port
            for name, port in self.port_declarations.items()
            if port.direction.includes_port_direction(direction)
        }

    def ports_by_declaration_direction(
        self, direction: PortDeclarationDirection
    ) -> Set[str]:
        return {
            name
            for name, port in self.port_declarations.items()
            if port.direction == direction
        }

    def get_positional_arg_decls(self) -> List[PositionalArg]:
        result: List[PositionalArg] = self.positional_arg_declarations
        if not result:
            result = [
                ClassicalParameterDeclaration(name=name, classical_type=ctype)
                for name, ctype in self.param_decls.items()
            ]
            result.extend(self.operand_declarations.values())
            result.extend(self.port_declarations.values())
        return result

    @pydantic.validator("operand_declarations")
    def _validate_operand_declarations_names(
        cls, operand_declarations: Dict[str, "QuantumOperandDeclaration"]
    ) -> Dict[str, "QuantumOperandDeclaration"]:
        validate_nameables_mapping(operand_declarations, "Operand")
        return operand_declarations

    @pydantic.validator("port_declarations")
    def _validate_port_declarations_names(
        cls, port_declarations: Dict[str, PortDeclaration]
    ) -> Dict[str, PortDeclaration]:
        validate_nameables_mapping(port_declarations, "Port")
        return port_declarations

    @pydantic.root_validator()
    def _validate_params_and_operands_uniqueness(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        operand_declarations = values.get("operand_declarations")
        parameter_declarations = values.get("param_decls")
        port_declarations = values.get("port_declarations")
        operand_parameter = validate_nameables_no_overlap(
            operand_declarations, parameter_declarations, "operand", "parameter"
        )
        operand_port = validate_nameables_no_overlap(
            operand_declarations, port_declarations, "operand", "port"
        )
        parameter_port = validate_nameables_no_overlap(
            parameter_declarations, port_declarations, "parameter", "port"
        )
        error_message = ",".join(
            msg
            for msg in [operand_parameter, operand_port, parameter_port]
            if msg is not None
        )

        if error_message:
            raise ClassiqValueError(error_message)

        return values

    @pydantic.root_validator()
    def _reduce_positional_declarations_to_keyword(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        operand_declarations = values.get("operand_declarations", dict())
        parameter_declarations = values.get("param_decls", dict())
        port_declarations = values.get("port_declarations", dict())

        positional_arg_declarations = values.get("positional_arg_declarations", list())

        _populate_declaration_dicts_with_positional_lists(
            positional_arg_declarations,
            parameter_declarations,
            ClassicalParameterDeclaration,
        )
        _populate_declaration_dicts_with_positional_lists(
            positional_arg_declarations,
            operand_declarations,
            QuantumOperandDeclaration,
        )
        _populate_declaration_dicts_with_positional_lists(
            positional_arg_declarations, port_declarations, PortDeclaration
        )

        values["operand_declarations"] = operand_declarations
        values["param_decls"] = parameter_declarations
        values["port_declarations"] = port_declarations

        return values


class QuantumOperandDeclaration(QuantumFunctionDeclaration):
    kind: Literal["QuantumOperandDeclaration"]

    is_list: bool = pydantic.Field(
        description="Indicate whether the operand expects an unnamed list of lambdas",
        default=False,
    )

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "QuantumOperandDeclaration")


QuantumFunctionDeclaration.update_forward_refs()
