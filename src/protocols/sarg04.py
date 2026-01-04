"""
SARG04 Protocol Implementation.

The SARG04 protocol, proposed by Scarani, Acín, Ribordy, and Gisin in 2004,
is a modification of BB84 designed to be more resistant to Photon Number
Splitting (PNS) attacks. It uses the same four quantum states as BB84 but
with a different classical post-processing step.

Key Difference from BB84:
Instead of announcing the basis, Alice announces a pair of non-orthogonal
states, one of which is the actual sent state. Bob can only determine the
bit if his measurement basis is orthogonal to the other state in the pair.

Protocol Steps:
1. Alice randomly prepares one of four states: |0⟩, |1⟩, |+⟩, |-⟩
2. Bob randomly measures in Z or X basis
3. Alice announces a pair of non-orthogonal states (not the basis!)
4. Bob can determine the bit only for certain measurement outcomes
5. This provides resistance against PNS attacks

References:
    Scarani, V., Acín, A., Ribordy, G., & Gisin, N. (2004).
    "Quantum cryptography protocols robust against photon number 
    splitting attacks for weak laser pulse implementations."
    Physical Review Letters, 92(5), 057901.
"""

from typing import Tuple, Optional, List, Dict
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator

from src.protocols.base_protocol import BaseQKDProtocol, QKDResult


class SARG04Protocol(BaseQKDProtocol):
    """
    Implementation of the SARG04 Quantum Key Distribution protocol.
    
    SARG04 uses the same four states as BB84 but with different
    post-processing that provides resistance to PNS attacks.
    
    States:
    - |0⟩, |1⟩ (Z-basis)
    - |+⟩, |-⟩ (X-basis)
    
    Announcement pairs (non-orthogonal):
    - {|0⟩, |+⟩}, {|0⟩, |-⟩}, {|1⟩, |+⟩}, {|1⟩, |-⟩}
    
    Attributes:
        key_length: Target length for the generated key
        
    Example:
        >>> sarg = SARG04Protocol(key_length=256)
        >>> result = sarg.run()
        >>> print(f"QBER: {result.qber:.4f}")
    """
    
    # State encodings
    STATES = {
        (0, 0): '|0⟩',   # Z-basis, bit 0
        (1, 0): '|1⟩',   # Z-basis, bit 1
        (0, 1): '|+⟩',   # X-basis, bit 0
        (1, 1): '|-⟩',   # X-basis, bit 1
    }
    
    # Non-orthogonal pairs for announcement
    # Key: (sent_bit, sent_basis) -> announced pair and associated bit value
    ANNOUNCEMENT_PAIRS = {
        # If Alice sent |0⟩ (bit=0, Z-basis), announce {|0⟩, |+⟩}
        (0, 0): {'pair': [(0, 0), (0, 1)], 'other_state': (0, 1)},
        # If Alice sent |1⟩ (bit=1, Z-basis), announce {|1⟩, |-⟩}
        (1, 0): {'pair': [(1, 0), (1, 1)], 'other_state': (1, 1)},
        # If Alice sent |+⟩ (bit=0, X-basis), announce {|+⟩, |0⟩}
        (0, 1): {'pair': [(0, 1), (0, 0)], 'other_state': (0, 0)},
        # If Alice sent |-⟩ (bit=1, X-basis), announce {|-⟩, |1⟩}
        (1, 1): {'pair': [(1, 1), (1, 0)], 'other_state': (1, 0)},
    }
    
    def __init__(
        self,
        key_length: int = 256,
        backend: Optional[AerSimulator] = None,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize the SARG04 protocol.
        
        Args:
            key_length: Target length for the generated key
            backend: Qiskit simulator backend
            verbose: Print progress information
            seed: Random seed for reproducibility
        """
        super().__init__(
            key_length=key_length,
            num_qubits=1,
            backend=backend,
            verbose=verbose,
            seed=seed
        )
        
        # Store announcement pairs
        self._announcements = None
    
    @property
    def protocol_name(self) -> str:
        """Return the protocol name."""
        return "SARG04"
    
    @property
    def num_bases(self) -> int:
        """Return the number of measurement bases (2 for SARG04)."""
        return 2
    
    def prepare_qubit(self, bit: int, basis: int) -> QuantumCircuit:
        """
        Prepare a qubit in the specified state and basis.
        
        Uses the same encoding as BB84:
        - Z-basis, bit=0: |0⟩
        - Z-basis, bit=1: |1⟩
        - X-basis, bit=0: |+⟩
        - X-basis, bit=1: |-⟩
        
        Args:
            bit: The bit value (0 or 1) to encode
            basis: The basis (0=Z, 1=X) to use
            
        Returns:
            QuantumCircuit with the prepared qubit
        """
        qr = QuantumRegister(1, 'q')
        cr = ClassicalRegister(1, 'c')
        qc = QuantumCircuit(qr, cr)
        
        if bit == 1:
            qc.x(qr[0])
        
        if basis == 1:  # X-basis
            qc.h(qr[0])
        
        return qc
    
    def measure_qubit(self, circuit: QuantumCircuit, basis: int) -> QuantumCircuit:
        """
        Add measurement operations in the specified basis.
        
        Args:
            circuit: The quantum circuit containing the qubit
            basis: The measurement basis (0=Z, 1=X)
            
        Returns:
            QuantumCircuit with measurement operations added
        """
        if basis == 1:  # X-basis
            circuit.h(0)
        
        circuit.measure(0, 0)
        return circuit
    
    def sift_keys(
        self,
        alice_bits: np.ndarray,
        alice_bases: np.ndarray,
        bob_bases: np.ndarray,
        bob_measurements: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform SARG04-specific key sifting.
        
        In SARG04, Bob keeps the bit when:
        1. Bob's measurement is in the basis orthogonal to the "other" state
        2. Bob's result is the orthogonal outcome to that other state
        
        This is more complex than BB84 and has ~25% sifting efficiency.
        
        Args:
            alice_bits: Alice's original bit string
            alice_bases: Alice's choice of bases
            bob_bases: Bob's choice of bases
            bob_measurements: Bob's measurement results
            
        Returns:
            Tuple of (Alice's sifted key, Bob's sifted key)
        """
        conclusive_mask = np.zeros(len(alice_bits), dtype=bool)
        bob_determined_bits = np.zeros(len(alice_bits), dtype=int)
        
        for i in range(len(alice_bits)):
            alice_bit = alice_bits[i]
            alice_basis = alice_bases[i]
            bob_basis = bob_bases[i]
            bob_result = bob_measurements[i]
            
            # Get the announcement for this transmission
            announcement = self.ANNOUNCEMENT_PAIRS[(alice_bit, alice_basis)]
            other_state = announcement['other_state']
            other_bit, other_basis = other_state
            
            # Bob can determine the bit if:
            # 1. He measures in the basis orthogonal to the "other" state
            # 2. His result rules out the "other" state
            
            if bob_basis == other_basis:
                # Bob measured in the same basis as the other state
                # He can determine if his result is orthogonal to the other state
                if bob_result != other_bit:
                    conclusive_mask[i] = True
                    # If the other state is ruled out, Alice sent the actual state
                    bob_determined_bits[i] = alice_bit
        
        alice_sifted = alice_bits[conclusive_mask]
        bob_sifted = bob_determined_bits[conclusive_mask]
        
        return alice_sifted, bob_sifted
    
    def run(
        self,
        noise_model=None,
        eavesdropper=None,
        shots: int = 1
    ) -> QKDResult:
        """
        Execute the SARG04 protocol.
        
        Args:
            noise_model: Optional noise model
            eavesdropper: Optional eavesdropper attack
            shots: Number of measurement shots
            
        Returns:
            QKDResult containing protocol results
        """
        import time
        start_time = time.time()
        
        # SARG04 has ~25% sifting efficiency
        raw_length = int(self.key_length * 5)
        
        self._alice_bits = np.random.randint(0, 2, raw_length)
        self._alice_bases = np.random.randint(0, 2, raw_length)
        self._bob_bases = np.random.randint(0, 2, raw_length)
        
        # Quantum transmission
        self._bob_measurements = self._quantum_transmission(
            self._alice_bits,
            self._alice_bases,
            self._bob_bases,
            noise_model=noise_model,
            eavesdropper=eavesdropper,
            shots=shots
        )
        
        # Generate announcements
        self._announcements = [
            self.ANNOUNCEMENT_PAIRS[(self._alice_bits[i], self._alice_bases[i])]
            for i in range(raw_length)
        ]
        
        # Sifting
        alice_sifted, bob_sifted = self.sift_keys(
            self._alice_bits,
            self._alice_bases,
            self._bob_bases,
            self._bob_measurements
        )
        
        # Error estimation
        qber = self._estimate_qber(alice_sifted, bob_sifted)
        
        # Truncate to desired length
        final_length = min(len(alice_sifted), self.key_length)
        alice_key = alice_sifted[:final_length]
        bob_key = bob_sifted[:final_length]
        
        execution_time = time.time() - start_time
        
        if self.verbose:
            print(f"\n{self.protocol_name} Protocol Results:")
            print(f"  Raw bits transmitted: {raw_length}")
            print(f"  Sifted key length: {len(alice_sifted)}")
            print(f"  Sifting efficiency: {len(alice_sifted)/raw_length:.2%}")
            print(f"  Final key length: {final_length}")
            print(f"  QBER: {qber:.4f}")
        
        return QKDResult(
            alice_key=alice_key,
            bob_key=bob_key,
            raw_key_length=raw_length,
            sifted_key_length=len(alice_sifted),
            final_key_length=final_length,
            qber=qber,
            execution_time=execution_time,
            protocol_name=self.protocol_name,
            additional_info={
                "sifting_efficiency": len(alice_sifted) / raw_length,
                "pns_resistant": True
            }
        )
    
    def is_pns_resistant(self) -> bool:
        """
        Check if the protocol provides PNS attack resistance.
        
        SARG04 is designed to be resistant to Photon Number Splitting
        attacks, making it suitable for practical implementations with
        weak coherent pulse sources.
        
        Returns:
            True (SARG04 is PNS-resistant by design)
        """
        return True
    
    @staticmethod
    def theoretical_key_rate(qber: float) -> float:
        """
        Calculate the theoretical secure key rate for SARG04.
        
        SARG04 has lower efficiency than BB84 (~25% vs 50% sifting)
        but provides better resistance to PNS attacks.
        
        Args:
            qber: Quantum Bit Error Rate
            
        Returns:
            Theoretical secure key rate per transmitted qubit
        """
        if qber <= 0:
            return 0.25  # Maximum with 25% sifting
        if qber >= 0.5:
            return 0.0
        
        h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if 0 < x < 1 else 0
        
        sifting_rate = 0.25
        key_rate = sifting_rate * max(0, 1 - 2 * h(qber))
        
        return key_rate
    
    @staticmethod
    def compare_with_bb84(qber: float) -> Dict[str, float]:
        """
        Compare SARG04 key rate with BB84.
        
        Args:
            qber: Quantum Bit Error Rate
            
        Returns:
            Dictionary with key rates for both protocols
        """
        from src.protocols.bb84 import BB84Protocol
        
        return {
            "bb84_key_rate": BB84Protocol.theoretical_key_rate(qber),
            "sarg04_key_rate": SARG04Protocol.theoretical_key_rate(qber),
            "sarg04_advantage": "PNS resistance"
        }
