#!/usr/bin/env python3
"""
Experiment 01: Basic BB84 Protocol Demonstration

This experiment demonstrates the fundamental BB84 QKD protocol
with various key lengths and noise levels.

Learning Objectives:
1. Understand the BB84 protocol steps
2. Observe the relationship between QBER and security
3. Analyze sifting efficiency

Run: python experiments/exp01_bb84_basic.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from src.protocols import BB84Protocol
from src.analysis import SecurityMetrics
from src.noise_models import DepolarizingChannel


def run_basic_bb84():
    """Run basic BB84 demonstration."""
    print("=" * 60)
    print("Experiment 01: Basic BB84 Protocol Demonstration")
    print("=" * 60)
    
    # Initialize protocol
    bb84 = BB84Protocol(key_length=256, verbose=True, seed=42)
    
    # Run without noise
    print("\n1. BB84 Protocol - No Noise")
    print("-" * 40)
    result = bb84.run()
    
    # Analyze security
    metrics = SecurityMetrics(
        result.alice_key, 
        result.bob_key,
        raw_length=result.raw_key_length
    )
    
    print(f"\nSecurity Analysis:")
    print(f"  QBER: {metrics.qber:.4f}")
    print(f"  Secret Key Rate: {metrics.secret_key_rate():.4f}")
    print(f"  Mutual Info (A:B): {metrics.mutual_information_ab():.4f}")
    print(f"  Is Secure: {metrics.is_secure()}")
    
    return result, metrics


def run_with_noise():
    """Run BB84 with various noise levels."""
    print("\n\n2. BB84 Protocol with Noise")
    print("-" * 40)
    
    noise_levels = [0.01, 0.03, 0.05, 0.08, 0.10, 0.12]
    results = []
    
    for noise in tqdm(noise_levels, desc="Testing noise levels"):
        bb84 = BB84Protocol(key_length=256, seed=42)
        noise_model = DepolarizingChannel(error_probability=noise).get_noise_model()
        
        result = bb84.run(noise_model=noise_model)
        metrics = SecurityMetrics(result.alice_key, result.bob_key)
        
        results.append({
            'noise': noise,
            'qber': result.qber,
            'key_rate': metrics.secret_key_rate(),
            'secure': metrics.is_secure()
        })
    
    print("\nResults:")
    print(f"{'Noise':>8} {'QBER':>8} {'Key Rate':>10} {'Secure':>8}")
    print("-" * 40)
    for r in results:
        print(f"{r['noise']:>8.2%} {r['qber']:>8.4f} {r['key_rate']:>10.4f} {r['secure']:>8}")
    
    return results


def run_key_length_analysis():
    """Analyze effect of key length on statistics."""
    print("\n\n3. Key Length Analysis")
    print("-" * 40)
    
    key_lengths = [50, 100, 256, 512, 1024]
    num_trials = 10
    
    results = []
    for length in tqdm(key_lengths, desc="Testing key lengths"):
        qbers = []
        for trial in range(num_trials):
            bb84 = BB84Protocol(key_length=length, seed=42 + trial)
            result = bb84.run()
            qbers.append(result.qber)
        
        results.append({
            'length': length,
            'mean_qber': np.mean(qbers),
            'std_qber': np.std(qbers)
        })
    
    print("\nResults:")
    print(f"{'Key Length':>12} {'Mean QBER':>12} {'Std QBER':>12}")
    print("-" * 40)
    for r in results:
        print(f"{r['length']:>12} {r['mean_qber']:>12.4f} {r['std_qber']:>12.4f}")
    
    return results


def create_visualizations(noise_results, length_results):
    """Create summary visualizations."""
    print("\n\n4. Creating Visualizations")
    print("-" * 40)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: QBER vs Key Rate
    noise_vals = [r['noise'] * 100 for r in noise_results]
    qber_vals = [r['qber'] * 100 for r in noise_results]
    rate_vals = [r['key_rate'] for r in noise_results]
    secure = [r['secure'] for r in noise_results]
    
    colors = ['green' if s else 'red' for s in secure]
    axes[0].scatter(qber_vals, rate_vals, c=colors, s=100, edgecolors='black')
    axes[0].set_xlabel('QBER (%)')
    axes[0].set_ylabel('Secret Key Rate')
    axes[0].set_title('BB84: QBER vs Secret Key Rate')
    axes[0].axvline(x=11, color='red', linestyle='--', alpha=0.7, label='Security threshold')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Key Length vs QBER variance
    lengths = [r['length'] for r in length_results]
    stds = [r['std_qber'] for r in length_results]
    
    axes[1].bar(range(len(lengths)), stds, color='steelblue', edgecolor='black')
    axes[1].set_xticks(range(len(lengths)))
    axes[1].set_xticklabels(lengths)
    axes[1].set_xlabel('Key Length')
    axes[1].set_ylabel('QBER Standard Deviation')
    axes[1].set_title('Statistical Variance vs Key Length')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('results/figures', exist_ok=True)
    fig.savefig('results/figures/exp01_bb84_basic.png', dpi=150, bbox_inches='tight')
    print(f"Saved figure to results/figures/exp01_bb84_basic.png")
    
    plt.show()


def main():
    """Main experiment runner."""
    # Basic demonstration
    result, metrics = run_basic_bb84()
    
    # Noise analysis
    noise_results = run_with_noise()
    
    # Key length analysis
    length_results = run_key_length_analysis()
    
    # Visualizations
    create_visualizations(noise_results, length_results)
    
    print("\n" + "=" * 60)
    print("Experiment Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
