from typing import Any, Callable, Dict, Iterator

from typing_extensions import Self


# Use this class as a type for complex data from the json, e.g., in the state_propagator function.
class Complex(complex):
    @classmethod
    def __get_validators__(cls) -> Iterator[Callable]:
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(
            pattern=r"[+-]?\d+\.?\d* *[+-] *\d+\.?\d*j",
        )

    @classmethod
    def validate(cls, v: Any) -> Self:
        if isinstance(v, str):
            v = "".join(v.split())

        return cls(v)
