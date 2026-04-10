# Assignment 01: Implementing B92 and E91

## Objective

In this assignment, you will implement and study two quantum key distribution protocols: B92 and E91. The goal is to help you understand how the protocols work by implementing them inside the existing repository rather than building a separate simulator.

By the end of the assignment, you should be able to:

1. Explain how B92 uses two non-orthogonal states for key distribution.
2. Explain how E91 uses entanglement and Bell inequality testing for security.
3. Implement protocol logic within the repository's existing Python architecture.
4. Run experiments and document what you observe.

## Before You Start

Set up the repository:

```bash
git clone https://github.com/ocblvck/quantum-cryptography-viceroy.git
cd quantum-cryptography-viceroy
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Read these files before writing code:

1. [../../src/protocols/base_protocol.py](../../src/protocols/base_protocol.py)
2. [../../src/protocols/bb84.py](../../src/protocols/bb84.py)
3. [../PROTOCOL_THEORY.md](../PROTOCOL_THEORY.md)
4. [../../tests/test_protocols.py](../../tests/test_protocols.py)
5. [../../experiments/exp02_protocol_comparison.py](../../experiments/exp02_protocol_comparison.py)
6. [../EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md)

## Working Rule

Most of what you need already exists in the repository. Use the current structure.

Do not create a new framework for protocol execution. Do not write large new helper layers unless they are actually necessary. If the repository already has a place for the logic, put the code there.

Use [../../src/protocols/bb84.py](../../src/protocols/bb84.py) as your reference for style and integration, but do not copy its logic blindly because B92 and E91 work differently.

## Part 1: Implement B92

Work in [../../src/protocols/b92.py](../../src/protocols/b92.py).

Your implementation should support the following ideas:

1. Alice encodes bit 0 as |0⟩ and bit 1 as |+⟩.
2. Bob uses measurements that can produce conclusive and inconclusive outcomes.
3. Only conclusive outcomes should contribute to the sifted key.
4. The protocol should return results through the repository's existing result structure.

At minimum, your B92 implementation should correctly handle:

1. State preparation
2. Measurement logic
3. Sifting logic
4. End-to-end execution through the shared protocol interface

As you implement B92, make sure you can explain why the protocol intentionally discards many rounds.

## Part 2: Implement E91

Work in [../../src/protocols/e91.py](../../src/protocols/e91.py).

Your implementation should support the following ideas:

1. A source creates entangled pairs.
2. Alice and Bob choose measurement settings independently.
3. Some rounds are used for key generation.
4. Some rounds are used for Bell inequality testing.
5. The result should include Bell-test-related information in addition to the key metrics.

At minimum, your E91 implementation should correctly handle:

1. Entangled pair creation
2. Measurement operations for both Alice and Bob
3. Key sifting for the valid key-generation rounds
4. Computation of a Bell parameter or equivalent security statistic
5. Integration with the existing result object and protocol interface

As you implement E91, make sure you can explain why Bell inequality violation matters for security.

## Part 3: Validate Your Work

Use the existing tests as a starting point.

1. Run the relevant protocol tests.
2. Fix any implementation issues until the protocol behavior is consistent.
3. Add at least one meaningful extra test of your own for B92 or E91.

Good test ideas include:

1. B92 should have lower sifting efficiency than BB84.
2. E91 should report Bell-test-related data in the result.
3. E91 key bits should come only from the designated basis combinations.

## Part 4: Run Experiments

Use the existing experiment patterns in [../../experiments/exp02_protocol_comparison.py](../../experiments/exp02_protocol_comparison.py). You may extend an existing experiment or add a focused experiment script if needed, but keep it consistent with the repository.

Run at least these experiments:

1. One no-noise run for B92
2. One no-noise run for E91
3. A comparison of BB84, B92, and E91 using:
   - raw key length
   - sifted key length
   - sifting efficiency
   - QBER
   - execution time
4. At least one noisy-channel run to observe how protocol behavior changes

## Part 5: Record Your Findings

You must document your work in [../EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md).

For each meaningful experiment, record:

1. Date
2. Objective
3. Method
4. Parameters
5. Results
6. Conclusions
7. Next steps or open questions

Do not leave your findings only in code comments or terminal output.

## Deliverables

Submit the following:

1. Your implementation updates in [../../src/protocols/b92.py](../../src/protocols/b92.py) and [../../src/protocols/e91.py](../../src/protocols/e91.py)
2. Any experiment updates in [../../experiments](../../experiments)
3. At least one meaningful added test in [../../tests/test_protocols.py](../../tests/test_protocols.py) or a related test file
4. Updated entries in [../EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md)
5. A short written summary answering:
   - How does B92 achieve security using only two states?
   - How does E91 use entanglement for security?
   - What was difficult about implementing each protocol?
   - What did you observe about efficiency and security metrics?

## Evaluation Criteria

Your work will be evaluated on:

1. Correctness of the B92 implementation
2. Correctness of the E91 implementation
3. Proper use of the existing repository architecture
4. Quality of testing
5. Quality of experiment documentation
6. Depth of conceptual understanding in your written summary

## Final Note

This assignment is designed to help you connect theory to code. The repository already contains the structure you need. Your task is to place the right logic in the right locations, validate it, and explain what the implementation is doing.