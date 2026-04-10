# Assignment 02: Attack and Noise Analysis

## Objective

In this assignment, you will study how quantum key distribution protocols behave when the channel is noisy or when an eavesdropper is present. The goal is to help you use the repository's attack, noise, analysis, and experiment code in a disciplined way.

By the end of the assignment, you should be able to:

1. Run controlled experiments with existing attack and noise components.
2. Compare how BB84, B92, and E91 behave under the same conditions.
3. Interpret changes in QBER, sifted key length, and key rate.
4. Document results clearly in the experiment log.

## Before You Start

Make sure your environment is set up:

```bash
git clone https://github.com/ocblvck/quantum-cryptography-viceroy.git
cd quantum-cryptography-viceroy
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Read these files first:

1. [../../experiments/exp02_protocol_comparison.py](../../experiments/exp02_protocol_comparison.py)
2. [../../experiments/exp03_attack_analysis.py](../../experiments/exp03_attack_analysis.py)
3. [../../experiments/exp04_noise_resilience.py](../../experiments/exp04_noise_resilience.py)
4. [../../src/attacks](../../src/attacks)
5. [../../src/noise_models](../../src/noise_models)
6. [../../src/analysis](../../src/analysis)
7. [../EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md)

## Working Rule

You are not being asked to build a new simulator. Use the attack classes, noise models, experiment patterns, and analysis utilities already provided in the repository.

If you need a new experiment script, keep it focused and place it in [../../experiments](../../experiments). Do not create a parallel project structure outside the repository.

## Part 1: Baseline Comparison

Run a baseline comparison with no attack and no noise.

Use BB84, B92, and E91 and record:

1. raw key length
2. sifted key length
3. sifting efficiency
4. QBER
5. execution time

Your baseline should give you a reference point before you introduce disturbances.

## Part 2: Attack Analysis

Use the existing attack framework to study at least one attack scenario. A good starting point is the intercept-resend attack.

For each protocol you test:

1. Run the protocol without attack.
2. Run it again with the attack enabled.
3. Compare the observed QBER and any other relevant security indicators.

Questions to answer:

1. Which protocol shows the clearest measurable effect under attack?
2. How does the attack change the final usable key length?
3. In E91, what happens to the Bell-test-related information when the channel is disturbed?

## Part 3: Noise Analysis

Use the repository's noise models to study how channel noise affects the protocols.

At minimum:

1. Choose one existing noise model.
2. Run each protocol across multiple noise levels.
3. Plot or tabulate how QBER changes as noise increases.
4. Identify the point where the protocol becomes practically unusable or clearly insecure.

If you add a new experiment script for this, follow the structure already used in the existing experiment files.

## Part 4: Comparative Interpretation

Write a short comparison of BB84, B92, and E91 based on your results.

Your comparison should address:

1. Which protocol is most efficient in clean conditions?
2. Which protocol appears most sensitive to noise?
3. Which protocol gives the clearest security signal under disturbance?
4. How do implementation complexity and security interpretation trade off against each other?

## Part 5: Testing and Code Quality

If you modify experiment code or protocol-facing logic, run the relevant tests and add a focused test if your change introduces new behavior that should be checked.

Do not add broad new utility code unless the assignment actually requires it.

## Part 6: Record Your Findings

Use [../EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md) to document your work.

For each experiment, include:

1. Date
2. Objective
3. Method
4. Protocols used
5. Attack or noise settings
6. Results
7. Conclusions
8. Next steps

## Deliverables

Submit the following:

1. Any experiment updates in [../../experiments](../../experiments)
2. Any relevant test updates in [../../tests](../../tests)
3. Updated entries in [../EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md)
4. A short written summary answering:
   - What changed most under attack?
   - What changed most under noise?
   - Which protocol was easiest to interpret from the results?
   - Which result surprised you most?

## Evaluation Criteria

Your work will be evaluated on:

1. Correct use of the repository's existing attack and noise components
2. Quality of the experimental comparison
3. Clarity of the written interpretation
4. Quality of experiment documentation
5. Discipline in working within the existing project structure

## Final Note

This assignment is about learning how to use a codebase for controlled scientific comparison. Focus on clear experiments, careful interpretation, and documented results.