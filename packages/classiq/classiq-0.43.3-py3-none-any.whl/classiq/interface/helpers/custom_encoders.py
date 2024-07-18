from typing import Any, Callable, Dict

CUSTOM_ENCODERS: Dict[type, Callable[[Any], Any]] = {complex: str}
