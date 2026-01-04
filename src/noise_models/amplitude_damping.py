"""
Amplitude Damping Channel Implementation.

The amplitude damping channel models energy loss from a quantum system,
such as spontaneous emission of a photon. This is particularly relevant
for photonic QKD systems.

Mathematical Description:
Kraus operators:
K0 = |0⟩⟨0| + √(1-γ)|1⟩⟨1| = [[1, 0], [0, √(1-γ)]]
K1 = √γ|0⟩⟨1| = [[0, √γ], [0, 0]]

Effect on states:
|0⟩ → |0⟩ (unchanged)
|1⟩ → √(1-γ)|1⟩ + √γ|0⟩ (decays to ground state)

Physical Interpretation:
- Models energy dissipation to environment
- Excited state decays to ground state
- γ = 1 - e^(-t/T1) for time t and relaxation time T1

Effect on QKD:
- Asymmetric errors (more 1→0 than 0→1)
- Reduces |1⟩ population
- Can leak information about |0⟩ vs |1⟩

References:
    Preskill, J. (1998). "Lecture notes for Physics 229:
    Quantum Information and Computation."
"""

from typing import Optional, Tuple
import numpy as np
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import amplitude_damping_error


class AmplitudeDampingChannel:
    """
    Amplitude damping quantum channel for QKD simulation.
    
    Models photon loss and energy decay in quantum communication.
    Particularly relevant for fiber-optic and satellite QKD.
    
    Attributes:
        damping_probability: Probability of amplitude damping (γ)
        
    Example:
        >>> channel = AmplitudeDampingChannel(damping_probability=0.05)
        >>> noise_model = channel.get_noise_model()
    """
    
    def __init__(
        self,
        damping_probability: float = 0.05,
        seed: Optional[int] = None
    ):
        """
        Initialize the amplitude damping channel.
        
        Args:
            damping_probability: Decay probability γ (0 to 1)
            seed: Random seed for reproducibility
        """
        if not 0 <= damping_probability <= 1:
            raise ValueError("Damping probability must be between 0 and 1")
        
        self.damping_probability = damping_probability
        self.seed = seed
        self._noise_model = None
    
    @property
    def name(self) -> str:
        """Return the channel name."""
        return "AmplitudeDamping"
    
    def get_noise_model(self) -> NoiseModel:
        """
        Create a Qiskit NoiseModel for amplitude damping.
        
        Returns:
            NoiseModel for the Aer simulator
        """
        if self._noise_model is not None:
            return self._noise_model
        
        noise_model = NoiseModel()
        
        # Create amplitude damping error
        error = amplitude_damping_error(self.damping_probability)
        
        # Add to identity and single-qubit gates
        noise_model.add_all_qubit_quantum_error(error, ['id', 'u1', 'u2', 'u3', 'h', 'x', 'y', 'z'])
        
        self._noise_model = noise_model
        return noise_model
    
    def kraus_operators(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Return the Kraus operators for the amplitude damping channel.
        
        Returns:
            Tuple of (K0, K1) matrices
        """
        gamma = self.damping_probability
        
        K0 = np.array([
            [1, 0],
            [0, np.sqrt(1 - gamma)]
        ])
        
        K1 = np.array([
            [0, np.sqrt(gamma)],
            [0, 0]
        ])
        
        return K0, K1
    
    def expected_qber(self, p_one: float = 0.5) -> float:
        """
        Calculate expected QBER from amplitude damping.
        
        Amplitude damping causes asymmetric errors:
        - P(0|1) = γ (1 decays to 0)
        - P(1|0) = 0 (0 never becomes 1)
        
        Args:
            p_one: Prior probability of |1⟩ state
            
        Returns:
            Expected QBER
        """
        gamma = self.damping_probability
        
        # Error only when |1⟩ sent and it decays
        return gamma * p_one
    
    def transmission_probability(self) -> float:
        """
        Calculate probability of successful transmission.
        
        For QKD, successful transmission means the qubit
        arrives without significant decay.
        
        Returns:
            Transmission probability
        """
        return 1 - self.damping_probability
    
    @staticmethod
    def from_fiber_length(
        length_km: float,
        attenuation_db_per_km: float = 0.2
    ) -> 'AmplitudeDampingChannel':
        """
        Create channel based on fiber optic parameters.
        
        Args:
            length_km: Fiber length in kilometers
            attenuation_db_per_km: Fiber loss (default 0.2 dB/km for telecom)
            
        Returns:
            AmplitudeDampingChannel with appropriate damping
        """
        total_loss_db = length_km * attenuation_db_per_km
        transmission = 10 ** (-total_loss_db / 10)
        damping = 1 - transmission
        
        return AmplitudeDampingChannel(damping_probability=damping)
    
    @staticmethod
    def from_relaxation_time(
        time_ns: float,
        T1_ns: float = 50000
    ) -> 'AmplitudeDampingChannel':
        """
        Create channel based on relaxation time.
        
        Args:
            time_ns: Transmission/storage time in nanoseconds
            T1_ns: Relaxation time T1 in nanoseconds
            
        Returns:
            AmplitudeDampingChannel with appropriate damping
        """
        gamma = 1 - np.exp(-time_ns / T1_ns)
        return AmplitudeDampingChannel(damping_probability=gamma)
    
    def apply_to_state(self, state_vector: np.ndarray) -> np.ndarray:
        """
        Apply amplitude damping to a state vector.
        
        Args:
            state_vector: Input state [α, β]
            
        Returns:
            Density matrix after channel action
        """
        rho_in = np.outer(state_vector, np.conj(state_vector))
        K0, K1 = self.kraus_operators()
        
        rho_out = K0 @ rho_in @ K0.conj().T + K1 @ rho_in @ K1.conj().T
        
        return rho_out
    
    def __repr__(self) -> str:
        return f"AmplitudeDampingChannel(γ={self.damping_probability})"
