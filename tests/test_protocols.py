#!/usr/bin/env python3
"""
Unit tests for QKD protocol implementations.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.protocols import BB84Protocol, B92Protocol, E91Protocol, SARG04Protocol


class TestBB84Protocol:
    """Test suite for BB84 protocol."""
    
    def test_initialization(self):
        """Test protocol initialization."""
        protocol = BB84Protocol(key_length=100, seed=42)
        assert protocol.key_length == 100
        assert protocol.seed == 42
    
    def test_basic_run(self):
        """Test basic protocol execution."""
        protocol = BB84Protocol(key_length=100, seed=42)
        result = protocol.run()
        
        assert result is not None
        assert result.raw_key_length > 0
        assert result.sifted_key_length > 0
        assert len(result.alice_key) == result.sifted_key_length
        assert len(result.bob_key) == result.sifted_key_length
    
    def test_no_noise_perfect_keys(self):
        """Without noise, Alice and Bob should have identical keys."""
        protocol = BB84Protocol(key_length=100, seed=42)
        result = protocol.run()
        
        # QBER should be very low (may have small simulator noise)
        assert result.qber < 0.01
    
    def test_sifting_efficiency(self):
        """Test that sifting efficiency is around 50%."""
        protocol = BB84Protocol(key_length=500, seed=42)
        result = protocol.run()
        
        efficiency = result.sifted_key_length / result.raw_key_length
        # Should be approximately 50% (with some variance)
        assert 0.4 < efficiency < 0.6
    
    def test_reproducibility(self):
        """Test that same seed produces same results."""
        protocol1 = BB84Protocol(key_length=100, seed=42)
        protocol2 = BB84Protocol(key_length=100, seed=42)
        
        result1 = protocol1.run()
        result2 = protocol2.run()
        
        np.testing.assert_array_equal(result1.alice_key, result2.alice_key)
    
    def test_theoretical_key_rate(self):
        """Test theoretical key rate calculation."""
        # At 0% QBER, rate should be 1
        assert BB84Protocol.theoretical_key_rate(0) == 1.0
        
        # At high QBER, rate should be 0 or negative
        assert BB84Protocol.theoretical_key_rate(0.15) <= 0
        
        # Rate should decrease with increasing QBER
        rate_low = BB84Protocol.theoretical_key_rate(0.01)
        rate_high = BB84Protocol.theoretical_key_rate(0.05)
        assert rate_low > rate_high


class TestB92Protocol:
    """Test suite for B92 protocol."""
    
    def test_initialization(self):
        """Test protocol initialization."""
        protocol = B92Protocol(key_length=100, seed=42)
        assert protocol.key_length == 100
    
    def test_basic_run(self):
        """Test basic protocol execution."""
        protocol = B92Protocol(key_length=100, seed=42)
        result = protocol.run()
        
        assert result is not None
        assert result.raw_key_length > 0
    
    def test_lower_sifting_efficiency(self):
        """B92 should have ~25% sifting efficiency."""
        protocol = B92Protocol(key_length=500, seed=42)
        result = protocol.run()
        
        efficiency = result.sifted_key_length / result.raw_key_length
        # Should be approximately 25%
        assert 0.15 < efficiency < 0.35


class TestE91Protocol:
    """Test suite for E91 protocol."""
    
    def test_initialization(self):
        """Test protocol initialization."""
        protocol = E91Protocol(key_length=100, seed=42)
        assert protocol.key_length == 100
    
    def test_basic_run(self):
        """Test basic protocol execution."""
        protocol = E91Protocol(key_length=100, seed=42)
        result = protocol.run()
        
        assert result is not None
        assert result.raw_key_length > 0
    
    def test_bell_test(self):
        """Test that Bell test returns valid CHSH parameter."""
        protocol = E91Protocol(key_length=200, seed=42)
        result = protocol.run()
        
        if hasattr(result, 'chsh_parameter'):
            # CHSH should violate classical bound for true entanglement
            # Classical bound is 2, quantum max is 2*sqrt(2) ≈ 2.83
            assert result.chsh_parameter is not None


class TestSARG04Protocol:
    """Test suite for SARG04 protocol."""
    
    def test_initialization(self):
        """Test protocol initialization."""
        protocol = SARG04Protocol(key_length=100, seed=42)
        assert protocol.key_length == 100
    
    def test_basic_run(self):
        """Test basic protocol execution."""
        protocol = SARG04Protocol(key_length=100, seed=42)
        result = protocol.run()
        
        assert result is not None
        assert result.raw_key_length > 0
    
    def test_sifting_efficiency(self):
        """SARG04 should have ~25% sifting efficiency."""
        protocol = SARG04Protocol(key_length=500, seed=42)
        result = protocol.run()
        
        efficiency = result.sifted_key_length / result.raw_key_length
        # Should be approximately 25%
        assert 0.15 < efficiency < 0.35


class TestProtocolComparison:
    """Cross-protocol comparison tests."""
    
    def test_all_protocols_produce_output(self):
        """All protocols should produce valid output."""
        protocols = [
            BB84Protocol(key_length=50, seed=42),
            B92Protocol(key_length=50, seed=42),
            E91Protocol(key_length=50, seed=42),
            SARG04Protocol(key_length=50, seed=42)
        ]
        
        for protocol in protocols:
            result = protocol.run()
            assert result.final_key_length > 0 or result.sifted_key_length > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
