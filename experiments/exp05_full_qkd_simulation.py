#!/usr/bin/env python3
"""
Experiment 05: Full QKD Simulation

This experiment runs a complete QKD simulation including:
- Protocol execution
- Error correction (CASCADE)
- Privacy amplification
- Statistical verification of final keys

This represents a full end-to-end QKD implementation.

Learning Objectives:
1. Understand complete QKD workflow
2. See post-processing effects on key length
3. Verify statistical properties of final keys

Run: python experiments/exp05_full_qkd_simulation.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
from datetime import datetime

from src.protocols import BB84Protocol
from src.attacks import InterceptResendAttack
from src.noise_models import DepolarizingChannel, RealisticFiberChannel, FiberParameters
from src.analysis import SecurityMetrics, RandomnessTests, QKDVisualizer
from src.utils import cascade_protocol, privacy_amplification, estimate_final_key_length


def run_full_qkd_simulation(
    key_length: int = 1000,
    noise_level: float = 0.02,
    with_attack: bool = False,
    verbose: bool = True
):
    """
    Run a complete QKD simulation.
    
    Args:
        key_length: Target sifted key length
        noise_level: Channel noise probability
        with_attack: Whether to include an eavesdropper
        verbose: Print detailed output
        
    Returns:
        Dictionary with simulation results
    """
    results = {
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'key_length': key_length,
            'noise_level': noise_level,
            'with_attack': with_attack
        }
    }
    
    if verbose:
        print("=" * 70)
        print("Full QKD Simulation")
        print("=" * 70)
    
    # =========================================
    # PHASE 1: Protocol Execution
    # =========================================
    if verbose:
        print("\n[Phase 1] Protocol Execution")
        print("-" * 50)
    
    bb84 = BB84Protocol(key_length=key_length, verbose=False, seed=42)
    
    # Set up channel
    noise_model = None
    if noise_level > 0:
        noise_model = DepolarizingChannel(noise_level).get_noise_model()
    
    # Set up eavesdropper
    eavesdropper = None
    if with_attack:
        eavesdropper = InterceptResendAttack(attack_probability=0.3, seed=42)
    
    # Run protocol
    protocol_result = bb84.run(noise_model=noise_model, eavesdropper=eavesdropper)
    
    results['phase1_protocol'] = {
        'raw_bits': protocol_result.raw_key_length,
        'sifted_bits': protocol_result.sifted_key_length,
        'sifting_efficiency': protocol_result.sifted_key_length / protocol_result.raw_key_length,
        'raw_qber': protocol_result.qber,
        'execution_time': protocol_result.execution_time
    }
    
    if verbose:
        print(f"  Raw bits transmitted: {protocol_result.raw_key_length}")
        print(f"  Sifted key length: {protocol_result.sifted_key_length}")
        print(f"  Sifting efficiency: {results['phase1_protocol']['sifting_efficiency']:.2%}")
        print(f"  Raw QBER: {protocol_result.qber:.4f}")
    
    # =========================================
    # PHASE 2: Error Estimation
    # =========================================
    if verbose:
        print("\n[Phase 2] Error Estimation")
        print("-" * 50)
    
    # Use 10% of bits for error estimation
    sample_size = max(100, int(protocol_result.sifted_key_length * 0.1))
    sample_indices = np.random.choice(
        protocol_result.sifted_key_length, 
        sample_size, 
        replace=False
    )
    
    alice_sample = protocol_result.alice_key[sample_indices]
    bob_sample = protocol_result.bob_key[sample_indices]
    
    estimated_qber = np.mean(alice_sample != bob_sample)
    
    # Remove sample bits from key
    remaining_indices = np.setdiff1d(
        np.arange(protocol_result.sifted_key_length),
        sample_indices
    )
    alice_key = protocol_result.alice_key[remaining_indices]
    bob_key = protocol_result.bob_key[remaining_indices]
    
    results['phase2_estimation'] = {
        'sample_size': sample_size,
        'estimated_qber': estimated_qber,
        'remaining_bits': len(alice_key)
    }
    
    if verbose:
        print(f"  Sample size: {sample_size}")
        print(f"  Estimated QBER: {estimated_qber:.4f}")
        print(f"  Remaining bits: {len(alice_key)}")
    
    # Security check
    if estimated_qber > 0.11:
        if verbose:
            print("\n  *** ABORT: QBER exceeds security threshold! ***")
        results['aborted'] = True
        results['abort_reason'] = 'QBER exceeds threshold'
        return results
    
    # =========================================
    # PHASE 3: Error Correction
    # =========================================
    if verbose:
        print("\n[Phase 3] Error Correction (CASCADE)")
        print("-" * 50)
    
    corrected_key, bits_disclosed = cascade_protocol(alice_key, bob_key, num_passes=4)
    
    # Verify correction
    remaining_errors = np.sum(alice_key != corrected_key)
    
    results['phase3_error_correction'] = {
        'bits_disclosed': bits_disclosed,
        'remaining_errors': int(remaining_errors),
        'correction_success': remaining_errors == 0
    }
    
    if verbose:
        print(f"  Bits disclosed: {bits_disclosed}")
        print(f"  Remaining errors: {remaining_errors}")
        print(f"  Correction {'successful' if remaining_errors == 0 else 'FAILED'}")
    
    # =========================================
    # PHASE 4: Privacy Amplification
    # =========================================
    if verbose:
        print("\n[Phase 4] Privacy Amplification")
        print("-" * 50)
    
    # Calculate final key length
    n = len(alice_key)
    
    # Bits to remove: Eve's information + EC leakage + finite-key correction
    security_param = 1e-10
    
    # Estimate Eve's information (Holevo bound)
    h_e = -estimated_qber * np.log2(estimated_qber + 1e-10) - \
          (1 - estimated_qber) * np.log2(1 - estimated_qber + 1e-10) if estimated_qber > 0 else 0
    
    eve_bits = int(n * h_e)
    finite_correction = int(np.sqrt(n) * np.log2(1/security_param))
    
    final_length = max(0, n - eve_bits - bits_disclosed - finite_correction)
    
    # Apply privacy amplification
    if final_length > 0:
        final_key = privacy_amplification(alice_key, final_length, method='toeplitz')
    else:
        final_key = np.array([])
    
    results['phase4_privacy_amplification'] = {
        'pre_pa_length': n,
        'eve_information_bits': eve_bits,
        'ec_disclosed_bits': bits_disclosed,
        'finite_key_correction': finite_correction,
        'final_key_length': len(final_key)
    }
    
    if verbose:
        print(f"  Pre-PA key length: {n}")
        print(f"  Eve's information (est): {eve_bits} bits")
        print(f"  EC disclosed: {bits_disclosed} bits")
        print(f"  Finite-key correction: {finite_correction} bits")
        print(f"  Final key length: {len(final_key)}")
    
    # =========================================
    # PHASE 5: Key Verification
    # =========================================
    if verbose:
        print("\n[Phase 5] Key Verification")
        print("-" * 50)
    
    if len(final_key) >= 100:
        randomness = RandomnessTests()
        test_results = randomness.run_all_tests(final_key)
        
        passed = sum(1 for r in test_results if r.passed)
        total = len(test_results)
        
        results['phase5_verification'] = {
            'tests_passed': passed,
            'tests_total': total,
            'pass_rate': passed / total,
            'test_details': [r.to_dict() for r in test_results]
        }
        
        if verbose:
            print(f"  Randomness tests: {passed}/{total} passed")
            for r in test_results:
                status = "✓" if r.passed else "✗"
                print(f"    {status} {r.test_name}: p-value = {r.p_value:.4f}")
    else:
        results['phase5_verification'] = {
            'message': 'Key too short for statistical tests'
        }
        if verbose:
            print("  Key too short for statistical tests")
    
    # =========================================
    # SUMMARY
    # =========================================
    if verbose:
        print("\n" + "=" * 70)
        print("Simulation Summary")
        print("=" * 70)
        print(f"  Initial transmission: {protocol_result.raw_key_length} qubits")
        print(f"  After sifting: {protocol_result.sifted_key_length} bits")
        print(f"  After estimation: {len(alice_key)} bits")
        print(f"  Final secure key: {len(final_key)} bits")
        print(f"  Overall efficiency: {len(final_key)/protocol_result.raw_key_length:.4f}")
        print(f"  Security: {'VERIFIED' if estimated_qber < 0.11 else 'COMPROMISED'}")
    
    results['summary'] = {
        'initial_qubits': protocol_result.raw_key_length,
        'final_key_bits': len(final_key),
        'overall_efficiency': len(final_key) / protocol_result.raw_key_length,
        'security_verified': estimated_qber < 0.11
    }
    
    results['final_key'] = final_key.tolist() if len(final_key) > 0 else []
    results['aborted'] = False
    
    return results


def run_comparison_simulations():
    """Run simulations under different conditions."""
    print("\n\n" + "=" * 70)
    print("Comparative Simulations")
    print("=" * 70)
    
    scenarios = [
        {'name': 'Ideal Channel', 'noise': 0.0, 'attack': False},
        {'name': 'Low Noise', 'noise': 0.02, 'attack': False},
        {'name': 'Medium Noise', 'noise': 0.05, 'attack': False},
        {'name': 'High Noise', 'noise': 0.08, 'attack': False},
        {'name': 'With Eavesdropper', 'noise': 0.02, 'attack': True},
    ]
    
    comparison_results = []
    
    for scenario in tqdm(scenarios, desc="Running scenarios"):
        result = run_full_qkd_simulation(
            key_length=500,
            noise_level=scenario['noise'],
            with_attack=scenario['attack'],
            verbose=False
        )
        
        comparison_results.append({
            'scenario': scenario['name'],
            'noise': scenario['noise'],
            'attack': scenario['attack'],
            'qber': result.get('phase2_estimation', {}).get('estimated_qber', 0),
            'final_key': result.get('summary', {}).get('final_key_bits', 0),
            'efficiency': result.get('summary', {}).get('overall_efficiency', 0),
            'secure': result.get('summary', {}).get('security_verified', False),
            'aborted': result.get('aborted', False)
        })
    
    print("\nComparison Results:")
    print(f"{'Scenario':>20} {'QBER':>8} {'Final Key':>12} {'Efficiency':>12} {'Secure':>8}")
    print("-" * 65)
    for r in comparison_results:
        status = 'ABORT' if r['aborted'] else ('YES' if r['secure'] else 'NO')
        print(f"{r['scenario']:>20} {r['qber']*100:>7.2f}% "
              f"{r['final_key']:>12} {r['efficiency']*100:>11.2f}% {status:>8}")
    
    return comparison_results


def create_simulation_visualization(comparison_results):
    """Create visualization of simulation results."""
    print("\nCreating Visualization...")
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    scenarios = [r['scenario'] for r in comparison_results if not r['aborted']]
    
    # Plot 1: QBER by scenario
    qbers = [r['qber'] * 100 for r in comparison_results if not r['aborted']]
    colors = ['green' if r['secure'] else 'red' for r in comparison_results if not r['aborted']]
    axes[0].barh(scenarios, qbers, color=colors, edgecolor='black')
    axes[0].axvline(x=11, color='red', linestyle='--', alpha=0.7, label='Threshold')
    axes[0].set_xlabel('QBER (%)')
    axes[0].set_title('QBER by Scenario')
    axes[0].legend()
    
    # Plot 2: Final key length
    final_keys = [r['final_key'] for r in comparison_results if not r['aborted']]
    axes[1].barh(scenarios, final_keys, color='steelblue', edgecolor='black')
    axes[1].set_xlabel('Final Key Length (bits)')
    axes[1].set_title('Secure Key Generated')
    
    # Plot 3: Overall efficiency
    efficiencies = [r['efficiency'] * 100 for r in comparison_results if not r['aborted']]
    axes[2].barh(scenarios, efficiencies, color='orange', edgecolor='black')
    axes[2].set_xlabel('Efficiency (%)')
    axes[2].set_title('Overall QKD Efficiency')
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('results/figures', exist_ok=True)
    fig.savefig('results/figures/exp05_full_simulation.png', dpi=150, bbox_inches='tight')
    print(f"Saved figure to results/figures/exp05_full_simulation.png")
    
    plt.show()


def main():
    """Main experiment runner."""
    # Run detailed single simulation
    result = run_full_qkd_simulation(
        key_length=1000,
        noise_level=0.02,
        with_attack=False,
        verbose=True
    )
    
    # Save detailed result
    os.makedirs('results/data', exist_ok=True)
    with open('results/data/exp05_detailed_result.json', 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        result_copy = result.copy()
        if 'final_key' in result_copy:
            del result_copy['final_key']  # Don't save key
        json.dump(result_copy, f, indent=2, default=str)
    print(f"\nSaved detailed result to results/data/exp05_detailed_result.json")
    
    # Run comparison simulations
    comparison_results = run_comparison_simulations()
    
    # Create visualization
    create_simulation_visualization(comparison_results)
    
    print("\n" + "=" * 70)
    print("Experiment Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
