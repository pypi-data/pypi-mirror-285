from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import (
    ClassicalList,
    Integer,
    Real,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)

DEFAULT_TARGET_NAME = "target"

H_FUNCTION = QuantumFunctionDeclaration(
    name="H",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


X_FUNCTION = QuantumFunctionDeclaration(
    name="X",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


Y_FUNCTION = QuantumFunctionDeclaration(
    name="Y",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)

Z_FUNCTION = QuantumFunctionDeclaration(
    name="Z",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


I_FUNCTION = QuantumFunctionDeclaration(
    name="I",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


S_FUNCTION = QuantumFunctionDeclaration(
    name="S",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


T_FUNCTION = QuantumFunctionDeclaration(
    name="T",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


SDG_FUNCTION = QuantumFunctionDeclaration(
    name="SDG",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


TDG_FUNCTION = QuantumFunctionDeclaration(
    name="TDG",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


PHASE_FUNCTION = QuantumFunctionDeclaration(
    name="PHASE",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


RX_FUNCTION = QuantumFunctionDeclaration(
    name="RX",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


RY_FUNCTION = QuantumFunctionDeclaration(
    name="RY",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


RZ_FUNCTION = QuantumFunctionDeclaration(
    name="RZ",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)

R_FUNCTION = QuantumFunctionDeclaration(
    name="R",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        ClassicalParameterDeclaration(
            name="phi",
            classical_type=Real(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


RXX_FUNCTION = QuantumFunctionDeclaration(
    name="RXX",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="2"),
        ),
    ],
)


RYY_FUNCTION = QuantumFunctionDeclaration(
    name="RYY",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="2"),
        ),
    ],
)


RZZ_FUNCTION = QuantumFunctionDeclaration(
    name="RZZ",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="2"),
        ),
    ],
)


CH_FUNCTION = QuantumFunctionDeclaration(
    name="CH",
    positional_arg_declarations=[
        PortDeclaration(
            name="control",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


CX_FUNCTION = QuantumFunctionDeclaration(
    name="CX",
    positional_arg_declarations=[
        PortDeclaration(
            name="control",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


CY_FUNCTION = QuantumFunctionDeclaration(
    name="CY",
    positional_arg_declarations=[
        PortDeclaration(
            name="control",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


CZ_FUNCTION = QuantumFunctionDeclaration(
    name="CZ",
    positional_arg_declarations=[
        PortDeclaration(
            name="control",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


CRX_FUNCTION = QuantumFunctionDeclaration(
    name="CRX",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name="control",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


CRY_FUNCTION = QuantumFunctionDeclaration(
    name="CRY",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name="control",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


CRZ_FUNCTION = QuantumFunctionDeclaration(
    name="CRZ",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name="control",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


CPHASE_FUNCTION = QuantumFunctionDeclaration(
    name="CPHASE",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        PortDeclaration(
            name="control",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


SWAP_FUNCTION = QuantumFunctionDeclaration(
    name="SWAP",
    positional_arg_declarations=[
        PortDeclaration(
            name="qbit0",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
        PortDeclaration(
            name="qbit1",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


IDENTITY_FUNCTION = QuantumFunctionDeclaration(
    name="IDENTITY",
    positional_arg_declarations=[
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
        )
    ],
)

UNITARY_FUNCTION = QuantumFunctionDeclaration(
    name="unitary",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="elements",
            classical_type=ClassicalList(
                element_type=ClassicalList(element_type=Real())
            ),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="log(get_field(elements[0], 'len'), 2)"),
        ),
    ],
)


PREPARE_STATE_FUNCTION = QuantumFunctionDeclaration(
    name="prepare_state",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="probabilities",
            classical_type=ClassicalList(element_type=Real()),
        ),
        ClassicalParameterDeclaration(name="bound", classical_type=Real()),
        PortDeclaration(
            name="out",
            direction=PortDeclarationDirection.Output,
            size=Expression(expr="log(get_field(probabilities, 'len'), 2)"),
        ),
    ],
)

PREPARE_AMPLITUDES_FUNCTION = QuantumFunctionDeclaration(
    name="prepare_amplitudes",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="amplitudes",
            classical_type=ClassicalList(element_type=Real()),
        ),
        ClassicalParameterDeclaration(
            name="bound",
            classical_type=Real(),
        ),
        PortDeclaration(
            name="out",
            direction=PortDeclarationDirection.Output,
            size=Expression(expr="log(get_field(amplitudes, 'len'), 2)"),
        ),
    ],
)

ADD_FUNCTION = QuantumFunctionDeclaration(
    name="add",
    positional_arg_declarations=[
        PortDeclaration(
            name="left",
            direction=PortDeclarationDirection.Inout,
        ),
        PortDeclaration(
            name="right",
            direction=PortDeclarationDirection.Inout,
        ),
        PortDeclaration(
            name="result",
            direction=PortDeclarationDirection.Output,
            size=Expression(
                expr="Max(get_field(left, 'len'), get_field(right, 'len')) + 1"
            ),
        ),
    ],
)


MODULAR_ADD_FUNCTION = QuantumFunctionDeclaration(
    name="modular_add",
    positional_arg_declarations=[
        PortDeclaration(
            name="left",
            direction=PortDeclarationDirection.Inout,
        ),
        PortDeclaration(
            name="right",
            direction=PortDeclarationDirection.Inout,
        ),
    ],
)


INTEGER_XOR_FUNCTION = QuantumFunctionDeclaration(
    name="integer_xor",
    positional_arg_declarations=[
        PortDeclaration(
            name="left",
            direction=PortDeclarationDirection.Inout,
        ),
        PortDeclaration(
            name="right",
            direction=PortDeclarationDirection.Inout,
        ),
    ],
)


U_FUNCTION = QuantumFunctionDeclaration(
    name="U",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="theta",
            classical_type=Real(),
        ),
        ClassicalParameterDeclaration(
            name="phi",
            classical_type=Real(),
        ),
        ClassicalParameterDeclaration(
            name="lam",
            classical_type=Real(),
        ),
        ClassicalParameterDeclaration(
            name="gam",
            classical_type=Real(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


CCX_FUNCTION = QuantumFunctionDeclaration(
    name="CCX",
    positional_arg_declarations=[
        PortDeclaration(
            name="control",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="2"),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="1"),
        ),
    ],
)


ALLOCATE_FUNCTION = QuantumFunctionDeclaration(
    name="allocate",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="num_qubits",
            classical_type=Integer(),
        ),
        PortDeclaration(
            name="out",
            direction=PortDeclarationDirection.Output,
            size=Expression(expr="num_qubits"),
        ),
    ],
)


FREE_FUNCTION = QuantumFunctionDeclaration(
    name="free",
    positional_arg_declarations=[
        PortDeclaration(
            name="in",
            direction=PortDeclarationDirection.Input,
        )
    ],
)


RANDOMIZED_BENCHMARKING = QuantumFunctionDeclaration(
    name="randomized_benchmarking",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="num_of_cliffords",
            classical_type=Integer(),
        ),
        PortDeclaration(
            name=DEFAULT_TARGET_NAME,
            direction=PortDeclarationDirection.Inout,
        ),
    ],
)


INPLACE_PREPARE_STATE = QuantumFunctionDeclaration(
    name="inplace_prepare_state",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="probabilities",
            classical_type=ClassicalList(element_type=Real()),
        ),
        ClassicalParameterDeclaration(
            name="bound",
            classical_type=Real(),
        ),
        PortDeclaration(
            name="target",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="log(get_field(probabilities, 'len'), 2)"),
        ),
    ],
)


INPLACE_PREPARE_AMPLITUDES = QuantumFunctionDeclaration(
    name="inplace_prepare_amplitudes",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="amplitudes",
            classical_type=ClassicalList(element_type=Real()),
        ),
        ClassicalParameterDeclaration(
            name="bound",
            classical_type=Real(),
        ),
        PortDeclaration(
            name="target",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="log(get_field(amplitudes, 'len'), 2)"),
        ),
    ],
)


__all__ = [
    "H_FUNCTION",
    "X_FUNCTION",
    "Y_FUNCTION",
    "Z_FUNCTION",
    "I_FUNCTION",
    "S_FUNCTION",
    "T_FUNCTION",
    "SDG_FUNCTION",
    "TDG_FUNCTION",
    "PHASE_FUNCTION",
    "RX_FUNCTION",
    "RY_FUNCTION",
    "RZ_FUNCTION",
    "R_FUNCTION",
    "RXX_FUNCTION",
    "RYY_FUNCTION",
    "RZZ_FUNCTION",
    "CH_FUNCTION",
    "CX_FUNCTION",
    "CY_FUNCTION",
    "CZ_FUNCTION",
    "CRX_FUNCTION",
    "CRY_FUNCTION",
    "CRZ_FUNCTION",
    "CPHASE_FUNCTION",
    "SWAP_FUNCTION",
    "IDENTITY_FUNCTION",
    "PREPARE_STATE_FUNCTION",
    "PREPARE_AMPLITUDES_FUNCTION",
    "UNITARY_FUNCTION",
    "ADD_FUNCTION",
    "MODULAR_ADD_FUNCTION",
    "INTEGER_XOR_FUNCTION",
    "U_FUNCTION",
    "CCX_FUNCTION",
    "ALLOCATE_FUNCTION",
    "FREE_FUNCTION",
    "RANDOMIZED_BENCHMARKING",
    "INPLACE_PREPARE_STATE",
    "INPLACE_PREPARE_AMPLITUDES",
]
