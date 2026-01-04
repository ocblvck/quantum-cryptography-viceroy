"""
Utility functions for QKD implementations.
"""

from src.utils.quantum_utils import (
    create_bell_state,
    measure_in_basis,
    apply_pauli_error,
    fidelity,
    trace_distance
)
from src.utils.classical_utils import (
    error_correction,
    privacy_amplification,
    cascade_protocol,
    universal_hash
)

__all__ = [
    # Quantum utilities
    "create_bell_state",
    "measure_in_basis",
    "apply_pauli_error",
    "fidelity",
    "trace_distance",
    # Classical utilities
    "error_correction",
    "privacy_amplification",
    "cascade_protocol",
    "universal_hash",
]
