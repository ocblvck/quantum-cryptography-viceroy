"""
Depolarizing Channel Implementation.

The depolarizing channel is a fundamental quantum noise model that describes
the situation where a qubit is randomly replaced with a completely mixed state.

Mathematical Description:
ε(ρ) = (1-p)ρ + p(I/2)
     = (1-p)ρ + (p/3)(XρX + YρY + ZρZ)

where p is the depolarizing probability.

Physical Interpretation:
- With probability (1-p), the qubit is unchanged
- With probability p/3, an X (bit-flip) error occurs
- With probability p/3, a Y error occurs
- With probability p/3, a Z (phase-flip) error occurs

Effect on QKD:
- Introduces symmetric errors in both bases
- Increases QBER proportional to p
- QBER ≈ p/2 for small p

References:
    Nielsen, M. A., & Chuang, I. L. (2010). Quantum Computation and 
    Quantum Information. Cambridge University Press.
"""

from typing import Optional
import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error


class DepolarizingChannel:
    """
    Depolarizing quantum channel for QKD simulation.
    
    This channel applies depolarizing noise to qubits, simulating
    the effect of random errors in the quantum channel.
    
    Attributes:
        error_probability: Probability of depolarization
        
    Example:
        >>> channel = DepolarizingChannel(error_probability=0.01)
        >>> noise_model = channel.get_noise_model()
        >>> result = backend.run(circuit, noise_model=noise_model)
    """
    
    def __init__(
        self,
        error_probability: float = 0.01,
        seed: Optional[int] = None
    ):
        """
        Initialize the depolarizing channel.
        
        Args:
            error_probability: Probability of depolarization (0 to 1)
            seed: Random seed for reproducibility
        """
        if not 0 <= error_probability <= 1:
            raise ValueError("Error probability must be between 0 and 1")
        
        self.error_probability = error_probability
        self.seed = seed
        self._noise_model = None
    
    @property
    def name(self) -> str:
        """Return the channel name."""
        return "Depolarizing"
    
    def get_noise_model(self) -> NoiseModel:
        """
        Create a Qiskit NoiseModel for the depolarizing channel.
        
        Returns:
            NoiseModel that can be passed to the Aer simulator
        """
        if self._noise_model is not None:
            return self._noise_model
        
        noise_model = NoiseModel()
        
        # Create depolarizing error for single-qubit gates
        error = depolarizing_error(self.error_probability, 1)
        
        # Add error to all single-qubit gates
        noise_model.add_all_qubit_quantum_error(error, ['id', 'u1', 'u2', 'u3', 'h', 'x', 'y', 'z'])
        
        self._noise_model = noise_model
        return noise_model
    
    def expected_qber(self) -> float:
        """
        Calculate the expected QBER from this noise.
        
        For a depolarizing channel:
        QBER ≈ p/2 for small p
        
        More precisely:
        QBER = (2p/3) for the depolarizing model with X,Y,Z errors
        
        Returns:
            Expected QBER
        """
        p = self.error_probability
        # X and Y errors flip the bit, Z doesn't
        # QBER = P(X) + P(Y) = p/3 + p/3 = 2p/3
        return 2 * p / 3
    
    def channel_capacity(self) -> float:
        """
        Calculate the quantum channel capacity.
        
        For the depolarizing channel:
        Q = 1 - H(p) for p ≤ 0.25
        
        Returns:
            Quantum capacity in bits per channel use
        """
        p = self.error_probability
        
        if p == 0:
            return 1.0
        if p >= 0.25:
            return 0.0
        
        # Binary entropy
        h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if 0 < x < 1 else 0
        
        # Hashing bound (simplified)
        return max(0, 1 - 2 * h(p))
    
    def apply_to_state(self, state_vector: np.ndarray) -> np.ndarray:
        """
        Apply depolarizing channel to a state vector.
        
        This is a simplified classical simulation.
        
        Args:
            state_vector: Input quantum state [α, β]
            
        Returns:
            Density matrix after channel action
        """
        rho_in = np.outer(state_vector, np.conj(state_vector))
        
        p = self.error_probability
        I = np.eye(2)
        X = np.array([[0, 1], [1, 0]])
        Y = np.array([[0, -1j], [1j, 0]])
        Z = np.array([[1, 0], [0, -1]])
        
        rho_out = (1 - p) * rho_in + (p/3) * (
            X @ rho_in @ X +
            Y @ rho_in @ Y +
            Z @ rho_in @ Z
        )
        
        return rho_out
    
    def __repr__(self) -> str:
        return f"DepolarizingChannel(p={self.error_probability})"
