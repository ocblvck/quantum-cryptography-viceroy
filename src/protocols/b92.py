"""
B92 Protocol Implementation.

The B92 protocol, proposed by Charles Bennett in 1992, is a simplified
version of BB84 that uses only two non-orthogonal quantum states instead
of four. Despite using fewer states, it achieves the same level of security.

Key Insight:
Two non-orthogonal states cannot be reliably distinguished, providing
security against eavesdropping. Alice only uses |0⟩ and |+⟩ states.

Protocol Steps:
1. Alice sends |0⟩ for bit 0, |+⟩ for bit 1
2. Bob randomly measures in Z or X basis
3. Bob announces when he gets |1⟩ or |-⟩ (conclusive results)
4. Alice and Bob keep only conclusive measurements

States used:
- Bit 0: |0⟩ (Z-basis eigenstate)
- Bit 1: |+⟩ (X-basis eigenstate)

References:
    Bennett, C. H. (1992). "Quantum cryptography using any two nonorthogonal
    states." Physical Review Letters, 68(21), 3121.
"""

from typing import Tuple, Optional, List
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator

from src.protocols.base_protocol import BaseQKDProtocol, QKDResult


class B92Protocol(BaseQKDProtocol):
    """
    Implementation of the B92 Quantum Key Distribution protocol.
    
    B92 uses only two non-orthogonal quantum states:
    - |0⟩ represents bit 0
    - |+⟩ represents bit 1
    
    Security relies on the impossibility of distinguishing 
    non-orthogonal states with certainty.
    
    Attributes:
        key_length: Target length for the generated key
        
    Example:
        >>> b92 = B92Protocol(key_length=256)
        >>> result = b92.run()
        >>> print(f"QBER: {result.qber:.4f}")
    """
    
    def __init__(
        self,
        key_length: int = 256,
        backend: Optional[AerSimulator] = None,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize the B92 protocol.
        
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
        
        # Store conclusive measurement results for sifting
        self._conclusive_indices = None
    
    @property
    def protocol_name(self) -> str:
        """Return the protocol name."""
        return "B92"
    
    @property
    def num_bases(self) -> int:
        """Return the number of measurement bases (2 for B92)."""
        return 2
    
    def prepare_qubit(self, bit: int, basis: int = None) -> QuantumCircuit:
        """
        Prepare a qubit in the B92 encoding.
        
        In B92, Alice doesn't use a random basis - she encodes:
        - Bit 0 as |0⟩
        - Bit 1 as |+⟩
        
        The basis parameter is ignored for B92.
        
        Args:
            bit: The bit value (0 or 1) to encode
            basis: Ignored (included for interface compatibility)
            
        Returns:
            QuantumCircuit with the prepared qubit
        """
        qr = QuantumRegister(1, 'q')
        cr = ClassicalRegister(1, 'c')
        qc = QuantumCircuit(qr, cr)
        
        if bit == 0:
            # |0⟩ state - no operation needed
            pass
        else:
            # |+⟩ state - apply Hadamard
            qc.h(qr[0])
        
        return qc
    
    def measure_qubit(self, circuit: QuantumCircuit, basis: int) -> QuantumCircuit:
        """
        Add measurement operations in the specified basis.
        
        Bob measures in randomly chosen basis:
        - Z-basis: Conclusive if result is |1⟩ (means Alice sent |+⟩, so bit=1)
        - X-basis: Conclusive if result is |-⟩ (means Alice sent |0⟩, so bit=0)
        
        Args:
            circuit: The quantum circuit containing the qubit
            basis: The measurement basis (0=Z, 1=X)
            
        Returns:
            QuantumCircuit with measurement operations added
        """
        # Change to appropriate basis before measurement
        if basis == 1:  # X-basis
            circuit.h(0)
        
        # Measure in computational basis
        circuit.measure(0, 0)
        
        return circuit
    
    def sift_keys(
        self,
        alice_bits: np.ndarray,
        alice_bases: np.ndarray,  # Not used in B92 but kept for interface
        bob_bases: np.ndarray,
        bob_measurements: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform B92-specific key sifting.
        
        In B92, Bob announces positions where he got conclusive results:
        - Z-basis measurement yielding |1⟩: Conclusive, bit = 1
        - X-basis measurement yielding |-⟩ (encoded as 1): Conclusive, bit = 0
        
        Expected sifting efficiency: 25%
        
        Args:
            alice_bits: Alice's original bit string
            alice_bases: Not used (included for interface compatibility)
            bob_bases: Bob's choice of bases
            bob_measurements: Bob's measurement results
            
        Returns:
            Tuple of (Alice's sifted key, Bob's sifted key)
        """
        conclusive_mask = np.zeros(len(alice_bits), dtype=bool)
        bob_conclusive_bits = np.zeros(len(alice_bits), dtype=int)
        
        for i in range(len(alice_bits)):
            if bob_bases[i] == 0:  # Z-basis measurement
                # Conclusive if Bob measured |1⟩
                # This means Alice sent |+⟩, so bit = 1
                if bob_measurements[i] == 1:
                    conclusive_mask[i] = True
                    bob_conclusive_bits[i] = 1
            else:  # X-basis measurement
                # Conclusive if Bob measured |1⟩ (which represents |-⟩)
                # This means Alice sent |0⟩, so bit = 0
                if bob_measurements[i] == 1:
                    conclusive_mask[i] = True
                    bob_conclusive_bits[i] = 0
        
        self._conclusive_indices = np.where(conclusive_mask)[0]
        
        alice_sifted = alice_bits[conclusive_mask]
        bob_sifted = bob_conclusive_bits[conclusive_mask]
        
        return alice_sifted, bob_sifted
    
    def run(
        self,
        noise_model=None,
        eavesdropper=None,
        shots: int = 1
    ) -> QKDResult:
        """
        Execute the B92 protocol.
        
        Note: B92 has lower efficiency than BB84 (25% vs 50% sifting rate)
        but uses simpler state preparation.
        
        Args:
            noise_model: Optional noise model
            eavesdropper: Optional eavesdropper attack
            shots: Number of measurement shots
            
        Returns:
            QKDResult containing protocol results
        """
        import time
        start_time = time.time()
        
        # B92 needs more raw bits due to lower sifting efficiency
        raw_length = int(self.key_length * 5)  # ~25% sifting efficiency
        self._alice_bits = np.random.randint(0, 2, raw_length)
        self._alice_bases = np.zeros(raw_length, dtype=int)  # Dummy (not used)
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
            print(f"  Conclusive results: {len(alice_sifted)}")
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
                "num_conclusive": len(self._conclusive_indices)
            }
        )
    
    @staticmethod
    def theoretical_key_rate(qber: float) -> float:
        """
        Calculate the theoretical secure key rate for B92.
        
        B92 has a lower key rate than BB84 due to:
        1. Lower sifting efficiency (25% vs 50%)
        2. Higher sensitivity to certain attacks
        
        Args:
            qber: Quantum Bit Error Rate
            
        Returns:
            Theoretical secure key rate per transmitted qubit
        """
        if qber <= 0:
            return 0.25  # Maximum with 25% sifting
        if qber >= 0.25:
            return 0.0
        
        # Binary entropy
        h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if 0 < x < 1 else 0
        
        # B92 key rate (lower than BB84)
        sifting_rate = 0.25
        key_rate = sifting_rate * max(0, 1 - 2 * h(qber))
        
        return key_rate
