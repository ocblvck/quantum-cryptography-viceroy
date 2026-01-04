"""
Realistic Fiber Optic Channel Model.

This module provides a comprehensive noise model for fiber-optic
quantum communication channels, incorporating multiple physical effects:

1. Fiber Loss (attenuation)
2. Polarization Mode Dispersion (PMD)
3. Chromatic Dispersion
4. Depolarization from fiber imperfections
5. Dark counts in detectors
6. Detector efficiency

This is designed for realistic QKD simulation and benchmarking.

References:
    - Gisin, N., et al. (2002). "Quantum cryptography." Reviews of Modern Physics.
    - Xu, F., et al. (2020). "Secure quantum key distribution with realistic devices."
"""

from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import (
    depolarizing_error,
    amplitude_damping_error,
    phase_damping_error
)


@dataclass
class FiberParameters:
    """Physical parameters for fiber optic channel."""
    
    length_km: float = 50.0
    attenuation_db_per_km: float = 0.2  # Standard telecom fiber
    pmd_coefficient: float = 0.1  # ps/√km
    chromatic_dispersion: float = 17.0  # ps/(nm·km)
    wavelength_nm: float = 1550.0  # Telecom C-band
    
    def total_loss_db(self) -> float:
        """Calculate total fiber loss in dB."""
        return self.length_km * self.attenuation_db_per_km
    
    def transmission(self) -> float:
        """Calculate transmission probability."""
        return 10 ** (-self.total_loss_db() / 10)


@dataclass
class DetectorParameters:
    """Single-photon detector parameters."""
    
    efficiency: float = 0.15  # Detection efficiency
    dark_count_rate: float = 100  # Dark counts per second
    timing_jitter_ps: float = 50  # Timing jitter
    dead_time_ns: float = 50  # Recovery time
    afterpulse_probability: float = 0.02


class RealisticFiberChannel:
    """
    Realistic fiber optic quantum channel model.
    
    Combines multiple noise sources to simulate practical
    QKD implementations over optical fiber.
    
    Attributes:
        fiber: FiberParameters instance
        detector: DetectorParameters instance
        
    Example:
        >>> fiber = FiberParameters(length_km=100)
        >>> detector = DetectorParameters(efficiency=0.1)
        >>> channel = RealisticFiberChannel(fiber, detector)
        >>> noise_model = channel.get_noise_model()
    """
    
    def __init__(
        self,
        fiber: Optional[FiberParameters] = None,
        detector: Optional[DetectorParameters] = None,
        extra_loss_db: float = 0.0,
        misalignment_rad: float = 0.0,
        seed: Optional[int] = None
    ):
        """
        Initialize the realistic fiber channel.
        
        Args:
            fiber: Fiber parameters
            detector: Detector parameters
            extra_loss_db: Additional system losses
            misalignment_rad: Polarization misalignment
            seed: Random seed
        """
        self.fiber = fiber or FiberParameters()
        self.detector = detector or DetectorParameters()
        self.extra_loss_db = extra_loss_db
        self.misalignment_rad = misalignment_rad
        self.seed = seed
        
        self._noise_model = None
    
    @property
    def name(self) -> str:
        """Return the channel name."""
        return f"RealisticFiber_{self.fiber.length_km}km"
    
    def total_transmission(self) -> float:
        """
        Calculate total system transmission.
        
        Includes fiber loss, extra losses, and detector efficiency.
        
        Returns:
            Total transmission probability
        """
        fiber_trans = self.fiber.transmission()
        extra_trans = 10 ** (-self.extra_loss_db / 10)
        detector_eff = self.detector.efficiency
        
        return fiber_trans * extra_trans * detector_eff
    
    def effective_error_probability(self) -> float:
        """
        Calculate effective error probability from all sources.
        
        Returns:
            Combined error probability
        """
        # Depolarization from fiber
        depol = self._depolarization_probability()
        
        # Dark count contribution to errors
        dark = self._dark_count_error_rate()
        
        # Misalignment contribution
        misalign = self._misalignment_error()
        
        # Combine (approximately independent)
        return min(0.5, depol + dark + misalign)
    
    def _depolarization_probability(self) -> float:
        """Calculate depolarization from fiber effects."""
        # Simple model: depolarization increases with length
        # and PMD coefficient
        pmd = self.fiber.pmd_coefficient * np.sqrt(self.fiber.length_km)
        
        # Convert PMD to depolarization probability
        # (simplified model)
        depol = 0.001 * pmd
        
        return min(0.5, depol)
    
    def _dark_count_error_rate(self) -> float:
        """Calculate error rate from dark counts."""
        # Gate time (detection window)
        gate_time_s = 1e-9  # 1 ns typical
        
        # Dark count probability per gate
        p_dark = self.detector.dark_count_rate * gate_time_s
        
        # Total transmission (signal probability)
        p_signal = self.total_transmission()
        
        if p_signal + p_dark == 0:
            return 0.0
        
        # Error rate: dark counts cause 50% errors
        error_rate = 0.5 * p_dark / (p_signal + p_dark)
        
        return error_rate
    
    def _misalignment_error(self) -> float:
        """Calculate error from polarization misalignment."""
        return 0.5 * np.sin(self.misalignment_rad) ** 2
    
    def get_noise_model(self) -> NoiseModel:
        """
        Create a comprehensive NoiseModel.
        
        Returns:
            Qiskit NoiseModel combining all effects
        """
        if self._noise_model is not None:
            return self._noise_model
        
        noise_model = NoiseModel()
        
        # Depolarizing component
        depol_prob = self._depolarization_probability()
        if depol_prob > 0:
            depol_error = depolarizing_error(depol_prob, 1)
            noise_model.add_all_qubit_quantum_error(
                depol_error, ['h', 'x', 'y', 'z', 'id']
            )
        
        # Amplitude damping (photon loss)
        loss_prob = 1 - self.fiber.transmission()
        if loss_prob > 0 and loss_prob < 1:
            amp_error = amplitude_damping_error(loss_prob * 0.1)  # Scaled
            noise_model.add_all_qubit_quantum_error(
                amp_error, ['id']
            )
        
        # Phase damping (dephasing)
        phase_prob = self._depolarization_probability() * 0.5
        if phase_prob > 0 and phase_prob < 1:
            phase_error = phase_damping_error(phase_prob)
            noise_model.add_all_qubit_quantum_error(
                phase_error, ['h']
            )
        
        self._noise_model = noise_model
        return noise_model
    
    def expected_qber(self) -> float:
        """
        Calculate expected QBER for BB84 over this channel.
        
        Returns:
            Expected QBER
        """
        return self.effective_error_probability()
    
    def secure_key_rate(self, source_rate_hz: float = 1e9) -> float:
        """
        Calculate achievable secure key rate.
        
        Args:
            source_rate_hz: Source repetition rate
            
        Returns:
            Secure key rate in bits per second
        """
        transmission = self.total_transmission()
        qber = self.expected_qber()
        
        # Sifting efficiency (50% for BB84)
        sift = 0.5
        
        # Binary entropy
        if qber <= 0:
            h_qber = 0
        elif qber >= 0.5:
            return 0.0
        else:
            h_qber = -qber * np.log2(qber) - (1-qber) * np.log2(1-qber)
        
        # Secret key fraction
        key_fraction = max(0, 1 - 2 * h_qber)
        
        # Key rate
        key_rate = source_rate_hz * transmission * sift * key_fraction
        
        return key_rate
    
    def maximum_distance(
        self,
        min_key_rate: float = 1.0,
        source_rate_hz: float = 1e9
    ) -> float:
        """
        Calculate maximum secure transmission distance.
        
        Args:
            min_key_rate: Minimum acceptable key rate (bps)
            source_rate_hz: Source repetition rate
            
        Returns:
            Maximum distance in km
        """
        # Binary search for maximum distance
        low, high = 0, 1000
        
        while high - low > 0.1:
            mid = (low + high) / 2
            
            # Create channel at test distance
            test_fiber = FiberParameters(
                length_km=mid,
                attenuation_db_per_km=self.fiber.attenuation_db_per_km
            )
            test_channel = RealisticFiberChannel(
                fiber=test_fiber,
                detector=self.detector
            )
            
            rate = test_channel.secure_key_rate(source_rate_hz)
            
            if rate >= min_key_rate:
                low = mid
            else:
                high = mid
        
        return low
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of channel parameters and performance.
        
        Returns:
            Dictionary with channel summary
        """
        return {
            "fiber_length_km": self.fiber.length_km,
            "total_loss_db": self.fiber.total_loss_db(),
            "total_transmission": self.total_transmission(),
            "expected_qber": self.expected_qber(),
            "secure_key_rate_bps": self.secure_key_rate(),
            "detector_efficiency": self.detector.efficiency,
            "dark_count_rate": self.detector.dark_count_rate
        }
    
    @classmethod
    def create_metropolitan(cls) -> 'RealisticFiberChannel':
        """Create channel typical for metropolitan QKD (20-50 km)."""
        return cls(
            fiber=FiberParameters(length_km=30, attenuation_db_per_km=0.2),
            detector=DetectorParameters(efficiency=0.15)
        )
    
    @classmethod
    def create_intercity(cls) -> 'RealisticFiberChannel':
        """Create channel typical for intercity QKD (100-200 km)."""
        return cls(
            fiber=FiberParameters(length_km=150, attenuation_db_per_km=0.18),
            detector=DetectorParameters(efficiency=0.2)
        )
    
    @classmethod
    def create_laboratory(cls) -> 'RealisticFiberChannel':
        """Create low-noise laboratory channel."""
        return cls(
            fiber=FiberParameters(length_km=1, attenuation_db_per_km=0.2),
            detector=DetectorParameters(efficiency=0.9, dark_count_rate=10)
        )
    
    def __repr__(self) -> str:
        return (f"RealisticFiberChannel(length={self.fiber.length_km}km, "
                f"loss={self.fiber.total_loss_db():.1f}dB)")
