from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from classiq.qmod.builtins.enums import FinanceFunctionType


def get_finance_function_dict() -> Dict[str, "FinanceFunctionType"]:
    from classiq.qmod.builtins.enums import FinanceFunctionType

    return {
        "var": FinanceFunctionType.VAR,
        "expected shortfall": FinanceFunctionType.SHORTFALL,
        "x**2": FinanceFunctionType.X_SQUARE,
        "european call option": FinanceFunctionType.EUROPEAN_CALL_OPTION,
    }
