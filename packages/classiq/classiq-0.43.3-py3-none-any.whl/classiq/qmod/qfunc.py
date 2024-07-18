from typing import Callable, Optional, Union, overload

from classiq.qmod.quantum_callable import QCallable
from classiq.qmod.quantum_function import ExternalQFunc, QFunc


@overload
def qfunc(func: Callable, *, external: bool = False) -> QFunc: ...


@overload
def qfunc(func: None = None, *, external: bool) -> Callable[[Callable], QCallable]: ...


def qfunc(
    func: Optional[Callable] = None, *, external: bool = False
) -> Union[Callable[[Callable], QCallable], QCallable]:
    def wrapper(func: Callable) -> QCallable:
        if external:
            return ExternalQFunc(func)

        return QFunc(func)

    if func is not None:
        return wrapper(func)

    return wrapper
