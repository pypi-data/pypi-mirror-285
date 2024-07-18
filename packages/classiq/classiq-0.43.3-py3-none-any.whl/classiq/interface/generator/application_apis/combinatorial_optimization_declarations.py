from classiq.interface.generator.functions.classical_function_declaration import (
    ClassicalFunctionDeclaration,
)
from classiq.interface.generator.functions.classical_type import (
    ClassicalList,
    Integer,
    Real,
    Struct,
    StructMetaType,
    VQEResult,
)
from classiq.interface.generator.types.struct_declaration import StructDeclaration

COMBINATORIAL_OPTIMIZATION_SOLUTION = StructDeclaration(
    name="CombinatorialOptimizationSolution",
    variables={
        "probability": Real(),
        "cost": Real(),
        "solution": ClassicalList(element_type=Integer()),
        "count": Integer(),
    },
)

OPTIMIZATION_PROBLEM_TO_HAMILTONIAN = ClassicalFunctionDeclaration(
    name="optimization_problem_to_hamiltonian",
    param_decls={
        "problem_type": StructMetaType(),
        "penalty_energy": Real(),
    },
    return_type=ClassicalList(element_type=Struct(name="PauliTerm")),
)

GET_OPTIMIZATION_SOLUTION = ClassicalFunctionDeclaration(
    name="get_optimization_solution",
    param_decls={
        "problem_type": StructMetaType(),
        "vqe_result_handle": VQEResult(),
        "penalty_energy": Real(),
    },
    return_type=ClassicalList(
        element_type=Struct(name="CombinatorialOptimizationSolution")
    ),
)
