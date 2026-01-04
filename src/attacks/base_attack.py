"""
Base class for attack simulations.

This module defines the abstract interface for all attack implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import numpy as np
from qiskit import QuantumCircuit


@dataclass
class AttackResult:
    """Container for attack simulation results."""
    
    attack_name: str
    eve_information: float  # Information gained by Eve (bits)
    induced_qber: float     # QBER caused by the attack
    detection_probability: float  # Probability of detection
    intercepted_bits: Optional[np.ndarray] = None
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "attack_name": self.attack_name,
            "eve_information": self.eve_information,
            "induced_qber": self.induced_qber,
            "detection_probability": self.detection_probability,
            "num_intercepted": len(self.intercepted_bits) if self.intercepted_bits is not None else 0,
            **self.additional_info
        }


class BaseAttack(ABC):
    """
    Abstract base class for quantum attacks against QKD protocols.
    
    All attack implementations should inherit from this class and
    implement the required methods.
    
    Attributes:
        attack_probability: Probability of attacking each qubit (0-1)
        verbose: Whether to print attack information
    """
    
    def __init__(
        self,
        attack_probability: float = 1.0,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize the attack.
        
        Args:
            attack_probability: Fraction of qubits to attack (0-1)
            verbose: Print attack progress
            seed: Random seed for reproducibility
        """
        self.attack_probability = attack_probability
        self.verbose = verbose
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
        
        # Track attack statistics
        self._num_intercepted = 0
        self._intercepted_bits = []
        self._measurement_bases = []
    
    @property
    @abstractmethod
    def attack_name(self) -> str:
        """Return the name of the attack."""
        pass
    
    @abstractmethod
    def intercept(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """
        Intercept and potentially modify a quantum circuit.
        
        This is the main attack method that simulates Eve's
        interception of the quantum channel.
        
        Args:
            circuit: The quantum circuit being transmitted
            
        Returns:
            Modified quantum circuit (or original if not attacking)
        """
        pass
    
    @abstractmethod
    def get_results(self) -> AttackResult:
        """
        Get the results of the attack simulation.
        
        Returns:
            AttackResult containing attack statistics
        """
        pass
    
    def should_attack(self) -> bool:
        """
        Determine whether to attack this qubit.
        
        Uses attack_probability to decide randomly.
        
        Returns:
            True if Eve should attack this qubit
        """
        return np.random.random() < self.attack_probability
    
    def reset(self):
        """Reset attack state for a new simulation."""
        self._num_intercepted = 0
        self._intercepted_bits = []
        self._measurement_bases = []
    
    @staticmethod
    def theoretical_induced_qber() -> float:
        """
        Return the theoretical QBER induced by this attack.
        
        Should be overridden by specific attack implementations.
        
        Returns:
            Expected QBER when attack is performed
        """
        return 0.0
    
    @staticmethod
    def theoretical_detection_probability(num_test_bits: int) -> float:
        """
        Calculate probability of detecting the attack.
        
        Args:
            num_test_bits: Number of bits used for QBER estimation
            
        Returns:
            Probability of detecting the attack
        """
        return 0.0
