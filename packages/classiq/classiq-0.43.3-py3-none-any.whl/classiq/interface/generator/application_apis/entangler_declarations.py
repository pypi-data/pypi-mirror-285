from classiq.interface.generator.functions.classical_function_declaration import (
    ClassicalFunctionDeclaration,
)
from classiq.interface.generator.functions.classical_type import (
    Bool,
    ClassicalList,
    Integer,
)

GRID_ENTANGLER_GRAPH = ClassicalFunctionDeclaration(
    name="grid_entangler_graph",
    param_decls={
        "num_qubits": Integer(),
        "schmidt_rank": Integer(),
        "grid_randomization": Bool(),
    },
    return_type=ClassicalList(element_type=ClassicalList(element_type=Integer())),
)

HYPERCUBE_ENTANGLER_GRAPH = ClassicalFunctionDeclaration(
    name="hypercube_entangler_graph",
    param_decls={"num_qubits": Integer()},
    return_type=ClassicalList(element_type=ClassicalList(element_type=Integer())),
)
