"""
Trojan Horse Attack Implementation.

The Trojan Horse attack is a side-channel attack that exploits imperfections
in the physical implementation of QKD systems. Eve sends bright probe pulses
into Alice's or Bob's equipment and analyzes the reflected light to gain
information about their settings.

Attack Variants:
1. Large Pulse Attack: Eve sends bright pulses and analyzes reflections
2. Phase Remapping Attack: Exploits phase-dependent losses
3. Detector Blinding: Blinds single-photon detectors with bright light

Attack Description:
1. Eve sends probe light into Alice's modulator
2. Light interacts with the modulator and reflects back
3. Eve analyzes reflection to learn modulator setting (basis/bit)
4. Eve can then perform targeted intercept-resend or PNS attacks

Countermeasures:
- Optical isolators and circulators
- Watchdog detectors
- Randomized modulator timing
- Intensity monitoring

References:
    Gisin, N., et al. (2006). "Trojan-horse attacks on quantum-key-
    distribution systems." Physical Review A, 73(2), 022320.
"""

from typing import Optional, List, Dict, Tuple
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator

from src.attacks.base_attack import BaseAttack, AttackResult


class TrojanHorseAttack(BaseAttack):
    """
    Implementation of the Trojan Horse side-channel attack.
    
    Eve sends probe pulses to learn Alice's modulator settings,
    enabling a more effective intercept-resend attack.
    
    Attributes:
        probe_intensity: Intensity of Eve's probe pulses
        reflection_efficiency: Efficiency of reflection from target
        information_gain: Bits of information gained per probe
        
    Example:
        >>> eve = TrojanHorseAttack(probe_intensity=1e6)
        >>> result = eve.get_results()
        >>> print(f"Basis knowledge: {result.additional_info['basis_knowledge']:.2%}")
    """
    
    def __init__(
        self,
        probe_intensity: float = 1e6,
        reflection_efficiency: float = 0.01,
        detector_sensitivity: float = 0.1,
        backend: Optional[AerSimulator] = None,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize the Trojan Horse attack.
        
        Args:
            probe_intensity: Number of photons in probe pulse
            reflection_efficiency: Fraction of light reflected back
            detector_sensitivity: Alice's watchdog detector sensitivity
            backend: Qiskit simulator
            verbose: Print attack information
            seed: Random seed
        """
        super().__init__(
            attack_probability=1.0,
            verbose=verbose,
            seed=seed
        )
        self.probe_intensity = probe_intensity
        self.reflection_efficiency = reflection_efficiency
        self.detector_sensitivity = detector_sensitivity
        self.backend = backend or AerSimulator()
        
        # Track learned information
        self._learned_bases = []
        self._learned_bits = []
        self._probe_detections = 0
    
    @property
    def attack_name(self) -> str:
        """Return the attack name."""
        return "Trojan Horse"
    
    def probe_modulator(self, true_basis: int, true_bit: int) -> Tuple[int, int]:
        """
        Probe Alice's modulator to learn settings.
        
        Args:
            true_basis: Alice's actual basis setting
            true_bit: Alice's actual bit value
            
        Returns:
            Tuple of (learned_basis, learned_bit) - may be incorrect
        """
        # Calculate number of reflected photons
        n_reflected = self.probe_intensity * self.reflection_efficiency
        
        # Check if Alice's watchdog detects the probe
        if np.random.random() < self._detection_probability_single():
            self._probe_detections += 1
            if self.verbose:
                print("[Eve] Probe detected by Alice's watchdog!")
        
        # Information gain depends on reflected photons
        # More photons = more information
        snr = n_reflected / np.sqrt(n_reflected + 100)  # With dark counts
        
        # Probability of correctly learning each setting
        p_correct = min(0.99, 0.5 + 0.5 * np.tanh(snr / 10))
        
        # Eve's guess
        if np.random.random() < p_correct:
            learned_basis = true_basis
        else:
            learned_basis = 1 - true_basis
        
        if np.random.random() < p_correct:
            learned_bit = true_bit
        else:
            learned_bit = 1 - true_bit
        
        return learned_basis, learned_bit
    
    def intercept(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """
        Perform Trojan Horse attack on a quantum circuit.
        
        Eve probes Alice's equipment to learn the encoding,
        then performs targeted intercept-resend if successful.
        
        Args:
            circuit: Original quantum circuit from Alice
            
        Returns:
            Potentially modified quantum circuit
        """
        self._num_intercepted += 1
        
        # For simulation, we need to know Alice's actual settings
        # In a real attack, Eve probes the physical equipment
        # Here we'll simulate imperfect information extraction
        
        # Eve attempts to extract information
        # We simulate by assuming Eve learns with some probability
        info_gain = self._calculate_info_gain()
        
        self._intercepted_bits.append(info_gain)
        
        if self.verbose and self._num_intercepted % 100 == 0:
            print(f"[Eve] Probed {self._num_intercepted} qubits")
        
        return circuit  # Trojan horse doesn't modify the quantum state
    
    def _calculate_info_gain(self) -> float:
        """
        Calculate information gained from a single probe.
        
        Returns:
            Bits of information (0 to 1)
        """
        n_reflected = self.probe_intensity * self.reflection_efficiency
        
        if n_reflected < 1:
            return 0.0
        
        # Shannon information based on SNR
        snr = n_reflected / np.sqrt(n_reflected + 100)
        p_correct = min(0.99, 0.5 + 0.5 * np.tanh(snr / 10))
        
        # Binary entropy
        if p_correct <= 0.5 or p_correct >= 1.0:
            return 0.0
        
        h = -p_correct * np.log2(p_correct) - (1-p_correct) * np.log2(1-p_correct)
        return 1 - h
    
    def _detection_probability_single(self) -> float:
        """
        Calculate probability of probe being detected per probe.
        
        Returns:
            Detection probability
        """
        # Detection depends on probe intensity and detector sensitivity
        incoming_photons = self.probe_intensity
        threshold = 1000 / self.detector_sensitivity
        
        if incoming_photons > threshold:
            return min(0.99, incoming_photons / (10 * threshold))
        return 0.0
    
    def get_results(self) -> AttackResult:
        """
        Get the results of the Trojan Horse attack.
        
        Returns:
            AttackResult with attack statistics
        """
        info_gains = np.array(self._intercepted_bits)
        total_info = np.sum(info_gains)
        
        return AttackResult(
            attack_name=self.attack_name,
            eve_information=total_info,
            induced_qber=0.0,  # Side channel doesn't affect quantum channel
            detection_probability=self._overall_detection_probability(),
            intercepted_bits=np.array([int(ig > 0.5) for ig in info_gains]),
            additional_info={
                "probe_intensity": self.probe_intensity,
                "reflection_efficiency": self.reflection_efficiency,
                "num_probes": self._num_intercepted,
                "probe_detections": self._probe_detections,
                "avg_info_per_probe": np.mean(info_gains) if len(info_gains) > 0 else 0,
                "basis_knowledge": self._basis_knowledge_fraction()
            }
        )
    
    def _overall_detection_probability(self) -> float:
        """
        Calculate overall probability of attack being detected.
        
        Returns:
            Detection probability
        """
        p_single = self._detection_probability_single()
        if self._num_intercepted == 0:
            return p_single
        
        # Probability of at least one detection
        return 1 - (1 - p_single) ** self._num_intercepted
    
    def _basis_knowledge_fraction(self) -> float:
        """
        Calculate fraction of bases Eve learns.
        
        Returns:
            Fraction of bases correctly learned
        """
        avg_info = self._calculate_info_gain()
        return 0.5 + 0.5 * avg_info  # 50% is random guessing
    
    def reset(self):
        """Reset attack state."""
        super().reset()
        self._learned_bases = []
        self._learned_bits = []
        self._probe_detections = 0
    
    @staticmethod
    def theoretical_induced_qber() -> float:
        """
        Trojan Horse doesn't directly induce QBER.
        
        Returns:
            0.0 (side channel attack)
        """
        return 0.0
    
    @staticmethod
    def required_isolation_db(
        acceptable_leakage: float,
        probe_intensity: float
    ) -> float:
        """
        Calculate required optical isolation to prevent attack.
        
        Args:
            acceptable_leakage: Maximum acceptable photon leakage
            probe_intensity: Eve's probe intensity
            
        Returns:
            Required isolation in dB
        """
        if acceptable_leakage <= 0:
            return float('inf')
        
        required_attenuation = probe_intensity / acceptable_leakage
        return 10 * np.log10(required_attenuation)


class DetectorBlindingAttack(TrojanHorseAttack):
    """
    Detector blinding attack - a variant of Trojan Horse.
    
    Eve sends bright light to blind Bob's single-photon detectors,
    then sends classical light pulses to control their clicks.
    """
    
    def __init__(
        self,
        blinding_power: float = 1e-3,  # mW
        trigger_pulse_energy: float = 1e-15,  # J
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize detector blinding attack.
        
        Args:
            blinding_power: CW blinding power (mW)
            trigger_pulse_energy: Energy to trigger detector click
            verbose: Print information
            seed: Random seed
        """
        super().__init__(
            probe_intensity=blinding_power * 1e6,  # Convert to photon-like units
            verbose=verbose,
            seed=seed
        )
        self.blinding_power = blinding_power
        self.trigger_pulse_energy = trigger_pulse_energy
    
    @property
    def attack_name(self) -> str:
        return "Detector Blinding"
    
    def get_results(self) -> AttackResult:
        """Get attack results with blinding-specific info."""
        result = super().get_results()
        result.additional_info["blinding_power_mW"] = self.blinding_power
        result.additional_info["trigger_energy_J"] = self.trigger_pulse_energy
        result.additional_info["full_control"] = self._has_full_control()
        return result
    
    def _has_full_control(self) -> bool:
        """
        Check if Eve has full control of Bob's detectors.
        
        Returns:
            True if blinding is successful
        """
        # Successful if blinding power > threshold
        threshold_power = 0.5e-3  # 0.5 mW typical threshold
        return self.blinding_power > threshold_power
