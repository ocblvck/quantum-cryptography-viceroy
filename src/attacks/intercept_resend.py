"""
Intercept-Resend Attack Implementation.

The Intercept-Resend attack is the most fundamental attack against QKD protocols.
Eve intercepts each qubit, measures it in a randomly chosen basis, and then
prepares and sends a new qubit to Bob based on her measurement result.

Attack Description:
1. Eve intercepts the qubit from Alice
2. Eve randomly chooses a measurement basis
3. Eve measures the qubit, obtaining a classical result
4. Eve prepares a new qubit in the state she measured
5. Eve sends this new qubit to Bob

Impact on BB84:
- Eve chooses wrong basis 50% of the time
- When Eve's basis is wrong, she introduces 50% error
- Overall induced QBER: 25%
- Detection: If Alice and Bob compare 10% of bits, P(detect) ≈ 1 - (0.75)^n

References:
    Bennett, C. H., et al. (1992). "Experimental quantum cryptography."
    Journal of Cryptology, 5(1), 3-28.
"""

from typing import Optional, List
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator

from src.attacks.base_attack import BaseAttack, AttackResult


class InterceptResendAttack(BaseAttack):
    """
    Implementation of the Intercept-Resend attack.
    
    Eve measures each intercepted qubit and prepares a replacement
    based on her measurement outcome. This attack is detectable
    through QBER estimation.
    
    Attributes:
        attack_probability: Fraction of qubits Eve intercepts
        num_bases: Number of measurement bases Eve uses (2 for BB84)
        
    Example:
        >>> eve = InterceptResendAttack(attack_probability=1.0)
        >>> # In protocol execution
        >>> qc = eve.intercept(qc)
    """
    
    def __init__(
        self,
        attack_probability: float = 1.0,
        num_bases: int = 2,
        backend: Optional[AerSimulator] = None,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize the Intercept-Resend attack.
        
        Args:
            attack_probability: Probability of intercepting each qubit
            num_bases: Number of measurement bases to choose from
            backend: Qiskit simulator for measurements
            verbose: Print attack information
            seed: Random seed for reproducibility
        """
        super().__init__(
            attack_probability=attack_probability,
            verbose=verbose,
            seed=seed
        )
        self.num_bases = num_bases
        self.backend = backend or AerSimulator()
    
    @property
    def attack_name(self) -> str:
        """Return the attack name."""
        return "Intercept-Resend"
    
    def intercept(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """
        Perform intercept-resend attack on a quantum circuit.
        
        Eve measures the qubit and prepares a replacement based on
        her measurement result.
        
        Args:
            circuit: Original quantum circuit from Alice
            
        Returns:
            New circuit with Eve's replacement qubit
        """
        if not self.should_attack():
            return circuit
        
        self._num_intercepted += 1
        
        # Eve chooses a random measurement basis
        eve_basis = np.random.randint(0, self.num_bases)
        self._measurement_bases.append(eve_basis)
        
        # Create a copy of the circuit for Eve's measurement
        eve_circuit = circuit.copy()
        
        # Eve transforms to her measurement basis and measures
        if eve_basis == 1:  # X-basis
            eve_circuit.h(0)
        
        # Add a classical register for Eve's measurement if needed
        if eve_circuit.num_clbits == 0:
            eve_circuit.add_register(ClassicalRegister(1, 'eve'))
        
        eve_circuit.measure(0, 0)
        
        # Execute Eve's measurement
        result = self.backend.run(eve_circuit, shots=1).result()
        counts = result.get_counts()
        eve_result = int(list(counts.keys())[0][-1])  # Get the measurement result
        self._intercepted_bits.append(eve_result)
        
        # Eve prepares a new qubit based on her measurement
        qr = QuantumRegister(1, 'q')
        cr = ClassicalRegister(1, 'c')
        new_circuit = QuantumCircuit(qr, cr)
        
        # Prepare state based on Eve's result
        if eve_result == 1:
            new_circuit.x(qr[0])
        
        # Transform to Eve's basis if she used X-basis
        if eve_basis == 1:
            new_circuit.h(qr[0])
        
        if self.verbose:
            print(f"[Eve] Intercepted qubit, measured in basis {eve_basis}, got {eve_result}")
        
        return new_circuit
    
    def get_results(self) -> AttackResult:
        """
        Get the results of the attack simulation.
        
        Returns:
            AttackResult with attack statistics
        """
        intercepted_bits = np.array(self._intercepted_bits)
        
        return AttackResult(
            attack_name=self.attack_name,
            eve_information=self._calculate_eve_information(),
            induced_qber=self.theoretical_induced_qber() * self.attack_probability,
            detection_probability=self._calculate_detection_probability(),
            intercepted_bits=intercepted_bits,
            additional_info={
                "num_intercepted": self._num_intercepted,
                "attack_probability": self.attack_probability,
                "num_bases": self.num_bases
            }
        )
    
    def _calculate_eve_information(self) -> float:
        """
        Calculate information gained by Eve.
        
        For intercept-resend on BB84:
        - Eve gets correct bit 75% of the time (correct basis 50%, 
          plus 25% of wrong basis cases)
        
        Returns:
            Bits of information per intercepted qubit
        """
        if self._num_intercepted == 0:
            return 0.0
        
        # Eve gets 0.5 bits of information per qubit on average
        # (she's correct 75% of the time)
        return 0.5 * self._num_intercepted
    
    def _calculate_detection_probability(self) -> float:
        """
        Calculate probability of attack being detected.
        
        For a sample of n test bits with 25% induced QBER,
        the probability of detecting at least one error is:
        P(detect) = 1 - (1 - 0.25)^n
        
        Returns:
            Detection probability
        """
        # Assume 10% of key is used for testing
        test_fraction = 0.1
        n_test = int(self._num_intercepted * test_fraction)
        
        if n_test == 0:
            return 0.0
        
        qber = self.theoretical_induced_qber() * self.attack_probability
        return 1 - (1 - qber) ** n_test
    
    @staticmethod
    def theoretical_induced_qber() -> float:
        """
        Return the theoretical QBER induced by intercept-resend attack.
        
        For BB84:
        - Eve chooses wrong basis 50% of time
        - Wrong basis causes 50% error
        - Induced QBER = 0.5 * 0.5 = 0.25
        
        Returns:
            Expected QBER (0.25 for BB84)
        """
        return 0.25
    
    @staticmethod
    def theoretical_detection_probability(num_test_bits: int, qber: float = 0.25) -> float:
        """
        Calculate theoretical detection probability.
        
        Args:
            num_test_bits: Number of bits used for QBER estimation
            qber: Expected QBER from attack (default 0.25)
            
        Returns:
            Probability of detecting the attack
        """
        if num_test_bits <= 0:
            return 0.0
        return 1 - (1 - qber) ** num_test_bits


class SelectiveBasisAttack(InterceptResendAttack):
    """
    Variant of intercept-resend where Eve only attacks when confident.
    
    Eve may use additional information (side channels, timing, etc.)
    to make better guesses about Alice's basis choice.
    """
    
    def __init__(
        self,
        attack_probability: float = 1.0,
        basis_guess_accuracy: float = 0.5,
        backend: Optional[AerSimulator] = None,
        verbose: bool = False,
        seed: Optional[int] = None
    ):
        """
        Initialize selective basis attack.
        
        Args:
            attack_probability: Probability of intercepting each qubit
            basis_guess_accuracy: Eve's accuracy in guessing Alice's basis
            backend: Qiskit simulator
            verbose: Print information
            seed: Random seed
        """
        super().__init__(
            attack_probability=attack_probability,
            num_bases=2,
            backend=backend,
            verbose=verbose,
            seed=seed
        )
        self.basis_guess_accuracy = basis_guess_accuracy
    
    @property
    def attack_name(self) -> str:
        return "Selective-Basis Intercept-Resend"
    
    def theoretical_induced_qber(self) -> float:
        """
        QBER depends on Eve's basis-guessing accuracy.
        
        If Eve always guesses correctly: QBER = 0
        If Eve guesses randomly (50%): QBER = 25%
        
        Returns:
            Expected QBER based on guess accuracy
        """
        wrong_guess_prob = 1 - self.basis_guess_accuracy
        return wrong_guess_prob * 0.5 * self.attack_probability
