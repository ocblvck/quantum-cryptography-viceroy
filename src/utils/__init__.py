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
import math

def estimate_final_key_length(sifted_length, qber, efficiency_factor=1.1):
    """
    Estimates the final secret key length after error correction and 
    privacy amplification using the Devetak-Winter bound logic.
    """
    if qber >= 0.11 or sifted_length == 0:
        return 0
        
    # Binary entropy function h(e)
    def h(e):
        if e == 0 or e >= 1: return 0
        return -e * math.log2(e) - (1 - e) * math.log2(1 - e)
    
    # Final length ≈ n * [1 - (1 + f)*h(e) - h(e)]
    # where f is the error correction efficiency factor
    leaked_bits = efficiency_factor * h(qber)
    privacy_bits = h(qber)
    
    final_length = int(sifted_length * (1 - leaked_bits - privacy_bits))
    return max(0, final_length)
