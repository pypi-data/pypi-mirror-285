import warnings
from dataclasses import dataclass
from typing import Type


def struct(user_class: Type) -> Type:
    warnings.warn(
        "@struct is deprecated and will be removed in a future release. "
        "Use @dataclass instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return dataclass(user_class)
