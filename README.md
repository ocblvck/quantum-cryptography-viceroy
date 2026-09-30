# Quantum Cryptography Viceroy

## Quantum Key Distribution Protocol Suite: Implementation, Attack Simulation, and Security Analysis

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.0+-purple.svg)](https://qiskit.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Project Overview

This project collects implementations and analysis tools for Quantum Key Distribution (QKD) protocols as part of an undergraduate research project for Spring 2026. It focuses on protocol behavior, security analysis, and reproducible experiments.

## For Students

If you are joining the project as a student, start here:

1. Read [docs/assignments/README.md](docs/assignments/README.md) for the assignment list.
2. Read [docs/PROTOCOL_THEORY.md](docs/PROTOCOL_THEORY.md) before modifying protocol code.
3. Use [docs/EXPERIMENT_LOG.md](docs/EXPERIMENT_LOG.md) to record your experiments and conclusions.
4. Use the existing files in `src/`, `experiments/`, and `tests/` rather than building a separate project structure.

### Research Objectives

1. **Protocol Implementation**: Implement and validate multiple QKD protocols (BB84, B92, E91, SARG04)
2. **Attack Simulation**: Simulate and analyze common quantum attacks (Intercept-Resend, Photon Number Splitting, Trojan Horse)
3. **Noise Analysis**: Study protocol performance under realistic quantum channel noise models
4. **Security Metrics**: Develop and compute security metrics including Quantum Bit Error Rate (QBER), key rate, and information leakage
5. **Comparative Analysis**: Compare protocol performance and security characteristics under common conditions

### Expected Outcomes

- Poster presentation at an undergraduate research symposium
- A paper or extended report if the project results support it
- A codebase that future students can read and extend

## Project Structure

```
quantum-cryptography-viceroy/
├── README.md
├── requirements.txt
├── setup.py
├── docs/
│   ├── PROTOCOL_THEORY.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── EXPERIMENT_LOG.md
│   ├── assignments/
│   │   ├── README.md
│   │   └── assignment_01_b92_e91.md
│   │   └── assignment_02_attack_noise_analysis.md
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

## Quick Start

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
result = bb84.run()

# Analyze security
metrics = SecurityMetrics(result.alice_key, result.bob_key)
print(f"QBER: {result.qber:.4f}")
print(f"Secure Key Rate: {metrics.secret_key_rate():.4f}")
```

## Student Assignments

Assignment handouts for the undergraduate research group live in `docs/assignments/`.

- Assignment index: [docs/assignments/README.md](docs/assignments/README.md)
- Current B92/E91 implementation assignment: [docs/assignments/assignment_01_b92_e91.md](docs/assignments/assignment_01_b92_e91.md)
- Current attack and noise analysis assignment: [docs/assignments/assignment_02_attack_noise_analysis.md](docs/assignments/assignment_02_attack_noise_analysis.md)
- Current SARG04 assignment: [docs/assignments/assignment_03_sarg04_pns_resistance.md](docs/assignments/assignment_03_sarg04_pns_resistance.md)
- Experiment notes and findings: [docs/EXPERIMENT_LOG.md](docs/EXPERIMENT_LOG.md)

## Theoretical Background

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

## Semester Timeline

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

## Team

- **Faculty Mentor**: Chibuike Okekeogbu
- **Undergraduate Researcher 1**: Malcolm Wyatt
- **Undergraduate Researcher 2**: Jerald Fisher
- **Undergraduate Researcher 2**: Habiba Sorour

## References

1. Bennett, C. H., & Brassard, G. (1984). Quantum cryptography: Public key distribution and coin tossing.
2. Bennett, C. H. (1992). Quantum cryptography using any two nonorthogonal states.
3. Ekert, A. K. (1991). Quantum cryptography based on Bell's theorem.
4. Scarani, V., et al. (2004). Quantum cryptography protocols robust against photon number splitting attacks.
5. Pirandola, S., et al. (2020). Advances in quantum cryptography. Advances in Optics and Photonics.

## Citation

If you use this code, cite this repository and credit the CREO VICEROY undergraduate
research program at North Carolina A&T State University (graduate mentor Chibuike C.
Okekeogbu, faculty PI Ahmad Patooghy). A machine-readable citation is in `CITATION.cff`.
If a paper from this project is published, it will be added there.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

If you are contributing to this repository, keep changes small, document experiments, and follow the existing project structure. See [Contributing Guidelines](CONTRIBUTING.md) if that file is present in your local copy.

---

*This project is part of the Spring 2026 Undergraduate Research Program.*
