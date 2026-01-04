#!/usr/bin/env python3
"""
Unit tests for analysis modules.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis import SecurityMetrics, RandomnessTests


class TestSecurityMetrics:
    """Test suite for security metrics."""
    
    def test_initialization_identical_keys(self):
        """Test with identical keys (no errors)."""
        key = np.random.randint(0, 2, 100)
        metrics = SecurityMetrics(key, key.copy())
        
        assert metrics.qber == 0
    
    def test_qber_calculation(self):
        """Test QBER calculation."""
        alice_key = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        bob_key = np.array([0, 1, 1, 1, 0, 0, 0, 1, 0, 1])  # 2 errors
        
        metrics = SecurityMetrics(alice_key, bob_key)
        assert metrics.qber == 0.2  # 2/10
    
    def test_is_secure(self):
        """Test security threshold check."""
        key_length = 100
        
        # Low QBER - secure
        alice = np.random.randint(0, 2, key_length)
        bob_low = alice.copy()
        bob_low[:5] = 1 - bob_low[:5]  # 5% errors
        
        metrics_low = SecurityMetrics(alice, bob_low)
        assert metrics_low.is_secure() == True
        
        # High QBER - not secure
        bob_high = alice.copy()
        bob_high[:15] = 1 - bob_high[:15]  # 15% errors
        
        metrics_high = SecurityMetrics(alice, bob_high)
        assert metrics_high.is_secure() == False
    
    def test_secret_key_rate(self):
        """Test secret key rate calculation."""
        # No errors - high key rate
        alice = np.random.randint(0, 2, 100)
        metrics_good = SecurityMetrics(alice, alice.copy())
        
        # Many errors - low/negative key rate
        bob_bad = alice.copy()
        bob_bad[:15] = 1 - bob_bad[:15]
        metrics_bad = SecurityMetrics(alice, bob_bad)
        
        assert metrics_good.secret_key_rate() > metrics_bad.secret_key_rate()
    
    def test_mutual_information(self):
        """Test mutual information calculation."""
        alice = np.random.randint(0, 2, 100)
        bob = alice.copy()
        bob[:5] = 1 - bob[:5]  # 5% errors
        
        metrics = SecurityMetrics(alice, bob)
        
        mi_ab = metrics.mutual_information_ab()
        
        # Mutual information should be high for low QBER
        assert mi_ab > 0.5


class TestRandomnessTests:
    """Test suite for randomness testing."""
    
    def test_frequency_test_random(self):
        """Frequency test on random data should pass."""
        random_bits = np.random.randint(0, 2, 1000)
        tests = RandomnessTests()
        
        result = tests.frequency_test(random_bits)
        # Random data should typically pass
        assert result.p_value > 0.001
    
    def test_frequency_test_biased(self):
        """Frequency test on biased data should fail."""
        biased_bits = np.ones(1000, dtype=int)  # All ones
        tests = RandomnessTests()
        
        result = tests.frequency_test(biased_bits)
        # Biased data should fail
        assert not result.passed
    
    def test_runs_test_random(self):
        """Runs test on random data."""
        random_bits = np.random.randint(0, 2, 1000)
        tests = RandomnessTests()
        
        result = tests.runs_test(random_bits)
        # Should get a result
        assert result.p_value is not None
    
    def test_runs_test_patterned(self):
        """Runs test on patterned data should fail."""
        patterned = np.array([0, 1] * 500)  # Alternating pattern
        tests = RandomnessTests()
        
        result = tests.runs_test(patterned)
        # Patterned data should fail
        assert not result.passed or result.p_value < 0.01
    
    def test_run_all_tests(self):
        """Test running all tests."""
        random_bits = np.random.randint(0, 2, 1000)
        tests = RandomnessTests()
        
        results = tests.run_all_tests(random_bits)
        
        # Should return multiple test results
        assert len(results) > 0
        
        # Each result should have required attributes
        for r in results:
            assert hasattr(r, 'test_name')
            assert hasattr(r, 'p_value')
            assert hasattr(r, 'passed')


class TestEntropyCalculations:
    """Test entropy-related calculations."""
    
    def test_binary_entropy_bounds(self):
        """Binary entropy should be bounded [0, 1]."""
        from src.analysis.security_metrics import binary_entropy
        
        for p in [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
            h = binary_entropy(p)
            assert 0 <= h <= 1
    
    def test_binary_entropy_maximum(self):
        """Binary entropy is maximum at p=0.5."""
        from src.analysis.security_metrics import binary_entropy
        
        h_half = binary_entropy(0.5)
        h_quarter = binary_entropy(0.25)
        h_tenth = binary_entropy(0.1)
        
        assert h_half > h_quarter
        assert h_quarter > h_tenth
        assert abs(h_half - 1.0) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
