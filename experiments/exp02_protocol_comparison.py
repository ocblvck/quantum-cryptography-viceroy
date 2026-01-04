#!/usr/bin/env python3
"""
Experiment 02: Protocol Comparison

This experiment provides a comprehensive comparison of all
implemented QKD protocols: BB84, B92, E91, and SARG04.

Learning Objectives:
1. Compare sifting efficiency across protocols
2. Understand trade-offs between protocols
3. Analyze security properties

Run: python experiments/exp02_protocol_comparison.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd

from src.protocols import BB84Protocol, B92Protocol, E91Protocol, SARG04Protocol
from src.analysis import SecurityMetrics
from src.noise_models import DepolarizingChannel


def run_single_protocol(protocol_class, name, key_length=256, noise=0.0, seed=42):
    """Run a single protocol and return metrics."""
    protocol = protocol_class(key_length=key_length, seed=seed)
    
    if noise > 0:
        noise_model = DepolarizingChannel(error_probability=noise).get_noise_model()
        result = protocol.run(noise_model=noise_model)
    else:
        result = protocol.run()
    
    metrics = SecurityMetrics(
        result.alice_key,
        result.bob_key,
        raw_length=result.raw_key_length
    )
    
    return {
        'protocol': name,
        'raw_length': result.raw_key_length,
        'sifted_length': result.sifted_key_length,
        'final_length': result.final_key_length,
        'sifting_efficiency': result.sifted_key_length / result.raw_key_length,
        'qber': result.qber,
        'key_rate': metrics.secret_key_rate(),
        'execution_time': result.execution_time,
        'is_secure': metrics.is_secure()
    }


def compare_protocols():
    """Compare all protocols under identical conditions."""
    print("=" * 70)
    print("Experiment 02: QKD Protocol Comparison")
    print("=" * 70)
    
    protocols = [
        (BB84Protocol, 'BB84'),
        (B92Protocol, 'B92'),
        (E91Protocol, 'E91'),
        (SARG04Protocol, 'SARG04')
    ]
    
    print("\n1. Protocol Comparison - No Noise")
    print("-" * 50)
    
    results = []
    for protocol_class, name in tqdm(protocols, desc="Running protocols"):
        result = run_single_protocol(protocol_class, name)
        results.append(result)
    
    # Display results
    df = pd.DataFrame(results)
    print("\nResults Summary:")
    print(df.to_string(index=False))
    
    return results


def compare_under_noise():
    """Compare protocols under various noise levels."""
    print("\n\n2. Protocol Comparison Under Noise")
    print("-" * 50)
    
    protocols = [
        (BB84Protocol, 'BB84'),
        (B92Protocol, 'B92'),
        (SARG04Protocol, 'SARG04')
    ]
    
    noise_levels = [0.0, 0.02, 0.05, 0.08, 0.10]
    
    all_results = []
    for noise in tqdm(noise_levels, desc="Testing noise levels"):
        for protocol_class, name in protocols:
            result = run_single_protocol(
                protocol_class, name, 
                noise=noise, seed=42
            )
            result['noise'] = noise
            all_results.append(result)
    
    return all_results


def theoretical_comparison():
    """Compare theoretical key rates."""
    print("\n\n3. Theoretical Key Rate Comparison")
    print("-" * 50)
    
    qber_range = np.linspace(0, 0.12, 50)
    
    bb84_rates = []
    b92_rates = []
    sarg04_rates = []
    
    for q in qber_range:
        bb84_rates.append(BB84Protocol.theoretical_key_rate(q))
        b92_rates.append(B92Protocol.theoretical_key_rate(q))
        sarg04_rates.append(SARG04Protocol.theoretical_key_rate(q))
    
    return qber_range, bb84_rates, b92_rates, sarg04_rates


def create_comparison_plots(basic_results, noise_results, theory_data):
    """Create comprehensive comparison plots."""
    print("\n\n4. Creating Comparison Visualizations")
    print("-" * 50)
    
    fig = plt.figure(figsize=(16, 12))
    
    # Plot 1: Sifting Efficiency Comparison
    ax1 = fig.add_subplot(2, 2, 1)
    protocols = [r['protocol'] for r in basic_results]
    sift_eff = [r['sifting_efficiency'] * 100 for r in basic_results]
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    ax1.bar(protocols, sift_eff, color=colors, edgecolor='black')
    ax1.set_ylabel('Sifting Efficiency (%)')
    ax1.set_title('Protocol Sifting Efficiency')
    ax1.set_ylim(0, 60)
    # Add theoretical values
    theoretical = [50, 25, 22, 25]  # Approximate
    for i, (p, t) in enumerate(zip(protocols, theoretical)):
        ax1.axhline(y=t, xmin=i/4, xmax=(i+1)/4, color='red', linestyle='--', alpha=0.7)
    
    # Plot 2: Execution Time
    ax2 = fig.add_subplot(2, 2, 2)
    times = [r['execution_time'] for r in basic_results]
    ax2.bar(protocols, times, color=colors, edgecolor='black')
    ax2.set_ylabel('Execution Time (s)')
    ax2.set_title('Protocol Execution Time')
    
    # Plot 3: Theoretical Key Rates
    ax3 = fig.add_subplot(2, 2, 3)
    qber_range, bb84_rates, b92_rates, sarg04_rates = theory_data
    ax3.plot(qber_range * 100, bb84_rates, label='BB84', color='#2E86AB', linewidth=2)
    ax3.plot(qber_range * 100, b92_rates, label='B92', color='#A23B72', linewidth=2)
    ax3.plot(qber_range * 100, sarg04_rates, label='SARG04', color='#C73E1D', linewidth=2)
    ax3.axvline(x=11, color='red', linestyle='--', alpha=0.7, label='Threshold')
    ax3.set_xlabel('QBER (%)')
    ax3.set_ylabel('Key Rate')
    ax3.set_title('Theoretical Key Rate vs QBER')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Performance Under Noise
    ax4 = fig.add_subplot(2, 2, 4)
    for protocol in ['BB84', 'B92', 'SARG04']:
        protocol_data = [r for r in noise_results if r['protocol'] == protocol]
        noise_vals = [r['noise'] * 100 for r in protocol_data]
        qber_vals = [r['qber'] * 100 for r in protocol_data]
        color = {'BB84': '#2E86AB', 'B92': '#A23B72', 'SARG04': '#C73E1D'}[protocol]
        ax4.plot(noise_vals, qber_vals, 'o-', label=protocol, color=color, linewidth=2)
    
    ax4.axhline(y=11, color='red', linestyle='--', alpha=0.7, label='Threshold')
    ax4.set_xlabel('Channel Noise (%)')
    ax4.set_ylabel('Observed QBER (%)')
    ax4.set_title('QBER vs Channel Noise')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('results/figures', exist_ok=True)
    fig.savefig('results/figures/exp02_protocol_comparison.png', dpi=150, bbox_inches='tight')
    print(f"Saved figure to results/figures/exp02_protocol_comparison.png")
    
    plt.show()


def print_protocol_summary():
    """Print theoretical summary of protocols."""
    print("\n\n5. Protocol Summary")
    print("-" * 70)
    
    summary = """
    | Protocol | Year | States | Sifting  | PNS-Resist | Complexity |
    |----------|------|--------|----------|------------|------------|
    | BB84     | 1984 | 4      | 50%      | No         | Low        |
    | B92      | 1992 | 2      | 25%      | No         | Very Low   |
    | E91      | 1991 | 2 (ent)| 22%      | Yes        | Medium     |
    | SARG04   | 2004 | 4      | 25%      | Yes        | Low        |
    
    Key Trade-offs:
    - BB84: Best sifting efficiency, widely implemented
    - B92: Simplest, but lowest efficiency
    - E91: Device-independent security via Bell test
    - SARG04: Same complexity as BB84, but PNS resistant
    """
    print(summary)


def main():
    """Main experiment runner."""
    # Basic comparison
    basic_results = compare_protocols()
    
    # Noise comparison
    noise_results = compare_under_noise()
    
    # Theoretical comparison
    theory_data = theoretical_comparison()
    
    # Create visualizations
    create_comparison_plots(basic_results, noise_results, theory_data)
    
    # Print summary
    print_protocol_summary()
    
    print("\n" + "=" * 70)
    print("Experiment Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
