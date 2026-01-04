"""
Base class for all QKD protocol implementations.

This module provides the abstract base class that defines the interface
for all Quantum Key Distribution protocols in this package.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict, Any
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


@dataclass
class QKDResult:
    """Container for QKD protocol execution results."""
    
    alice_key: np.ndarray
    bob_key: np.ndarray
    raw_key_length: int
    sifted_key_length: int
    final_key_length: int
    qber: float
    execution_time: float
    protocol_name: str
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}
    
    @property
    def key_agreement_rate(self) -> float:
        """Calculate the fraction of bits that Alice and Bob agree on."""
        if len(self.alice_key) == 0:
            return 0.0
        return 1.0 - np.mean(self.alice_key != self.bob_key)
    
    @property
    def sifting_efficiency(self) -> float:
        """Calculate the sifting efficiency (sifted/raw ratio)."""
        if self.raw_key_length == 0:
            return 0.0
        return self.sifted_key_length / self.raw_key_length
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "protocol_name": self.protocol_name,
            "raw_key_length": self.raw_key_length,
            "sifted_key_length": self.sifted_key_length,
            "final_key_length": self.final_key_length,
            "qber": self.qber,
            "key_agreement_rate": self.key_agreement_rate,
            "sifting_efficiency": self.sifting_efficiency,
            "execution_time": self.execution_time,
            **self.additional_info
        }


class BaseQKDProtocol(ABC):
    """
    Abstract base class for Quantum Key Distribution protocols.
    
    This class defines the common interface and shared functionality
    for all QKD protocol implementations.
    
    Attributes:
        key_length: Target length for the generated key
        num_qubits: Number of qubits to use in quantum circuits
        backend: Qiskit backend for quantum simulation
        verbose: Whether to print progress information
    """
    
    def __init__(
        self,
        key_length: int = 256,
        num_qubits: int = 1,
        backend: Optional[AerSimulator] = None,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize the QKD protocol.
        
        Args:
            key_length: Target length for the generated key
            num_qubits: Number of qubits per transmission
            backend: Qiskit simulator backend (default: AerSimulator)
            verbose: Print progress information
            seed: Random seed for reproducibility
        """
        self.key_length = key_length
        self.num_qubits = num_qubits
        self.backend = backend or AerSimulator()
        self.verbose = verbose
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
        
        # Protocol state
        self._alice_bits = None
        self._alice_bases = None
        self._bob_bases = None
        self._bob_measurements = None
        
    @property
    @abstractmethod
    def protocol_name(self) -> str:
        """Return the name of the protocol."""
        pass
    
    @property
    @abstractmethod
    def num_bases(self) -> int:
        """Return the number of measurement bases used by the protocol."""
        pass
    
    @abstractmethod
    def prepare_qubit(self, bit: int, basis: int) -> QuantumCircuit:
        """
        Prepare a qubit in the specified state and basis.
        
        Args:
            bit: The bit value (0 or 1) to encode
            basis: The basis to use for encoding
            
        Returns:
            QuantumCircuit with the prepared qubit
        """
        pass
    
    @abstractmethod
    def measure_qubit(self, circuit: QuantumCircuit, basis: int) -> QuantumCircuit:
        """
        Add measurement operations to the circuit in the specified basis.
        
        Args:
            circuit: The quantum circuit containing the qubit
            basis: The basis to use for measurement
            
        Returns:
            QuantumCircuit with measurement operations added
        """
        pass
    
    @abstractmethod
    def sift_keys(
        self,
        alice_bits: np.ndarray,
        alice_bases: np.ndarray,
        bob_bases: np.ndarray,
        bob_measurements: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform the sifting step to extract matching basis measurements.
        
        Args:
            alice_bits: Alice's original bit string
            alice_bases: Alice's choice of bases
            bob_bases: Bob's choice of bases
            bob_measurements: Bob's measurement results
            
        Returns:
            Tuple of (Alice's sifted key, Bob's sifted key)
        """
        pass
    
    def run(
        self,
        noise_model=None,
        eavesdropper=None,
        shots: int = 1
    ) -> QKDResult:
        """
        Execute the complete QKD protocol.
        
        Args:
            noise_model: Optional noise model to apply to the channel
            eavesdropper: Optional eavesdropper attack simulation
            shots: Number of shots per circuit execution
            
        Returns:
            QKDResult containing the protocol execution results
        """
        import time
        start_time = time.time()
        
        # Step 1: Generate random bits and bases for Alice
        # We need extra bits because sifting will discard some
        raw_length = int(self.key_length * 2.5)  # Account for sifting loss
        self._alice_bits = np.random.randint(0, 2, raw_length)
        self._alice_bases = np.random.randint(0, self.num_bases, raw_length)
        
        # Step 2: Generate random bases for Bob
        self._bob_bases = np.random.randint(0, self.num_bases, raw_length)
        
        # Step 3: Quantum transmission and measurement
        self._bob_measurements = self._quantum_transmission(
            self._alice_bits,
            self._alice_bases,
            self._bob_bases,
            noise_model=noise_model,
            eavesdropper=eavesdropper,
            shots=shots
        )
        
        # Step 4: Sifting
        alice_sifted, bob_sifted = self.sift_keys(
            self._alice_bits,
            self._alice_bases,
            self._bob_bases,
            self._bob_measurements
        )
        
        # Step 5: Error estimation (using a subset of the sifted key)
        qber = self._estimate_qber(alice_sifted, bob_sifted)
        
        # Step 6: Truncate to desired key length
        final_length = min(len(alice_sifted), self.key_length)
        alice_key = alice_sifted[:final_length]
        bob_key = bob_sifted[:final_length]
        
        execution_time = time.time() - start_time
        
        if self.verbose:
            print(f"\n{self.protocol_name} Protocol Results:")
            print(f"  Raw bits transmitted: {raw_length}")
            print(f"  Sifted key length: {len(alice_sifted)}")
            print(f"  Final key length: {final_length}")
            print(f"  QBER: {qber:.4f}")
            print(f"  Execution time: {execution_time:.2f}s")
        
        return QKDResult(
            alice_key=alice_key,
            bob_key=bob_key,
            raw_key_length=raw_length,
            sifted_key_length=len(alice_sifted),
            final_key_length=final_length,
            qber=qber,
            execution_time=execution_time,
            protocol_name=self.protocol_name
        )
    
    def _quantum_transmission(
        self,
        alice_bits: np.ndarray,
        alice_bases: np.ndarray,
        bob_bases: np.ndarray,
        noise_model=None,
        eavesdropper=None,
        shots: int = 1
    ) -> np.ndarray:
        """
        Simulate quantum transmission of qubits from Alice to Bob.
        
        Args:
            alice_bits: Alice's bit string to transmit
            alice_bases: Bases used by Alice for encoding
            bob_bases: Bases used by Bob for measurement
            noise_model: Optional noise model for the quantum channel
            eavesdropper: Optional eavesdropper attack
            shots: Number of measurement shots
            
        Returns:
            Bob's measurement results
        """
        bob_measurements = np.zeros(len(alice_bits), dtype=int)
        
        for i in range(len(alice_bits)):
            # Alice prepares the qubit
            qc = self.prepare_qubit(alice_bits[i], alice_bases[i])
            
            # Apply eavesdropper attack if present
            if eavesdropper is not None:
                qc = eavesdropper.intercept(qc)
            
            # Bob measures the qubit
            qc = self.measure_qubit(qc, bob_bases[i])
            
            # Execute the circuit
            if noise_model is not None:
                result = self.backend.run(
                    qc, 
                    shots=shots, 
                    noise_model=noise_model
                ).result()
            else:
                result = self.backend.run(qc, shots=shots).result()
            
            counts = result.get_counts()
            # Get the most frequent measurement outcome
            bob_measurements[i] = int(max(counts, key=counts.get))
        
        return bob_measurements
    
    def _estimate_qber(
        self,
        alice_key: np.ndarray,
        bob_key: np.ndarray,
        sample_fraction: float = 0.1
    ) -> float:
        """
        Estimate the Quantum Bit Error Rate (QBER).
        
        Uses a random sample of the sifted key to estimate errors.
        
        Args:
            alice_key: Alice's sifted key
            bob_key: Bob's sifted key
            sample_fraction: Fraction of key to use for estimation
            
        Returns:
            Estimated QBER
        """
        if len(alice_key) == 0:
            return 0.0
        
        sample_size = max(1, int(len(alice_key) * sample_fraction))
        sample_indices = np.random.choice(len(alice_key), sample_size, replace=False)
        
        errors = np.sum(alice_key[sample_indices] != bob_key[sample_indices])
        qber = errors / sample_size
        
        return qber
    
    def reset(self):
        """Reset the protocol state for a new run."""
        self._alice_bits = None
        self._alice_bases = None
        self._bob_bases = None
        self._bob_measurements = None
