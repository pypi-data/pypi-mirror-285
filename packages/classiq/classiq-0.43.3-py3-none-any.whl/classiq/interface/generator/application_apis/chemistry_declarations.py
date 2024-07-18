import functools
from enum import Enum

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_function_declaration import (
    ClassicalFunctionDeclaration,
)
from classiq.interface.generator.functions.classical_type import (
    Bool,
    ClassicalList,
    Integer,
    Real,
    Struct,
    TypeName,
    VQEResult,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.types.struct_declaration import StructDeclaration
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)

MOLECULE_PROBLEM_PARAM = {"molecule_problem": Struct(name="MoleculeProblem")}
MOLECULE_PROBLEM_SIZE = "get_field(get_field(molecule_problem_to_hamiltonian(molecule_problem)[0], 'pauli'), 'len')"
MOLECULE_PROBLEM_PORT = {
    "qbv": PortDeclaration(
        name="qbv",
        direction=PortDeclarationDirection.Inout,
        size=Expression(
            expr=MOLECULE_PROBLEM_SIZE,
        ),
    )
}

FOCK_HAMILTONIAN_PROBLEM_PARAM = {
    "fock_hamiltonian_problem": Struct(name="FockHamiltonianProblem")
}
FOCK_HAMILTONIAN_SIZE = "get_field(get_field(fock_hamiltonian_problem_to_hamiltonian(fock_hamiltonian_problem)[0], 'pauli'), 'len')"

FOCK_HAMILTONIAN_PROBLEM_PORT = {
    "qbv": PortDeclaration(
        name="qbv",
        direction=PortDeclarationDirection.Inout,
        size=Expression(expr=FOCK_HAMILTONIAN_SIZE),
    )
}


class ChemistryProblemType(Enum):
    MoleculeProblem = "molecule_problem"
    FockHamiltonianProblem = "fock_hamiltonian_problem"


MOLECULE_UCC_ANSATZ = QuantumFunctionDeclaration(
    name="molecule_ucc",
    param_decls={
        **MOLECULE_PROBLEM_PARAM,
        "excitations": ClassicalList(element_type=Integer()),
    },
    port_declarations=MOLECULE_PROBLEM_PORT,
)


MOLECULE_HVA_ANSATZ = QuantumFunctionDeclaration(
    name="molecule_hva",
    param_decls={
        **MOLECULE_PROBLEM_PARAM,
        "reps": Integer(),
    },
    port_declarations=MOLECULE_PROBLEM_PORT,
)


MOLECULE_HARTREE_FOCK = QuantumFunctionDeclaration(
    name="molecule_hartree_fock",
    param_decls={
        **MOLECULE_PROBLEM_PARAM,
    },
    port_declarations=MOLECULE_PROBLEM_PORT,
)


FOCK_HAMILTONIAN_UCC_ANSATZ = QuantumFunctionDeclaration(
    name="fock_hamiltonian_ucc",
    param_decls={
        **FOCK_HAMILTONIAN_PROBLEM_PARAM,
        "excitations": ClassicalList(element_type=Integer()),
    },
    port_declarations=FOCK_HAMILTONIAN_PROBLEM_PORT,
)

FOCK_HAMILTONIAN_HVA_ANSATZ = QuantumFunctionDeclaration(
    name="fock_hamiltonian_hva",
    param_decls={
        **FOCK_HAMILTONIAN_PROBLEM_PARAM,
        "reps": Integer(),
    },
    port_declarations=FOCK_HAMILTONIAN_PROBLEM_PORT,
)

FOCK_HAMILTONIAN_HARTREE_FOCK = QuantumFunctionDeclaration(
    name="fock_hamiltonian_hartree_fock",
    param_decls={
        **FOCK_HAMILTONIAN_PROBLEM_PARAM,
    },
    port_declarations=FOCK_HAMILTONIAN_PROBLEM_PORT,
)


MOLECULE_PROBLEM = StructDeclaration(
    name="MoleculeProblem",
    variables={
        "mapping": Integer(),
        "z2_symmetries": Bool(),
        # A negative number of qubits is considered None
        # basis: str = pydantic.Field(default="sto3g", description="Molecular basis set")
        "molecule": Struct(name="Molecule"),
        "freeze_core": Bool(),
        "remove_orbitals": ClassicalList(element_type=Integer()),
    },
)

MOLECULE = StructDeclaration(
    name="Molecule",
    variables={
        "atoms": ClassicalList(element_type=Struct(name="ChemistryAtom")),
        "spin": Integer(),
        "charge": Integer(),
    },
)

CHEMISTRY_ATOM = StructDeclaration(
    name="ChemistryAtom",
    variables={
        "element": Integer(),
        "position": Struct(name="Position"),
    },
)

POSITION = StructDeclaration(
    name="Position", variables={"x": Real(), "y": Real(), "z": Real()}
)

FockHamiltonian = functools.partial(
    ClassicalList, element_type=Struct(name="LadderTerm")
)

FOCK_HAMILTONIAN_PROBLEM = StructDeclaration(
    name="FockHamiltonianProblem",
    variables={
        "mapping": Integer(),
        "z2_symmetries": Bool(),
        "terms": FockHamiltonian(),
        "num_particles": ClassicalList(element_type=Integer()),
    },
)

LADDER_TERM = StructDeclaration(
    name="LadderTerm",
    variables={
        "coefficient": Real(),
        "ops": ClassicalList(element_type=Struct(name="LadderOp")),
    },
)

LADDER_OP = StructDeclaration(
    name="LadderOp",
    variables={
        "op": TypeName(name="LadderOperator"),
        "index": Integer(),
    },
)

MOLECULE_RESULT = StructDeclaration(
    name="MoleculeResult",
    variables={
        "energy": Real(),
        "nuclear_repulsion_energy": Real(),
        "total_energy": Real(),
        "hartree_fock_energy": Real(),
        "vqe_result": VQEResult(),
    },
)

MOLECULE_PROBLEM_TO_HAMILTONIAN = ClassicalFunctionDeclaration(
    name="molecule_problem_to_hamiltonian",
    param_decls={"problem": Struct(name="MoleculeProblem")},
    return_type=ClassicalList(element_type=Struct(name="PauliTerm")),
)

FOCK_HAMILTONIAN_PROBLEM_TO_HAMILTONIAN = ClassicalFunctionDeclaration(
    name="fock_hamiltonian_problem_to_hamiltonian",
    param_decls={"problem": Struct(name="FockHamiltonianProblem")},
    return_type=ClassicalList(element_type=Struct(name="PauliTerm")),
)


MOLECULE_GROUND_STATE_SOLUTION_POST_PROCESS = ClassicalFunctionDeclaration(
    name="molecule_ground_state_solution_post_process",
    param_decls={"problem": Struct(name="MoleculeProblem"), "vqe_result": VQEResult()},
    return_type=Struct(name="MoleculeResult"),
)

__all__ = [
    "MOLECULE_UCC_ANSATZ",
    "MOLECULE_HVA_ANSATZ",
    "MOLECULE_HARTREE_FOCK",
    "FOCK_HAMILTONIAN_UCC_ANSATZ",
    "FOCK_HAMILTONIAN_HVA_ANSATZ",
    "FOCK_HAMILTONIAN_HARTREE_FOCK",
    "MOLECULE_PROBLEM",
    "MOLECULE",
    "CHEMISTRY_ATOM",
    "POSITION",
    "FOCK_HAMILTONIAN_PROBLEM",
    "LADDER_TERM",
    "LADDER_OP",
    "MOLECULE_PROBLEM_TO_HAMILTONIAN",
    "FOCK_HAMILTONIAN_PROBLEM_TO_HAMILTONIAN",
    "MOLECULE_GROUND_STATE_SOLUTION_POST_PROCESS",
    "MOLECULE_RESULT",
]
