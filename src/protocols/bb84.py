"""
BB84 Protocol Implementation.

The BB84 protocol, proposed by Bennett and Brassard in 1984, is the first
and most well-known Quantum Key Distribution protocol. It uses four quantum
states in two conjugate bases (rectilinear and diagonal) to establish a
secure key between Alice and Bob.

Protocol Steps:
1. Alice randomly generates bits and bases
2. Alice encodes each bit in the chosen basis and sends to Bob
3. Bob randomly chooses measurement bases and measures
4. Alice and Bob publicly compare bases and keep matching ones
5. They estimate QBER and apply error correction/privacy amplification

States used:
- Rectilinear basis (Z): |0⟩ = bit 0, |1⟩ = bit 1
- Diagonal basis (X): |+⟩ = bit 0, |-⟩ = bit 1

References:
    Bennett, C. H., & Brassard, G. (1984). "Quantum cryptography: Public key
    distribution and coin tossing." Proceedings of IEEE International
    Conference on Computers, Systems and Signal Processing.
"""

from typing import Tuple, Optional
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator

from src.protocols.base_protocol import BaseQKDProtocol, QKDResult


class BB84Protocol(BaseQKDProtocol):
    """
    Implementation of the BB84 Quantum Key Distribution protocol.
    
    The BB84 protocol uses two mutually unbiased bases:
    - Z-basis (computational/rectilinear): |0⟩, |1⟩
    - X-basis (Hadamard/diagonal): |+⟩, |-⟩
    
    Attributes:
        key_length: Target length for the generated key
        num_decoy_states: Number of decoy states for PNS attack detection
        error_threshold: Maximum acceptable QBER before aborting
        
    Example:
        >>> bb84 = BB84Protocol(key_length=256)
        >>> result = bb84.run()
        >>> print(f"QBER: {result.qber:.4f}")
    """
    
    # Basis constants
    Z_BASIS = 0  # Computational basis (|0⟩, |1⟩)
    X_BASIS = 1  # Hadamard basis (|+⟩, |-⟩)
    
    def __init__(
        self,
        key_length: int = 256,
        num_decoy_states: int = 0,
        error_threshold: float = 0.11,
        backend: Optional[AerSimulator] = None,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize the BB84 protocol.
        
        Args:
            key_length: Target length for the generated key
            num_decoy_states: Number of decoy states for enhanced security
            error_threshold: Maximum QBER threshold (default 11% for unconditional security)
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
        self.num_decoy_states = num_decoy_states
        self.error_threshold = error_threshold
    
    @property
    def protocol_name(self) -> str:
        """Return the protocol name."""
        return "BB84"
    
    @property
    def num_bases(self) -> int:
        """Return the number of measurement bases (2 for BB84)."""
        return 2
    
    def prepare_qubit(self, bit: int, basis: int) -> QuantumCircuit:
        """
        Prepare a qubit in the specified state and basis.
        
        Encoding scheme:
        - Z-basis, bit=0: |0⟩ (no operation)
        - Z-basis, bit=1: |1⟩ (X gate)
        - X-basis, bit=0: |+⟩ (H gate)
        - X-basis, bit=1: |-⟩ (X then H gate)
        
        Args:
            bit: The bit value (0 or 1) to encode
            basis: The basis (0=Z, 1=X) to use for encoding
            
        Returns:
            QuantumCircuit with the prepared qubit
        """
        qr = QuantumRegister(1, 'q')
        cr = ClassicalRegister(1, 'c')
        qc = QuantumCircuit(qr, cr)
        
        # Encode the bit value
        if bit == 1:
            qc.x(qr[0])
        
        # Change basis if using X-basis
        if basis == self.X_BASIS:
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
        # Change to Z-basis before measurement if needed
        if basis == self.X_BASIS:
            circuit.h(0)
        
        # Measure in computational basis
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
        Perform key sifting to extract bits where bases match.
        
        In BB84, Alice and Bob publicly announce their basis choices
        and keep only the bits where they used the same basis.
        Expected sifting efficiency: 50%
        
        Args:
            alice_bits: Alice's original bit string
            alice_bases: Alice's choice of bases
            bob_bases: Bob's choice of bases
            bob_measurements: Bob's measurement results
            
        Returns:
            Tuple of (Alice's sifted key, Bob's sifted key)
        """
        # Find positions where bases match
        matching_bases = alice_bases == bob_bases
        
        # Extract bits at matching positions
        alice_sifted = alice_bits[matching_bases]
        bob_sifted = bob_measurements[matching_bases]
        
        return alice_sifted, bob_sifted
    
    def run_with_decoy(
        self,
        noise_model=None,
        eavesdropper=None,
        shots: int = 1
    ) -> QKDResult:
        """
        Run BB84 with decoy state protocol for enhanced security.
        
        The decoy state protocol helps detect photon number splitting (PNS)
        attacks by varying the intensity of transmitted pulses.
        
        Args:
            noise_model: Optional noise model
            eavesdropper: Optional eavesdropper
            shots: Number of measurement shots
            
        Returns:
            QKDResult with additional decoy state information
        """
        # Run base protocol
        result = self.run(
            noise_model=noise_model,
            eavesdropper=eavesdropper,
            shots=shots
        )
        
        if self.num_decoy_states > 0:
            # Add decoy state analysis
            decoy_qber = self._analyze_decoy_states()
            result.additional_info["decoy_qber"] = decoy_qber
            result.additional_info["num_decoy_states"] = self.num_decoy_states
        
        return result
    
    def _analyze_decoy_states(self) -> float:
        """
        Analyze decoy states to detect PNS attacks.
        
        Returns:
            QBER estimated from decoy state analysis
        """
        # Simplified decoy state analysis
        # In practice, this would compare error rates across different intensities
        decoy_indices = np.random.choice(
            len(self._alice_bits),
            min(self.num_decoy_states, len(self._alice_bits)),
            replace=False
        )
        
        if len(decoy_indices) == 0:
            return 0.0
        
        # Calculate error rate in decoy states
        matching = self._alice_bases[decoy_indices] == self._bob_bases[decoy_indices]
        if np.sum(matching) == 0:
            return 0.0
            
        errors = np.sum(
            self._alice_bits[decoy_indices][matching] != 
            self._bob_measurements[decoy_indices][matching]
        )
        
        return errors / np.sum(matching)
    
    def is_secure(self, qber: float) -> bool:
        """
        Check if the estimated QBER indicates a secure channel.
        
        For BB84, the theoretical security threshold is ~11% QBER.
        Above this threshold, an eavesdropper could potentially have
        enough information to compromise the key.
        
        Args:
            qber: Quantum Bit Error Rate
            
        Returns:
            True if QBER is below the security threshold
        """
        return qber < self.error_threshold
    
    @staticmethod
    def theoretical_key_rate(qber: float, sifting_rate: float = 0.5) -> float:
        """
        Calculate the theoretical secure key rate.
        
        The asymptotic secret key rate for BB84 is:
        r = sifting_rate * [1 - h(qber) - h(qber)]
        
        where h(x) is the binary entropy function.
        
        Args:
            qber: Quantum Bit Error Rate
            sifting_rate: Fraction of bits kept after sifting (default 0.5)
            
        Returns:
            Theoretical secure key rate per transmitted qubit
        """
        if qber <= 0:
            return sifting_rate
        if qber >= 0.5:
            return 0.0
        
        # Binary entropy function
        h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if 0 < x < 1 else 0
        
        # Secret key rate formula
        key_rate = sifting_rate * max(0, 1 - 2 * h(qber))
        
        return key_rate
