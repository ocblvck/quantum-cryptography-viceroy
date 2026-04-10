import random
import numpy as np

def simulate_decoy_state_protocol(trials=1000, attack_prob=0.5):
    """
    Simulates BB84 with Decoy States to detect a PNS attack.
    Alice sends Signal pulses (high intensity) and Decoy pulses (low intensity).
    """
    signal_intensity = 0.5  # Mean photon number for Signal
    decoy_intensity = 0.1   # Mean photon number for Decoy
    
    # Track statistics
    counts = {"signal": {"total": 0, "detected": 0}, "decoy": {"total": 0, "detected": 0}}
    
    for _ in range(trials):
        # Alice chooses to send either a Signal or a Decoy pulse
        pulse_type = random.choice(["signal", "decoy"])
        intensity = signal_intensity if pulse_type == "signal" else decoy_intensity
        
        counts[pulse_type]["total"] += 1
        
        # Simulate PNS Attack: Eve steals a photon but lets one pass
        # In a real PNS attack, Eve's presence changes the detection rate 
        # of different intensities differently.
        is_detected = True
        if random.random() < attack_prob:
            # Eve "clips" the intensity of the pulses
            # This disproportionately affects the lower intensity Decoy pulses
            if pulse_type == "decoy" and random.random() < 0.2: 
                is_detected = False # Eve accidentally blocks a weak decoy pulse
        
        if is_detected:
            counts[pulse_type]["detected"] += 1

    # Calculate Yield (Probability of detection)
    y_signal = counts["signal"]["detected"] / counts["signal"]["total"]
    y_decoy = counts["decoy"]["detected"] / counts["decoy"]["total"]
    
    return y_signal, y_decoy

# Run the test
attack_probs = [0.0, 0.2, 0.5, 0.8, 1.0]
print(f"{'Attack %':<10} | {'Signal Yield':<15} | {'Decoy Yield':<15} | {'Status'}")
print("-" * 60)

for p in attack_probs:
    s_yield, d_yield = simulate_decoy_state_protocol(attack_prob=p)
    # If the ratio between signal and decoy yield changes, an attack is detected
    status = "UNDER ATTACK" if (s_yield / d_yield) > 1.1 else "SECURE"
    print(f"{p*100:>8.0f}% | {s_yield:>14.4f} | {d_yield:>14.4f} | {status}")