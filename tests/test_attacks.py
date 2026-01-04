#!/usr/bin/env python3
"""
Unit tests for attack simulations.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.protocols import BB84Protocol
from src.attacks import InterceptResendAttack, PNSAttack, TrojanHorseAttack


class TestInterceptResendAttack:
    """Test suite for intercept-resend attack."""
    
    def test_initialization(self):
        """Test attack initialization."""
        attack = InterceptResendAttack(attack_probability=0.5, seed=42)
        assert attack.attack_probability == 0.5
    
    def test_attack_increases_qber(self):
        """Attack should increase QBER."""
        # Without attack
        bb84_clean = BB84Protocol(key_length=200, seed=42)
        result_clean = bb84_clean.run()
        
        # With attack
        bb84_attacked = BB84Protocol(key_length=200, seed=42)
        eve = InterceptResendAttack(attack_probability=1.0, seed=42)
        result_attacked = bb84_attacked.run(eavesdropper=eve)
        
        # QBER should be higher with attack
        assert result_attacked.qber > result_clean.qber
    
    def test_full_attack_qber_bound(self):
        """Full intercept-resend should cause ~25% QBER."""
        bb84 = BB84Protocol(key_length=500, seed=42)
        eve = InterceptResendAttack(attack_probability=1.0, seed=42)
        result = bb84.run(eavesdropper=eve)
        
        # Expected QBER is 25% for full intercept-resend
        assert 0.15 < result.qber < 0.35
    
    def test_partial_attack(self):
        """Partial attack should cause proportionally lower QBER."""
        qbers = []
        for prob in [0.0, 0.5, 1.0]:
            bb84 = BB84Protocol(key_length=200, seed=42)
            if prob > 0:
                eve = InterceptResendAttack(attack_probability=prob, seed=42)
                result = bb84.run(eavesdropper=eve)
            else:
                result = bb84.run()
            qbers.append(result.qber)
        
        # QBER should increase with attack probability
        assert qbers[0] < qbers[1] < qbers[2]
    
    def test_attack_results(self):
        """Attack should provide result metrics."""
        bb84 = BB84Protocol(key_length=100, seed=42)
        eve = InterceptResendAttack(attack_probability=1.0, seed=42)
        bb84.run(eavesdropper=eve)
        
        results = eve.get_results()
        assert results is not None
        assert hasattr(results, 'eve_information')


class TestPNSAttack:
    """Test suite for PNS attack."""
    
    def test_initialization(self):
        """Test attack initialization."""
        attack = PNSAttack(mean_photon_number=0.1, seed=42)
        assert attack.mean_photon_number == 0.1
    
    def test_vulnerable_fraction_calculation(self):
        """Test vulnerable key fraction calculation."""
        # Higher mean photon number = more vulnerable
        low_mu = PNSAttack.vulnerable_key_fraction(0.1)
        high_mu = PNSAttack.vulnerable_key_fraction(0.5)
        
        assert high_mu > low_mu
        assert 0 <= low_mu <= 1
        assert 0 <= high_mu <= 1
    
    def test_safe_distance_calculation(self):
        """Test safe distance calculation."""
        # Lower mean photon = longer safe distance
        low_mu_dist = PNSAttack.safe_distance_km(0.1)
        high_mu_dist = PNSAttack.safe_distance_km(0.5)
        
        assert low_mu_dist > high_mu_dist
        assert low_mu_dist > 0


class TestTrojanHorseAttack:
    """Test suite for Trojan horse attack."""
    
    def test_initialization(self):
        """Test attack initialization."""
        attack = TrojanHorseAttack(probe_intensity=0.01, seed=42)
        assert attack.probe_intensity == 0.01
    
    def test_information_gain_calculation(self):
        """Test information gain is reasonable."""
        attack = TrojanHorseAttack(probe_intensity=0.01, seed=42)
        
        # Simulate attack on a key
        test_key = np.random.randint(0, 2, 100)
        eve_info = attack.estimate_information_gain(test_key)
        
        # Should gain some information
        assert 0 <= eve_info <= len(test_key)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
