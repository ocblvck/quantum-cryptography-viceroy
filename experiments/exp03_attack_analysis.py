#!/usr/bin/env python3
"""
Experiment 03: Attack Analysis

This experiment simulates and analyzes various attacks on QKD protocols,
including intercept-resend, PNS, and Trojan horse attacks.

Learning Objectives:
1. Understand how attacks affect QBER
2. Learn detection mechanisms
3. Compare attack effectiveness

Run: python experiments/exp03_attack_analysis.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from src.protocols import BB84Protocol, SARG04Protocol
from src.attacks import InterceptResendAttack, PNSAttack, TrojanHorseAttack
from src.analysis import SecurityMetrics


def analyze_intercept_resend():
    """Analyze intercept-resend attack on BB84."""
    print("=" * 70)
    print("Experiment 03: Attack Analysis")
    print("=" * 70)
    
    print("\n1. Intercept-Resend Attack Analysis")
    print("-" * 50)
    
    attack_probabilities = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    results = []
    
    for prob in tqdm(attack_probabilities, desc="Testing attack probabilities"):
        bb84 = BB84Protocol(key_length=256, seed=42)
        
        if prob > 0:
            eve = InterceptResendAttack(attack_probability=prob, seed=42)
            result = bb84.run(eavesdropper=eve)
            attack_result = eve.get_results()
        else:
            result = bb84.run()
            attack_result = None
        
        metrics = SecurityMetrics(result.alice_key, result.bob_key)
        
        results.append({
            'attack_prob': prob,
            'qber': result.qber,
            'key_rate': metrics.secret_key_rate(),
            'is_secure': metrics.is_secure(),
            'eve_info': attack_result.eve_information if attack_result else 0,
            'detection_prob': attack_result.detection_probability if attack_result else 0
        })
    
    print("\nIntercept-Resend Attack Results:")
    print(f"{'Attack %':>10} {'QBER':>8} {'Key Rate':>10} {'Eve Info':>10} {'Secure':>8}")
    print("-" * 50)
    for r in results:
        print(f"{r['attack_prob']*100:>9.0f}% {r['qber']:>8.4f} "
              f"{r['key_rate']:>10.4f} {r['eve_info']:>10.1f} {r['is_secure']:>8}")
    
    return results


def analyze_pns_attack():
    """Analyze PNS attack vulnerability."""
    print("\n\n2. Photon Number Splitting Attack Analysis")
    print("-" * 50)
    
    # Compare BB84 and SARG04 under PNS
    mean_photon_numbers = [0.05, 0.1, 0.2, 0.3, 0.5]
    
    results = []
    for mu in tqdm(mean_photon_numbers, desc="Testing photon numbers"):
        # Calculate vulnerable fraction
        pns = PNSAttack(mean_photon_number=mu)
        vulnerable_fraction = PNSAttack.vulnerable_key_fraction(mu)
        safe_distance = PNSAttack.safe_distance_km(mu)
        
        results.append({
            'mean_photon': mu,
            'vulnerable_fraction': vulnerable_fraction,
            'safe_distance_km': safe_distance
        })
    
    print("\nPNS Attack Vulnerability Analysis:")
    print(f"{'μ (mean)':>10} {'Vulnerable %':>14} {'Safe Distance':>15}")
    print("-" * 45)
    for r in results:
        print(f"{r['mean_photon']:>10.2f} "
              f"{r['vulnerable_fraction']*100:>13.1f}% "
              f"{r['safe_distance_km']:>14.1f} km")
    
    return results


def analyze_detection_probability():
    """Analyze detection probability vs sample size."""
    print("\n\n3. Attack Detection Probability")
    print("-" * 50)
    
    sample_sizes = [10, 20, 50, 100, 200, 500, 1000]
    
    # Theoretical detection probabilities
    qber_25 = 0.25  # Intercept-resend induced QBER
    
    detection_probs = []
    for n in sample_sizes:
        # Probability of detecting at least one error
        p_detect = 1 - (1 - qber_25) ** n
        detection_probs.append(p_detect)
    
    print("\nDetection Probability (Intercept-Resend, 100% attack):")
    print(f"{'Sample Size':>12} {'Detection Prob':>15}")
    print("-" * 30)
    for n, p in zip(sample_sizes, detection_probs):
        print(f"{n:>12} {p*100:>14.2f}%")
    
    return sample_sizes, detection_probs


def compare_attack_effectiveness():
    """Compare different attacks."""
    print("\n\n4. Attack Effectiveness Comparison")
    print("-" * 50)
    
    attacks = {
        'Intercept-Resend': {
            'induced_qber': 0.25,
            'eve_information': 0.5,  # bits per intercepted qubit
            'detection_method': 'QBER estimation',
            'detectable': True
        },
        'PNS': {
            'induced_qber': 0.0,
            'eve_information': 1.0,  # complete info on multi-photon
            'detection_method': 'Decoy states',
            'detectable': True  # With countermeasures
        },
        'Trojan Horse': {
            'induced_qber': 0.0,
            'eve_information': 0.5,  # depends on probe strength
            'detection_method': 'Watchdog detectors',
            'detectable': True
        }
    }
    
    print("\nAttack Comparison Summary:")
    print(f"{'Attack':>18} {'QBER':>8} {'Info Gain':>12} {'Detection':>20}")
    print("-" * 65)
    for name, props in attacks.items():
        print(f"{name:>18} {props['induced_qber']*100:>7.0f}% "
              f"{props['eve_information']:>11.1f}b "
              f"{props['detection_method']:>20}")
    
    return attacks


def create_attack_visualizations(ir_results, pns_results, detection_data):
    """Create attack analysis visualizations."""
    print("\n\n5. Creating Visualizations")
    print("-" * 50)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Intercept-Resend - Attack probability vs QBER
    ax1 = axes[0, 0]
    attack_probs = [r['attack_prob'] * 100 for r in ir_results]
    qbers = [r['qber'] * 100 for r in ir_results]
    ax1.plot(attack_probs, qbers, 'bo-', linewidth=2, markersize=8)
    ax1.axhline(y=11, color='red', linestyle='--', label='Security threshold')
    ax1.axhline(y=25, color='orange', linestyle=':', label='Max theoretical QBER')
    ax1.set_xlabel('Attack Probability (%)')
    ax1.set_ylabel('Observed QBER (%)')
    ax1.set_title('Intercept-Resend: Attack Probability vs QBER')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Intercept-Resend - Key rate degradation
    ax2 = axes[0, 1]
    key_rates = [r['key_rate'] for r in ir_results]
    colors = ['green' if r['is_secure'] else 'red' for r in ir_results]
    ax2.bar(range(len(attack_probs)), key_rates, color=colors, edgecolor='black')
    ax2.set_xticks(range(len(attack_probs)))
    ax2.set_xticklabels([f'{p:.0f}%' for p in attack_probs])
    ax2.set_xlabel('Attack Probability')
    ax2.set_ylabel('Secret Key Rate')
    ax2.set_title('Intercept-Resend: Key Rate Degradation')
    
    # Plot 3: PNS - Vulnerable fraction vs mean photon number
    ax3 = axes[1, 0]
    mus = [r['mean_photon'] for r in pns_results]
    vuln = [r['vulnerable_fraction'] * 100 for r in pns_results]
    ax3.plot(mus, vuln, 'rs-', linewidth=2, markersize=8)
    ax3.set_xlabel('Mean Photon Number (μ)')
    ax3.set_ylabel('Vulnerable Key Fraction (%)')
    ax3.set_title('PNS Attack: Vulnerability vs Source Intensity')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Detection probability vs sample size
    ax4 = axes[1, 1]
    sample_sizes, detection_probs = detection_data
    ax4.semilogx(sample_sizes, [p * 100 for p in detection_probs], 'go-', 
                  linewidth=2, markersize=8)
    ax4.axhline(y=99.9, color='green', linestyle='--', alpha=0.7, 
                label='99.9% detection')
    ax4.set_xlabel('Sample Size (test bits)')
    ax4.set_ylabel('Detection Probability (%)')
    ax4.set_title('Attack Detection vs Sample Size')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 105)
    
    plt.tight_layout()
    
    # Save figure
    os.makedirs('results/figures', exist_ok=True)
    fig.savefig('results/figures/exp03_attack_analysis.png', dpi=150, bbox_inches='tight')
    print(f"Saved figure to results/figures/exp03_attack_analysis.png")
    
    plt.show()


def main():
    """Main experiment runner."""
    # Intercept-Resend analysis
    ir_results = analyze_intercept_resend()
    
    # PNS attack analysis
    pns_results = analyze_pns_attack()
    
    # Detection probability
    detection_data = analyze_detection_probability()
    
    # Attack comparison
    compare_attack_effectiveness()
    
    # Create visualizations
    create_attack_visualizations(ir_results, pns_results, detection_data)
    
    print("\n" + "=" * 70)
    print("Experiment Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
