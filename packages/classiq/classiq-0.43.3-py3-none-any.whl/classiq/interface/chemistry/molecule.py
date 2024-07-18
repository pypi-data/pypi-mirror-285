from typing import List, Literal, Union

import pydantic

from classiq.interface.chemistry.elements import ELEMENTS
from classiq.interface.helpers.custom_pydantic_types import AtomType
from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)

from classiq.exceptions import ClassiqValueError


class Atom(HashablePydanticBaseModel):
    symbol: Literal[tuple(ELEMENTS)] = pydantic.Field(description="The atom symbol")  # type: ignore[valid-type]
    x: float = pydantic.Field(description="The x coordinate of the atom")
    y: float = pydantic.Field(description="The y coordinate of the atom")
    z: float = pydantic.Field(description="The z coordinate of the atom")


class Molecule(HashablePydanticBaseModel):
    atoms: List[Atom] = pydantic.Field(
        description="A list of atoms each containing the atoms symbol and  its (x,y,z) location",
        min_items=1,
    )
    spin: pydantic.NonNegativeInt = pydantic.Field(
        default=1, description="spin of the molecule"
    )
    charge: pydantic.NonNegativeInt = pydantic.Field(
        default=0, description="charge of the molecule"
    )

    @property
    def atoms_type(self) -> List[AtomType]:
        return [(atom.symbol, [atom.x, atom.y, atom.z]) for atom in self.atoms]

    @pydantic.validator("atoms", each_item=True, pre=True)
    def _validate_atoms(cls, atom: Union[AtomType, Atom]) -> Atom:
        if isinstance(atom, (list, tuple)):
            return cls._validate_old_atoms_type(atom)
        return atom

    @staticmethod
    def _validate_old_atoms_type(atom: AtomType) -> Atom:
        if len(atom) != 2:
            raise ClassiqValueError(
                "each atom should be a list of two entries: 1) name pf the elemnt (str) 2) list of its (x,y,z) location"
            )
        if not isinstance(atom[0], str):
            raise ClassiqValueError(
                f"atom name should be a string. unknown element: {atom[0]}."
            )
        if len(atom[1]) != 3:
            raise ClassiqValueError(
                f"location of the atom is of length three, representing the (x,y,z) coordinates of the atom, error value: {atom[1]}"
            )
        for idx in atom[1]:
            if not isinstance(idx, (float, int)):
                raise ClassiqValueError(
                    f"coordinates of the atom should be of type float. error value: {idx}"
                )
        symbol, coordinate = atom

        return Atom(symbol=symbol, x=coordinate[0], y=coordinate[1], z=coordinate[2])

    class Config:
        frozen = True
