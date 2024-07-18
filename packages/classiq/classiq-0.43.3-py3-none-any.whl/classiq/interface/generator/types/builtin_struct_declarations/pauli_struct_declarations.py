import functools

from classiq.interface.generator.functions.classical_type import (
    ClassicalList,
    Enum,
    Real,
    Struct,
)
from classiq.interface.generator.types.struct_declaration import StructDeclaration
from classiq.interface.helpers.pydantic_model_helpers import nameables_to_dict

PAULI_TERM = StructDeclaration(
    name="PauliTerm",
    variables={
        "pauli": ClassicalList(element_type=Enum(name="Pauli")),
        "coefficient": Real(),
    },
)

Hamiltonian = functools.partial(ClassicalList, element_type=Struct(name="PauliTerm"))

StructDeclaration.BUILTIN_STRUCT_DECLARATIONS.update(nameables_to_dict([PAULI_TERM]))
