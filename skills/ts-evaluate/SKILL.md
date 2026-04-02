---
name: ts-evaluate
description: "Evaluate forecast accuracy with MAPE, RMSE, SMAPE, coverage, and Winkler score. Includes error pattern analysis."
aliases: [forecast evaluation, forecast accuracy, ts metrics, forecast metrics]
extends: spark
user_invocable: true
---

# Time Series Evaluate

Evaluate forecast accuracy against actuals. Computes point forecast metrics (MAPE, RMSE, MAE, SMAPE, MASE, bias), interval forecast metrics (coverage, width, Winkler score), and error pattern analysis (autocorrelation, systematic bias by calendar, degradation over horizon). Identifies worst predictions and recommends improvements.

## When to Use

- Measuring how well a forecast performed against observed actuals
- Comparing metric profiles across multiple forecasting runs
- Diagnosing systematic error patterns (e.g., consistent under-prediction on weekends)
- Validating that prediction intervals achieve their nominal coverage

## Workflow

1. **Env Check** - Verify required libraries (pandas, numpy); install missing packages.
2. **Data Alignment** - Load forecast and actual files, align on date index, handle missing or mismatched timestamps, and report alignment summary.
3. **Point Metric Computation** - Calculate the requested `--metrics` (default: MAPE, RMSE, SMAPE, coverage) plus MAE, MASE, and bias.
4. **Interval Metric Computation** - If prediction intervals are present, compute coverage, average width, and Winkler score.
5. **Error Pattern Analysis** - Check residual autocorrelation, test for systematic bias by day-of-week or month, and measure accuracy degradation over the forecast horizon.
6. **Summary Report** - Rank worst-predicted periods, provide improvement recommendations, and save metrics report JSON.

## Report Bus Integration

```python
from ml_utils import save_agent_report
save_agent_report("forecast-evaluator", {
    "status": "completed",
    "findings": {
        "metrics": {"mape": 5.1, "rmse": 14.3, "smape": 4.9, "coverage": 91.5},
        "error_patterns": {"weekend_bias": -2.3, "horizon_degradation": True},
        "worst_periods": ["2024-12-25", "2024-01-01"],
    },
    "recommendations": [
        {"text": "Add holiday regressors to reduce weekend/holiday bias", "target_agent": "forecaster"}
    ],
    "artifacts": [".claude/ts_evaluate_report.json"]
})
```

## Full Specification

Usage: `/ts-evaluate <forecast_file> --actual <actual_file> [--metrics mape,rmse,smape,coverage]`

See `commands/ts-evaluate.md` for the complete workflow.
