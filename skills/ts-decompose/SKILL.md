---
name: ts-decompose
description: "Decompose time series into trend, seasonal, and residual components using STL, classical, or MSTL methods."
aliases: [decompose, time series decomposition, seasonal decomposition, stl]
extends: spark
user_invocable: true
---

# Time Series Decompose

Decompose a time series into trend, seasonal, and residual components. Supports STL (robust to outliers), classical (additive/multiplicative), and MSTL (multiple seasonalities). Auto-detects seasonal period and model type. Analyzes each component: trend direction and changepoints, seasonal amplitude and stability, and residual white noise properties.

## When to Use

- Understanding the underlying structure of a time series before forecasting
- Isolating trend from seasonality to analyze each independently
- Detecting multiple overlapping seasonal patterns (e.g., daily + weekly)
- Deciding between additive and multiplicative modeling approaches

## Workflow

1. **Env Check** - Verify required libraries (statsmodels, matplotlib); install missing packages.
2. **Data Loading** - Read the dataset, parse dates, sort chronologically, detect frequency, and handle missing values via interpolation.
3. **Model Selection** - If `--model auto`, test both additive and multiplicative fits; select the one with smaller residual variance.
4. **Decomposition** - Apply the selected `--method` (STL, classical, or MSTL) with the chosen model type and detected/specified seasonal period.
5. **Component Analysis** - Analyze trend (direction, changepoints), seasonal (amplitude stability across cycles), and residuals (normality, autocorrelation, white noise test).
6. **Visualization and Report** - Plot the original series and each component; save decomposition results and component statistics as report JSON.

## Report Bus Integration

```python
from ml_utils import save_agent_report
save_agent_report("timeseries-analyst", {
    "status": "completed",
    "findings": {
        "method": "stl", "model": "additive", "seasonal_period": 7,
        "trend_direction": "upward",
        "seasonal_amplitude_stable": True,
        "residual_white_noise": True,
    },
    "recommendations": [
        {"text": "Additive model with period=7 is appropriate for forecasting", "target_agent": "forecaster"}
    ],
    "artifacts": [".claude/ts_decompose_report.json"]
})
```

## Full Specification

Usage: `/ts-decompose <data_path> [--method stl|classical|mstl] [--model additive|multiplicative|auto]`

See `commands/ts-decompose.md` for the complete workflow.
