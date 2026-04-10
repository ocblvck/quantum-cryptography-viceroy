# Quantum Key Distribution: Protocol Theory

This document summarizes the theory behind the QKD protocols implemented
in this repository. It is written for students who need enough background
to read the code and run experiments.

## Table of Contents

1. [Introduction to Quantum Cryptography](#introduction)
2. [BB84 Protocol](#bb84-protocol)
3. [B92 Protocol](#b92-protocol)
4. [E91 Protocol](#e91-protocol)
5. [SARG04 Protocol](#sarg04-protocol)
6. [Security Proofs Overview](#security-proofs)
7. [References](#references)

---

## Introduction to Quantum Cryptography {#introduction}

Quantum Key Distribution (QKD) enables two parties (Alice and Bob) to
establish a shared secret key with information-theoretic security. The
idea is that eavesdropping changes the quantum system in a detectable way.

### Key Principles

1. **No-Cloning Theorem**: Quantum states cannot be perfectly copied
2. **Measurement Disturbance**: Measuring a quantum state disturbs it
3. **Heisenberg Uncertainty**: Incompatible observables cannot be measured simultaneously

These principles are what allow Alice and Bob to detect interference.

### QKD vs Classical Cryptography

| Aspect | Classical (RSA, AES) | Quantum (QKD) |
|--------|---------------------|---------------|
| Security Basis | Computational complexity | Laws of physics |
| Quantum Computer Threat | Vulnerable | Immune |
| Key Distribution | Asymmetric encryption | Quantum channel |
| Eavesdropping Detection | Not possible | Automatic |

---

## BB84 Protocol {#bb84-protocol}

Published by Bennett and Brassard in 1984, BB84 is the first and most
well-known QKD protocol.

### Protocol Description

**States Used**: 4 polarization states in 2 bases
- Z-basis: |0⟩ (horizontal) and |1⟩ (vertical)
- X-basis: |+⟩ = (|0⟩+|1⟩)/√2 and |−⟩ = (|0⟩−|1⟩)/√2

**Protocol Steps**:

1. **Preparation (Alice)**:
   - For each bit, randomly choose a basis (Z or X)
   - Encode bit: 0→|0⟩ or |+⟩, 1→|1⟩ or |−⟩
   - Send qubit to Bob

2. **Measurement (Bob)**:
   - For each qubit, randomly choose measurement basis
   - Record result and basis

3. **Sifting**:
   - Alice and Bob publicly compare bases
   - Keep only bits where bases match (~50%)

4. **Error Estimation**:
   - Sacrifice ~10% of sifted key to estimate QBER
   - Abort if QBER > 11%

5. **Error Correction**:
   - Use CASCADE or similar protocol
   - Correct remaining errors

6. **Privacy Amplification**:
   - Apply hash function to reduce key
   - Eliminates Eve's information

### Theoretical Key Rate

The asymptotic secret key rate is:

```
R = 1 - H(QBER) - H(QBER)
  = 1 - 2H(QBER)
```

where H(x) = -x log₂(x) - (1-x) log₂(1-x) is the binary entropy.

### Security Threshold

BB84 is secure when QBER < 11%:
- At QBER = 11%, R = 0
- Above 11%, Eve may have more information than Bob

---

## B92 Protocol {#b92-protocol}

Bennett's 1992 simplified protocol uses only 2 non-orthogonal states.

### Protocol Description

**States Used**: 2 non-orthogonal states
- |0⟩ for bit 0
- |+⟩ for bit 1

**Key Insight**: Non-orthogonal states cannot be perfectly distinguished.

**Protocol Steps**:

1. Alice sends |0⟩ or |+⟩
2. Bob measures in X or Z basis (random)
3. Bob announces conclusive results only
4. Sifting efficiency: ~25%

### Why Only 2 States Work

The security comes from the overlap ⟨0|+⟩ = 1/√2:
- If Eve measures to distinguish, she disturbs the state
- Non-orthogonality ensures measurement disturbance

### Advantages and Disadvantages

| Advantages | Disadvantages |
|------------|---------------|
| Simpler implementation | Lower key rate |
| Fewer components | Higher loss sensitivity |
| Conceptually elegant | PNS vulnerable |

---

## E91 Protocol {#e91-protocol}

Ekert's 1991 protocol uses quantum entanglement and Bell's theorem.

### Protocol Description

**Resource**: Entangled Bell pairs |Φ⁺⟩ = (|00⟩ + |11⟩)/√2

**Measurement Bases**:
- Alice: 0°, 22.5°, 45°
- Bob: 22.5°, 45°, 67.5°

**Protocol Steps**:

1. Source distributes entangled pairs
2. Alice and Bob measure in random bases
3. Public announcement of measurement bases
4. Matching bases (22.5°, 45°) → sifted key
5. Non-matching bases → Bell test

### Bell Inequality Testing

The CHSH inequality for classical correlations:

```
|S| = |E(a,b) - E(a,b') + E(a',b) + E(a',b')| ≤ 2
```

Quantum mechanics predicts |S| = 2√2 ≈ 2.83 for entangled states.

**Security from Bell Violation**:
- If |S| > 2, states are genuinely entangled
- Entanglement cannot be shared with Eve
- Device-independent security guarantee

### Device Independence

E91 can, in principle, support security claims even with partially untrusted devices:
- Bell violation certifies genuine entanglement
- No assumptions about device internals needed
- Stronger security interpretation than prepare-and-measure protocols

---

## SARG04 Protocol {#sarg04-protocol}

Scarani et al.'s 2004 protocol modifies BB84 to resist PNS attacks.

### Protocol Description

**States Used**: Same 4 states as BB84

**Key Difference**: State announcement strategy
- BB84: Announce basis
- SARG04: Announce one of two non-orthogonal states

**Example**:
- Alice sends |0⟩ (Z-basis, bit 0)
- Alice announces "either |0⟩ or |+⟩"
- Bob can only decode if he measured in Z-basis

### Why This Resists PNS

In a PNS attack with weak coherent pulses:
- Eve keeps multi-photon pulses
- Eve measures after basis announcement

**SARG04 Defense**:
- Announcement reveals one of two non-orthogonal states
- Even with copy, Eve cannot determine which
- Information gain is limited

### Trade-offs

| Aspect | BB84 | SARG04 |
|--------|------|--------|
| Sifting efficiency | 50% | 25% |
| PNS resistance | No | Yes |
| Implementation | Simpler | Similar |
| Security threshold | ~11% | ~10.9% |

---

## Security Proofs Overview {#security-proofs}

### Unconditional Security

QKD provides "unconditional" or "information-theoretic" security:
- Security based on physics, not computational assumptions
- No algorithm can break it (given enough key material)
- Even future technologies cannot compromise past keys

### Key Rate Formulas

**BB84 Asymptotic Rate**:
```
R_∞ = 1 - H(QBER) - f·H(QBER)
```
where f ≥ 1 is the error correction efficiency.

**Finite-Key Rate**:
```
R_n = R_∞ - O(√(log(1/ε)/n))
```
where n is key length and ε is security parameter.

### Composable Security

Modern security proofs provide "composable" security:
- Key can be used in any cryptographic task
- Security composes with other protocols
- Universal definition of security

---

## References {#references}

### Original Protocol Papers

1. Bennett, C. H., & Brassard, G. (1984). "Quantum cryptography: Public key 
   distribution and coin tossing." *Proceedings of IEEE International 
   Conference on Computers, Systems and Signal Processing*, 175-179.

2. Bennett, C. H. (1992). "Quantum cryptography using any two nonorthogonal 
   states." *Physical Review Letters*, 68(21), 3121-3124.

3. Ekert, A. K. (1991). "Quantum cryptography based on Bell's theorem." 
   *Physical Review Letters*, 67(6), 661-663.

4. Scarani, V., Acín, A., Ribordy, G., & Gisin, N. (2004). "Quantum 
   cryptography protocols robust against photon number splitting attacks 
   for weak laser pulse implementations." *Physical Review Letters*, 92(5).

### Security Proofs

5. Shor, P. W., & Preskill, J. (2000). "Simple proof of security of the BB84 
   quantum key distribution protocol." *Physical Review Letters*, 85, 441.

6. Renner, R. (2005). "Security of quantum key distribution." 
   *arXiv:quant-ph/0512258*.

### Textbooks

7. Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and 
   Quantum Information*. Cambridge University Press.

8. Gisin, N., Ribordy, G., Tittel, W., & Zbinden, H. (2002). "Quantum 
   cryptography." *Reviews of Modern Physics*, 74(1), 145-195.

---

## Further Reading

### Online Resources

- [Qiskit Textbook - Quantum Cryptography](https://qiskit.org/textbook)
- [IBM Quantum Learning](https://learning.quantum.ibm.com/)
- [arXiv Quantum Physics](https://arxiv.org/list/quant-ph/recent)

### Video Lectures

- MIT OpenCourseWare: Quantum Information Science
- Caltech: Quantum Computation course

---

*Document prepared for the Quantum Cryptography Research Project*
*Last updated: 2025*
