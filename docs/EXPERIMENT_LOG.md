# Experiment Log

This document tracks all experiments conducted during the project.
Update this log after each significant experiment or finding.

---

## Log Format

```
## [Date] [Name] Experiment Title

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
Example, I think
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


[2026-02-26] BB84 Statistical and Security Analysis
Objective
To analyze the relationship between key length and statistical variance, and to verify theoretical sifting efficiency and noise thresholds.

Method
Protocol: BB84

Task 1: 5 trials each for key lengths 50, 100, 256, 512, 1024.

Task 2: 20 trials with key_length=256 to calculate actual sifting efficiency.

Task 3: Noise testing from 1% to 12%.

Results
Task 1 (Variance): Mean QBER remained 0.0000 across all lengths in ideal conditions. In noise tests, larger key lengths showed lower standard deviation.

Task 2 (Sifting): Average sifting efficiency was 48.28%.

Task 3 (Noise):

10% Noise: QBER 0.1000 (Secure)

12% Noise: QBER 0.1333 (Insecure)

Conclusions
Statistical Variance: Larger key lengths provide more stable results.

Efficiency: Experimental data confirms the theoretical 50% sifting rate.

Security: The protocol successfully identifies an insecure channel once the QBER exceeds the 11% threshold.

Next Steps
Test advanced attacks (Intercept-Resend) to observe how QBER reacts to active eavesdropping.

Notes and Observations
Week 1
Successfully activated virtual environment and ran initial baseline.

Confirmed that the results/ folder properly stores visual data.

Key Findings Summary
BB84 sifting efficiency consistently hovers around 48-50%.

The security threshold for BB84 is strictly capped at 11% QBER.

Standard deviation in results decreases as the key length increases.

Questions for Discussion
Why does the sifting efficiency rarely hit exactly 50% in small samples?

How do different noise models (like Depolarizing vs. Phase Flip) affect the QBER?

Experiment Log - Quantum Cryptography Project Started: 2026-02-26 Last Updated: 2026-02-26


[2026-03-15] Experiment 02: Protocol Comparison
Objective: To compare the sifting efficiency, execution time, and noise resilience of BB84, B92, E91, and SARG04 protocols.
MethodProtocols: BB84, B92, E91, SARG04
Parameters: key_length=256, 0% to 10% noise sweep.
Metric: Sifting Efficiency (%) and Execution Time (s).

Results:

Protocol,Sifting Eff. (%),Execution Time (s),Efficiency Rank
BB84,~48-50%,~0.25s,1st (Highest)
B92,~25%,~0.45s,2nd
SARG04,~25%,~0.42s,3rd
E91,~22%,~0.75s,4th (Lowest)

Conclusions:
 Efficiency Trade-off: BB84 remains the gold standard for speed and efficiency, matching bases twice as often as B92 or SARG04.
 Computational Cost: E91 is significantly slower due to the complexity of simulating entangled states.
 Noise Resilience: B92 is the most "fragile" under noise, hitting the 11% QBER threshold much sooner than BB84 or SARG04.
 
 Next Steps

 Investigate the Intercept-Resend Attack on these protocols to see which one detects eavesdropping the fastest.

 Notes and Observations Week 3

 Confirmed that SARG04 and B92 have similar sifting efficiencies (~25%) but serve different security purposes (SARG04 is specifically for PNS resistance). Noticed that E91 execution time scales more aggressively with key length than the other protocols.



[2026-03-15] Experiment 03: Attack Analysis
Objective
Simulate eavesdropping (Eve) to determine detection probabilities and induced error rates.

Method
Attacks: Intercept-Resend (IR), Photon Number Splitting (PNS).

Metric: Induced QBER and Detection Probability.

Results:

Intercept-Resend: Induced a ~25% QBER when 100% of bits were attacked. This is because Eve chooses the wrong basis 50% of the time, causing Bob to measure a random bit.

PNS Attack: Produced 0% QBER, making it "invisible" to standard error checking.

Detection: A sample size of just 50 bits provided a >99.9% probability of detecting an IR attack.

Conclusions
The "Magic 25%" QBER is the hallmark of an active eavesdropper. While IR attacks are easy to catch, the PNS attack proves that simply monitoring QBER is not enough for total security; researchers must implement Decoy States to detect Eve when she steals photons without disturbing the state.

Notes and Observations
Week 3: Noticed that B92 is much more sensitive to channel noise, reaching the 11% cutoff faster than BB84.

Discussion Point: If the PNS attack creates 0% error, the next phase of research should focus on Decoy State implementation to protect multi-photon sources.


