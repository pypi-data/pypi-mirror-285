# This file was generated automatically - do not edit manually

from dataclasses import dataclass

from classiq.qmod.builtins.enums import LadderOperator, Pauli
from classiq.qmod.qmod_parameter import CArray, CBool, CInt, CReal


@dataclass
class PauliTerm:
    pauli: CArray[Pauli]
    coefficient: CReal


@dataclass
class MoleculeProblem:
    mapping: CInt
    z2_symmetries: CBool
    molecule: "Molecule"
    freeze_core: CBool
    remove_orbitals: CArray[CInt]


@dataclass
class Molecule:
    atoms: CArray["ChemistryAtom"]
    spin: CInt
    charge: CInt


@dataclass
class ChemistryAtom:
    element: CInt
    position: "Position"


@dataclass
class Position:
    x: CReal
    y: CReal
    z: CReal


@dataclass
class FockHamiltonianProblem:
    mapping: CInt
    z2_symmetries: CBool
    terms: CArray["LadderTerm"]
    num_particles: CArray[CInt]


@dataclass
class LadderTerm:
    coefficient: CReal
    ops: CArray["LadderOp"]


@dataclass
class LadderOp:
    op: LadderOperator
    index: CInt


@dataclass
class CombinatorialOptimizationSolution:
    probability: CReal
    cost: CReal
    solution: CArray[CInt]
    count: CInt


@dataclass
class GaussianModel:
    num_qubits: CInt
    normal_max_value: CReal
    default_probabilities: CArray[CReal]
    rhos: CArray[CReal]
    loss: CArray[CInt]
    min_loss: CInt


@dataclass
class LogNormalModel:
    num_qubits: CInt
    mu: CReal
    sigma: CReal


@dataclass
class FinanceFunction:
    f: CInt
    threshold: CReal
    larger: CBool
    polynomial_degree: CInt
    use_chebyshev_polynomial_approximation: CBool
    tail_probability: CReal


@dataclass
class QsvmResult:
    test_score: CReal
    predicted_labels: CArray[CReal]


@dataclass
class QSVMFeatureMapPauli:
    feature_dimension: CInt
    reps: CInt
    entanglement: CInt
    alpha: CReal
    paulis: CArray[CArray[Pauli]]


__all__ = [
    "PauliTerm",
    "MoleculeProblem",
    "Molecule",
    "ChemistryAtom",
    "Position",
    "FockHamiltonianProblem",
    "LadderTerm",
    "LadderOp",
    "CombinatorialOptimizationSolution",
    "GaussianModel",
    "LogNormalModel",
    "FinanceFunction",
    "QsvmResult",
    "QSVMFeatureMapPauli",
]
