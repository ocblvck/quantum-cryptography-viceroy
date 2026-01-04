# Implementation Guide

This guide provides detailed instructions for understanding and extending
the QKD implementation in this project.

## Table of Contents

1. [Project Architecture](#architecture)
2. [Protocol Implementation Guide](#protocols)
3. [Adding New Attacks](#attacks)
4. [Noise Model Development](#noise)
5. [Analysis Tools](#analysis)
6. [Experimental Workflow](#experiments)
7. [Best Practices](#best-practices)

---

## Project Architecture {#architecture}

```
quantum-cryptography-viceroy/
├── src/                    # Source code
│   ├── protocols/          # QKD protocol implementations
│   ├── attacks/            # Eavesdropping attack simulations
│   ├── noise_models/       # Channel noise models
│   ├── analysis/           # Security and statistical analysis
│   └── utils/              # Helper functions
├── experiments/            # Runnable experiment scripts
├── tests/                  # Unit tests
├── notebooks/              # Jupyter notebooks (tutorials)
├── docs/                   # Documentation
└── results/                # Output data and figures
```

### Design Principles

1. **Modularity**: Each component is independent
2. **Extensibility**: Easy to add new protocols/attacks
3. **Educational**: Code is well-documented and readable
4. **Reproducibility**: Seed-based random number generation

---

## Protocol Implementation Guide {#protocols}

### Base Protocol Class

All protocols inherit from `BaseQKDProtocol`:

```python
from src.protocols import BaseQKDProtocol

class MyProtocol(BaseQKDProtocol):
    def __init__(self, key_length: int, seed: int = None, **kwargs):
        super().__init__(key_length, seed)
        # Additional initialization
    
    def prepare_state(self, bit: int, basis: int) -> QuantumCircuit:
        """Prepare quantum state for given bit and basis."""
        pass
    
    def measure_state(self, circuit: QuantumCircuit, basis: int) -> int:
        """Measure state in given basis."""
        pass
    
    def sift_keys(self, alice_bases, bob_bases, measurements) -> tuple:
        """Perform key sifting."""
        pass
    
    def run(self, noise_model=None, eavesdropper=None) -> QKDResult:
        """Execute full protocol."""
        pass
```

### QKDResult Dataclass

Protocol execution returns a standardized result:

```python
@dataclass
class QKDResult:
    alice_key: np.ndarray        # Alice's sifted key
    bob_key: np.ndarray          # Bob's sifted key
    raw_key_length: int          # Bits transmitted
    sifted_key_length: int       # Bits after sifting
    final_key_length: int        # Bits after processing
    qber: float                  # Quantum bit error rate
    execution_time: float        # Runtime in seconds
    metadata: dict               # Protocol-specific data
```

### Example: Implementing Six-State Protocol

```python
class SixStateProtocol(BaseQKDProtocol):
    """
    Six-state protocol with 3 bases for enhanced security.
    Bases: Z (|0⟩,|1⟩), X (|+⟩,|-⟩), Y (|+i⟩,|-i⟩)
    """
    
    def __init__(self, key_length: int, seed: int = None):
        super().__init__(key_length, seed)
        self.num_bases = 3
    
    def prepare_state(self, bit: int, basis: int) -> QuantumCircuit:
        qc = QuantumCircuit(1, 1)
        
        if bit == 1:
            qc.x(0)
        
        if basis == 0:  # Z basis
            pass
        elif basis == 1:  # X basis
            qc.h(0)
        elif basis == 2:  # Y basis
            qc.h(0)
            qc.s(0)
        
        return qc
    
    def sift_keys(self, alice_bases, bob_bases, measurements):
        matching = alice_bases == bob_bases
        return measurements[matching], matching
```

---

## Adding New Attacks {#attacks}

### Base Attack Class

```python
from src.attacks import BaseAttack

class MyAttack(BaseAttack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def attack_qubit(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Apply attack to a single qubit."""
        pass
    
    def get_results(self) -> AttackResult:
        """Return attack metrics."""
        pass
```

### Example: Beam Splitting Attack

```python
class BeamSplittingAttack(BaseAttack):
    """
    Eve splits off a fraction of each pulse for later measurement.
    """
    
    def __init__(self, splitting_ratio: float = 0.1, seed: int = None):
        super().__init__(seed=seed)
        self.splitting_ratio = splitting_ratio
        self.stored_qubits = []
    
    def attack_qubit(self, circuit: QuantumCircuit) -> QuantumCircuit:
        # In simulation, we model this as weak measurement
        # Store probability of interception
        if self.rng.random() < self.splitting_ratio:
            self.stored_qubits.append(circuit.copy())
        return circuit  # Original continues to Bob
    
    def measure_stored(self, basis_announcement):
        """Measure stored qubits after basis reveal."""
        eve_bits = []
        for qc, basis in zip(self.stored_qubits, basis_announcement):
            # Measure in announced basis
            eve_bits.append(self.measure(qc, basis))
        return eve_bits
```

---

## Noise Model Development {#noise}

### Creating Custom Noise Models

Noise models use Qiskit Aer's noise framework:

```python
from qiskit_aer.noise import NoiseModel, depolarizing_error

class CustomChannel:
    def __init__(self, parameters):
        self.parameters = parameters
    
    def get_noise_model(self) -> NoiseModel:
        noise_model = NoiseModel()
        
        # Define errors
        error = depolarizing_error(self.parameters['p'])
        
        # Attach to gates
        noise_model.add_all_qubit_quantum_error(error, ['x', 'h'])
        
        return noise_model
```

### Realistic Fiber Model Example

```python
class FiberWithTurbulence(RealisticFiberChannel):
    """Extended fiber model with atmospheric effects for free-space link."""
    
    def __init__(self, length_km, turbulence_strength='moderate'):
        super().__init__(length_km)
        self.turbulence = {
            'weak': 0.01,
            'moderate': 0.05,
            'strong': 0.15
        }[turbulence_strength]
    
    def get_noise_model(self):
        base_model = super().get_noise_model()
        
        # Add turbulence-induced phase noise
        phase_error = phase_damping_error(self.turbulence)
        base_model.add_all_qubit_quantum_error(phase_error, ['id'])
        
        return base_model
```

---

## Analysis Tools {#analysis}

### Security Metrics

```python
from src.analysis import SecurityMetrics

# Create metrics object
metrics = SecurityMetrics(alice_key, bob_key, raw_length=1000)

# Access metrics
print(f"QBER: {metrics.qber}")
print(f"Key Rate: {metrics.secret_key_rate()}")
print(f"Secure: {metrics.is_secure()}")
print(f"I(A:B): {metrics.mutual_information_ab()}")
```

### Statistical Testing

```python
from src.analysis import RandomnessTests

tests = RandomnessTests()
results = tests.run_all_tests(final_key)

for result in results:
    print(f"{result.test_name}: p={result.p_value:.4f} - "
          f"{'PASS' if result.passed else 'FAIL'}")
```

### Visualization

```python
from src.analysis import QKDVisualizer

viz = QKDVisualizer()

# Security dashboard
viz.create_security_dashboard(
    qber=0.03,
    key_rate=0.85,
    eve_info=0.02
)

# Protocol comparison
viz.plot_protocol_comparison(results_dict)
```

---

## Experimental Workflow {#experiments}

### Standard Experiment Structure

```python
#!/usr/bin/env python3
"""Experiment: [Title]"""

import sys
sys.path.insert(0, '..')

from src.protocols import BB84Protocol
from src.analysis import SecurityMetrics

def run_experiment():
    """Main experiment function."""
    # 1. Setup parameters
    params = {...}
    
    # 2. Run trials
    results = []
    for trial in range(num_trials):
        result = run_single_trial(params)
        results.append(result)
    
    # 3. Analyze
    analysis = analyze_results(results)
    
    # 4. Visualize
    create_figures(analysis)
    
    # 5. Save
    save_results(results, analysis)

if __name__ == "__main__":
    run_experiment()
```

### Data Management

```python
import json
import pandas as pd

# Save results
def save_results(results, filename):
    df = pd.DataFrame(results)
    df.to_csv(f'results/data/{filename}.csv', index=False)
    
    with open(f'results/data/{filename}.json', 'w') as f:
        json.dump(results, f, indent=2)

# Load results
def load_results(filename):
    return pd.read_csv(f'results/data/{filename}.csv')
```

---

## Best Practices {#best-practices}

### Code Style

1. **Type Hints**: Always use type hints
   ```python
   def process_key(key: np.ndarray, method: str = 'cascade') -> np.ndarray:
   ```

2. **Docstrings**: Use Google-style docstrings
   ```python
   def function(arg1: int, arg2: str) -> bool:
       """Short description.
       
       Longer description if needed.
       
       Args:
           arg1: Description of arg1.
           arg2: Description of arg2.
           
       Returns:
           Description of return value.
           
       Raises:
           ValueError: If arg1 is negative.
       """
   ```

3. **Constants**: Use UPPER_CASE for constants
   ```python
   SECURITY_THRESHOLD = 0.11
   DEFAULT_KEY_LENGTH = 256
   ```

### Testing

1. **Write tests first** (TDD when possible)
2. **Test edge cases**: Empty keys, single bits, maximum values
3. **Use fixtures** for common setups
4. **Mock randomness** for reproducibility

```python
@pytest.fixture
def sample_protocol():
    return BB84Protocol(key_length=100, seed=42)

def test_with_fixture(sample_protocol):
    result = sample_protocol.run()
    assert result.qber < 0.01
```

### Version Control

1. **Commit messages**: Use conventional commits
   ```
   feat: add six-state protocol implementation
   fix: correct QBER calculation for edge cases
   docs: update protocol theory documentation
   test: add tests for SARG04 protocol
   ```

2. **Branches**: Use feature branches
   ```
   feature/six-state-protocol
   bugfix/qber-calculation
   experiment/noise-comparison
   ```

### Documentation

1. Keep README up to date
2. Document experiments in EXPERIMENT_LOG.md
3. Add comments for non-obvious code
4. Include references for algorithms

---

## Troubleshooting

### Common Issues

1. **Qiskit version mismatch**
   ```bash
   pip install qiskit>=1.0.0 qiskit-aer>=0.14.0
   ```

2. **Memory issues with large simulations**
   - Reduce key_length
   - Use batched execution
   - Enable garbage collection

3. **Slow simulations**
   - Use statevector simulator for no-noise cases
   - Reduce number of shots
   - Profile code for bottlenecks

---

*Implementation Guide - Quantum Cryptography Project*
