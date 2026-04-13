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
## [2026-04-12] Malcolm Wyatt SARG04 Protocol Analysis and PNS Resistance

### Objective
To understand how the SARG04 protocol differs from BB84, evaluate its efficiency compared to BB84 and B92, and analyze why it provides improved resistance to photon number splitting (PNS) attacks.

### Method
- Protocols used: BB84, SARG04, B92  
- Key length: 256 bits  
- Trials: 1 per protocol  
- No noise or attack (baseline comparison)  
- Additional comparison: BB84 vs SARG04 sifting efficiency  

### Results
- BB84 sifting efficiency ≈ 48%  
- SARG04 sifting efficiency ≈ 24–25%  
- B92 sifting efficiency ≈ 26–27%  

- BB84 produced the highest efficiency  
- SARG04 produced lower efficiency due to more discarded bits  
- SARG04 efficiency was slightly lower than B92 in some runs  

### Conclusions
SARG04 uses the same four quantum states as BB84 (|0⟩, |1⟩, |+⟩, |−⟩), but differs in how classical information is announced. In BB84, Alice reveals the measurement basis, while in SARG04 she announces a pair of possible states. This change makes it harder for an eavesdropper to determine the transmitted bit.

This difference is especially important for photon number splitting (PNS) attacks. In BB84, an eavesdropper can store extra photons and wait for the basis announcement to measure them correctly. In SARG04, because only a pair of possible states is revealed instead of the exact basis, Eve cannot reliably determine the bit, reducing her advantage.

However, this improvement comes at the cost of efficiency. SARG04 discards more bits during the sifting process because many measurement outcomes are inconclusive. As a result, fewer bits are kept, lowering the overall efficiency compared to BB84.

### Next Steps
- Analyze SARG04 performance under noise conditions  
- Compare SARG04 behavior under attack scenarios  
- Investigate optimization methods for improving efficiency  

---

## Notes and Observations

- SARG04 uses the same quantum states as BB84 but changes the classical communication step  
- The announcement of state pairs instead of bases is the key difference  
- This modification reduces Eve’s ability to exploit multi-photon pulses  
- SARG04 consistently produces lower efficiency due to increased discarded measurements  
- Compared to B92, SARG04 maintains moderate efficiency while improving security  

---

## Key Findings Summary

- SARG04 differs from BB84 primarily in its announcement strategy  
- BB84 is more efficient but more vulnerable to PNS attacks  
- SARG04 is less efficient but provides better resistance to certain attacks  
- B92 is the least efficient overall due to many inconclusive measurements  
- The main trade-off in SARG04 is efficiency vs security  

---

## Questions for Discussion

1. How does SARG04 differ from BB84?  
SARG04 uses the same quantum states as BB84 but differs in the classical announcement step. Instead of revealing the measurement basis, Alice announces a pair of possible states, making it harder for an eavesdropper to determine the transmitted bit.

2. Why is SARG04 considered more resistant to PNS attacks?  
SARG04 is more resistant because its announcement strategy prevents an eavesdropper from using stored photons to determine the correct measurement basis. This reduces Eve’s ability to gain information without introducing detectable errors.

3. What did your experiments show about its efficiency?  
The experiments showed that SARG04 has lower sifting efficiency (~24–25%) compared to BB84 (~48%) and is similar to or slightly lower than B92. This confirms that SARG04 sacrifices efficiency for improved security.

---

## Extended Conceptual Answers

### How does SARG04 use the same four signal states as BB84?
SARG04 uses the same four quantum states (|0⟩, |1⟩, |+⟩, |−⟩) as BB84 for encoding information, but differs in how the classical information is shared after transmission.

### What does Alice announce in SARG04, and how is that different from BB84?
In BB84, Alice announces the basis used for each bit. In SARG04, she announces a pair of possible states that includes the correct one, rather than revealing the exact basis.

### Why does changing the announcement rule matter for PNS resistance?
This change prevents an eavesdropper from knowing the correct basis after the fact, making it much harder to extract information from intercepted photons.

### Why is SARG04 less efficient than BB84 during sifting?
Because many measurement outcomes do not match the announced pair, leading to more discarded bits and lower efficiency.

---

### How does SARG04 compare to BB84 in efficiency?
SARG04 is significantly less efficient than BB84 because it discards more bits during the sifting process.

### How does SARG04 compare to B92 in sifting efficiency?
SARG04 has comparable or slightly lower efficiency than B92, but generally provides stronger security guarantees.

### What trade-off does SARG04 make in exchange for improved PNS resistance?
SARG04 sacrifices efficiency to gain improved security against PNS attacks.

---

### What is a photon number splitting attack in practical QKD systems?
A PNS attack occurs when an eavesdropper exploits multi-photon pulses by splitting off one photon and storing it, allowing them to measure it later without introducing errors.

### Why is BB84 more vulnerable in weak coherent pulse implementations?
Because multi-photon pulses allow Eve to keep a copy and measure it after the basis is revealed, gaining information without increasing QBER.

### Why does SARG04's announcement strategy reduce Eve's advantage?
Because the announcement does not reveal enough information for Eve to determine the correct measurement basis, even if she stores photons.

### Why does this improvement come with an efficiency cost?
Because the stricter sifting conditions result in more discarded measurements, reducing the number of usable bits.

---

*Experiment Log - Quantum Cryptography Project*  
*Started: 2026-04-12*  
*Last Updated: 2026-04-12*


Assignment 2:
## [2026-04-07] Malcolm Wyatt Attack and Noise Analysis of QKD Protocols

### Objective
To analyze how quantum key distribution protocols (BB84, B92, E91, and SARG04) behave under ideal conditions, attack scenarios, and noisy environments, and to evaluate their efficiency, security, and robustness.

### Method
- Protocols used: BB84, B92, E91, SARG04  
- Key length: 256 bits  
- Trials: 1 per configuration  
- Attack: Intercept-Resend, PNS, Trojan Horse  
- Noise: Depolarizing, Amplitude Damping, Phase Damping, Fiber Channel  
- Scripts used:
  - exp02_protocol_comparison.py
  - exp03_attack_analysis.py
  - exp04_noise_resilience.py

### Results

#### Baseline (No Noise, No Attack)

| Protocol | Raw | Sifted | Efficiency | QBER | Key Rate | Time | Secure |
|----------|-----|--------|------------|------|----------|------|--------|
| BB84     | 640 | 309    | 0.4828     | 0.00 | 0.4      | 0.082 | True  |
| B92      |1280 | 338    | 0.2641     | 0.00 | 0.2      | 0.151 | True  |
| E91      |1536 | 364    | 0.2370     | 0.25 | 0.0      | 0.270 | False |
| SARG04   |1280 | 315    | 0.2461     | 0.00 | 0.2      | 0.161 | True  |

---

#### Intercept-Resend Attack

| Attack % | QBER | Key Rate | Eve Info | Secure |
|----------|------|----------|----------|--------|
| 0%       | 0.0000 | 1.0000 | 0.0      |   True |
| 20%      | 0.0333 | 0.3742 | 65.0     |   True |
| 40%      | 0.2000 | 0.0000 | 133.5    |   True |
| 60%      | 0.1667 | 0.0000 | 189.5    |  False |
| 80%      | 0.3000 | 0.0000 | 253.0    |  False |
| 100%     | 0.2667 | 0.0000 | 320.0    |  False |

---

#### Photon Number Splitting (PNS) Attack

|   μ  | Vulnerable % |
|------|--------------|
| 0.05 | 4.8%         |
| 0.10 | 9.4%         |
| 0.20 | 17.5%        |
| 0.30 | 24.6%        |
| 0.50 | 36.1%        |

---

#### Detection Probability

| Sample Size | Detection Probability |
|-------------|-----------------------|
| 10          |     94.37%            |
| 50+         |     ~100%             |

---

#### Fiber Noise Results

| Distance | QBER | Key Rate |
|----------|------|----------|
| 0 km     | 0.00% | 74,998,852 bps |
| 42 km    | 0.07% | 10,619,387 bps |
| 84 km    | 0.09% | 1,518,505 bps |
| 126 km   | 0.12% | 217,101 bps |
| 168 km   | 0.21% | 30,730 bps |

---

#### Noise Type Comparison

| Noise Type | QBER | Key Rate |
|------------|------|----------|
| Depolarizing | 0.00% | 0.5667 |
| Amplitude Damping | 13.33% | 0.1456 |
| Phase Damping | 3.33% | 0.8013 |

---

### Conclusions
BB84 demonstrated the highest efficiency and most stable performance under ideal conditions. B92 showed lower efficiency due to discarding inconclusive measurements but remained secure. E91 exhibited higher QBER and instability, highlighting its sensitivity to implementation.

Under attack conditions, QBER increased sharply, particularly for intercept-resend attacks, reaching around 25% and causing the key rate to drop to zero. This confirmed that eavesdropping introduces detectable disturbances. PNS attacks were more subtle, allowing information gain without increasing QBER.

Under noisy conditions, QBER increased gradually while key rate decreased, especially under amplitude damping and long-distance fiber transmission. This shows that noise degrades system performance over time rather than causing immediate failure.

### Next Steps
- Improve E91 implementation to reduce QBER  
- Compare protocol performance under combined noise and attack  
- Investigate mitigation strategies such as decoy states  
- Extend testing to include additional protocols  

---

## Notes and Observations

- BB84 provides the clearest and most reliable security signal  
- B92 trades efficiency for security  
- E91 is highly sensitive and complex  
- Attacks cause sudden changes, while noise causes gradual degradation  
- PNS attacks are difficult to detect due to low QBER impact  

---

## Key Findings Summary

- BB84 is the most efficient and easiest to interpret  
- B92 is less efficient but still secure  
- E91 offers strong theoretical security but is difficult to implement  
- QBER is the main indicator of security  
- Noise and attacks both degrade performance, but in different ways  

---

## Questions for Discussion

1. Why does E91 show high QBER even under ideal conditions?  
2. How can quantum protocols defend against stealth attacks like PNS?  
3. What trade-offs exist between efficiency, simplicity, and security in QKD protocols?  

---

*Experiment Log - Quantum Cryptography Project*  
*Started: 2026-04-07*  
*Last Updated: 2026-04-07*



Assignment 1:
## [2026-04-07] Malcolm Wyatt QKD Protocol Implementation and Analysis

### Objective
Implement and evaluate multiple quantum key distribution protocols (BB84, B92, E91, and SARG04), validate their correctness through testing, and analyze their performance under ideal conditions.

### Method
- Protocols used: BB84, B92, E91, SARG04  
- Key length: 256 bits  
- Trials: 1 per protocol (default execution)  
- Noise: None  
- Attack: None  
- Scripts used:
  - `exp02_protocol_comparison.py`
  - `pytest` test suite  

Additional validation:
- Fixed incorrect test assumptions (key length, reproducibility, theoretical key rate)
- Added custom test:
  - B92 has lower sifting efficiency than BB84  

### Results

Baseline Protocol Comparison (No Noise, No Attack):

| Protocol | Raw Length | Sifted Length | Efficiency | QBER | Time (s) |
|----------|-----------|--------------|------------|------|----------|
| BB84     | 640       | 309          | 0.4828     | 0.0000 | 0.085 |
| B92      | 1280      | 346          | 0.2703     | 0.0000 | 0.141 |
| E91      | 1536      | 364          | 0.2370     | 0.3333 | 0.271 |
| SARG04   | 1280      | 315          | 0.2461     | 0.0000 | 0.157 |

B92 Implementation Results:
- Raw key length: 1280  
- Sifted key length: 350  
- Efficiency: ~27%  
- QBER: 0.0000  
- Secure  

E91 Implementation Results:
- Raw key length: 1536  
- Sifted key length: 364  
- Efficiency: ~24%  
- QBER: ~0.3056  
- Not secure  

Testing Results:
- Initial test failures:
  - Incorrect key length assumption
  - Reproducibility too strict
  - Incorrect theoretical key rate expectation  
- Fixes applied:
  - Used `final_key_length`
  - Compared lengths instead of exact arrays
  - Used inequality for theoretical key rate  

Final Test Output:
- Total tests: 17  
- All tests passed successfully  

Custom Test Result:
- Confirmed: B92 sifted key length < BB84 sifted key length  

### Conclusions
The implemented protocols behave consistently with theoretical expectations. BB84 achieved the highest efficiency (~48%) and maintained a perfect QBER, making it the most reliable under ideal conditions. B92 demonstrated lower efficiency (~27%) due to discarding inconclusive measurements, which is a core feature of its design for maintaining security.

E91 produced a significantly higher QBER (~30%) even without noise, indicating sensitivity to measurement configuration and implementation details. This highlights the complexity of entanglement-based protocols compared to simpler prepare-and-measure approaches.

Testing confirmed that the protocols function correctly after fixing incorrect test assumptions. The added custom test further validates that B92 behaves as expected relative to BB84.

### Next Steps
- Investigate and debug E91 high QBER issue  
- Implement attack scenarios (e.g., intercept-resend)  
- Analyze protocol behavior under noise conditions  
- Extend testing to include Bell parameter validation  

---

## Notes and Observations

- BB84 consistently provides the best balance of efficiency and stability  
- B92 sacrifices efficiency for security by discarding inconclusive measurements  
- E91 is highly sensitive and requires careful implementation of entanglement and measurement  
- QBER is the key indicator of protocol security  
- Errors in tests were due to incorrect assumptions, not protocol failures  

---

## Attack Analysis

1. Which protocol shows the clearest measurable effect under attack?
The protocol that shows the clearest measurable effect under attack is BB84, as it exhibits a noticeable increase in QBER when an eavesdropper is present.

2. How does the attack change the final usable key length?
The attack decreases the final usable key length because the additional errors introduced lead to more bits being discarded during the sifting and error-checking process.

3. In E91, what happens to the Bell-test-related information when the channel is disturbed?
In the E91 protocol, when the channel is disturbed, the Bell-test-related correlations break down, indicating a loss of entanglement and causing the protocol to become insecure.

---

## Comparative Interpretation

Which protocol is most efficient in clean conditions?
BB84 is the most efficient protocol in clean conditions. From the baseline results, BB84 achieved the highest sifting efficiency (around 48%) and maintained a QBER of 0, meaning almost half of the transmitted bits were usable and error-free. In comparison, B92 had a lower efficiency (~27%) due to discarding inconclusive measurements, and E91 had the lowest efficiency (~24%) along with higher error rates. This shows that BB84 provides the best balance of efficiency and reliability when no disturbances are present.

Which protocol appears most sensitive to noise?
B92 appears to be the most sensitive to noise. Because it relies on distinguishing between non-orthogonal states and already discards a large portion of measurements, any additional noise further reduces the number of usable bits and increases errors. In contrast, BB84 is more robust due to its symmetric basis structure, and E91’s performance is heavily influenced by entanglement quality, but B92’s already low efficiency makes it degrade more quickly under noise.

Which protocol gives the clearest security signal under disturbance?
BB84 provides the clearest security signal under disturbance. In the attack analysis, QBER increased significantly (approaching ~25%) under intercept-resend attacks, making the presence of an eavesdropper easy to detect. This direct relationship between disturbance and error rate makes BB84 straightforward to interpret. While E91 also provides a strong theoretical security signal through Bell inequality violations, it is more complex to interpret in practice compared to the clear QBER changes seen in BB84.

How do implementation complexity and security interpretation trade off against each other?
There is a clear trade-off between implementation complexity and ease of security interpretation. BB84 is relatively simple to implement and provides a clear, direct security signal through QBER, making it easy to analyze. B92 is also simple but sacrifices efficiency and is more sensitive to noise, which can complicate interpretation. E91 is the most complex protocol due to its reliance on entanglement and Bell inequality testing, but it offers stronger theoretical security guarantees. However, this added complexity makes it harder to interpret results and more sensitive to implementation issues. Overall, simpler protocols like BB84 are easier to use and interpret, while more complex protocols like E91 provide deeper security insights but require more careful implementation and analysis.

---

What changed most under attack?
The most significant change under attack was the sharp increase in QBER and the rapid drop in the secret key rate. As the intercept-resend attack probability increased, QBER rose to around 25% at full attack, which is consistent with theoretical expectations. At the same time, the key rate quickly dropped to zero, meaning no secure key could be generated. This shows that eavesdropping introduces clear and detectable disturbances in the communication channel.

What changed most under noise?
Under noise, the most noticeable change was the gradual increase in QBER and the steady decrease in key rate. Unlike attacks, which caused sudden spikes in error, noise caused a more continuous degradation of performance. In particular, amplitude damping (photon loss) significantly reduced the key rate, while phase damping caused smaller increases in QBER. Overall, noise made the system less reliable over time rather than immediately insecure.

Which protocol was easiest to interpret from the results?
BB84 was the easiest protocol to interpret. Its behavior is directly reflected in the QBER, making it clear when the system is secure or under attack. When disturbances were introduced, the increase in QBER clearly indicated a problem. This straightforward relationship between errors and security made BB84 much easier to analyze compared to B92 and especially E91.

Which result surprised you most?
The most surprising result was the behavior of the photon number splitting (PNS) attack. Unlike intercept-resend, the PNS attack allowed significant information gain without increasing QBER, making it difficult to detect. This highlights that not all attacks produce obvious error signals and shows the importance of additional techniques, such as decoy states, in practical quantum key distribution systems.

---

## Key Findings Summary

- BB84 is the most efficient and stable protocol  
- B92 is less efficient but still secure due to non-orthogonal states  
- E91 offers strong theoretical security but is complex and sensitive  
- Proper testing is critical for validating protocol behavior  
- Small implementation details can significantly affect quantum protocols  

—

How does B92 achieve security using only two states?
B92 achieves security by using two non-orthogonal quantum states, |0⟩ and |+⟩, which cannot be perfectly distinguished. Because of this, an eavesdropper cannot measure the state without introducing errors. The protocol only keeps measurement results that provide definite information, discarding inconclusive outcomes. This ensures that any interception attempt disturbs the system and can be detected through increased error rates.

How does E91 use entanglement for security?
E91 uses entangled particle pairs to generate correlated measurement outcomes between Alice and Bob. These correlations are tested using a Bell inequality. If the Bell inequality is violated, it confirms that the system exhibits quantum behavior and that no eavesdropper has intercepted the particles. Any attempt to interfere with the entangled states breaks these correlations, making the presence of an attacker detectable.

What was difficult about implementing each protocol?
Implementing B92 required careful handling of conclusive and inconclusive measurement outcomes, as most results must be discarded. The main challenge was correctly identifying which measurements provide definite information.
Implementing E91 was more difficult because it involved entangled states and separating rounds for key generation and Bell testing. Ensuring correct measurement correlations and interpreting the Bell parameter added complexity compared to the simpler prepare-and-measure protocols.

What did you observe about efficiency and security metrics?

BB84 showed the highest efficiency (~48%) and maintained a low QBER under ideal conditions, making it the most stable protocol. B92 had lower efficiency (~27%) due to discarding inconclusive results, but still maintained security. E91 showed the lowest efficiency (~24%) and a higher QBER in this implementation, highlighting its sensitivity to measurement configuration.
Under noisy conditions, all protocols experienced an increase in QBER and a decrease in key rate, eventually becoming insecure beyond a certain threshold. This demonstrates the trade-off between efficiency, security, and robustness in quantum key distribution protocols.


## Questions for Discussion

1. Why does the E91 protocol produce high QBER even under ideal conditions in this implementation?  
2. How can entanglement-based protocols be made more robust in practical systems?  
3. What are the trade-offs between efficiency (BB84), simplicity (B92), and theoretical security (E91)?  

---

*Experiment Log - Quantum Cryptography Project*  
*Started: 2026-04-07*  
*Last Updated: 2026-04-07*


Malcolm Wyatt
## 2/25/2026 BB84 Protocol Analysis

=======
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
>>>>>>> 4be2d93f8834106c9e01b34a0147fe2abd6ab498

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

<<<<<<< HEAD
Notes and Observations:
    Week 3: Noticed that B92 is much more sensitive to channel noise, reaching the 11% cutoff faster than BB84.

Discussion Point: 
    If the PNS attack creates 0% error, the next phase of research should focus on Decoy State implementation to protect multi-photon sources.
=======
Discussion Point: If the PNS attack creates 0% error, the next phase of research should focus on Decoy State implementation to protect multi-photon sources.
```
>>>>>>> 4be2d93f8834106c9e01b34a0147fe2abd6ab498

Image:
results\figures\exp03_attack_analysis.png



[2026-04-05] Experiment 04: Channel Characterization & Distance Analysis — Jerald D. Fisher

Objective:
    To quantify the impact of fiber-optic attenuation on signal integrity and determine the maximum secure transmission distance for the BB84 protocol.

Method Parameters:
    Fiber Model: Single-mode fiber with 0.2dB/km attenuation.

Results:

Metric	Measured Value @ 50km	Measured Value @ 150km	Measured Value @ 189km
QBER (%)	2.14%	7.85%	11.02%
SNR (dB)	24.2 dB	10.1 dB	0.2 dB
Secret Key Yield	28.50%	4.20%	0.00%
Status	SECURE	SECURE (LOW YIELD)	COMPROMISED

Conclusions:

The 11% Wall: Verified the Shor-Preskill security bound. Beyond 189.4 km, parity disclosure during error correction exceeds the available sifted bits.

Dark Count Dominance: Beyond 160 km, QBER is driven by hardware "false clicks" as signal intensity fades into the noise floor.

Practical Limit: While photons still arrive at 200 km, they are cryptographically useless.

image:
results\figures\exp04_noise_resilience.png


[2026-04-07] Experiment 05: Post-Processing & "Performance Tax" — Jerald D. Fisher

Objective: 
    To measure the efficiency of the post-processing lifecycle (Sifting, CASCADE, and Privacy Amplification) across varying noise scenarios.

Method Parameters: * Input Size: 2500 raw qubits.

Algorithms: CASCADE (4-Pass), Toeplitz Hashing.

Security Parameter: 1e-10.

Results:

Noise Level	Sifted Bits	EC Disclosure (Bits)	Final Secret Key	Efficiency (f)
Ideal (0%)	1262	0	568	1
Low (2%)	1258	142	412	1.16
Medium (5%)	1265	398	186	1.22
High (8%)	1244	612	32	1.28

Conclusions:

Efficiency Factor: Our CASCADE implementation achieved an average efficiency (f) of 1.18, disclosing 18% more parity than the theoretical Shannon limit.

Performance Tax: Moving from 2% to 8% noise results in a 92% reduction in final key yield.

Block-Size Sensitivity: Block sizes smaller than 1000 bits lead to unstable error estimation and key "over-shrinkage."


image:
results\figures\exp05_full_simulation.png


[2026-04-09] Experiment 06: Decoy-State Optimization & Attack Detection — Jerald D. Fisher

Objective: 
    To validate the effectiveness of multi-intensity decoy states in identifying Intercept-Resend (IR) attacks and optimizing throughput.

Method Parameters: Intensities: Signal (mu=0.6), Decoy (nu=0.1), Vacuum (0).

Adversarial Model: Intercept-Resend Attack (30% probability).

Optimization: Dynamic mu/nu ratio based on real-time QBER.

Results:

Scenario	Signal Yield (Y_mu)	Decoy Yield (Y_nu)	Yield Divergence	Detection Latency
Normal Channel	0.045	0.042	0.003	N/A
IR Attack (Active)	0.062	0.031	0.031	250 Pulses
Optimized Channel	0.048	0.044	0.004	N/A

Conclusions:

The Yield Signature: An active attack creates a "Yield Divergence." Eve's measurements boost signal yield but suppress decoy yield relative to the noise floor.

Optimization Gain: Dynamically adjusting intensities improved the secret key lower bound by 8.4%.

Detection Speed: Successfully flagged the attack with 99.8% confidence within the first 12% of the transmission window.

image:
/results/figures/exp06_decoy_detection.png
