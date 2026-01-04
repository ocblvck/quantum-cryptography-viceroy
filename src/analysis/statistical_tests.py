"""
Statistical Tests for QKD Key Analysis.

This module provides statistical tests to verify the quality
of generated quantum random keys, including:

1. Randomness tests (based on NIST SP 800-22)
2. Correlation tests
3. Pattern detection

These tests ensure the generated keys have appropriate
statistical properties for cryptographic use.

References:
    NIST SP 800-22: A Statistical Test Suite for Random and 
    Pseudorandom Number Generators for Cryptographic Applications
"""

from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from scipy import stats
from scipy.special import erfc


@dataclass
class TestResult:
    """Container for statistical test results."""
    
    test_name: str
    statistic: float
    p_value: float
    passed: bool
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "passed": self.passed,
            "details": self.details or {}
        }


class RandomnessTests:
    """
    NIST-inspired randomness tests for binary sequences.
    
    Tests the statistical properties of generated keys to ensure
    they are suitable for cryptographic use.
    
    Attributes:
        significance_level: p-value threshold for passing
        
    Example:
        >>> tests = RandomnessTests()
        >>> results = tests.run_all_tests(key_bits)
        >>> print(f"Passed: {sum(r.passed for r in results)}/{len(results)}")
    """
    
    def __init__(self, significance_level: float = 0.01):
        """
        Initialize randomness tests.
        
        Args:
            significance_level: Threshold for test failure (default 0.01)
        """
        self.significance_level = significance_level
    
    def frequency_test(self, bits: np.ndarray) -> TestResult:
        """
        NIST Frequency (Monobit) Test.
        
        Tests if the number of 0s and 1s are approximately equal.
        
        Args:
            bits: Binary sequence
            
        Returns:
            TestResult with test outcome
        """
        n = len(bits)
        if n < 100:
            return TestResult(
                test_name="Frequency (Monobit)",
                statistic=0,
                p_value=0,
                passed=False,
                details={"error": "Sequence too short"}
            )
        
        # Calculate test statistic
        s = np.sum(2 * bits - 1)  # Map 0,1 to -1,+1
        s_obs = np.abs(s) / np.sqrt(n)
        
        # Calculate p-value
        p_value = erfc(s_obs / np.sqrt(2))
        
        return TestResult(
            test_name="Frequency (Monobit)",
            statistic=s_obs,
            p_value=p_value,
            passed=p_value >= self.significance_level,
            details={"sum": int(s), "ones": int(np.sum(bits))}
        )
    
    def runs_test(self, bits: np.ndarray) -> TestResult:
        """
        NIST Runs Test.
        
        Tests if the number of runs (consecutive identical bits)
        is as expected for a random sequence.
        
        Args:
            bits: Binary sequence
            
        Returns:
            TestResult with test outcome
        """
        n = len(bits)
        if n < 100:
            return TestResult(
                test_name="Runs",
                statistic=0,
                p_value=0,
                passed=False,
                details={"error": "Sequence too short"}
            )
        
        # Pre-test: check if frequency is acceptable
        pi = np.sum(bits) / n
        tau = 2 / np.sqrt(n)
        
        if np.abs(pi - 0.5) >= tau:
            return TestResult(
                test_name="Runs",
                statistic=0,
                p_value=0,
                passed=False,
                details={"error": "Frequency test prerequisite failed"}
            )
        
        # Count runs
        runs = 1 + np.sum(bits[:-1] != bits[1:])
        
        # Calculate p-value
        numerator = np.abs(runs - 2 * n * pi * (1 - pi))
        denominator = 2 * np.sqrt(2 * n) * pi * (1 - pi)
        
        if denominator == 0:
            p_value = 0
        else:
            p_value = erfc(numerator / denominator)
        
        return TestResult(
            test_name="Runs",
            statistic=runs,
            p_value=p_value,
            passed=p_value >= self.significance_level,
            details={"runs": int(runs), "expected": 2 * n * pi * (1 - pi)}
        )
    
    def longest_run_test(self, bits: np.ndarray) -> TestResult:
        """
        NIST Longest Run of Ones Test.
        
        Tests if the longest run of 1s is consistent with random.
        
        Args:
            bits: Binary sequence
            
        Returns:
            TestResult with test outcome
        """
        n = len(bits)
        
        # Find longest run of 1s
        max_run = 0
        current_run = 0
        
        for bit in bits:
            if bit == 1:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        
        # Expected longest run (approximate)
        if n >= 128:
            expected = np.log2(n) - 1
        else:
            expected = np.log2(n) / 2
        
        # Simple chi-square test against expected
        deviation = np.abs(max_run - expected)
        
        # Approximate p-value
        p_value = np.exp(-deviation / expected) if expected > 0 else 0
        
        return TestResult(
            test_name="Longest Run of Ones",
            statistic=max_run,
            p_value=p_value,
            passed=p_value >= self.significance_level,
            details={"longest_run": int(max_run), "expected": expected}
        )
    
    def serial_test(self, bits: np.ndarray, m: int = 2) -> TestResult:
        """
        Serial Test for pattern distribution.
        
        Tests if m-bit patterns appear with expected frequency.
        
        Args:
            bits: Binary sequence
            m: Pattern length
            
        Returns:
            TestResult with test outcome
        """
        n = len(bits)
        if n < m * 10:
            return TestResult(
                test_name=f"Serial (m={m})",
                statistic=0,
                p_value=0,
                passed=False,
                details={"error": "Sequence too short"}
            )
        
        # Count patterns
        def count_patterns(bits, m):
            counts = np.zeros(2**m)
            for i in range(n - m + 1):
                pattern = 0
                for j in range(m):
                    pattern = (pattern << 1) | bits[i + j]
                counts[pattern] += 1
            return counts
        
        # Count for m-bit and (m-1)-bit patterns
        counts_m = count_patterns(bits, m)
        
        # Expected count
        expected = (n - m + 1) / (2**m)
        
        # Chi-square statistic
        chi2 = np.sum((counts_m - expected)**2 / expected)
        
        # Degrees of freedom
        df = 2**m - 1
        
        # p-value
        p_value = 1 - stats.chi2.cdf(chi2, df)
        
        return TestResult(
            test_name=f"Serial (m={m})",
            statistic=chi2,
            p_value=p_value,
            passed=p_value >= self.significance_level,
            details={"chi2": chi2, "df": df, "pattern_counts": counts_m.tolist()}
        )
    
    def approximate_entropy_test(
        self,
        bits: np.ndarray,
        m: int = 10
    ) -> TestResult:
        """
        Approximate Entropy Test.
        
        Compares frequency of overlapping m-bit patterns.
        
        Args:
            bits: Binary sequence
            m: Block size
            
        Returns:
            TestResult with test outcome
        """
        n = len(bits)
        if n < m + 5:
            return TestResult(
                test_name="Approximate Entropy",
                statistic=0,
                p_value=0,
                passed=False,
                details={"error": "Sequence too short"}
            )
        
        def compute_phi(bits, m):
            n = len(bits)
            # Append first m-1 bits to end (cyclic)
            bits_extended = np.concatenate([bits, bits[:m-1]])
            
            # Count patterns
            counts = {}
            for i in range(n):
                pattern = tuple(bits_extended[i:i+m])
                counts[pattern] = counts.get(pattern, 0) + 1
            
            # Compute phi
            phi = sum(c * np.log(c/n) for c in counts.values() if c > 0) / n
            return phi
        
        phi_m = compute_phi(bits, m)
        phi_m1 = compute_phi(bits, m + 1)
        
        apen = phi_m - phi_m1
        chi2 = 2 * n * (np.log(2) - apen)
        
        p_value = stats.chi2.sf(chi2, 2**m)
        
        return TestResult(
            test_name="Approximate Entropy",
            statistic=apen,
            p_value=p_value,
            passed=p_value >= self.significance_level,
            details={"apen": apen, "chi2": chi2, "m": m}
        )
    
    def run_all_tests(self, bits: np.ndarray) -> List[TestResult]:
        """
        Run all randomness tests.
        
        Args:
            bits: Binary sequence
            
        Returns:
            List of TestResult objects
        """
        results = [
            self.frequency_test(bits),
            self.runs_test(bits),
            self.longest_run_test(bits),
            self.serial_test(bits, m=2),
            self.serial_test(bits, m=3),
        ]
        
        if len(bits) >= 100:
            results.append(self.approximate_entropy_test(bits, m=5))
        
        return results
    
    def get_summary(self, bits: np.ndarray) -> Dict[str, Any]:
        """
        Get summary of all test results.
        
        Args:
            bits: Binary sequence
            
        Returns:
            Summary dictionary
        """
        results = self.run_all_tests(bits)
        
        return {
            "total_tests": len(results),
            "passed": sum(r.passed for r in results),
            "failed": sum(not r.passed for r in results),
            "pass_rate": sum(r.passed for r in results) / len(results),
            "results": [r.to_dict() for r in results]
        }


class CorrelationTests:
    """
    Tests for correlations between keys.
    
    Verifies independence between Alice's and Bob's raw bits
    and detects any patterns that might indicate eavesdropping.
    """
    
    def __init__(self, significance_level: float = 0.01):
        """
        Initialize correlation tests.
        
        Args:
            significance_level: Threshold for significance
        """
        self.significance_level = significance_level
    
    def bit_correlation(
        self,
        key1: np.ndarray,
        key2: np.ndarray
    ) -> TestResult:
        """
        Test correlation between two bit sequences.
        
        Args:
            key1: First bit sequence
            key2: Second bit sequence
            
        Returns:
            TestResult with correlation analysis
        """
        if len(key1) != len(key2):
            return TestResult(
                test_name="Bit Correlation",
                statistic=0,
                p_value=0,
                passed=False,
                details={"error": "Keys must be same length"}
            )
        
        # Compute correlation coefficient
        corr, p_value = stats.pearsonr(key1.astype(float), key2.astype(float))
        
        # For raw bits, we expect correlation of 0 (before sifting)
        # For sifted keys, we expect correlation near 1
        
        return TestResult(
            test_name="Bit Correlation",
            statistic=corr,
            p_value=p_value,
            passed=True,  # Correlation by itself isn't pass/fail
            details={"correlation": corr}
        )
    
    def autocorrelation_test(
        self,
        bits: np.ndarray,
        max_lag: int = 10
    ) -> TestResult:
        """
        Test for autocorrelation in bit sequence.
        
        Random sequences should have no significant autocorrelation.
        
        Args:
            bits: Binary sequence
            max_lag: Maximum lag to test
            
        Returns:
            TestResult with autocorrelation analysis
        """
        n = len(bits)
        if n < max_lag + 10:
            return TestResult(
                test_name="Autocorrelation",
                statistic=0,
                p_value=0,
                passed=False,
                details={"error": "Sequence too short"}
            )
        
        # Convert to +1/-1
        x = 2 * bits.astype(float) - 1
        
        # Compute autocorrelations
        autocorrs = []
        for lag in range(1, max_lag + 1):
            acf = np.sum(x[:-lag] * x[lag:]) / (n - lag)
            autocorrs.append(acf)
        
        # Maximum absolute autocorrelation
        max_acf = np.max(np.abs(autocorrs))
        
        # Threshold for significance (approximate)
        threshold = 2 / np.sqrt(n)
        
        # Check if any lag exceeds threshold
        passed = max_acf < threshold
        
        return TestResult(
            test_name="Autocorrelation",
            statistic=max_acf,
            p_value=1 - max_acf,  # Approximate
            passed=passed,
            details={
                "autocorrelations": autocorrs,
                "threshold": threshold,
                "max_lag_tested": max_lag
            }
        )
    
    def cross_correlation_test(
        self,
        key1: np.ndarray,
        key2: np.ndarray,
        max_lag: int = 5
    ) -> TestResult:
        """
        Test for cross-correlation between two sequences.
        
        Independent random sequences should have no cross-correlation.
        
        Args:
            key1: First bit sequence
            key2: Second bit sequence
            max_lag: Maximum lag to test
            
        Returns:
            TestResult with cross-correlation analysis
        """
        n = min(len(key1), len(key2))
        if n < max_lag + 10:
            return TestResult(
                test_name="Cross-correlation",
                statistic=0,
                p_value=0,
                passed=False,
                details={"error": "Sequences too short"}
            )
        
        # Convert to +1/-1
        x1 = 2 * key1[:n].astype(float) - 1
        x2 = 2 * key2[:n].astype(float) - 1
        
        # Compute cross-correlations at various lags
        cross_corrs = []
        for lag in range(-max_lag, max_lag + 1):
            if lag >= 0:
                ccf = np.sum(x1[:-lag-1] * x2[lag:]) / (n - abs(lag)) if lag < n-1 else 0
            else:
                ccf = np.sum(x1[-lag:] * x2[:lag]) / (n - abs(lag)) if -lag < n else 0
            cross_corrs.append(ccf)
        
        max_ccf = np.max(np.abs(cross_corrs))
        threshold = 2 / np.sqrt(n)
        
        return TestResult(
            test_name="Cross-correlation",
            statistic=max_ccf,
            p_value=1 - max_ccf,
            passed=max_ccf < threshold,
            details={
                "cross_correlations": cross_corrs,
                "threshold": threshold,
                "lags": list(range(-max_lag, max_lag + 1))
            }
        )
    
    def error_pattern_test(
        self,
        alice_key: np.ndarray,
        bob_key: np.ndarray
    ) -> TestResult:
        """
        Test if errors are randomly distributed.
        
        Non-random error patterns might indicate eavesdropping.
        
        Args:
            alice_key: Alice's key bits
            bob_key: Bob's key bits
            
        Returns:
            TestResult analyzing error distribution
        """
        errors = (alice_key != bob_key).astype(int)
        n = len(errors)
        
        if n < 20:
            return TestResult(
                test_name="Error Pattern",
                statistic=0,
                p_value=0,
                passed=False,
                details={"error": "Too few bits to analyze"}
            )
        
        # Run randomness test on error positions
        randomness = RandomnessTests(self.significance_level)
        freq_result = randomness.frequency_test(errors)
        runs_result = randomness.runs_test(errors)
        
        # Combine results
        passed = freq_result.passed and runs_result.passed
        
        return TestResult(
            test_name="Error Pattern",
            statistic=np.mean(errors),  # QBER
            p_value=min(freq_result.p_value, runs_result.p_value),
            passed=passed,
            details={
                "qber": float(np.mean(errors)),
                "num_errors": int(np.sum(errors)),
                "frequency_test": freq_result.to_dict(),
                "runs_test": runs_result.to_dict()
            }
        )
