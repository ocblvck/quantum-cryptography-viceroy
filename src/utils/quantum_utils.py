"""
Quantum Utility Functions.

Helper functions for common quantum operations in QKD implementations.
"""

from typing import Tuple, Optional, List
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


def create_bell_state(state_type: str = "phi+") -> QuantumCircuit:
    """
    Create a Bell state circuit.
    
    Bell states:
    - |Φ+⟩ = (|00⟩ + |11⟩)/√2
    - |Φ-⟩ = (|00⟩ - |11⟩)/√2
    - |Ψ+⟩ = (|01⟩ + |10⟩)/√2
    - |Ψ-⟩ = (|01⟩ - |10⟩)/√2
    
    Args:
        state_type: One of "phi+", "phi-", "psi+", "psi-"
        
    Returns:
        QuantumCircuit preparing the Bell state
    """
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # Start with |Φ+⟩
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])
    
    # Transform to desired Bell state
    if state_type == "phi-":
        qc.z(qr[0])
    elif state_type == "psi+":
        qc.x(qr[1])
    elif state_type == "psi-":
        qc.x(qr[1])
        qc.z(qr[0])
    
    return qc


def measure_in_basis(
    circuit: QuantumCircuit,
    qubit: int,
    basis: str,
    classical_bit: int
) -> QuantumCircuit:
    """
    Add measurement in specified basis to circuit.
    
    Args:
        circuit: Quantum circuit to modify
        qubit: Qubit index to measure
        basis: Basis name ("Z", "X", "Y", or angle in radians)
        classical_bit: Classical bit to store result
        
    Returns:
        Modified quantum circuit
    """
    if basis == "Z" or basis == 0:
        # Computational basis - measure directly
        pass
    elif basis == "X" or basis == 1:
        circuit.h(qubit)
    elif basis == "Y":
        circuit.sdg(qubit)
        circuit.h(qubit)
    elif isinstance(basis, (int, float)):
        # Arbitrary angle
        circuit.ry(-basis, qubit)
    
    circuit.measure(qubit, classical_bit)
    return circuit


def apply_pauli_error(
    circuit: QuantumCircuit,
    qubit: int,
    error_type: str
) -> QuantumCircuit:
    """
    Apply a Pauli error to a qubit.
    
    Args:
        circuit: Quantum circuit
        qubit: Qubit index
        error_type: "X", "Y", "Z", or "I"
        
    Returns:
        Modified circuit
    """
    if error_type == "X":
        circuit.x(qubit)
    elif error_type == "Y":
        circuit.y(qubit)
    elif error_type == "Z":
        circuit.z(qubit)
    # "I" does nothing
    
    return circuit


def fidelity(state1: np.ndarray, state2: np.ndarray) -> float:
    """
    Calculate fidelity between two quantum states.
    
    For pure states: F = |⟨ψ|φ⟩|²
    
    Args:
        state1: First state vector
        state2: Second state vector
        
    Returns:
        Fidelity value (0 to 1)
    """
    state1 = np.array(state1).flatten()
    state2 = np.array(state2).flatten()
    
    overlap = np.abs(np.vdot(state1, state2)) ** 2
    return float(overlap)


def trace_distance(rho1: np.ndarray, rho2: np.ndarray) -> float:
    """
    Calculate trace distance between two density matrices.
    
    D(ρ, σ) = (1/2) Tr|ρ - σ|
    
    Args:
        rho1: First density matrix
        rho2: Second density matrix
        
    Returns:
        Trace distance (0 to 1)
    """
    diff = rho1 - rho2
    eigenvalues = np.linalg.eigvalsh(diff)
    return 0.5 * np.sum(np.abs(eigenvalues))


def random_qubit_state(seed: Optional[int] = None) -> np.ndarray:
    """
    Generate a random pure qubit state.
    
    Args:
        seed: Random seed
        
    Returns:
        Normalized state vector [α, β]
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Random point on Bloch sphere
    theta = np.arccos(2 * np.random.random() - 1)
    phi = 2 * np.pi * np.random.random()
    
    alpha = np.cos(theta / 2)
    beta = np.exp(1j * phi) * np.sin(theta / 2)
    
    return np.array([alpha, beta])


def bloch_vector(state: np.ndarray) -> Tuple[float, float, float]:
    """
    Calculate Bloch vector from state vector.
    
    Args:
        state: Qubit state vector [α, β]
        
    Returns:
        Tuple (x, y, z) on Bloch sphere
    """
    rho = np.outer(state, np.conj(state))
    
    # Pauli matrices
    X = np.array([[0, 1], [1, 0]])
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]])
    
    x = np.real(np.trace(rho @ X))
    y = np.real(np.trace(rho @ Y))
    z = np.real(np.trace(rho @ Z))
    
    return (x, y, z)


def partial_trace(rho: np.ndarray, dims: List[int], trace_out: int) -> np.ndarray:
    """
    Compute partial trace of a density matrix.
    
    Args:
        rho: Density matrix
        dims: Dimensions of subsystems
        trace_out: Index of subsystem to trace out
        
    Returns:
        Reduced density matrix
    """
    n = len(dims)
    total_dim = int(np.prod(dims))
    
    # Reshape into tensor
    rho_tensor = rho.reshape(dims + dims)
    
    # Trace over specified subsystem
    trace_axes = (trace_out, trace_out + n)
    rho_reduced = np.trace(rho_tensor, axis1=trace_axes[0], axis2=trace_axes[1])
    
    # Reshape back to matrix
    remaining_dims = [d for i, d in enumerate(dims) if i != trace_out]
    new_dim = int(np.prod(remaining_dims))
    
    return rho_reduced.reshape(new_dim, new_dim)


def quantum_entropy(rho: np.ndarray) -> float:
    """
    Calculate von Neumann entropy.
    
    S(ρ) = -Tr(ρ log ρ)
    
    Args:
        rho: Density matrix
        
    Returns:
        Entropy in bits
    """
    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = eigenvalues[eigenvalues > 1e-15]  # Remove zeros
    
    return -np.sum(eigenvalues * np.log2(eigenvalues))


def bb84_states() -> dict:
    """
    Return the four BB84 states.
    
    Returns:
        Dictionary mapping (bit, basis) to state vectors
    """
    states = {
        (0, 0): np.array([1, 0]),         # |0⟩
        (1, 0): np.array([0, 1]),         # |1⟩
        (0, 1): np.array([1, 1]) / np.sqrt(2),   # |+⟩
        (1, 1): np.array([1, -1]) / np.sqrt(2),  # |-⟩
    }
    return states
