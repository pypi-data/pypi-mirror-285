from typing import Sequence, Union

from classiq import EnumDeclaration, StructDeclaration
from classiq.qmod.semantics.error_manager import ErrorManager


def check_duplicate_types(
    types: Sequence[Union[EnumDeclaration, StructDeclaration]]
) -> None:
    known_types = {
        type_.name for type_ in EnumDeclaration.BUILTIN_ENUM_DECLARATIONS.values()
    }
    known_types |= {
        type_.name for type_ in StructDeclaration.BUILTIN_STRUCT_DECLARATIONS.values()
    }
    for type_ in types:
        if type_.name in known_types:
            with ErrorManager().node_context(type_):
                ErrorManager().add_error(f"Type {type_.name!r} already exists")
        else:
            known_types.add(type_.name)
