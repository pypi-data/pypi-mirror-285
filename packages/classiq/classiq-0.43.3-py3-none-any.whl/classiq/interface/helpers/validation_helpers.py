from typing import Hashable, List, Mapping, Optional

from classiq.interface.helpers.pydantic_model_helpers import Nameable

from classiq.exceptions import ClassiqValueError


def is_list_unique(lst: List[Hashable]) -> bool:
    return len(set(lst)) == len(lst)


def validate_nameables_mapping(
    nameables_dict: Mapping[str, Nameable], declaration_type: str
) -> None:
    if not all(name == nameable.name for (name, nameable) in nameables_dict.items()):
        raise ClassiqValueError(
            f"{declaration_type} declaration names should match the keys of their names."
        )


def validate_nameables_no_overlap(
    left_nameables_dict: Optional[Mapping[str, Nameable]],
    right_nameables_dict: Optional[Mapping[str, Nameable]],
    left_declaration_type: str,
    right_declaration_type: str,
) -> Optional[str]:
    if left_nameables_dict is None or right_nameables_dict is None:
        return None

    matched_names = left_nameables_dict.keys() & right_nameables_dict.keys()
    if matched_names:
        return f"{left_declaration_type} declaration names overlap with {right_declaration_type} declaration names: {matched_names}"

    return None
