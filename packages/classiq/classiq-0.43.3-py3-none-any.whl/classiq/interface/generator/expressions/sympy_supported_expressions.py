from typing import List

BASIC_ARITHMETIC_OPERATORS: List[str] = ["+", "-", "*", "/", "%"]
MATHEMATICAL_FUNCTIONS: List[str] = [
    "sin",
    "cos",
    "tan",
    "cot",
    "sec",
    "csc",
    "asin",
    "acos",
    "atan",
    "acot",
    "asec",
    "acsc",
    "sinh",
    "cosh",
    "tanh",
    "coth",
    "sech",
    "csch",
    "asinh",
    "acosh",
    "atanh",
    "acoth",
    "asech",
    "exp",
    "log",
    "ln",
    "sqrt",
    "abs",
    "floor",
    "ceiling",
    "Max",
    "Min",
    "mod_inverse",
]
SPECIAL_FUNCTIONS: List[str] = [
    "erf",
    "erfc",
    "gamma",
    "beta",
    "besselj",
    "bessely",
    "besseli",
    "besselk",
    "dirichlet_eta",
    "polygamma",
    "loggamma",
    "factorial",
    "binomial",
    "subfactorial",
    "primorial",
    "bell",
    "bernoulli",
    "euler",
    "catalan",
]
PIECEWISE_FUNCTIONS: List[str] = ["Piecewise", "Heaviside"]
NUMERIC_CONSTANTS: List[str] = [
    "pi",
    "E",
    "I",
    "GoldenRatio",
    "EulerGamma",
    "Catalan",
]
CONSTANTS: List[str] = NUMERIC_CONSTANTS + ["true", "false"]

DATA_TYPES: List[str] = ["Matrix"]
LOGIC_OPERATORS: List[str] = [
    "And",
    "Or",
    "Not",
    "Xor",
    "Equivalent",
    "Implies",
    "Nand",
    "Nor",
]
RELATIONAL_OPERATORS: List[str] = ["<", "<=", ">", ">=", "!=", "<>", "Eq", "Ne"]

SYMPY_SUPPORTED_EXPRESSIONS: List[str] = (
    BASIC_ARITHMETIC_OPERATORS
    + MATHEMATICAL_FUNCTIONS
    + SPECIAL_FUNCTIONS
    + PIECEWISE_FUNCTIONS
    + CONSTANTS
    + LOGIC_OPERATORS
    + RELATIONAL_OPERATORS
    + DATA_TYPES
)
