"""
Quantum Noise Models.

This module provides various noise models for simulating realistic
quantum channels in QKD implementations.
"""

from src.noise_models.depolarizing import DepolarizingChannel
from src.noise_models.amplitude_damping import AmplitudeDampingChannel
from src.noise_models.phase_damping import PhaseDampingChannel
from src.noise_models.realistic_fiber import RealisticFiberChannel

__all__ = [
    "DepolarizingChannel",
    "AmplitudeDampingChannel", 
    "PhaseDampingChannel",
    "RealisticFiberChannel",
]
