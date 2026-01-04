"""
Security Metrics for QKD Protocol Evaluation.

This module provides comprehensive security metrics for analyzing
the performance and security of QKD protocol implementations.

Key Metrics:
- Quantum Bit Error Rate (QBER)
- Secret Key Rate
- Mutual Information (Alice-Bob, Alice-Eve, Bob-Eve)
- Privacy Amplification Parameters
- Finite-key Effects

References:
    Scarani, V., et al. (2009). "The security of practical quantum 
    key distribution." Reviews of Modern Physics, 81(3), 1301.
"""

from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class KeyRateResult:
    """Container for key rate calculation results."""
    
    asymptotic_rate: float
    finite_key_rate: float
    qber: float
    phase_error_rate: float
    privacy_amplification_bits: int
    error_correction_bits: int
    final_key_length: int
    security_parameter: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "asymptotic_rate": self.asymptotic_rate,
            "finite_key_rate": self.finite_key_rate,
            "qber": self.qber,
            "phase_error_rate": self.phase_error_rate,
            "privacy_amplification_bits": self.privacy_amplification_bits,
            "error_correction_bits": self.error_correction_bits,
            "final_key_length": self.final_key_length,
            "security_parameter": self.security_parameter
        }


def binary_entropy(p: float) -> float:
    """
    Calculate binary entropy function H(p).
    
    H(p) = -p*log2(p) - (1-p)*log2(1-p)
    
    Args:
        p: Probability (0 to 1)
        
    Returns:
        Binary entropy in bits
    """
    if p <= 0 or p >= 1:
        return 0.0
    return -p * np.log2(p) - (1 - p) * np.log2(1 - p)


def compute_secret_key_rate(
    qber: float,
    sifting_rate: float = 0.5,
    error_correction_efficiency: float = 1.16
) -> float:
    """
    Compute the asymptotic secret key rate for BB84.
    
    r = sifting_rate * [1 - H(QBER) - f*H(QBER)]
    
    Args:
        qber: Quantum Bit Error Rate
        sifting_rate: Fraction of bits kept after sifting
        error_correction_efficiency: Efficiency factor (≥1, typically 1.16)
        
    Returns:
        Secret key rate per transmitted qubit
    """
    if qber >= 0.11:  # Beyond security threshold
        return 0.0
    if qber <= 0:
        return sifting_rate
    
    h = binary_entropy(qber)
    
    # Secret key rate formula
    rate = sifting_rate * max(0, 1 - h - error_correction_efficiency * h)
    
    return rate


class SecurityMetrics:
    """
    Comprehensive security metrics calculator for QKD.
    
    Computes various security-related metrics from protocol
    execution data.
    
    Attributes:
        alice_key: Alice's raw/sifted key
        bob_key: Bob's raw/sifted key
        eve_information: Optional information leaked to Eve
        
    Example:
        >>> metrics = SecurityMetrics(alice_key, bob_key)
        >>> print(f"QBER: {metrics.qber:.4f}")
        >>> print(f"Key Rate: {metrics.secret_key_rate():.4f}")
    """
    
    def __init__(
        self,
        alice_key: np.ndarray,
        bob_key: np.ndarray,
        eve_key: Optional[np.ndarray] = None,
        raw_length: Optional[int] = None
    ):
        """
        Initialize security metrics calculator.
        
        Args:
            alice_key: Alice's key bits
            bob_key: Bob's key bits
            eve_key: Eve's intercepted bits (if known)
            raw_length: Original number of transmitted qubits
        """
        self.alice_key = np.array(alice_key)
        self.bob_key = np.array(bob_key)
        self.eve_key = np.array(eve_key) if eve_key is not None else None
        self.raw_length = raw_length or len(alice_key)
    
    @property
    def qber(self) -> float:
        """
        Calculate Quantum Bit Error Rate.
        
        QBER = (number of errors) / (total bits)
        
        Returns:
            QBER as a fraction (0 to 1)
        """
        if len(self.alice_key) == 0:
            return 0.0
        
        errors = np.sum(self.alice_key != self.bob_key)
        return errors / len(self.alice_key)
    
    @property
    def key_length(self) -> int:
        """Return the sifted key length."""
        return len(self.alice_key)
    
    @property
    def sifting_rate(self) -> float:
        """Calculate the sifting rate (kept/raw)."""
        if self.raw_length == 0:
            return 0.0
        return len(self.alice_key) / self.raw_length
    
    def secret_key_rate(
        self,
        error_correction_efficiency: float = 1.16
    ) -> float:
        """
        Calculate asymptotic secret key rate.
        
        Args:
            error_correction_efficiency: EC efficiency factor
            
        Returns:
            Secret key rate per transmitted qubit
        """
        return compute_secret_key_rate(
            self.qber,
            self.sifting_rate,
            error_correction_efficiency
        )
    
    def mutual_information_ab(self) -> float:
        """
        Calculate mutual information between Alice and Bob.
        
        I(A:B) = 1 - H(QBER)
        
        Returns:
            Mutual information in bits
        """
        return 1 - binary_entropy(self.qber)
    
    def mutual_information_ae(self) -> float:
        """
        Calculate mutual information between Alice and Eve.
        
        For intercept-resend attack:
        I(A:E) ≈ H(QBER) assuming Eve causes all errors
        
        Returns:
            Estimated mutual information with Eve
        """
        if self.eve_key is None:
            # Estimate from QBER (worst case)
            return binary_entropy(self.qber)
        
        # If Eve's key is known, calculate directly
        eve_errors = np.sum(self.alice_key != self.eve_key) / len(self.alice_key)
        return 1 - binary_entropy(eve_errors)
    
    def holevo_bound(self) -> float:
        """
        Calculate Holevo bound on Eve's information.
        
        For BB84 with QBER e:
        χ ≤ H(e)
        
        Returns:
            Holevo bound in bits
        """
        return binary_entropy(self.qber)
    
    def privacy_amplification_factor(self) -> float:
        """
        Calculate the fraction of bits to remove in privacy amplification.
        
        Returns:
            Fraction of bits to hash away
        """
        return binary_entropy(self.qber)
    
    def error_correction_overhead(
        self,
        efficiency: float = 1.16
    ) -> float:
        """
        Calculate bits leaked during error correction.
        
        Args:
            efficiency: EC efficiency factor
            
        Returns:
            Bits leaked per sifted key bit
        """
        return efficiency * binary_entropy(self.qber)
    
    def final_key_length(
        self,
        error_correction_efficiency: float = 1.16,
        security_parameter: float = 1e-10
    ) -> int:
        """
        Calculate expected final secure key length.
        
        Args:
            error_correction_efficiency: EC efficiency
            security_parameter: Desired security level ε
            
        Returns:
            Expected secure key length
        """
        rate = self.secret_key_rate(error_correction_efficiency)
        
        # Finite-key correction
        n = self.key_length
        if n < 100:
            return 0
        
        finite_correction = np.sqrt(n) * np.log2(1/security_parameter)
        
        final_length = int(n * rate - finite_correction)
        return max(0, final_length)
    
    def compute_all_metrics(
        self,
        error_correction_efficiency: float = 1.16,
        security_parameter: float = 1e-10
    ) -> KeyRateResult:
        """
        Compute comprehensive key rate analysis.
        
        Args:
            error_correction_efficiency: EC efficiency factor
            security_parameter: Security parameter ε
            
        Returns:
            KeyRateResult with all metrics
        """
        n = self.key_length
        qber = self.qber
        
        asymptotic_rate = self.secret_key_rate(error_correction_efficiency)
        
        # Finite-key rate
        if n < 100:
            finite_rate = 0.0
        else:
            correction = np.sqrt(n) * np.log2(1/security_parameter) / n
            finite_rate = max(0, asymptotic_rate - correction)
        
        # Privacy amplification bits
        pa_bits = int(n * self.privacy_amplification_factor())
        
        # Error correction bits
        ec_bits = int(n * self.error_correction_overhead(error_correction_efficiency))
        
        # Final key
        final_length = self.final_key_length(
            error_correction_efficiency, 
            security_parameter
        )
        
        return KeyRateResult(
            asymptotic_rate=asymptotic_rate,
            finite_key_rate=finite_rate,
            qber=qber,
            phase_error_rate=qber,  # Same for BB84 with symmetric channel
            privacy_amplification_bits=pa_bits,
            error_correction_bits=ec_bits,
            final_key_length=final_length,
            security_parameter=security_parameter
        )
    
    def is_secure(self, threshold: float = 0.11) -> bool:
        """
        Check if QBER is below security threshold.
        
        For BB84: theoretical threshold ≈ 11%
        
        Args:
            threshold: Maximum acceptable QBER
            
        Returns:
            True if secure
        """
        return self.qber < threshold
    
    def security_margin(self, threshold: float = 0.11) -> float:
        """
        Calculate how much margin below security threshold.
        
        Args:
            threshold: Security threshold
            
        Returns:
            Margin (positive = secure, negative = insecure)
        """
        return threshold - self.qber
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all security metrics.
        
        Returns:
            Dictionary with all computed metrics
        """
        return {
            "qber": self.qber,
            "key_length": self.key_length,
            "sifting_rate": self.sifting_rate,
            "secret_key_rate": self.secret_key_rate(),
            "mutual_info_ab": self.mutual_information_ab(),
            "mutual_info_ae": self.mutual_information_ae(),
            "holevo_bound": self.holevo_bound(),
            "is_secure": self.is_secure(),
            "security_margin": self.security_margin(),
            "final_key_length": self.final_key_length()
        }
    
    def __repr__(self) -> str:
        return (f"SecurityMetrics(QBER={self.qber:.4f}, "
                f"key_length={self.key_length}, "
                f"secure={self.is_secure()})")
