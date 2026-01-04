"""
Photon Number Splitting (PNS) Attack Implementation.

The PNS attack exploits a practical weakness in QKD implementations that use
weak coherent pulses (WCP) instead of true single-photon sources. When a pulse
contains multiple photons, Eve can split off extra photons, store them, and
measure after learning the basis information.

Attack Description:
1. Eve monitors the quantum channel for multi-photon pulses
2. When detected, Eve splits off one photon and stores it
3. Eve forwards the remaining photon(s) to Bob
4. After basis reconciliation, Eve measures her stored photons
5. Eve gains information without introducing errors

Why it works:
- WCP sources follow Poisson distribution
- Some pulses contain 2+ photons
- Splitting doesn't disturb the forwarded photon

Countermeasures:
- Decoy state protocols (vary pulse intensity)
- SARG04 protocol (different basis announcement)
- True single-photon sources

References:
    Brassard, G., et al. (2000). "Limitations on practical quantum 
    cryptography." Physical Review Letters, 85(6), 1330.
"""

from typing import Optional, List, Tuple
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator

from src.attacks.base_attack import BaseAttack, AttackResult


class PNSAttack(BaseAttack):
    """
    Implementation of the Photon Number Splitting attack.
    
    This attack is specific to weak coherent pulse implementations
    of QKD. Eve splits multi-photon pulses and stores photons for
    later measurement.
    
    Attributes:
        mean_photon_number: Mean photon number of Alice's source (μ)
        splitting_efficiency: Eve's photon splitting efficiency
        
    Example:
        >>> eve = PNSAttack(mean_photon_number=0.1)
        >>> result = eve.get_results()
        >>> print(f"Information gained: {result.eve_information:.4f} bits")
    """
    
    def __init__(
        self,
        mean_photon_number: float = 0.1,
        splitting_efficiency: float = 1.0,
        storage_efficiency: float = 1.0,
        backend: Optional[AerSimulator] = None,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize the PNS attack.
        
        Args:
            mean_photon_number: Alice's source mean photon number (μ)
            splitting_efficiency: Eve's ability to split photons
            storage_efficiency: Eve's quantum memory efficiency
            backend: Qiskit simulator
            verbose: Print attack information
            seed: Random seed
        """
        super().__init__(
            attack_probability=1.0,  # Eve always monitors
            verbose=verbose,
            seed=seed
        )
        self.mean_photon_number = mean_photon_number
        self.splitting_efficiency = splitting_efficiency
        self.storage_efficiency = storage_efficiency
        self.backend = backend or AerSimulator()
        
        # Track stored photons and basis announcements
        self._stored_photons = []  # List of stored quantum states
        self._stored_indices = []  # Indices of stored photons
        self._announced_bases = []  # Bases announced by Alice
    
    @property
    def attack_name(self) -> str:
        """Return the attack name."""
        return "Photon Number Splitting (PNS)"
    
    def sample_photon_number(self) -> int:
        """
        Sample from Poisson distribution to get photon number.
        
        Returns:
            Number of photons in the pulse
        """
        return np.random.poisson(self.mean_photon_number)
    
    def intercept(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """
        Attempt PNS attack on a quantum circuit.
        
        Eve checks if the pulse is multi-photon and splits if possible.
        
        Args:
            circuit: Original quantum circuit from Alice
            
        Returns:
            Circuit (potentially with reduced photon number)
        """
        self._num_intercepted += 1
        
        # Simulate photon number
        n_photons = self.sample_photon_number()
        
        if n_photons >= 2 and np.random.random() < self.splitting_efficiency:
            # Multi-photon pulse detected - split!
            if self.verbose:
                print(f"[Eve] Multi-photon pulse ({n_photons}) - splitting")
            
            # Eve stores the circuit state information
            # In real attack, Eve stores the actual photon
            self._stored_photons.append(circuit.copy())
            self._stored_indices.append(self._num_intercepted - 1)
            
            # Eve forwards the pulse (with one fewer photon conceptually)
            # In simulation, we just track that this happened
        
        return circuit
    
    def receive_basis_announcement(self, bases: np.ndarray):
        """
        Receive Alice's basis announcements after transmission.
        
        Eve uses this information to measure her stored photons.
        
        Args:
            bases: Array of Alice's basis choices
        """
        self._announced_bases = bases
        
        # Now Eve can measure stored photons in correct bases
        for idx in self._stored_indices:
            if idx < len(bases):
                correct_basis = bases[idx]
                # Eve measures in the correct basis
                self._measure_stored_photon(idx, correct_basis)
    
    def _measure_stored_photon(self, index: int, basis: int):
        """
        Measure a stored photon in the announced basis.
        
        Args:
            index: Index of the stored photon
            basis: Correct measurement basis
        """
        if index not in self._stored_indices:
            return
        
        # Find the stored circuit
        storage_idx = self._stored_indices.index(index)
        circuit = self._stored_photons[storage_idx]
        
        # Apply storage loss
        if np.random.random() > self.storage_efficiency:
            if self.verbose:
                print(f"[Eve] Photon {index} lost from storage")
            return
        
        # Measure in correct basis
        if basis == 1:  # X-basis
            circuit.h(0)
        
        if circuit.num_clbits == 0:
            circuit.add_register(ClassicalRegister(1, 'eve'))
        circuit.measure(0, 0)
        
        result = self.backend.run(circuit, shots=1).result()
        counts = result.get_counts()
        eve_bit = int(list(counts.keys())[0][-1])
        
        self._intercepted_bits.append(eve_bit)
        
        if self.verbose:
            print(f"[Eve] Measured stored photon {index}: bit = {eve_bit}")
    
    def get_results(self) -> AttackResult:
        """
        Get the results of the PNS attack simulation.
        
        Returns:
            AttackResult with attack statistics
        """
        return AttackResult(
            attack_name=self.attack_name,
            eve_information=len(self._intercepted_bits),
            induced_qber=0.0,  # PNS introduces no errors!
            detection_probability=self._detection_probability(),
            intercepted_bits=np.array(self._intercepted_bits),
            additional_info={
                "mean_photon_number": self.mean_photon_number,
                "multi_photon_fraction": self._multi_photon_probability(),
                "num_stored": len(self._stored_photons),
                "splitting_efficiency": self.splitting_efficiency,
                "storage_efficiency": self.storage_efficiency
            }
        )
    
    def _multi_photon_probability(self) -> float:
        """
        Calculate probability of multi-photon pulses.
        
        P(n >= 2) = 1 - P(0) - P(1)
        
        Returns:
            Probability of 2+ photons
        """
        mu = self.mean_photon_number
        p0 = np.exp(-mu)
        p1 = mu * np.exp(-mu)
        return 1 - p0 - p1
    
    def _detection_probability(self) -> float:
        """
        Calculate probability of detecting PNS attack.
        
        PNS is undetectable without decoy states!
        With decoy states, detection depends on comparison of
        yields at different intensities.
        
        Returns:
            Detection probability (0 without countermeasures)
        """
        # Standard PNS is undetectable without decoy states
        return 0.0
    
    def reset(self):
        """Reset attack state."""
        super().reset()
        self._stored_photons = []
        self._stored_indices = []
        self._announced_bases = []
    
    @staticmethod
    def theoretical_induced_qber() -> float:
        """
        PNS attack introduces no errors.
        
        Returns:
            0.0 (no errors introduced)
        """
        return 0.0
    
    @staticmethod
    def vulnerable_key_fraction(mean_photon_number: float) -> float:
        """
        Calculate fraction of key vulnerable to PNS attack.
        
        Without countermeasures, Eve can obtain all bits from
        multi-photon pulses.
        
        Args:
            mean_photon_number: Source's mean photon number
            
        Returns:
            Fraction of key Eve can obtain
        """
        mu = mean_photon_number
        # Probability of multi-photon
        p_multi = 1 - np.exp(-mu) - mu * np.exp(-mu)
        # Sifting efficiency
        sift = 0.5
        
        return p_multi / (mu * sift)
    
    @staticmethod
    def safe_distance_km(
        mean_photon_number: float,
        fiber_loss_db_per_km: float = 0.2
    ) -> float:
        """
        Calculate maximum safe transmission distance.
        
        Beyond this distance, Eve can block all single-photon pulses
        and only forward multi-photon pulses.
        
        Args:
            mean_photon_number: Source's mean photon number
            fiber_loss_db_per_km: Fiber attenuation
            
        Returns:
            Maximum safe distance in km
        """
        mu = mean_photon_number
        
        # Single photon probability
        p1 = mu * np.exp(-mu)
        # Multi-photon probability
        p_multi = 1 - np.exp(-mu) - p1
        
        if p1 <= 0 or p_multi <= 0:
            return float('inf')
        
        # Eve can block singles when channel loss equals p1/p_multi
        critical_transmission = p1 / p_multi
        critical_loss_db = -10 * np.log10(critical_transmission)
        
        return critical_loss_db / fiber_loss_db_per_km
