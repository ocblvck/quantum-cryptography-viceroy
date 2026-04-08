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


    ---

    ## Key Findings Summary

    ---

    ## Questions for Discussion

    1. 

    2. 

    3. 

    ---

    *Experiment Log - Quantum Cryptography Project*
    *Started: [DATE]*
    *Last Updated: [DATE]*

```
Malcolm Wyatt
## 2/25/2026 BB84 Protocol Analysis

### Objective
Evaluate the performance of the BB84 quantum key distribution protocol by analyzing:
- Key length vs QBER statistical variance
- Sifting efficiency relative to theoretical expectation (~50%)
- QBER and security behavior under channel noise

### Method
- Protocol used: BB84 Quantum Key Distribution
- Key length settings: 50, 100, 256, 512, 1024 bits
- Trials per key length: 10
- Noise levels tested: 0% to 20% (11 levels total)
- Sifting efficiency trials: 20 runs at key_length = 256

### Results

| Protocol | Sifting Eff. | Mean QBER NN| Mean QBER N|Std QBER NN|Std QBER N| Time (s) |
|----------|--------------|-------------|------------|-----------|----------|----------|
| BB84     | 0.4991       |     0       |  ~0.0576   |    0      | ~0.044   |   0.08   |
| B92      |              |             |            |           |          |          |
| E91      |              |             |            |           |          |          |
| SARG04   |              |             |            |           |          |          |

1. BB84 Protocol - No Noise
----------------------------------------

BB84 Protocol Results:
  Raw bits transmitted: 640
  Sifted key length: 309
  Final key length: 256
  QBER: 0.0000
  Execution time: 0.08s

Security Analysis:
  QBER: 0.0000
  Secret Key Rate: 0.4000
  Mutual Info (A:B): 1.0000
  Is Secure: True


2. BB84 Protocol with Noise
----------------------------------------

Results:
   Noise     QBER   Key Rate   Secure
----------------------------------------
   0.00%   0.0000     1.0000        1
   2.00%   0.0333     0.8576        1
   4.00%   0.0333     0.8013        1
   6.00%   0.0000     0.5256        1
   8.00%   0.0000     0.4476        1
  10.00%   0.0667     0.3391        1
  12.00%   0.1000     0.0000        1
  14.00%   0.0667     0.0305        1
  16.00%   0.1000     0.0000        0
  18.00%   0.1333     0.0000        1
  20.00%   0.1000     0.0000        1
Average Secret Key Rate: 0.3638

3. Key Length Analysis
----------------------------------------

Results:
  Key Length    Mean QBER     Std QBER
----------------------------------------
          50       0.0000       0.0000
         100       0.0000       0.0000
         256       0.0000       0.0000
         512       0.0000       0.0000
        1024       0.0000       0.0000

Sifting Efficiency Analysis
----------------------------------------
Mean sifting efficiency: 0.4991
Std deviation: 0.0210

---



### Conclusions
1. The BB84 protocol implementation demonstrates stable performance under low noise conditions.

2. Statistical variance in QBER is negligible without channel noise, indicating deterministic state preparation and measurement in the simulation.
   In a noiseless simulation, QBER remains identically zero regardless of key length.

3. Experimental sifting efficiency closely matches theoretical expectations.

4. Protocol security degrades as channel noise increases, and insecurity emerges near high noise regimes.

5. Overall results validate expected behavior of quantum key distribution under simulated depolarizing noise.

---

### Next Steps

- Extend experiments to compare BB84 performance with other QKD protocols.
- Increase trial counts to improve statistical confidence.
- Analyze mutual information between communicating parties under varying noise levels.
- Explore adaptive error correction integration.

---

## Notes and Observations

- Baseline BB84 protocol behavior verified under noiseless simulation.

- Channel noise experiments show expected degradation in security metrics.

- Sifting efficiency converges near theoretical 50% expectation.

- Pending future multi-protocol comparison experiments.

---

## Key Findings Summary


1. BB84 sifting efficiency experimentally approaches theoretical 50% efficiency.

2. 

3. 

---

## Questions for Discussion

1. Why did I receive 0 for QBER and mean and STD for each key length?

2. 

3. 

---

*Experiment Log - Quantum Cryptography Project*
*Started: 2/25/2026*
*Last Updated: 2/25/2026*
```
```
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
```

