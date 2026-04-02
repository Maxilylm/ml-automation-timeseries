---
name: ts-analyze
description: "Comprehensive time series EDA: decomposition, stationarity tests (ADF, KPSS), ACF/PACF analysis, and seasonality detection with spectral methods."
aliases: [time series eda, time series analysis, ts eda, temporal analysis]
extends: ml-automation
user_invocable: true
---

# Time Series Analyze

Run comprehensive exploratory analysis on time series data. Performs STL decomposition, stationarity testing (ADF, KPSS), ACF/PACF computation with significant lag detection, seasonal period identification via periodogram analysis, and missing value gap analysis. Produces a full diagnostic summary with recommended forecasting approaches.

## When to Use

- Exploring a new time series dataset before forecasting or modeling
- Diagnosing stationarity issues, trend behavior, or seasonal patterns
- Identifying the dominant frequency and appropriate differencing order
- Generating a diagnostic summary to guide downstream model selection

## Workflow

1. **Env Check** - Verify required libraries (statsmodels, pandas, matplotlib) are available; install missing packages.
2. **Data Loading** - Read the dataset, auto-detect or use the specified `--date-col` and `--value-col`, parse dates, sort chronologically, and report basic shape/frequency.
3. **Decomposition** - Apply STL decomposition to extract trend, seasonal, and residual components; plot each component.
4. **Stationarity Testing** - Run ADF and KPSS tests, report test statistics and p-values, recommend differencing order (`d`).
5. **ACF/PACF Analysis** - Compute autocorrelation and partial autocorrelation up to 40 lags, identify significant lags, and suggest candidate ARIMA orders.
6. **Seasonality Detection** - Use periodogram / spectral analysis to detect dominant seasonal periods and their strength.
7. **Summary Report** - Consolidate findings into a structured diagnostic with modeling recommendations.

## Report Bus Integration

```python
from ml_utils import save_agent_report
save_agent_report("timeseries-analyst", {
    "status": "completed",
    "findings": {
        "rows": 1000, "frequency": "D",
        "is_stationary": False, "recommended_d": 1,
        "seasonal_periods": [7, 365],
        "significant_acf_lags": [1, 7, 14],
    },
    "recommendations": [
        {"text": "Apply first differencing before ARIMA fitting", "target_agent": "forecaster"}
    ],
    "artifacts": [".claude/ts_analyze_report.json"]
})
```

## Full Specification

Usage: `/ts-analyze <data_path> [--date-col <col>] [--value-col <col>] [--freq auto|D|W|M|H]`

Delegated agent: `timeseries-analyst`

See `commands/ts-analyze.md` for the complete workflow.
