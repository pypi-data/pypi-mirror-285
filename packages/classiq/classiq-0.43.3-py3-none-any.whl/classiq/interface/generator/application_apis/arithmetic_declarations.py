from classiq.interface.generator.functions.classical_function_declaration import (
    ClassicalFunctionDeclaration,
)
from classiq.interface.generator.functions.classical_type import Integer, Real

qft_const_adder_phase = ClassicalFunctionDeclaration(
    name="qft_const_adder_phase",
    param_decls={
        "bit_index": Integer(),
        "value": Integer(),
        "reg_len": Integer(),
    },
    return_type=Real(),
)
