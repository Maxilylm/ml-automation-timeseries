# /ts-evaluate

Evaluate forecast accuracy with standard time series metrics.

## Usage

```
/ts-evaluate <forecast_file> --actual <actual_file> [--metrics mape,rmse,smape,coverage] [--date-col <col>] [--forecast-col <col>] [--actual-col <col>]
```

- `forecast_file`: CSV with forecast values (date, forecast, lower_95, upper_95)
- `--actual`: CSV with actual values for the forecast period
- `--metrics`: comma-separated metrics (default: all)
- `--date-col`: datetime column name (default: auto-detect)
- `--forecast-col`: forecast values column (default: `forecast`)
- `--actual-col`: actual values column (default: auto-detect first numeric)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `timeseries_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/timeseries_utils.py`
3. Verify both forecast and actual files exist and are readable
4. Verify date ranges overlap

### Stage 1: Data Loading and Alignment

1. Load forecast file and actual file
2. Parse dates and set as index
3. Align on common dates (inner join)
4. Report: forecast periods, actual periods, overlap count, any gaps

### Stage 2: Point Forecast Metrics

1. **MAPE** (Mean Absolute Percentage Error):
   - `mean(|actual - forecast| / |actual|) * 100`
   - Exclude zeros in actual (report count excluded)
2. **RMSE** (Root Mean Squared Error):
   - `sqrt(mean((actual - forecast)^2))`
3. **MAE** (Mean Absolute Error):
   - `mean(|actual - forecast|)`
4. **SMAPE** (Symmetric Mean Absolute Percentage Error):
   - `mean(2 * |actual - forecast| / (|actual| + |forecast|)) * 100`
5. **MASE** (Mean Absolute Scaled Error):
   - Scale by naive forecast error (one-step seasonal naive)
6. **Bias** (Mean Error):
   - `mean(forecast - actual)` — positive = over-forecast, negative = under-forecast
7. Report: all metrics in summary table

### Stage 3: Interval Forecast Metrics (if prediction intervals available)

1. **Coverage** — percentage of actuals within prediction interval:
   - `mean(lower_95 <= actual <= upper_95) * 100`
   - Target: 95% for 95% intervals
2. **Interval Width** — average width of prediction interval:
   - `mean(upper_95 - lower_95)`
3. **Winkler Score** — penalizes wide intervals and misses:
   - Combines interval width with penalty for actuals outside interval
4. Report: coverage, average width, Winkler score

### Stage 4: Error Analysis

1. Compute error at each time step: `actual - forecast`
2. Analyze error patterns:
   - Autocorrelation of errors (should be white noise)
   - Error by day-of-week / month (systematic bias)
   - Error magnitude over forecast horizon (does accuracy degrade?)
3. Identify worst predictions (top 10 by absolute error)
4. Report: error distribution, systematic patterns, worst predictions

### Stage 5: Report

```python
from ml_utils import save_agent_report
save_agent_report("forecaster", {
    "status": "completed",
    "evaluation_type": "forecast_accuracy",
    "periods_evaluated": n_periods,
    "metrics": {
        "mape": mape,
        "rmse": rmse,
        "mae": mae,
        "smape": smape,
        "mase": mase,
        "bias": bias
    },
    "interval_metrics": {
        "coverage": coverage,
        "avg_width": avg_width,
        "winkler_score": winkler_score
    },
    "error_analysis": {
        "error_autocorrelation": error_acf_significant,
        "systematic_bias": systematic_patterns,
        "worst_predictions": worst_predictions[:10]
    },
    "recommendations": recommendations
})
```

Print: metrics summary table, interval metrics, error analysis findings, improvement recommendations.
