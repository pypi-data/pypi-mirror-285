from typing import Dict

from classiq.interface.generator.constant import Constant
from classiq.interface.generator.types.enum_declaration import EnumDeclaration
from classiq.interface.model.native_function_definition import NativeFunctionDefinition

from classiq import StructDeclaration


class ModelStateContainer:
    enum_decls: Dict[str, EnumDeclaration]
    type_decls: Dict[str, StructDeclaration]
    native_defs: Dict[str, NativeFunctionDefinition]
    constants: Dict[str, Constant]


QMODULE = ModelStateContainer()
