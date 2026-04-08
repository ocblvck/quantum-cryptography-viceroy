# Experiment Log

This document tracks all experiments conducted during the project.
Update this log after each significant experiment or finding.

---

## Log Format

```
## [Date] Experiment Title

### Objective
What we aimed to learn/test

### Method
- Protocol used
- Parameters
- Number of trials

### Results
Key findings and data

### Conclusions
What we learned

### Next Steps
Follow-up experiments
```

---
    ## [2025-XX-XX] Project Setup and Baseline

    ### Objective
    Establish baseline performance for all implemented protocols.

    ### Method
    - Protocols: BB84, B92, E91, SARG04
    - Key length: 256 bits
    - Trials: 10 per protocol
    - Noise: None

    ### Results
    *(To be filled after running experiments)*

    | Protocol | Sifting Eff. | Mean QBER | Std QBER | Time (s) |
    |----------|--------------|-----------|----------|----------|
    | BB84     |              |           |          |          |
    | B92      |              |           |          |          |
    | E91      |              |           |          |          |
    | SARG04   |              |           |          |          |

    ### Conclusions
    *(To be filled)*

    ### Next Steps
    *(To be filled)*

    ---

    ## [YYYY-MM-DD] Template for Future Experiments

    ### Objective


    ### Method


    ### Results


    ### Conclusions


    ### Next Steps


    ---

    ## Notes and Observations

    ### Week 1
    - 

    ### Week 2
    - 

    ### Week 3
    - 

    ### Week 4
    - 

    ---

    ## Key Findings Summary

    *(Update as project progresses)*

    1. 

    2. 

    3. 

    ---

    ## Questions for Discussion

    1. 

    2. 

    3. 

    ---

    *Experiment Log - Quantum Cryptography Project*
    *Started: [DATE]*
    *Last Updated: [DATE]*


[2026-02-26] BB84 Statistical and Security Analysis   - Jerald D. Fisher

Objective
    To analyze the relationship between key length and statistical variance, and to verify theoretical sifting efficiency and noise thresholds.

Task 1: 5 trials each for key lengths 50, 100, 256, 512, 1024.

Task 2: 20 trials with key_length=256 to calculate actual sifting efficiency.

Task 3: Noise testing from 1% to 12%.

Results

    Task 1 (Variance): Mean QBER remained 0.0000 across all lengths in ideal conditions. In noise tests, larger key lengths showed lower standard deviation.

    Task 2 (Sifting): Average sifting efficiency was 48.28%.

    Task 3 (Noise): - 10% Noise: QBER 0.1000 (Secure)

Conclusions:

    Statistical Variance: Larger key lengths provide more stable results.

    Efficiency: Experimental data confirms the theoretical 50% sifting rate.

    Security: The protocol successfully identifies an insecure channel once the QBER exceeds the 11% threshold.

Image:
results\figures\exp01_bb84_basic.png


[2026-03-15] Experiment 02: Protocol Comparison   - Jerald D. Fisher

Objective: 
    To compare the sifting efficiency, execution time, and noise resilience of BB84, B92, E91, and SARG04 protocols.

MethodProtocols: 
    BB84, B92, E91, SARG04

Results:

    | Protocol | Sifting Eff. | Mean QBER | Std QBER | Time (s) |
    |----------|--------------|-----------|----------|----------|
    | BB84     |   ~48-50%    |  0.0000   |  0.0000  |    ~0.25s|
    | B92      |     ~25%     |  0.0000   |  0.0000  |    ~0.45s|
    | E91      |     ~25%     |  0.0000   |  0.0000  |    ~0.75s|
    | SARG04   |     ~22%     |  0.0000   |  0.0000  |    ~0.42s|

Conclusions:
 Efficiency Trade-off: BB84 remains the gold standard for speed and efficiency, matching bases twice as often as B92 or SARG04.
 Computational Cost: E91 is significantly slower due to the complexity of simulating entangled states.
 Noise Resilience: B92 is the most "fragile" under noise, hitting the 11% QBER threshold much sooner than BB84 or SARG04.
 
 Next Steps:

    Investigate the Intercept-Resend Attack on these protocols to see which one detects eavesdropping the fastest.

    Notes and Observations Week 3

    Confirmed that SARG04 and B92 have similar sifting efficiencies (~25%) but serve different security purposes (SARG04 is specifically for PNS resistance). Noticed that E91 execution time scales more aggressively with key length than the other protocols.

Image:
results\figures\exp02_protocol_comparison.png


[2026-03-15] Experiment 03: Attack Analysis   - Jerald D. Fisher
Objective
Simulate eavesdropping (Eve) to determine detection probabilities and induced error rates.

Method
Attacks: Intercept-Resend (IR), Photon Number Splitting (PNS).

Metric: Induced QBER and Detection Probability.

Results:

    Intercept-Resend: Induced a ~25% QBER when 100% of bits were attacked. This is because Eve chooses the wrong basis 50% of the time, causing Bob to measure a random bit.

    PNS Attack: Produced 0% QBER, making it "invisible" to standard error checking.

    Detection: A sample size of just 50 bits provided a >99.9% probability of detecting an IR attack.

Conclusions:

    The "Magic 25%" QBER is the hallmark of an active eavesdropper. While IR attacks are easy to catch, the PNS attack proves that simply monitoring QBER is not enough for total security; researchers must implement Decoy States to detect Eve when she steals photons without disturbing the state.

Notes and Observations:
    Week 3: Noticed that B92 is much more sensitive to channel noise, reaching the 11% cutoff faster than BB84.

Discussion Point: 
    If the PNS attack creates 0% error, the next phase of research should focus on Decoy State implementation to protect multi-photon sources.

Image:
results\figures\exp03_attack_analysis.png
