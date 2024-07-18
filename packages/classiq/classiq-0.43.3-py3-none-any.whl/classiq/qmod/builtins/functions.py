# This file was generated automatically - do not edit manually

from classiq.qmod.builtins.enums import Pauli
from classiq.qmod.qfunc import qfunc
from classiq.qmod.qmod_parameter import CArray, CBool, CInt, CReal
from classiq.qmod.qmod_variable import Input, Output, QArray, QBit, QNum
from classiq.qmod.quantum_callable import QCallable, QCallableList

from .structs import *


@qfunc(external=True)
def permute(
    functions: QCallableList,
) -> None:
    pass


@qfunc(external=True)
def apply(
    operand: QCallable,
) -> None:
    pass


@qfunc(external=True)
def molecule_ucc(
    molecule_problem: MoleculeProblem,
    excitations: CArray[CInt],
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def molecule_hva(
    molecule_problem: MoleculeProblem,
    reps: CInt,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def molecule_hartree_fock(
    molecule_problem: MoleculeProblem,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def fock_hamiltonian_ucc(
    fock_hamiltonian_problem: FockHamiltonianProblem,
    excitations: CArray[CInt],
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def fock_hamiltonian_hva(
    fock_hamiltonian_problem: FockHamiltonianProblem,
    reps: CInt,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def fock_hamiltonian_hartree_fock(
    fock_hamiltonian_problem: FockHamiltonianProblem,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def log_normal_finance(
    finance_model: LogNormalModel,
    finance_function: FinanceFunction,
    func_port: QArray[QBit],
    obj_port: QBit,
) -> None:
    pass


@qfunc(external=True)
def gaussian_finance(
    finance_model: GaussianModel,
    finance_function: FinanceFunction,
    func_port: QArray[QBit],
    obj_port: QBit,
) -> None:
    pass


@qfunc(external=True)
def pauli_feature_map(
    feature_map: QSVMFeatureMapPauli,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def bloch_sphere_feature_map(
    feature_dimension: CInt,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def H(
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def X(
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def Y(
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def Z(
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def I(
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def S(
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def T(
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def SDG(
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def TDG(
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def PHASE(
    theta: CReal,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def RX(
    theta: CReal,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def RY(
    theta: CReal,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def RZ(
    theta: CReal,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def R(
    theta: CReal,
    phi: CReal,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def RXX(
    theta: CReal,
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def RYY(
    theta: CReal,
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def RZZ(
    theta: CReal,
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def CH(
    control: QBit,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def CX(
    control: QBit,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def CY(
    control: QBit,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def CZ(
    control: QBit,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def CRX(
    theta: CReal,
    control: QBit,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def CRY(
    theta: CReal,
    control: QBit,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def CRZ(
    theta: CReal,
    control: QBit,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def CPHASE(
    theta: CReal,
    control: QBit,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def SWAP(
    qbit0: QBit,
    qbit1: QBit,
) -> None:
    pass


@qfunc(external=True)
def IDENTITY(
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def prepare_state(
    probabilities: CArray[CReal],
    bound: CReal,
    out: Output[QArray[QBit]],
) -> None:
    pass


@qfunc(external=True)
def prepare_amplitudes(
    amplitudes: CArray[CReal],
    bound: CReal,
    out: Output[QArray[QBit]],
) -> None:
    pass


@qfunc(external=True)
def unitary(
    elements: CArray[CArray[CReal]],
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def add(
    left: QArray[QBit],
    right: QArray[QBit],
    result: Output[QArray[QBit]],
) -> None:
    pass


@qfunc(external=True)
def modular_add(
    left: QArray[QBit],
    right: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def integer_xor(
    left: QArray[QBit],
    right: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def U(
    theta: CReal,
    phi: CReal,
    lam: CReal,
    gam: CReal,
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def CCX(
    control: QArray[QBit],
    target: QBit,
) -> None:
    pass


@qfunc(external=True)
def allocate(
    num_qubits: CInt,
    out: Output[QArray[QBit]],
) -> None:
    pass


@qfunc(external=True)
def free(
    in_: Input[QArray[QBit]],
) -> None:
    pass


@qfunc(external=True)
def randomized_benchmarking(
    num_of_cliffords: CInt,
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def inplace_prepare_state(
    probabilities: CArray[CReal],
    bound: CReal,
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def inplace_prepare_amplitudes(
    amplitudes: CArray[CReal],
    bound: CReal,
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def single_pauli_exponent(
    pauli_string: CArray[Pauli],
    coefficient: CReal,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def suzuki_trotter(
    pauli_operator: CArray[PauliTerm],
    evolution_coefficient: CReal,
    order: CInt,
    repetitions: CInt,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qdrift(
    pauli_operator: CArray[PauliTerm],
    evolution_coefficient: CReal,
    num_qdrift: CInt,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def exponentiation_with_depth_constraint(
    pauli_operator: CArray[PauliTerm],
    evolution_coefficient: CReal,
    max_depth: CInt,
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qft(
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qpe_flexible(
    unitary_with_power: QCallable[CInt],
    phase: QNum,
) -> None:
    pass


@qfunc(external=True)
def qpe(
    unitary: QCallable,
    phase: QNum,
) -> None:
    pass


@qfunc(external=True)
def single_pauli(
    slope: CReal,
    offset: CReal,
    q1_qfunc: QCallable[CReal, QBit],
    x: QArray[QBit],
    q: QBit,
) -> None:
    pass


@qfunc(external=True)
def linear_pauli_rotations(
    bases: CArray[Pauli],
    slopes: CArray[CReal],
    offsets: CArray[CReal],
    x: QArray[QBit],
    q: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def amplitude_estimation(
    oracle: QCallable[QArray[QBit]],
    space_transform: QCallable[QArray[QBit]],
    phase: QNum,
    packed_vars: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def phase_oracle(
    predicate: QCallable[QArray[QBit], QBit],
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def reflect_about_zero(
    packed_vars: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def grover_diffuser(
    space_transform: QCallable[QArray[QBit]],
    packed_vars: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def grover_operator(
    oracle: QCallable[QArray[QBit]],
    space_transform: QCallable[QArray[QBit]],
    packed_vars: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def grover_search(
    reps: CInt,
    oracle: QCallable[QArray[QBit]],
    packed_vars: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def hadamard_transform(
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def apply_to_all(
    gate_operand: QCallable[QBit],
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qft_no_swap(
    qbv: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def _check_msb(
    ref: CInt,
    x: QArray[QBit],
    aux: QBit,
) -> None:
    pass


@qfunc(external=True)
def _ctrl_x(
    ref: CInt,
    ctrl: QNum,
    aux: QBit,
) -> None:
    pass


@qfunc(external=True)
def qft_space_add_const(
    value: CInt,
    phi_b: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def cc_modular_add(
    n: CInt,
    a: CInt,
    phi_b: QArray[QBit],
    c1: QBit,
    c2: QBit,
    aux: QBit,
) -> None:
    pass


@qfunc(external=True)
def c_modular_multiply(
    n: CInt,
    a: CInt,
    b: QArray[QBit],
    x: QArray[QBit],
    ctrl: QBit,
    aux: QBit,
) -> None:
    pass


@qfunc(external=True)
def multiswap(
    x: QArray[QBit],
    y: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def inplace_c_modular_multiply(
    n: CInt,
    a: CInt,
    x: QArray[QBit],
    ctrl: QBit,
    aux: QBit,
) -> None:
    pass


@qfunc(external=True)
def modular_exp(
    n: CInt,
    a: CInt,
    x: QArray[QBit],
    power: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qsvt_step(
    phase1: CReal,
    phase2: CReal,
    proj_cnot_1: QCallable[QArray[QBit], QBit],
    proj_cnot_2: QCallable[QArray[QBit], QBit],
    u: QCallable[QArray[QBit]],
    qvar: QArray[QBit],
    aux: QBit,
) -> None:
    pass


@qfunc(external=True)
def qsvt(
    phase_seq: CArray[CReal],
    proj_cnot_1: QCallable[QArray[QBit], QBit],
    proj_cnot_2: QCallable[QArray[QBit], QBit],
    u: QCallable[QArray[QBit]],
    qvar: QArray[QBit],
    aux: QBit,
) -> None:
    pass


@qfunc(external=True)
def projector_controlled_phase(
    phase: CReal,
    proj_cnot: QCallable[QArray[QBit], QBit],
    qvar: QArray[QBit],
    aux: QBit,
) -> None:
    pass


@qfunc(external=True)
def qsvt_inversion(
    phase_seq: CArray[CReal],
    block_encoding_cnot: QCallable[QArray[QBit], QBit],
    u: QCallable[QArray[QBit]],
    qvar: QArray[QBit],
    aux: QBit,
) -> None:
    pass


@qfunc(external=True)
def allocate_num(
    num_qubits: CInt,
    is_signed: CBool,
    fraction_digits: CInt,
    out: Output[QNum],
) -> None:
    pass


@qfunc(external=True)
def qaoa_mixer_layer(
    b: CReal,
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qaoa_cost_layer(
    g: CReal,
    hamiltonian: CArray[PauliTerm],
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qaoa_layer(
    g: CReal,
    b: CReal,
    hamiltonian: CArray[PauliTerm],
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qaoa_init(
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qaoa_penalty(
    num_qubits: CInt,
    params_list: CArray[CReal],
    hamiltonian: CArray[PauliTerm],
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def full_hea(
    num_qubits: CInt,
    is_parametrized: CArray[CInt],
    angle_params: CArray[CReal],
    connectivity_map: CArray[CArray[CInt]],
    reps: CInt,
    operands_1qubit: QCallableList[CReal, QBit],
    operands_2qubit: QCallableList[CReal, QBit, QBit],
    x: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def swap_test(
    state1: QArray[QBit],
    state2: QArray[QBit],
    test: Output[QBit],
) -> None:
    pass


@qfunc(external=True)
def prepare_ghz_state(
    size: CInt,
    q: Output[QArray[QBit]],
) -> None:
    pass


@qfunc(external=True)
def prepare_exponential_state(
    rate: CInt,
    q: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def prepare_bell_state(
    state_num: CInt,
    q: Output[QArray[QBit]],
) -> None:
    pass


@qfunc(external=True)
def inplace_prepare_int(
    value: CInt,
    target: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def prepare_int(
    value: CInt,
    out: Output[QNum],
) -> None:
    pass


@qfunc(external=True)
def switch(
    selector: CInt,
    cases: QCallableList,
) -> None:
    pass


@qfunc(external=True)
def _qct_d_operator(
    x: QNum,
    q: QBit,
) -> None:
    pass


@qfunc(external=True)
def _qct_pi_operator(
    x: QArray[QBit],
    q: QBit,
) -> None:
    pass


@qfunc(external=True)
def qct_qst_type1(
    x: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qct_qst_type2(
    x: QArray[QBit],
    q: QBit,
) -> None:
    pass


@qfunc(external=True)
def qct_type2(
    x: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def qst_type2(
    x: QArray[QBit],
) -> None:
    pass


@qfunc(external=True)
def modular_increment(
    a: CInt,
    x: QArray[QBit],
) -> None:
    pass


__all__ = [
    "permute",
    "apply",
    "molecule_ucc",
    "molecule_hva",
    "molecule_hartree_fock",
    "fock_hamiltonian_ucc",
    "fock_hamiltonian_hva",
    "fock_hamiltonian_hartree_fock",
    "log_normal_finance",
    "gaussian_finance",
    "pauli_feature_map",
    "bloch_sphere_feature_map",
    "H",
    "X",
    "Y",
    "Z",
    "I",
    "S",
    "T",
    "SDG",
    "TDG",
    "PHASE",
    "RX",
    "RY",
    "RZ",
    "R",
    "RXX",
    "RYY",
    "RZZ",
    "CH",
    "CX",
    "CY",
    "CZ",
    "CRX",
    "CRY",
    "CRZ",
    "CPHASE",
    "SWAP",
    "IDENTITY",
    "prepare_state",
    "prepare_amplitudes",
    "unitary",
    "add",
    "modular_add",
    "integer_xor",
    "U",
    "CCX",
    "allocate",
    "free",
    "randomized_benchmarking",
    "inplace_prepare_state",
    "inplace_prepare_amplitudes",
    "single_pauli_exponent",
    "suzuki_trotter",
    "qdrift",
    "exponentiation_with_depth_constraint",
    "qft",
    "qpe_flexible",
    "qpe",
    "single_pauli",
    "linear_pauli_rotations",
    "amplitude_estimation",
    "phase_oracle",
    "reflect_about_zero",
    "grover_diffuser",
    "grover_operator",
    "grover_search",
    "hadamard_transform",
    "apply_to_all",
    "qft_no_swap",
    "_check_msb",
    "_ctrl_x",
    "qft_space_add_const",
    "cc_modular_add",
    "c_modular_multiply",
    "multiswap",
    "inplace_c_modular_multiply",
    "modular_exp",
    "qsvt_step",
    "qsvt",
    "projector_controlled_phase",
    "qsvt_inversion",
    "allocate_num",
    "qaoa_mixer_layer",
    "qaoa_cost_layer",
    "qaoa_layer",
    "qaoa_init",
    "qaoa_penalty",
    "full_hea",
    "swap_test",
    "prepare_ghz_state",
    "prepare_exponential_state",
    "prepare_bell_state",
    "inplace_prepare_int",
    "prepare_int",
    "switch",
    "_qct_d_operator",
    "_qct_pi_operator",
    "qct_qst_type1",
    "qct_qst_type2",
    "qct_type2",
    "qst_type2",
    "modular_increment",
]
