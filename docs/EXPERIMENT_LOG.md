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