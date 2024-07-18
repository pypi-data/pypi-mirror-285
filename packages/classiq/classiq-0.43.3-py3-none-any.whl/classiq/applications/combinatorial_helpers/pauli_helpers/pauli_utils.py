from typing import List

from classiq.interface.generator.functions.qmod_python_interface import QmodPyStruct
from classiq.interface.helpers.custom_pydantic_types import PydanticPauliList

from classiq.exceptions import ClassiqNonNumericCoefficientInPauliError
from classiq.qmod.builtins import PauliTerm
from classiq.qmod.builtins.enums import Pauli


def pauli_operator_to_hamiltonian(pauli_list: PydanticPauliList) -> List[PauliTerm]:
    pauli_terms: List[PauliTerm] = []
    for pauli_term in pauli_list:
        if not isinstance(pauli_term[1], complex) or pauli_term[1].imag != 0:
            raise ClassiqNonNumericCoefficientInPauliError(
                "Coefficient is not a number."
            )
        term = PauliTerm(
            [Pauli[p] for p in pauli_term[0]],  # type: ignore[arg-type]
            pauli_term[1].real,  # type: ignore[arg-type]
        )
        pauli_terms.append(term)

    return pauli_terms


def pauli_enum_to_str(pauli: Pauli) -> str:
    return {
        Pauli.I: "Pauli.I",
        Pauli.X: "Pauli.X",
        Pauli.Y: "Pauli.Y",
        Pauli.Z: "Pauli.Z",
    }[pauli]


def _pauli_terms_to_qmod(hamiltonian: List[PauliTerm]) -> str:
    qmod_strings = []
    for term in hamiltonian:
        pauli_str = ", ".join([pauli_enum_to_str(p) for p in term.pauli])  # type: ignore[attr-defined]
        qmod_strings.append(
            f"struct_literal(PauliTerm, pauli=[{pauli_str}], coefficient={term.coefficient})"
        )

    return ", ".join(qmod_strings)


def _pauli_dict_to_str(hamiltonian: List[QmodPyStruct]) -> str:
    res = []
    for struct in hamiltonian:
        pauli_str = ", ".join([pauli_enum_to_str(p) for p in struct["pauli"]])
        res.append(f'"pauli": [{pauli_str}], "coefficient": {struct["coefficient"]}')

    return f"{{{', '.join(res)}}}"
