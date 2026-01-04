"""
Analysis Module for QKD Protocol Evaluation.

This module provides tools for analyzing QKD protocol performance,
computing security metrics, and generating visualizations.
"""

from src.analysis.security_metrics import SecurityMetrics, compute_secret_key_rate
from src.analysis.statistical_tests import RandomnessTests, CorrelationTests
from src.analysis.visualization import QKDVisualizer

__all__ = [
    "SecurityMetrics",
    "compute_secret_key_rate",
    "RandomnessTests",
    "CorrelationTests",
    "QKDVisualizer",
]
