---
name: ts-backtest
description: "Backtesting with expanding or sliding window temporal cross-validation. Multi-model comparison with Diebold-Mariano tests."
aliases: [backtest, temporal cross-validation, time series cv, ts cv, walk-forward]
extends: spark
user_invocable: true
---

# Time Series Backtest

Run rigorous backtesting on time series forecasting models using expanding or sliding window cross-validation. Trains and evaluates across multiple folds, computes per-fold and aggregate metrics (MAPE, RMSE, SMAPE, coverage), analyzes accuracy degradation over forecast horizon, and performs statistical model comparison (Diebold-Mariano test) when using auto mode.

## When to Use

- Validating a forecasting model with realistic temporal train/test splits
- Comparing multiple model families under identical CV conditions
- Measuring forecast stability across different time windows
- Producing statistically grounded model rankings with Diebold-Mariano tests

## Workflow

1. **Env Check** - Verify required libraries (prophet, statsmodels, pmdarima, scikit-learn as needed); install missing packages.
2. **Data Preparation** - Load data, parse dates, sort chronologically, detect frequency, and validate that sufficient history exists for the requested folds and horizon.
3. **Fold Generation** - Create `--folds` temporal splits using the selected `--strategy` (expanding or sliding window).
4. **Per-Fold Training and Evaluation** - For each fold, fit the selected `--model` (or all candidates in `auto` mode), generate forecasts, and compute per-fold metrics.
5. **Aggregate Metrics** - Compute mean, median, and standard deviation of metrics across folds; flag folds with anomalous performance.
6. **Multi-Model Comparison** (auto mode) - Rank models by aggregate metrics, run pairwise Diebold-Mariano tests, and report statistical significance of differences.
7. **Horizon Degradation Analysis** - Measure how accuracy degrades as forecast step increases; recommend a reliable horizon cutoff.
8. **Summary Report** - Save per-fold results, model rankings, and visualizations as report JSON and plots.

## Report Bus Integration

```python
from ml_utils import save_agent_report
save_agent_report("backtester", {
    "status": "completed",
    "findings": {
        "strategy": "expanding", "folds": 5,
        "models_tested": ["prophet", "arima", "ets"],
        "best_model": "prophet",
        "aggregate_metrics": {"mape": 4.8, "rmse": 11.7, "smape": 4.5},
        "dm_test_significant": True,
    },
    "recommendations": [
        {"text": "Prophet outperforms ARIMA (p<0.05); use for production forecast", "target_agent": "forecaster"}
    ],
    "artifacts": [".claude/ts_backtest_report.json"]
})
```

## Full Specification

Usage: `/ts-backtest <data_path> [--model prophet|arima|ets|auto] [--strategy expanding|sliding] [--folds 5]`

See `commands/ts-backtest.md` for the complete workflow.
