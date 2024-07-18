from classiq.interface.generator.functions.builtins.core_library import CORE_LIB_DECLS
from classiq.interface.generator.functions.builtins.open_lib_functions import (
    OPEN_LIB_DECLS,
)
from classiq.interface.generator.functions.builtins.quantum_operators import (
    STD_QMOD_OPERATORS,
)
from classiq.interface.helpers.pydantic_model_helpers import nameables_to_dict
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)

QuantumFunctionDeclaration.BUILTIN_FUNCTION_DECLARATIONS.update(
    nameables_to_dict(STD_QMOD_OPERATORS + CORE_LIB_DECLS + OPEN_LIB_DECLS)
)
