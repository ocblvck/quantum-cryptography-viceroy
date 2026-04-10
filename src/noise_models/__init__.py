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

import numpy as np

class FiberParameters:
    def __init__(self, length_km, attenuation_db_per_km=0.2, pmd_coefficient=0.1):
        self.length_km = length_km
        self.attenuation_db_per_km = attenuation_db_per_km
        # PMD (Polarization Mode Dispersion) coefficient in ps/sqrt(km)
        self.pmd_coefficient = pmd_coefficient

    def total_loss_db(self):
        return self.length_km * self.attenuation_db_per_km

    def transmission(self):
        return 10**(-self.total_loss_db() / 10)

class DetectorParameters:
    def __init__(self, efficiency=0.15, dark_count_rate=1e-6):
        self.efficiency = efficiency
        self.dark_count_rate = dark_count_rate