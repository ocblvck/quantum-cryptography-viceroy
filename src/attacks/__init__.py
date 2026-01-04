"""
Attack Simulation Module.

This module provides implementations of various quantum attacks
against QKD protocols for security analysis and testing.
"""

from src.attacks.base_attack import BaseAttack
from src.attacks.intercept_resend import InterceptResendAttack
from src.attacks.pns_attack import PNSAttack
from src.attacks.trojan_horse import TrojanHorseAttack

__all__ = [
    "BaseAttack",
    "InterceptResendAttack",
    "PNSAttack",
    "TrojanHorseAttack",
]
