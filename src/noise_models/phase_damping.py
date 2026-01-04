"""
Phase Damping Channel Implementation.

The phase damping channel models the loss of quantum phase information
without energy loss. This is also known as dephasing and is characterized
by the T2 relaxation time in physical systems.

Mathematical Description:
Kraus operators:
K0 = √(1-λ)I = [[√(1-λ), 0], [0, √(1-λ)]]
K1 = √λ|0⟩⟨0| = [[√λ, 0], [0, 0]]
K2 = √λ|1⟩⟨1| = [[0, 0], [0, √λ]]

Effect on density matrix:
ρ → [[ρ00, √(1-λ)ρ01], [√(1-λ)ρ10, ρ11]]

Physical Interpretation:
- Causes decoherence without energy loss
- Off-diagonal elements decay (coherence loss)
- Diagonal elements unchanged (populations preserved)
- λ = 1 - e^(-t/T2) for time t and dephasing time T2

Effect on QKD:
- Affects X-basis measurements
- Z-basis unaffected (phase doesn't matter)
- Reduces key rate for protocols using both bases
"""

from typing import Optional, Tuple
import numpy as np
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import phase_damping_error


class PhaseDampingChannel:
    """
    Phase damping (dephasing) quantum channel.
    
    Models loss of phase coherence without energy dissipation.
    Important for understanding T2 effects in quantum communication.
    
    Attributes:
        dephasing_probability: Probability of dephasing (λ)
        
    Example:
        >>> channel = PhaseDampingChannel(dephasing_probability=0.02)
        >>> noise_model = channel.get_noise_model()
    """
    
    def __init__(
        self,
        dephasing_probability: float = 0.02,
        seed: Optional[int] = None
    ):
        """
        Initialize the phase damping channel.
        
        Args:
            dephasing_probability: Dephasing probability λ (0 to 1)
            seed: Random seed for reproducibility
        """
        if not 0 <= dephasing_probability <= 1:
            raise ValueError("Dephasing probability must be between 0 and 1")
        
        self.dephasing_probability = dephasing_probability
        self.seed = seed
        self._noise_model = None
    
    @property
    def name(self) -> str:
        """Return the channel name."""
        return "PhaseDamping"
    
    def get_noise_model(self) -> NoiseModel:
        """
        Create a Qiskit NoiseModel for phase damping.
        
        Returns:
            NoiseModel for the Aer simulator
        """
        if self._noise_model is not None:
            return self._noise_model
        
        noise_model = NoiseModel()
        
        # Create phase damping error
        error = phase_damping_error(self.dephasing_probability)
        
        # Add to single-qubit gates
        noise_model.add_all_qubit_quantum_error(error, ['id', 'u1', 'u2', 'u3', 'h', 'x', 'y', 'z'])
        
        self._noise_model = noise_model
        return noise_model
    
    def kraus_operators(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Return the Kraus operators for phase damping.
        
        Returns:
            Tuple of (K0, K1) matrices
        """
        lam = self.dephasing_probability
        
        # Alternative representation using two operators
        K0 = np.array([
            [1, 0],
            [0, np.sqrt(1 - lam)]
        ])
        
        K1 = np.array([
            [0, 0],
            [0, np.sqrt(lam)]
        ])
        
        return K0, K1
    
    def expected_qber_x_basis(self) -> float:
        """
        Calculate expected QBER for X-basis measurements.
        
        Phase damping affects superposition states (X-basis)
        but not computational basis states (Z-basis).
        
        Returns:
            Expected QBER in X-basis
        """
        lam = self.dephasing_probability
        
        # For |+⟩ state under phase damping:
        # Probability of measuring wrong outcome
        return lam / 2
    
    def expected_qber_z_basis(self) -> float:
        """
        Calculate expected QBER for Z-basis measurements.
        
        Z-basis is unaffected by phase damping.
        
        Returns:
            0 (no error in Z-basis)
        """
        return 0.0
    
    def coherence_factor(self) -> float:
        """
        Calculate the remaining coherence after channel.
        
        Returns:
            Coherence factor (0 to 1)
        """
        return np.sqrt(1 - self.dephasing_probability)
    
    @staticmethod
    def from_dephasing_time(
        time_ns: float,
        T2_ns: float = 100000
    ) -> 'PhaseDampingChannel':
        """
        Create channel based on T2 dephasing time.
        
        Args:
            time_ns: Transmission/storage time in nanoseconds
            T2_ns: Dephasing time T2 in nanoseconds
            
        Returns:
            PhaseDampingChannel with appropriate dephasing
        """
        lam = 1 - np.exp(-time_ns / T2_ns)
        return PhaseDampingChannel(dephasing_probability=lam)
    
    @staticmethod
    def from_T1_T2(
        T1_ns: float,
        T2_ns: float,
        time_ns: float
    ) -> Tuple['PhaseDampingChannel', float]:
        """
        Create channel from T1 and T2 times.
        
        Pure dephasing is related to T1 and T2 by:
        1/T2 = 1/(2T1) + 1/Tφ
        
        Args:
            T1_ns: Relaxation time
            T2_ns: Total dephasing time
            time_ns: Evolution time
            
        Returns:
            Tuple of (PhaseDampingChannel, pure dephasing rate)
        """
        # Pure dephasing rate
        T_phi_inv = 1/T2_ns - 1/(2*T1_ns)
        
        if T_phi_inv <= 0:
            # T2-limited by T1
            return PhaseDampingChannel(0.0), 0.0
        
        T_phi = 1 / T_phi_inv
        lam = 1 - np.exp(-time_ns / T_phi)
        
        return PhaseDampingChannel(lam), T_phi_inv
    
    def apply_to_state(self, state_vector: np.ndarray) -> np.ndarray:
        """
        Apply phase damping to a state vector.
        
        Args:
            state_vector: Input state [α, β]
            
        Returns:
            Density matrix after channel action
        """
        rho_in = np.outer(state_vector, np.conj(state_vector))
        K0, K1 = self.kraus_operators()
        
        rho_out = K0 @ rho_in @ K0.conj().T + K1 @ rho_in @ K1.conj().T
        
        return rho_out
    
    def combined_with_amplitude_damping(
        self,
        amplitude_damping: float
    ) -> 'CombinedRelaxationChannel':
        """
        Combine with amplitude damping for full T1/T2 model.
        
        Args:
            amplitude_damping: Amplitude damping probability
            
        Returns:
            CombinedRelaxationChannel
        """
        from src.noise_models.amplitude_damping import AmplitudeDampingChannel
        
        ad_channel = AmplitudeDampingChannel(amplitude_damping)
        return CombinedRelaxationChannel(ad_channel, self)
    
    def __repr__(self) -> str:
        return f"PhaseDampingChannel(λ={self.dephasing_probability})"


class CombinedRelaxationChannel:
    """
    Combined amplitude and phase damping channel.
    
    Models complete T1/T2 relaxation behavior.
    """
    
    def __init__(self, amplitude_channel, phase_channel):
        self.amplitude_channel = amplitude_channel
        self.phase_channel = phase_channel
    
    @property
    def name(self) -> str:
        return "CombinedRelaxation"
    
    def get_noise_model(self) -> NoiseModel:
        """Combine both noise models."""
        from qiskit_aer.noise.errors import amplitude_damping_error, phase_damping_error
        
        noise_model = NoiseModel()
        
        # Get error parameters
        gamma = self.amplitude_channel.damping_probability
        lam = self.phase_channel.dephasing_probability
        
        # Create combined error (apply amplitude first, then phase)
        ad_error = amplitude_damping_error(gamma)
        pd_error = phase_damping_error(lam)
        
        combined_error = ad_error.compose(pd_error)
        
        noise_model.add_all_qubit_quantum_error(combined_error, ['id', 'u1', 'u2', 'u3', 'h', 'x', 'y', 'z'])
        
        return noise_model
