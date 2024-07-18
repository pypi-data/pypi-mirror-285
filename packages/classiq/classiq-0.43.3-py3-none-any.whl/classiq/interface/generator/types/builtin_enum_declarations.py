from classiq.interface.chemistry.elements import ELEMENTS
from classiq.interface.chemistry.ground_state_problem import FermionMapping
from classiq.interface.generator.types.enum_declaration import EnumDeclaration

ELEMENT = EnumDeclaration(
    name="Element", members={element: idx for idx, element in enumerate(ELEMENTS)}
)

FERMION_MAPPING = EnumDeclaration(
    name="FermionMapping",
    members={
        mapping.name: idx  # type:ignore[attr-defined]
        for idx, mapping in enumerate(FermionMapping)
    },
)

FINANCE_FUNCTION_TYPE = EnumDeclaration(
    name="FinanceFunctionType",
    members={
        "VAR": 0,
        "SHORTFALL": 1,
        "X_SQUARE": 2,
        "EUROPEAN_CALL_OPTION": 3,
    },
)

LADDER_OPERATOR = EnumDeclaration(
    name="LadderOperator",
    members={
        "PLUS": 0,
        "MINUS": 1,
    },
)

OPTIMIZER = EnumDeclaration(
    name="Optimizer",
    members={
        "COBYLA": 1,
        "SPSA": 2,
        "L_BFGS_B": 3,
        "NELDER_MEAD": 4,
        "ADAM": 5,
    },
)

PAULI = EnumDeclaration(
    name="Pauli",
    members={
        "I": 0,
        "X": 1,
        "Y": 2,
        "Z": 3,
    },
)

QSVM_FEATURE_MAP_ENTANGLEMENT = EnumDeclaration(
    name="QSVMFeatureMapEntanglement",
    members={
        "FULL": 0,
        "LINEAR": 1,
        "CIRCULAR": 2,
        "SCA": 3,
        "PAIRWISE": 4,
    },
)

for enum_decl in list(vars().values()):
    if isinstance(enum_decl, EnumDeclaration):
        EnumDeclaration.BUILTIN_ENUM_DECLARATIONS[enum_decl.name] = enum_decl
