# /ts-decompose

Decompose time series into trend, seasonal, and residual components.

## Usage

```
/ts-decompose <data_path> [--method stl|classical|mstl] [--model additive|multiplicative|auto] [--period <int>] [--date-col <col>] [--value-col <col>]
```

- `data_path`: path to CSV/Parquet file with time series data
- `--method`: decomposition method (default: stl)
- `--model`: additive or multiplicative (default: auto-detect)
- `--period`: seasonal period override (auto-detected if not specified)
- `--date-col`: datetime column name (auto-detected if not specified)
- `--value-col`: value column name (auto-detected if not specified)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `timeseries_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/timeseries_utils.py`
3. Verify data file exists and is readable
4. Check required packages: `statsmodels`

### Stage 1: Data Loading

1. Load and parse data (detect date and value columns)
2. Set datetime index, sort chronologically
3. Detect or validate frequency
4. Handle missing values (interpolation)
5. Report: row count, date range, frequency, value range

### Stage 2: Model Type Selection (if --model auto)

1. Compute coefficient of variation across seasonal periods
2. If variation increases with level: recommend multiplicative
3. If variation is constant: recommend additive
4. Check for zero or negative values (multiplicative requires all positive)
5. Report: selected model type with rationale

### Stage 3: Period Detection (if --period not specified)

1. Compute autocorrelation to find dominant lag
2. Compute periodogram for spectral analysis
3. Test standard periods: 7, 12, 24, 52, 365
4. Select period with strongest signal
5. Report: detected period with confidence

### Stage 4: Decomposition

Based on `--method`:

**STL (Seasonal and Trend decomposition using Loess):**
1. Fit STL with detected period
2. Configure robustness weights (robust to outliers)
3. Extract: trend, seasonal, residual
4. Compute seasonal strength and trend strength

**Classical Decomposition:**
1. Compute moving average for trend (window = period)
2. Detrend: subtract (additive) or divide (multiplicative)
3. Average detrended values per season position for seasonal component
4. Compute residual: observed - trend - seasonal (additive) or observed / (trend * seasonal) (multiplicative)

**MSTL (Multiple Seasonal-Trend decomposition using Loess):**
1. Detect multiple seasonal periods
2. Iteratively decompose with each period
3. Extract: trend, seasonal_1, seasonal_2, ..., residual
4. Report component strengths for each season

### Stage 5: Component Analysis

1. **Trend analysis:**
   - Direction: increasing, decreasing, or flat
   - Rate of change (slope)
   - Trend changepoints
2. **Seasonal analysis:**
   - Peak and trough positions within cycle
   - Seasonal amplitude (max - min)
   - Stability of seasonal pattern over time
3. **Residual analysis:**
   - Distribution (mean, std, skewness, kurtosis)
   - Autocorrelation of residuals (should be white noise)
   - Normality test (Shapiro-Wilk)
4. Report: component summaries

### Stage 6: Report

```python
from ml_utils import save_agent_report
save_agent_report("timeseries-analyst", {
    "status": "completed",
    "method": method,
    "model_type": model_type,
    "period": period,
    "trend": {
        "direction": direction,
        "slope": slope,
        "changepoints": changepoints
    },
    "seasonal": {
        "period": period,
        "strength": seasonal_strength,
        "amplitude": amplitude,
        "peak_position": peak_pos,
        "trough_position": trough_pos
    },
    "residual": {
        "mean": res_mean,
        "std": res_std,
        "is_white_noise": is_white_noise,
        "normality_pvalue": normality_pvalue
    },
    "recommendations": recommendations
})
```

Save decomposition results to `reports/decomposition.csv` with columns: date, observed, trend, seasonal, residual.
Print: component summary table, seasonal pattern description, residual diagnostics.
