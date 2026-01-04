# Results Data Directory

This directory stores experimental data in CSV and JSON formats.

## Files

- `exp01_*.csv/json`: BB84 basic experiment results
- `exp02_*.csv/json`: Protocol comparison data
- `exp03_*.csv/json`: Attack analysis results
- `exp04_*.csv/json`: Noise resilience data
- `exp05_*.csv/json`: Full simulation results

## Usage

```python
import pandas as pd

# Load experiment results
df = pd.read_csv('exp01_results.csv')
```
