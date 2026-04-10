#!/usr/bin/env python3
"""
Experiment 05: Full QKD Simulation (Fixed Version)
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
from datetime import datetime
import math

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.protocols import BB84Protocol
from src.attacks import InterceptResendAttack
from src.noise_models import DepolarizingChannel
from src.analysis import SecurityMetrics, RandomnessTests
from src.utils import cascade_protocol, privacy_amplification

def estimate_final_key_length_helper(sifted_length, qber, efficiency_factor=1.1):
    """Internal helper to calculate secret key yield."""
    if qber >= 0.11 or sifted_length <= 0:
        return 0
    def h(e):
        if e <= 0 or e >= 1: return 0
        return -e * math.log2(e) - (1 - e) * math.log2(1 - e)
    leaked_bits = efficiency_factor * h(qber)
    privacy_bits = h(qber)
    final_length = int(sifted_length * (1 - leaked_bits - privacy_bits))
    return max(0, final_length)

def run_full_qkd_simulation(key_length=1000, noise_level=0.02, with_attack=False, verbose=True):
    results = {
        'timestamp': datetime.now().isoformat(),
        'parameters': {'key_length': key_length, 'noise_level': noise_level, 'with_attack': with_attack}
    }
    
    if verbose:
        print("=" * 70)
        print("Full QKD Simulation: Logic Fixed")
        print("=" * 70)

    # PHASE 1: Protocol Execution
    bb84 = BB84Protocol(key_length=key_length, verbose=False, seed=42)
    noise_model = DepolarizingChannel(noise_level).get_noise_model() if noise_level > 0 else None
    eavesdropper = InterceptResendAttack(attack_probability=0.3, seed=42) if with_attack else None
    
    protocol_result = bb84.run(noise_model=noise_model, eavesdropper=eavesdropper)
    
    # PHASE 2: Error Estimation (FIXED: Uses actual array size)
    if verbose:
        print("\n[Phase 2] Error Estimation")
        print("-" * 50)
    
    # Measures the actual data array size to avoid IndexError: 1000
    actual_data_len = len(protocol_result.alice_key)
    sample_size = max(10, int(actual_data_len * 0.1))
    
    sample_indices = np.random.choice(actual_data_len, sample_size, replace=False)
    
    alice_sample = protocol_result.alice_key[sample_indices]
    bob_sample = protocol_result.bob_key[sample_indices]
    estimated_qber = np.mean(alice_sample != bob_sample)
    
    # Fix: Range calculation is now strictly 0 to (actual_data_len - 1)
    remaining_indices = np.setdiff1d(np.arange(actual_data_len), sample_indices)
    alice_key = protocol_result.alice_key[remaining_indices]
    bob_key = protocol_result.bob_key[remaining_indices]

    # PHASE 3: Error Correction
    if verbose: print("\n[Phase 3] Error Correction (CASCADE)")
    corrected_key, bits_disclosed = cascade_protocol(alice_key, bob_key, num_passes=4)
    remaining_errors = np.sum(alice_key != corrected_key)

    # PHASE 4: Privacy Amplification
    if verbose: print("\n[Phase 4] Privacy Amplification")
    final_length = estimate_final_key_length_helper(len(alice_key), estimated_qber)
    final_key = privacy_amplification(alice_key, final_length, method='toeplitz') if final_length > 0 else np.array([])

    if verbose:
        print(f"  Raw bits: {protocol_result.raw_key_length}")
        print(f"  Final Secure Key: {len(final_key)} bits")

    results['summary'] = {
        'initial_qubits': protocol_result.raw_key_length,
        'final_key_bits': len(final_key),
        'overall_efficiency': len(final_key) / protocol_result.raw_key_length if protocol_result.raw_key_length > 0 else 0,
        'security_verified': estimated_qber < 0.11
    }
    results['phase2_estimation'] = {'estimated_qber': estimated_qber}
    return results

def main():
    # Run the comparison suite
    scenarios = [
        {'name': 'Ideal Channel', 'noise': 0.0, 'attack': False},
        {'name': 'Low Noise', 'noise': 0.02, 'attack': False},
        {'name': 'Medium Noise', 'noise': 0.05, 'attack': False},
        {'name': 'High Noise', 'noise': 0.08, 'attack': False},
        {'name': 'With Eavesdropper', 'noise': 0.02, 'attack': True},
    ]
    
    comp_results = []
    print("Running Comparative Simulations...")
    for s in tqdm(scenarios):
        res = run_full_qkd_simulation(key_length=500, noise_level=s['noise'], with_attack=s['attack'], verbose=False)
        comp_results.append({
            'scenario': s['name'],
            'qber': res.get('phase2_estimation', {}).get('estimated_qber', 0),
            'bits': res['summary']['final_key_bits'],
            'secure': res['summary']['security_verified']
        })

    # Display results table
    print(f"\n{'Scenario':<20} {'QBER':<10} {'Secure Key':<15} {'Status'}")
    print("-" * 60)
    for r in comp_results:
        status = "SECURE" if r['secure'] else "INSECURE"
        print(f"{r['scenario']:<20} {r['qber']:<10.2%} {r['bits']:<15} {status}")

    # Generate Visualization
    names = [r['scenario'] for r in comp_results]
    bits = [r['bits'] for r in comp_results]
    
    plt.figure(figsize=(10, 6))
    plt.barh(names, bits, color='steelblue')
    plt.title("Experiment 05: Secret Key Yield Across Scenarios")
    plt.xlabel("Secure Bits Generated")
    
    os.makedirs('results/figures', exist_ok=True)
    plt.savefig('results/figures/exp05_full_simulation.png')
    print("\n[SUCCESS] Figure saved: results/figures/exp05_full_simulation.png")
    plt.show()

if __name__ == "__main__":
    main()