from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import (
    ClassicalList,
    Enum,
    Integer,
    Real,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.types.builtin_struct_declarations.pauli_struct_declarations import (
    Hamiltonian,
)
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)

SINGLE_PAULI_EXPONENT_FUNCTION = QuantumFunctionDeclaration(
    name="single_pauli_exponent",
    param_decls={
        "pauli_string": ClassicalList(element_type=Enum(name="Pauli")),
        "coefficient": Real(),
    },
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="get_field(pauli_string, 'len')"),
        )
    },
)


SUZUKI_TROTTER_FUNCTION = QuantumFunctionDeclaration(
    name="suzuki_trotter",
    param_decls={
        "pauli_operator": Hamiltonian(),
        "evolution_coefficient": Real(),
        "order": Integer(),
        "repetitions": Integer(),
    },
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(
                expr="get_field(get_field(pauli_operator[0], 'pauli'), 'len')"
            ),
        )
    },
)

QDRIFT_FUNCTION = QuantumFunctionDeclaration(
    name="qdrift",
    param_decls={
        "pauli_operator": Hamiltonian(),
        "evolution_coefficient": Real(),
        "num_qdrift": Integer(),
    },
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(
                expr="get_field(get_field(pauli_operator[0], 'pauli'), 'len')"
            ),
        )
    },
)

EXPONENTIATION_WITH_DEPTH_CONSTRAINT = QuantumFunctionDeclaration(
    name="exponentiation_with_depth_constraint",
    param_decls={
        "pauli_operator": Hamiltonian(),
        "evolution_coefficient": Real(),
        "max_depth": Integer(),
    },
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(
                expr="get_field(get_field(pauli_operator[0], 'pauli'), 'len')"
            ),
        )
    },
)

__all__ = [
    "SINGLE_PAULI_EXPONENT_FUNCTION",
    "SUZUKI_TROTTER_FUNCTION",
    "QDRIFT_FUNCTION",
    "EXPONENTIATION_WITH_DEPTH_CONSTRAINT",
]
