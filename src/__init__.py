"""
Quantum Cryptography Viceroy - A comprehensive QKD protocol suite.

This package provides implementations of various Quantum Key Distribution (QKD)
protocols, attack simulations, noise models, and security analysis tools.
"""

__version__ = "0.1.0"
__author__ = "Quantum Cryptography Research Team"

from src.protocols import BB84Protocol, B92Protocol, E91Protocol, SARG04Protocol
from src.analysis import SecurityMetrics

__all__ = [
    "BB84Protocol",
    "B92Protocol", 
    "E91Protocol",
    "SARG04Protocol",
    "SecurityMetrics",
]
