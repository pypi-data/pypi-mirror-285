from typing import Dict, List, Optional, Tuple

import black

from classiq.interface.generator.constant import Constant
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import (
    ClassicalArray,
    ConcreteClassicalType,
    TypeName,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.types.enum_declaration import EnumDeclaration
from classiq.interface.generator.visitor import NodeType, Visitor
from classiq.interface.model.bind_operation import BindOperation
from classiq.interface.model.classical_if import ClassicalIf
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.control import Control
from classiq.interface.model.handle_binding import (
    HandleBinding,
    SlicedHandleBinding,
    SubscriptHandleBinding,
)
from classiq.interface.model.inplace_binary_operation import InplaceBinaryOperation
from classiq.interface.model.invert import Invert
from classiq.interface.model.model import Model
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.power import Power
from classiq.interface.model.quantum_expressions.amplitude_loading_operation import (
    AmplitudeLoadingOperation,
)
from classiq.interface.model.quantum_expressions.arithmetic_operation import (
    ArithmeticOperation,
)
from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumAssignmentOperation,
)
from classiq.interface.model.quantum_function_call import (
    OperandIdentifier,
    QuantumFunctionCall,
)
from classiq.interface.model.quantum_function_declaration import (
    PositionalArg,
    QuantumFunctionDeclaration,
    QuantumOperandDeclaration,
)
from classiq.interface.model.quantum_lambda_function import QuantumLambdaFunction
from classiq.interface.model.quantum_type import (
    QuantumBit,
    QuantumBitvector,
    QuantumNumeric,
)
from classiq.interface.model.quantum_variable_declaration import (
    QuantumVariableDeclaration,
)
from classiq.interface.model.repeat import Repeat
from classiq.interface.model.statement_block import StatementBlock
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)
from classiq.interface.model.within_apply_operation import WithinApply

import classiq
from classiq import Bool, ClassicalList, Integer, Real, StructDeclaration
from classiq.qmod.pretty_print.expression_to_python import transform_expression
from classiq.qmod.utilities import DEFAULT_DECIMAL_PRECISION


class VariableDeclarationAssignment(Visitor):
    def __init__(self, pretty_printer: "PythonPrettyPrinter") -> None:
        self.pretty_printer = pretty_printer

    def visit(self, node: NodeType) -> Tuple[str, Optional[List[str]]]:
        res = super().visit(node)
        if not isinstance(res, tuple):
            raise AssertionError(f"Pretty printing for {type(node)} is not supported ")
        return res  # type: ignore[return-value]

    def visit_QuantumBit(self, qtype: QuantumBit) -> Tuple[str, Optional[List[str]]]:
        return "QBit", None

    def visit_QuantumBitvector(
        self, qtype: QuantumBitvector
    ) -> Tuple[str, Optional[List[str]]]:
        if qtype.length is not None:
            return "QArray", ["QBit", self.pretty_printer.visit(qtype.length)]
        return "QArray", ["QBit"]

    def visit_QuantumNumeric(
        self, qtype: QuantumNumeric
    ) -> Tuple[str, Optional[List[str]]]:
        params = []
        if qtype.size is not None:
            assert qtype.is_signed is not None
            assert qtype.fraction_digits is not None

            params = [
                self.pretty_printer.visit(param)
                for param in [qtype.size, qtype.is_signed, qtype.fraction_digits]
            ]

        return "QNum", params


class PythonPrettyPrinter(Visitor):
    def __init__(self, decimal_precision: int = DEFAULT_DECIMAL_PRECISION) -> None:
        self._level = 0
        self._decimal_precision = decimal_precision
        self._imports = {"qfunc": 1}
        self._import_enum = False
        self._import_dataclass = False
        self._symbolic_imports: Dict[str, int] = dict()
        self._functions: Optional[Dict[str, QuantumFunctionDeclaration]] = None

    def visit(self, node: NodeType) -> str:
        res = super().visit(node)
        if not isinstance(res, str):
            raise AssertionError(f"Pretty printing for {type(node)} is not supported ")
        return res

    def visit_Model(self, model: Model) -> str:
        self._functions = {
            **model.function_dict,
            **QuantumFunctionDeclaration.BUILTIN_FUNCTION_DECLARATIONS,
        }
        enum_decls = [self.visit(decl) for decl in model.enums]
        struct_decls = [self.visit(decl) for decl in model.types]
        func_defs = [self.visit(func) for func in model.functions]
        constants = [self.visit(const) for const in model.constants]
        classical_code = self.format_classical_code(model.classical_execution_code)

        code = f"{self.format_imports()}\n\n{self.join_code_parts(*constants, *enum_decls, *struct_decls, *func_defs, classical_code)}"
        return black.format_str(code, mode=black.FileMode())

    def format_classical_code(self, code: str) -> str:
        if not code:
            return ""
        self._imports["cfunc"] = 1
        self.check_execution_primitives(code)
        formatted_code = code.replace("\n", "\n" + self._indent + "    ")
        return f"{self._indent}@cfunc\n{self._indent}def cmain() -> None:\n{self._indent}    {formatted_code}"

    def check_execution_primitives(self, code: str) -> None:
        for primitive in dir(classiq.qmod.builtins.classical_execution_primitives):
            if primitive + "(" in code:
                self._imports[primitive] = 1

    def format_imports(self) -> str:
        imports = f"from classiq import {', '.join(self._imports.keys())}\n"
        symbolic_imports = (
            f"from classiq.qmod.symbolic import {', '.join(self._symbolic_imports.keys())}\n"
            if self._symbolic_imports
            else ""
        )
        return self.special_imports + imports + symbolic_imports

    @property
    def special_imports(self) -> str:
        imports = ""
        if self._import_dataclass:
            imports += "from dataclasses import dataclass\n"
        if self._import_enum:
            imports += "from enum import IntEnum\n"
        return imports

    def join_code_parts(self, *code_parts: str) -> str:
        return "\n".join(code_parts)

    def visit_Constant(self, constant: Constant) -> str:
        self._imports["QConstant"] = 1
        constant_name = self.visit(constant.name)
        return f'{self._indent}{constant_name} = QConstant("{constant_name}", {self.visit(constant.const_type)}, {self.visit(constant.value)})\n'

    def _visit_arg_decls(self, func_def: QuantumFunctionDeclaration) -> str:
        return ", ".join(
            self.visit(arg_decl) for arg_decl in func_def.get_positional_arg_decls()
        )

    def visit_QuantumFunctionDeclaration(
        self, func_decl: QuantumFunctionDeclaration
    ) -> str:
        return (
            f"@qfunc\ndef {func_decl.name}({self._visit_arg_decls(func_decl)}) -> None:"
        )

    def visit_EnumDeclaration(self, enum_decl: EnumDeclaration) -> str:
        self._import_enum = True
        return f"class {enum_decl.name}(IntEnum):\n{self._visit_members(enum_decl.members)}\n"

    def _visit_members(self, members: Dict[str, int]) -> str:
        self._level += 1
        members_str = "".join(
            f"{self._indent}{self.visit(member_name)} = {member_value}\n"
            for member_name, member_value in members.items()
        )
        self._level -= 1
        return members_str

    def visit_StructDeclaration(self, struct_decl: StructDeclaration) -> str:
        self._import_dataclass = True
        return f"@dataclass\nclass {struct_decl.name}:\n{self._visit_variables(struct_decl.variables)}\n"

    def _visit_variables(self, variables: Dict[str, ConcreteClassicalType]) -> str:
        self._level += 1
        variables_str = "".join(
            f"{self._indent}{self.visit(field_name)}: {self.visit(var_decl)};\n"
            for field_name, var_decl in variables.items()
        )
        self._level -= 1
        return variables_str

    def visit_QuantumVariableDeclaration(
        self, var_decl: QuantumVariableDeclaration
    ) -> str:
        return f"{var_decl.name}: {self.visit(var_decl.quantum_type)}"

    def visit_PortDeclaration(self, port_decl: PortDeclaration) -> str:
        var = self.visit_QuantumVariableDeclaration(port_decl)
        var_name, var_type = var.split(": ")
        for direction in PortDeclarationDirection:
            if port_decl.direction == PortDeclarationDirection.Inout:
                return var
            if port_decl.direction == direction:
                direction_identifier = direction.name
                self._imports[direction_identifier] = 1
                return f"{var_name}: {direction_identifier}[{var_type}]"
        raise RuntimeError("Should not reach here")

    def visit_QuantumBit(self, qtype: QuantumBit) -> str:
        self._imports["QBit"] = 1
        return "QBit"

    def visit_QuantumBitvector(self, qtype: QuantumBitvector) -> str:
        self._imports.update({"QArray": 1, "QBit": 1})
        element_type = self.visit(qtype.element_type)
        if qtype.length is not None:
            return f"QArray[{element_type}, {_add_quotes(self.visit(qtype.length))}]"
        return f"QArray[{element_type}]"

    def visit_QuantumNumeric(self, qtype: QuantumNumeric) -> str:
        params = ""
        self._imports["QNum"] = 1
        if qtype.size is not None:
            assert qtype.is_signed is not None
            assert qtype.fraction_digits is not None

            params = "[{}]".format(
                ", ".join(
                    _add_quotes(self.visit(param))
                    for param in [qtype.size, qtype.is_signed, qtype.fraction_digits]
                )
            )

        return f"QNum{params}"

    def visit_ClassicalParameterDeclaration(
        self, cparam: ClassicalParameterDeclaration
    ) -> str:
        return f"{cparam.name}: {self.visit(cparam.classical_type)}"

    def visit_Integer(self, ctint: Integer) -> str:
        self._imports["CInt"] = 1
        return "CInt"

    def visit_Real(self, ctint: Real) -> str:
        self._imports["CReal"] = 1
        return "CReal"

    def visit_Bool(self, ctbool: Bool) -> str:
        self._imports["CBool"] = 1
        return "CBool"

    def visit_ClassicalList(self, ctlist: ClassicalList) -> str:
        self._imports["CArray"] = 1
        return f"CArray[{self.visit(ctlist.element_type)}]"

    def visit_ClassicalArray(self, ctarray: ClassicalArray) -> str:
        self._imports["CArray"] = 1
        return f"CArray[{self.visit(ctarray.element_type)}, {ctarray.size}]"

    def visit_TypeName(self, type_: TypeName) -> str:
        if type_.name in dir(classiq.qmod.builtins.enums) + dir(
            classiq.qmod.builtins.structs
        ):
            self._imports[type_.name] = 1
        return type_.name

    def visit_VariableDeclarationStatement(
        self, local_decl: VariableDeclarationStatement
    ) -> str:
        type_name, params = VariableDeclarationAssignment(self).visit(
            local_decl.quantum_type
        )
        self._imports[type_name] = 1
        params = [f'"{local_decl.name}"'] + (params or [])
        param_args = ", ".join(params)
        return f"{self._indent}{self.visit_QuantumVariableDeclaration(local_decl)} = {type_name}({param_args})\n"

    def _visit_operand_arg_decl(self, arg_decl: PositionalArg) -> str:
        if isinstance(arg_decl, QuantumVariableDeclaration):
            return self.visit(arg_decl.quantum_type)
        if isinstance(arg_decl, ClassicalParameterDeclaration):
            return self.visit(arg_decl.classical_type)
        if isinstance(arg_decl, QuantumOperandDeclaration):
            return self.visit_QuantumOperandDeclaration(arg_decl)

    def visit_QuantumOperandDeclaration(
        self, op_decl: QuantumOperandDeclaration
    ) -> str:
        qcallable_identifier = "QCallable"
        if op_decl.is_list:
            qcallable_identifier = "QCallableList"
        self._imports[qcallable_identifier] = 1
        args = ", ".join(
            self._visit_operand_arg_decl(arg_decl)
            for arg_decl in op_decl.get_positional_arg_decls()
        )

        return f"{op_decl.name}: {qcallable_identifier}" + (f"[{args}]" if args else "")

    def visit_NativeFunctionDefinition(self, func_def: NativeFunctionDefinition) -> str:
        self._level += 1
        body = "".join(self.visit(statement) for statement in func_def.body)
        self._level -= 1
        return f"{self.visit_QuantumFunctionDeclaration(func_def)} \n{body}\n"

    def visit_QuantumFunctionCall(self, func_call: QuantumFunctionCall) -> str:
        if len(func_call.get_positional_args()) <= 2 or self._functions is None:
            args = ", ".join(self.visit(arg) for arg in func_call.get_positional_args())
        else:
            func_decl = self._functions[func_call.func_name]
            args = ", ".join(
                f"{self.visit(arg_decl.name)}={self.visit(arg)}"
                for arg_decl, arg in zip(
                    func_decl.get_positional_arg_decls(),
                    func_call.get_positional_args(),
                )
            )
        if func_call.func_name in dir(classiq.qmod.builtins.functions):
            self._imports[func_call.func_name] = 1
        return f"{self._indent}{func_call.func_name}{f'[{self.visit(func_call.function.index)}]' if isinstance(func_call.function, OperandIdentifier) else ''}({args})\n"

    def visit_Control(self, op: Control) -> str:
        self._imports["control"] = 1
        return f"{self._indent}control({self.visit(op.expression)}, {self._visit_body(op.body)})\n"

    def visit_ClassicalIf(self, op: ClassicalIf) -> str:
        self._imports["if_"] = 1
        return f"{self._indent}if_(condition={self.visit(op.condition)}, then={self._visit_body(op.then)}, else_={self._visit_body(op.else_)})\n"

    def visit_WithinApply(self, op: WithinApply) -> str:
        self._imports["within_apply"] = 1
        return f"{self._indent}within_apply({self._visit_body(op.compute)}, {self._visit_body(op.action)})\n"

    def visit_Repeat(self, repeat: Repeat) -> str:
        self._imports["repeat"] = 1
        return f"{self._indent}repeat({self.visit(repeat.count)}, {self._visit_body(repeat.body, [repeat.iter_var])})\n"

    def visit_Power(self, power: Power) -> str:
        self._imports["power"] = 1
        return f"{self._indent}power({self.visit(power.power)}, {self._visit_body(power.body)})\n"

    def visit_Invert(self, invert: Invert) -> str:
        self._imports["invert"] = 1
        return f"{self._indent}invert({self._visit_body(invert.body)})\n"

    def _visit_body(
        self, body: StatementBlock, operand_arguments: Optional[List[str]] = None
    ) -> str:
        if len(body) == 0:
            return "None"
        argument_string = (
            (" " + ", ".join(operand_arguments)) if operand_arguments else ""
        )
        code = f"lambda{argument_string}: {'[' if len(body) > 1 else ''}\n"
        self._level += 1
        for i, statement in enumerate(body):
            if isinstance(
                statement, (QuantumAssignmentOperation, VariableDeclarationStatement)
            ):
                raise AssertionError(
                    "pretty printing quantum assignment operations or variable declaration statements in quantum lambda function is unsupported."
                )
            code += self.visit(statement)
            if i < len(body) - 1:
                code += ","
        self._level -= 1
        return f"{code}{']' if len(body) > 1 else ''}"

    def visit_InplaceBinaryOperation(self, op: InplaceBinaryOperation) -> str:
        self._imports[op.operation.value] = 1
        return f"{self._indent}{op.operation.value}({self.visit(op.value)}, {self.visit(op.target)})\n"

    def visit_Expression(self, expr: Expression) -> str:
        return transform_expression(
            expr.expr,
            level=self._level,
            decimal_precision=self._decimal_precision,
            imports=self._imports,
            symbolic_imports=self._symbolic_imports,
        )

    def visit_QuantumLambdaFunction(self, qlambda: QuantumLambdaFunction) -> str:
        assert qlambda.func_decl is not None
        return self._visit_body(
            qlambda.body,
            list(qlambda.rename_params.values()),
        )

    def visit_HandleBinding(self, var_ref: HandleBinding) -> str:
        return var_ref.name

    def visit_SlicedHandleBinding(self, var_ref: SlicedHandleBinding) -> str:
        return f"{var_ref.name}[{self.visit(var_ref.start)}:{self.visit(var_ref.end)}]"

    def visit_SubscriptHandleBinding(self, var_ref: SubscriptHandleBinding) -> str:
        return f"{var_ref.name}[{self.visit(var_ref.index)}]"

    def visit_ArithmeticOperation(self, arith_op: ArithmeticOperation) -> str:
        op = "^=" if arith_op.inplace_result else "|="
        return f"{self._indent}{self.visit(arith_op.result_var)} {op} {self.visit(arith_op.expression)}\n"

    def visit_AmplitudeLoadingOperation(
        self, amplitude_loading_op: AmplitudeLoadingOperation
    ) -> str:
        return f"{self._indent}{self.visit(amplitude_loading_op.result_var)} *= {self.visit(amplitude_loading_op.expression)}\n"

    def _print_bind_handles(self, handles: List[HandleBinding]) -> str:
        if len(handles) == 1:
            return self.visit(handles[0])

        return "[" + ", ".join(self.visit(handle) for handle in handles) + "]"

    def visit_BindOperation(self, bind_op: BindOperation) -> str:
        self._imports["bind"] = 1
        return f"{self._indent}bind({self._print_bind_handles(bind_op.in_handles)}, {self._print_bind_handles(bind_op.out_handles)})\n"

    def visit_list(self, node: list) -> str:
        return "[" + ", ".join(self.visit(elem) for elem in node) + "]"

    @property
    def _indent(self) -> str:
        return "    " * self._level


def _add_quotes(exp: str) -> str:
    if exp.lower() == "true" or exp.lower() == "false" or _convertible_to_number(exp):
        return exp

    return f'"{exp}"'


def _convertible_to_number(exp: str) -> bool:
    for number_type in [int, float]:
        try:
            number_type(exp)
        except ValueError:
            pass
        else:
            return True
    return False
