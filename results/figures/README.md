# Results Figures Directory

This directory stores generated figures from experiments.

## Files

- `exp01_bb84_basic.png`: BB84 basic experiment figures
- `exp02_protocol_comparison.png`: Protocol comparison charts
- `exp03_attack_analysis.png`: Attack analysis visualizations
- `exp04_noise_resilience.png`: Noise resilience plots
- `exp05_full_simulation.png`: Full simulation dashboard

## For Publications

High-resolution figures for publications can be generated using:

```python
from src.analysis import QKDVisualizer

viz = QKDVisualizer()
viz.set_publication_mode()  # High DPI, larger fonts
```
