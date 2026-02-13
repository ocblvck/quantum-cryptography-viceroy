# Quantum Cryptography Viceroy 

## Quantum Key Distribution Protocol Suite: Implementation, Attack Simulation, and Security Analysis

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.0+-purple.svg)](https://qiskit.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

##  Project Overview

This project provides a comprehensive implementation and analysis of Quantum Key Distribution (QKD) protocols, designed as an undergraduate research project for Spring 2026. The project explores the theoretical foundations, practical implementations, and security analysis of quantum cryptographic protocols.

### Research Objectives

1. **Protocol Implementation**: Implement and validate multiple QKD protocols (BB84, B92, E91, SARG04)
2. **Attack Simulation**: Simulate and analyze common quantum attacks (Intercept-Resend, Photon Number Splitting, Trojan Horse)
3. **Noise Analysis**: Study protocol performance under realistic quantum channel noise models
4. **Security Metrics**: Develop and compute security metrics including Quantum Bit Error Rate (QBER), key rate, and information leakage
5. **Comparative Analysis**: Provide comprehensive comparison of protocol performance and security characteristics

### Expected Outcomes

- Poster presentation at undergraduate research symposium
- Conference paper submission (potential venues: IEEE QCE, ACM Q2B, SPIE Quantum)
- Open-source educational resource for quantum cryptography

##  Project Structure

```
quantum-cryptography-viceroy/
├── README.md
├── requirements.txt
├── setup.py
├── docs/
│   ├── PROTOCOL_THEORY.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── EXPERIMENT_LOG.md
│   └── PRESENTATION_MATERIALS/
├── src/
│   ├── __init__.py
│   ├── protocols/
│   │   ├── __init__.py
│   │   ├── bb84.py              # BB84 protocol implementation
│   │   ├── b92.py               # B92 protocol implementation
│   │   ├── e91.py               # E91 (Ekert) protocol implementation
│   │   ├── sarg04.py            # SARG04 protocol implementation
│   │   └── base_protocol.py     # Abstract base class for protocols
│   ├── attacks/
│   │   ├── __init__.py
│   │   ├── intercept_resend.py  # Intercept-resend attack
│   │   ├── pns_attack.py        # Photon number splitting attack
│   │   ├── trojan_horse.py      # Trojan horse attack
│   │   └── base_attack.py       # Abstract base class for attacks
│   ├── noise_models/
│   │   ├── __init__.py
│   │   ├── depolarizing.py      # Depolarizing noise channel
│   │   ├── amplitude_damping.py # Amplitude damping channel
│   │   ├── phase_damping.py     # Phase damping channel
│   │   └── realistic_fiber.py   # Realistic fiber optic channel model
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── security_metrics.py  # QBER, key rate, mutual information
│   │   ├── statistical_tests.py # Randomness and correlation tests
│   │   └── visualization.py     # Plotting and visualization utilities
│   └── utils/
│       ├── __init__.py
│       ├── quantum_utils.py     # Helper functions for quantum operations
│       └── classical_utils.py   # Classical post-processing utilities
├── experiments/
│   ├── exp01_bb84_basic.py
│   ├── exp02_protocol_comparison.py
│   ├── exp03_attack_analysis.py
│   ├── exp04_noise_resilience.py
│   └── exp05_full_qkd_simulation.py
├── tests/
│   ├── test_protocols.py
│   ├── test_attacks.py
│   └── test_analysis.py
├── notebooks/
│   ├── 01_QKD_Introduction.ipynb
│   ├── 02_BB84_Deep_Dive.ipynb
│   ├── 03_Attack_Visualization.ipynb
│   └── 04_Results_Analysis.ipynb
└── results/
    ├── figures/
    └── data/
```

##  Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ocblvck/quantum-cryptography-viceroy.git
cd quantum-cryptography-viceroy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Run Your First QKD Simulation

```python
from src.protocols import BB84Protocol
from src.analysis import SecurityMetrics

# Initialize BB84 protocol
bb84 = BB84Protocol(key_length=256, num_decoy_states=3)

# Run key distribution
alice_key, bob_key, qber = bb84.run()

# Analyze security
metrics = SecurityMetrics(alice_key, bob_key)
print(f"QBER: {qber:.4f}")
print(f"Secure Key Rate: {metrics.secure_key_rate():.4f}")
```

##  Theoretical Background

### Quantum Key Distribution (QKD)

QKD leverages the fundamental principles of quantum mechanics to establish secure cryptographic keys between two parties (Alice and Bob). The security is guaranteed by:

1. **No-Cloning Theorem**: Quantum states cannot be perfectly copied
2. **Measurement Disturbance**: Measuring a quantum state inevitably disturbs it
3. **Heisenberg Uncertainty Principle**: Certain pairs of properties cannot be simultaneously known

### Implemented Protocols

| Protocol | Year | Basis States | Security Proof | Complexity |
|----------|------|--------------|----------------|------------|
| BB84     | 1984 | 4 (2 bases)  | Unconditional  | Low        |
| B92      | 1992 | 2 (non-orthogonal) | Unconditional | Very Low |
| E91      | 1991 | Entangled pairs | Bell inequality | Medium   |
| SARG04   | 2004 | 4 (2 bases)  | PNS-resistant  | Low        |

##  Semester Timeline

### Phase 1: Foundation (Weeks 1-4)
- [ ] Literature review and theoretical foundations
- [ ] Environment setup and Qiskit familiarization
- [ ] Implement BB84 protocol
- [ ] Basic testing and validation

### Phase 2: Expansion (Weeks 5-8)
- [ ] Implement B92, E91, and SARG04 protocols
- [ ] Develop attack simulations
- [ ] Create noise models
- [ ] Comparative benchmarking

### Phase 3: Analysis (Weeks 9-12)
- [ ] Security analysis and metrics computation
- [ ] Statistical significance testing
- [ ] Generate publication-quality figures
- [ ] Draft conference paper/poster

### Phase 4: Dissemination (Weeks 13-16)
- [ ] Finalize paper/poster
- [ ] Prepare presentation materials
- [ ] Submit to conference/symposium
- [ ] Document and release code

##  Team

- **Faculty Mentor**: Chibuike Okekeogbu
- **Undergraduate Researcher 1**: Malcolm Wyatt
- **Undergraduate Researcher 2**: Jerald Fisher
- **Undergraduate Researcher 2**: Habiba Sorour

##  References

1. Bennett, C. H., & Brassard, G. (1984). Quantum cryptography: Public key distribution and coin tossing.
2. Bennett, C. H. (1992). Quantum cryptography using any two nonorthogonal states.
3. Ekert, A. K. (1991). Quantum cryptography based on Bell's theorem.
4. Scarani, V., et al. (2004). Quantum cryptography protocols robust against photon number splitting attacks.
5. Pirandola, S., et al. (2020). Advances in quantum cryptography. Advances in Optics and Photonics.

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

---

*This project is part of the Spring 2026 Undergraduate Research Program.*
