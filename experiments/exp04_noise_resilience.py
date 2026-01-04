#!/usr/bin/env python3
"""
Experiment 04: Noise Resilience Analysis

This experiment analyzes how QKD protocols perform under various
realistic noise conditions including fiber channels.

Learning Objectives:
1. Understand different noise models
2. Compare noise resilience across protocols
3. Analyze practical distance limits

Run: python experiments/exp04_noise_resilience.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from src.protocols import BB84Protocol
from src.noise_models import (
    DepolarizingChannel,
    AmplitudeDampingChannel,
    PhaseDampingChannel,
    RealisticFiberChannel,
    FiberParameters,
    DetectorParameters
)
from src.analysis import SecurityMetrics


def analyze_depolarizing_noise():
    """Analyze BB84 under depolarizing noise."""
    print("=" * 70)
    print("Experiment 04: Noise Resilience Analysis")
    print("=" * 70)
    
    print("\n1. Depolarizing Channel Analysis")
    print("-" * 50)
    
    noise_levels = np.linspace(0, 0.2, 15)
    results = []
    
    for noise in tqdm(noise_levels, desc="Testing depolarizing noise"):
        bb84 = BB84Protocol(key_length=256, seed=42)
        
        if noise > 0:
            channel = DepolarizingChannel(error_probability=noise)
            result = bb84.run(noise_model=channel.get_noise_model())
        else:
            result = bb84.run()
        
        metrics = SecurityMetrics(result.alice_key, result.bob_key)
        
        results.append({
            'noise': noise,
            'qber': result.qber,
            'key_rate': metrics.secret_key_rate(),
            'is_secure': metrics.is_secure(),
            'expected_qber': channel.expected_qber() if noise > 0 else 0
        })
    
    return results


def analyze_amplitude_damping():
    """Analyze effect of amplitude damping (photon loss)."""
    print("\n\n2. Amplitude Damping (Photon Loss) Analysis")
    print("-" * 50)
    
    damping_levels = np.linspace(0, 0.5, 15)
    results = []
    
    for damping in tqdm(damping_levels, desc="Testing amplitude damping"):
        bb84 = BB84Protocol(key_length=256, seed=42)
        
        if damping > 0:
            channel = AmplitudeDampingChannel(damping_probability=damping)
            result = bb84.run(noise_model=channel.get_noise_model())
        else:
            result = bb84.run()
        
        metrics = SecurityMetrics(result.alice_key, result.bob_key)
        
        results.append({
            'damping': damping,
            'qber': result.qber,
            'key_rate': metrics.secret_key_rate(),
            'transmission': 1 - damping
        })
    
    return results


def analyze_phase_damping():
    """Analyze effect of phase damping (dephasing)."""
    print("\n\n3. Phase Damping (Dephasing) Analysis")
    print("-" * 50)
    
    dephasing_levels = np.linspace(0, 0.5, 15)
    results = []
    
    for dephasing in tqdm(dephasing_levels, desc="Testing phase damping"):
        bb84 = BB84Protocol(key_length=256, seed=42)
        
        if dephasing > 0:
            channel = PhaseDampingChannel(dephasing_probability=dephasing)
            result = bb84.run(noise_model=channel.get_noise_model())
        else:
            result = bb84.run()
        
        metrics = SecurityMetrics(result.alice_key, result.bob_key)
        
        results.append({
            'dephasing': dephasing,
            'qber': result.qber,
            'key_rate': metrics.secret_key_rate()
        })
    
    return results


def analyze_fiber_distance():
    """Analyze QKD performance vs fiber distance."""
    print("\n\n4. Realistic Fiber Channel Analysis")
    print("-" * 50)
    
    distances = np.linspace(0, 200, 20)
    results = []
    
    for dist in tqdm(distances, desc="Testing fiber distances"):
        fiber = FiberParameters(
            length_km=dist,
            attenuation_db_per_km=0.2
        )
        detector = DetectorParameters(efficiency=0.15)
        channel = RealisticFiberChannel(fiber=fiber, detector=detector)
        
        # Get channel metrics (without running full protocol)
        summary = channel.get_summary()
        
        results.append({
            'distance': dist,
            'total_loss_db': summary['total_loss_db'],
            'transmission': summary['total_transmission'],
            'expected_qber': summary['expected_qber'],
            'key_rate': summary['secure_key_rate_bps']
        })
    
    # Print summary table
    print("\nFiber Distance Analysis:")
    print(f"{'Distance':>10} {'Loss (dB)':>12} {'QBER':>10} {'Key Rate':>15}")
    print("-" * 50)
    for r in results[::4]:  # Every 4th result
        print(f"{r['distance']:>9.0f}km {r['total_loss_db']:>11.1f} "
              f"{r['expected_qber']*100:>9.2f}% {r['key_rate']:>14.0f} bps")
    
    return results


def compare_noise_types():
    """Compare effect of different noise types at same error level."""
    print("\n\n5. Noise Type Comparison")
    print("-" * 50)
    
    # Fixed effective error rate for comparison
    target_qber = 0.05
    
    noise_types = {
        'Depolarizing': DepolarizingChannel(error_probability=target_qber * 1.5),
        'Amplitude Damping': AmplitudeDampingChannel(damping_probability=target_qber * 2),
        'Phase Damping': PhaseDampingChannel(dephasing_probability=target_qber * 2),
    }
    
    results = []
    for name, channel in tqdm(noise_types.items(), desc="Comparing noise types"):
        bb84 = BB84Protocol(key_length=256, seed=42)
        result = bb84.run(noise_model=channel.get_noise_model())
        metrics = SecurityMetrics(result.alice_key, result.bob_key)
        
        results.append({
            'noise_type': name,
            'qber': result.qber,
            'key_rate': metrics.secret_key_rate()
        })
    
    print("\nNoise Type Comparison:")
    print(f"{'Noise Type':>20} {'QBER':>10} {'Key Rate':>12}")
    print("-" * 45)
    for r in results:
        print(f"{r['noise_type']:>20} {r['qber']*100:>9.2f}% {r['key_rate']:>12.4f}")
    
    return results


def create_noise_visualizations(depol_results, amp_results, phase_results, fiber_results):
    """Create noise analysis visualizations."""
    print("\n\n6. Creating Visualizations")
    print("-" * 50)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Depolarizing - QBER vs noise
    ax1 = axes[0, 0]
    noise_vals = [r['noise'] * 100 for r in depol_results]
    qber_vals = [r['qber'] * 100 for r in depol_results]
    expected_vals = [r['expected_qber'] * 100 for r in depol_results]
    ax1.plot(noise_vals, qber_vals, 'bo-', label='Observed QBER', linewidth=2)
    ax1.plot(noise_vals, expected_vals, 'g--', label='Expected QBER', linewidth=2)
    ax1.axhline(y=11, color='red', linestyle='--', alpha=0.7, label='Threshold')
    ax1.set_xlabel('Depolarizing Probability (%)')
    ax1.set_ylabel('QBER (%)')
    ax1.set_title('Depolarizing Channel: QBER Analysis')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Compare all noise types - Key rate
    ax2 = axes[0, 1]
    # Depolarizing
    ax2.plot([r['noise']*100 for r in depol_results],
             [r['key_rate'] for r in depol_results],
             'b-', label='Depolarizing', linewidth=2)
    # Amplitude damping
    ax2.plot([r['damping']*100 for r in amp_results],
             [r['key_rate'] for r in amp_results],
             'r-', label='Amplitude Damping', linewidth=2)
    # Phase damping
    ax2.plot([r['dephasing']*100 for r in phase_results],
             [r['key_rate'] for r in phase_results],
             'g-', label='Phase Damping', linewidth=2)
    ax2.set_xlabel('Noise Parameter (%)')
    ax2.set_ylabel('Secret Key Rate')
    ax2.set_title('Key Rate vs Noise Level')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Fiber distance - Transmission and QBER
    ax3 = axes[1, 0]
    distances = [r['distance'] for r in fiber_results]
    transmissions = [r['transmission'] * 100 for r in fiber_results]
    qbers = [r['expected_qber'] * 100 for r in fiber_results]
    
    ax3_twin = ax3.twinx()
    line1, = ax3.plot(distances, transmissions, 'b-', linewidth=2, label='Transmission')
    line2, = ax3_twin.plot(distances, qbers, 'r-', linewidth=2, label='QBER')
    ax3_twin.axhline(y=11, color='red', linestyle='--', alpha=0.5)
    
    ax3.set_xlabel('Distance (km)')
    ax3.set_ylabel('Transmission (%)', color='blue')
    ax3_twin.set_ylabel('QBER (%)', color='red')
    ax3.set_title('Fiber Channel: Distance Effects')
    ax3.legend(handles=[line1, line2], loc='center right')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Fiber - Key rate vs distance
    ax4 = axes[1, 1]
    key_rates = [r['key_rate'] for r in fiber_results]
    ax4.semilogy(distances, key_rates, 'g-', linewidth=2)
    ax4.set_xlabel('Distance (km)')
    ax4.set_ylabel('Key Rate (bps)')
    ax4.set_title('Secure Key Rate vs Distance')
    ax4.grid(True, alpha=0.3)
    
    # Find maximum distance
    max_dist_idx = next((i for i, r in enumerate(fiber_results) 
                         if r['key_rate'] <= 1), len(fiber_results)-1)
    if max_dist_idx > 0:
        ax4.axvline(x=fiber_results[max_dist_idx-1]['distance'], 
                   color='red', linestyle='--', alpha=0.7,
                   label=f"Max ~{fiber_results[max_dist_idx-1]['distance']:.0f} km")
        ax4.legend()
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('results/figures', exist_ok=True)
    fig.savefig('results/figures/exp04_noise_resilience.png', dpi=150, bbox_inches='tight')
    print(f"Saved figure to results/figures/exp04_noise_resilience.png")
    
    plt.show()


def main():
    """Main experiment runner."""
    # Depolarizing noise analysis
    depol_results = analyze_depolarizing_noise()
    
    # Amplitude damping analysis
    amp_results = analyze_amplitude_damping()
    
    # Phase damping analysis
    phase_results = analyze_phase_damping()
    
    # Fiber channel analysis
    fiber_results = analyze_fiber_distance()
    
    # Compare noise types
    compare_noise_types()
    
    # Create visualizations
    create_noise_visualizations(depol_results, amp_results, phase_results, fiber_results)
    
    print("\n" + "=" * 70)
    print("Experiment Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
