# Assignment 03: SARG04 and PNS Resistance

## Objective

In this assignment, you will study the SARG04 protocol and understand why it is treated differently from BB84 even though it uses the same four quantum states. The main goal is to connect the protocol's classical announcement step to its resistance against photon number splitting (PNS) attacks.

By the end of the assignment, you should be able to:

1. Explain how SARG04 differs from BB84.
2. Explain why SARG04 is associated with stronger resistance to PNS attacks.
3. Work with the existing SARG04 implementation in the repository.
4. Compare SARG04 with BB84 and B92 using controlled experiments.
5. Record your results and interpretations clearly.

## Before You Start

Set up the repository if you have not already done so:

```bash
git clone https://github.com/ocblvck/quantum-cryptography-viceroy.git
cd quantum-cryptography-viceroy
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Read these files before you begin:

1. [../../src/protocols/sarg04.py](../../src/protocols/sarg04.py)
2. [../../src/protocols/bb84.py](../../src/protocols/bb84.py)
3. [../PROTOCOL_THEORY.md](../PROTOCOL_THEORY.md)
4. [../../tests/test_protocols.py](../../tests/test_protocols.py)
5. [../../experiments/exp02_protocol_comparison.py](../../experiments/exp02_protocol_comparison.py)
6. [../EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md)

## Working Rule

You are expected to use the existing repository structure. Do not create a separate simulator, separate protocol framework, or large new helper layer unless there is a clear need.

The SARG04 protocol is already implemented in the repository. Your job in this assignment is to understand it, validate it, compare it to related protocols, and if needed, make small, justified improvements within the current code structure.

## Part 1: Understand the Protocol

Study how SARG04 works in theory and in code.

Focus on these questions:

1. How does SARG04 use the same four signal states as BB84?
2. What does Alice announce in SARG04, and how is that different from BB84?
3. Why does changing the announcement rule matter for PNS resistance?
4. Why is SARG04 less efficient than BB84 during sifting?

Write a short explanation in your notes before running experiments.

## Part 2: Inspect the Existing Implementation

Read [../../src/protocols/sarg04.py](../../src/protocols/sarg04.py) carefully.

Make sure you can identify where the code handles:

1. State preparation
2. Measurement logic
3. Announcement pairs
4. Sifting logic
5. Protocol execution and returned metrics

If you notice issues or unclear logic, do not rewrite the whole file. Make only targeted changes and explain why they were needed.

## Part 3: Validate the Implementation

Use the existing tests in [../../tests/test_protocols.py](../../tests/test_protocols.py) as your starting point.

At minimum:

1. Run the SARG04 tests.
2. Confirm that the protocol executes successfully.
3. Confirm that the observed sifting efficiency is consistent with the expected rough range for SARG04.

Add at least one focused test of your own. Good options include:

1. Comparing BB84 and SARG04 sifting efficiency for the same key length
2. Checking that the result reports protocol-specific metadata such as PNS-related information
3. Checking that SARG04 produces a usable sifted key under no-noise conditions

## Part 4: Run Comparative Experiments

Use the existing experiment pattern in [../../experiments/exp02_protocol_comparison.py](../../experiments/exp02_protocol_comparison.py).

Compare at least these protocols:

1. BB84
2. SARG04
3. B92

Record and compare:

1. raw key length
2. sifted key length
3. sifting efficiency
4. QBER
5. execution time

Then answer:

1. How does SARG04 compare to BB84 in efficiency?
2. How does SARG04 compare to B92 in sifting efficiency?
3. What trade-off does SARG04 make in exchange for improved PNS resistance?

## Part 5: Connect SARG04 to PNS Attacks

This is the main conceptual part of the assignment.

You do not need to build a new PNS simulator unless you are explicitly extending an existing experiment. Instead, use the theory and the existing codebase to explain the protocol design.

In your written summary, address:

1. What is a photon number splitting attack in practical QKD systems?
2. Why is BB84 more vulnerable in weak coherent pulse implementations?
3. Why does SARG04's announcement strategy reduce Eve's advantage?
4. Why does this improvement come with an efficiency cost?

## Part 6: Record Your Findings

Use [../EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md) to document your work.

For each experiment, include:

1. Date
2. Objective
3. Method
4. Protocols used
5. Parameters
6. Results
7. Conclusions
8. Next steps or open questions

Do not leave your findings only in terminal output or code comments.

## Deliverables

Submit the following:

1. Any targeted updates you make to [../../src/protocols/sarg04.py](../../src/protocols/sarg04.py)
2. Any experiment updates in [../../experiments](../../experiments)
3. At least one added test in [../../tests/test_protocols.py](../../tests/test_protocols.py) or a related test file
4. Updated entries in [../EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md)
5. A short written summary answering:
   - How does SARG04 differ from BB84?
   - Why is SARG04 considered more resistant to PNS attacks?
   - What did your experiments show about its efficiency?
   - What trade-off do you think is most important in SARG04?

## Evaluation Criteria

Your work will be evaluated on:

1. Accuracy of your explanation of SARG04
2. Correct use of the existing repository structure
3. Quality of your testing and validation
4. Quality of your experimental comparison
5. Quality of your experiment documentation
6. Strength of your interpretation of the PNS-resistance trade-off

## Final Note

This assignment is meant to show that small changes in protocol post-processing can lead to meaningful differences in security interpretation. Focus on understanding the trade-off between efficiency and practical security rather than treating SARG04 as just another variant of BB84.