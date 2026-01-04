"""
E91 Protocol Implementation.

The E91 protocol, proposed by Artur Ekert in 1991, uses quantum entanglement
and Bell's inequality to establish secure key distribution. Unlike BB84 and B92,
E91 relies on the correlations of entangled particle pairs.

Key Insight:
When Alice and Bob share entangled pairs and measure in the same basis,
they get perfectly correlated results. Bell's inequality violations prove
the quantum nature and absence of eavesdropping.

Protocol Steps:
1. A source creates entangled pairs and sends one particle to each party
2. Alice and Bob randomly choose measurement bases
3. For matching bases, they get correlated bits for the key
4. For non-matching bases, they test Bell's inequality

States used:
- Entangled Bell state: |Φ+⟩ = (|00⟩ + |11⟩)/√2
- Three measurement bases at 0°, 45°, 90° angles

References:
    Ekert, A. K. (1991). "Quantum cryptography based on Bell's theorem."
    Physical Review Letters, 67(6), 661.
"""

from typing import Tuple, Optional, Dict, List
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator

from src.protocols.base_protocol import BaseQKDProtocol, QKDResult


class E91Protocol(BaseQKDProtocol):
    """
    Implementation of the E91 (Ekert) Quantum Key Distribution protocol.
    
    E91 uses entangled Bell pairs and Bell's inequality testing for security.
    Alice and Bob share maximally entangled |Φ+⟩ states.
    
    Measurement angles:
    - Alice: 0°, 45°, 90° (bases 0, 1, 2)
    - Bob: 45°, 90°, 135° (bases 0, 1, 2)
    
    Key is generated when Alice uses basis 2 (90°) and Bob uses basis 0 (45°)
    or Alice uses basis 0 (0°) and Bob uses basis 1 (90°).
    
    Attributes:
        key_length: Target length for the generated key
        bell_threshold: CHSH inequality violation threshold for security
        
    Example:
        >>> e91 = E91Protocol(key_length=256)
        >>> result = e91.run()
        >>> print(f"Bell parameter S: {result.additional_info['bell_parameter']:.4f}")
    """
    
    # Measurement angles in radians
    ALICE_ANGLES = [0, np.pi/4, np.pi/2]           # 0°, 45°, 90°
    BOB_ANGLES = [np.pi/4, np.pi/2, 3*np.pi/4]     # 45°, 90°, 135°
    
    # Matching basis pairs for key generation
    # (Alice basis, Bob basis) pairs that give anticorrelated results
    KEY_MATCHING_PAIRS = [(2, 0), (0, 1)]  # (90°, 45°) and (0°, 90°)
    
    def __init__(
        self,
        key_length: int = 256,
        bell_threshold: float = 2.0,
        backend: Optional[AerSimulator] = None,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize the E91 protocol.
        
        Args:
            key_length: Target length for the generated key
            bell_threshold: Minimum Bell parameter for secure channel (should be > 2)
            backend: Qiskit simulator backend
            verbose: Print progress information
            seed: Random seed for reproducibility
        """
        super().__init__(
            key_length=key_length,
            num_qubits=2,  # Two qubits for entangled pair
            backend=backend,
            verbose=verbose,
            seed=seed
        )
        self.bell_threshold = bell_threshold
        
        # Store measurement results for Bell test
        self._alice_results = None
        self._bob_results = None
        self._bell_parameter = None
    
    @property
    def protocol_name(self) -> str:
        """Return the protocol name."""
        return "E91"
    
    @property
    def num_bases(self) -> int:
        """Return the number of measurement bases (3 for E91)."""
        return 3
    
    def create_entangled_pair(self) -> QuantumCircuit:
        """
        Create a maximally entangled Bell state |Φ+⟩.
        
        |Φ+⟩ = (|00⟩ + |11⟩)/√2
        
        Returns:
            QuantumCircuit with entangled pair
        """
        qr = QuantumRegister(2, 'q')
        cr = ClassicalRegister(2, 'c')
        qc = QuantumCircuit(qr, cr)
        
        # Create Bell state |Φ+⟩
        qc.h(qr[0])
        qc.cx(qr[0], qr[1])
        
        return qc
    
    def prepare_qubit(self, bit: int, basis: int) -> QuantumCircuit:
        """
        Create entangled pair (bit parameter is ignored in E91).
        
        In E91, the source creates entangled pairs independently
        of any classical bit values.
        
        Args:
            bit: Ignored (included for interface compatibility)
            basis: Ignored (included for interface compatibility)
            
        Returns:
            QuantumCircuit with entangled pair
        """
        return self.create_entangled_pair()
    
    def measure_qubit(self, circuit: QuantumCircuit, basis: int) -> QuantumCircuit:
        """
        This method is not used directly in E91.
        See measure_both_parties for the actual measurement logic.
        """
        return circuit
    
    def measure_both_parties(
        self,
        circuit: QuantumCircuit,
        alice_basis: int,
        bob_basis: int
    ) -> QuantumCircuit:
        """
        Apply measurement operations for both Alice and Bob.
        
        Each party measures their qubit in their chosen basis,
        which corresponds to rotation by the appropriate angle.
        
        Args:
            circuit: Circuit containing the entangled pair
            alice_basis: Alice's basis choice (0, 1, or 2)
            bob_basis: Bob's basis choice (0, 1, or 2)
            
        Returns:
            QuantumCircuit with measurements added
        """
        # Alice measures qubit 0
        alice_angle = self.ALICE_ANGLES[alice_basis]
        if alice_angle != 0:
            circuit.ry(-alice_angle, 0)  # Rotate to measurement basis
        
        # Bob measures qubit 1
        bob_angle = self.BOB_ANGLES[bob_basis]
        if bob_angle != 0:
            circuit.ry(-bob_angle, 1)  # Rotate to measurement basis
        
        # Measure both qubits
        circuit.measure([0, 1], [0, 1])
        
        return circuit
    
    def sift_keys(
        self,
        alice_bits: np.ndarray,
        alice_bases: np.ndarray,
        bob_bases: np.ndarray,
        bob_measurements: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform E91-specific key sifting.
        
        In E91, Alice and Bob keep results only where their basis
        combination is in KEY_MATCHING_PAIRS.
        
        Args:
            alice_bits: Alice's measurement results
            alice_bases: Alice's choice of bases
            bob_bases: Bob's choice of bases
            bob_measurements: Bob's measurement results
            
        Returns:
            Tuple of (Alice's sifted key, Bob's sifted key)
        """
        key_mask = np.zeros(len(alice_bits), dtype=bool)
        
        for alice_b, bob_b in self.KEY_MATCHING_PAIRS:
            matching = (alice_bases == alice_b) & (bob_bases == bob_b)
            key_mask |= matching
        
        alice_sifted = alice_bits[key_mask]
        # For E91 with Bell state, results are correlated, so we flip Bob's
        bob_sifted = bob_measurements[key_mask]
        
        return alice_sifted, bob_sifted
    
    def run(
        self,
        noise_model=None,
        eavesdropper=None,
        shots: int = 1
    ) -> QKDResult:
        """
        Execute the E91 protocol.
        
        Includes Bell inequality testing for security verification.
        
        Args:
            noise_model: Optional noise model
            eavesdropper: Optional eavesdropper attack
            shots: Number of measurement shots
            
        Returns:
            QKDResult containing protocol results
        """
        import time
        start_time = time.time()
        
        # E91 has ~2/9 sifting efficiency for key generation
        raw_length = int(self.key_length * 6)
        
        # Generate random basis choices
        self._alice_bases = np.random.randint(0, 3, raw_length)
        self._bob_bases = np.random.randint(0, 3, raw_length)
        
        # Arrays to store measurement results
        alice_results = np.zeros(raw_length, dtype=int)
        bob_results = np.zeros(raw_length, dtype=int)
        
        # Run quantum circuits
        for i in range(raw_length):
            # Create entangled pair
            qc = self.create_entangled_pair()
            
            # Apply eavesdropper if present
            if eavesdropper is not None:
                qc = eavesdropper.intercept(qc)
            
            # Add measurements for both parties
            qc = self.measure_both_parties(
                qc, 
                self._alice_bases[i], 
                self._bob_bases[i]
            )
            
            # Execute circuit
            if noise_model is not None:
                result = self.backend.run(
                    qc, shots=shots, noise_model=noise_model
                ).result()
            else:
                result = self.backend.run(qc, shots=shots).result()
            
            counts = result.get_counts()
            outcome = max(counts, key=counts.get)
            alice_results[i] = int(outcome[1])  # First qubit (Alice)
            bob_results[i] = int(outcome[0])    # Second qubit (Bob)
        
        self._alice_bits = alice_results
        self._bob_measurements = bob_results
        self._alice_results = alice_results
        self._bob_results = bob_results
        
        # Perform Bell test
        self._bell_parameter = self._compute_bell_parameter(
            alice_results, bob_results,
            self._alice_bases, self._bob_bases
        )
        
        # Sift keys
        alice_sifted, bob_sifted = self.sift_keys(
            alice_results,
            self._alice_bases,
            self._bob_bases,
            bob_results
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
            print(f"  Entangled pairs used: {raw_length}")
            print(f"  Bell parameter S: {self._bell_parameter:.4f}")
            print(f"  Bell test: {'PASSED' if self._bell_parameter > self.bell_threshold else 'FAILED'}")
            print(f"  Sifted key length: {len(alice_sifted)}")
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
                "bell_parameter": self._bell_parameter,
                "bell_test_passed": self._bell_parameter > self.bell_threshold,
                "sifting_efficiency": len(alice_sifted) / raw_length
            }
        )
    
    def _compute_bell_parameter(
        self,
        alice_results: np.ndarray,
        bob_results: np.ndarray,
        alice_bases: np.ndarray,
        bob_bases: np.ndarray
    ) -> float:
        """
        Compute the CHSH Bell parameter S.
        
        S = |E(a1,b1) - E(a1,b2) + E(a2,b1) + E(a2,b2)|
        
        For quantum mechanics: S_max = 2√2 ≈ 2.828
        Classical limit: S ≤ 2
        
        Args:
            alice_results: Alice's measurement outcomes
            bob_results: Bob's measurement outcomes
            alice_bases: Alice's basis choices
            bob_bases: Bob's basis choices
            
        Returns:
            Bell parameter S
        """
        def correlation(a_basis, b_basis):
            """Compute correlation E(a,b) for given basis pair."""
            mask = (alice_bases == a_basis) & (bob_bases == b_basis)
            if np.sum(mask) == 0:
                return 0.0
            
            # Convert 0,1 outcomes to +1,-1
            a_vals = 2 * alice_results[mask] - 1
            b_vals = 2 * bob_results[mask] - 1
            
            return np.mean(a_vals * b_vals)
        
        # Compute correlations for CHSH test
        # Using Alice bases 0,1 and Bob bases 0,1
        E_00 = correlation(0, 0)
        E_01 = correlation(0, 1)
        E_10 = correlation(1, 0)
        E_11 = correlation(1, 1)
        
        # CHSH inequality
        S = abs(E_00 - E_01 + E_10 + E_11)
        
        return S
    
    def is_secure(self, result: QKDResult) -> bool:
        """
        Check if the protocol execution indicates a secure channel.
        
        Security is verified through Bell inequality violation:
        S > 2 indicates quantum correlations and no local hidden variables
        
        Args:
            result: QKDResult from protocol execution
            
        Returns:
            True if Bell test passed and QBER is acceptable
        """
        bell_passed = result.additional_info.get("bell_test_passed", False)
        qber_ok = result.qber < 0.11
        
        return bell_passed and qber_ok
    
    @staticmethod
    def theoretical_key_rate(qber: float, sifting_rate: float = 0.22) -> float:
        """
        Calculate the theoretical secure key rate for E91.
        
        E91 has unique security properties due to Bell inequality testing,
        but similar key rate formula to BB84.
        
        Args:
            qber: Quantum Bit Error Rate
            sifting_rate: Fraction of bits kept (default ~22% for E91)
            
        Returns:
            Theoretical secure key rate
        """
        if qber <= 0:
            return sifting_rate
        if qber >= 0.5:
            return 0.0
        
        h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if 0 < x < 1 else 0
        key_rate = sifting_rate * max(0, 1 - 2 * h(qber))
        
        return key_rate
