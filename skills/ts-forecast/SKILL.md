---
name: ts-forecast
description: "Train forecasting models (Prophet, ARIMA, ETS, N-BEATS, TFT) with temporal cross-validation and automatic model selection."
aliases: [forecast, time series forecast, predict time series, ts predict]
extends: spark
user_invocable: true
---

# Time Series Forecast

Train and evaluate forecasting models on time series data. Supports Prophet, ARIMA/SARIMA, exponential smoothing, N-BEATS, and Temporal Fusion Transformer. Runs temporal cross-validation with expanding or sliding windows, computes MAPE/RMSE/SMAPE/coverage per fold, and selects the best model automatically when using auto mode.

## When to Use

- Building a production forecast for a univariate or multivariate time series
- Comparing multiple model families on the same dataset with temporal CV
- Generating point forecasts plus prediction intervals for a specified horizon
- Letting auto mode select the best model and hyperparameters

## Workflow

1. **Env Check** - Verify required libraries (prophet, statsmodels, pmdarima, or pytorch-forecasting as needed); install missing packages.
2. **Task Setup** - Load data, detect or apply `--date-col` / `--value-col`, set forecast `--horizon`, resolve model choice (`--model`), and configure CV folds.
3. **Model Training** - Fit the selected model(s) on the training portion; in `auto` mode, fit all candidate models in parallel.
4. **Temporal Cross-Validation** - Run `--cv-folds` expanding-window CV splits, compute per-fold metrics (MAPE, RMSE, SMAPE, coverage), and aggregate results.
5. **Model Selection** (auto mode) - Rank models by aggregate CV metrics, select the winner, and refit on the full training set.
6. **Forecast Generation** - Produce point forecasts and prediction intervals for the specified horizon; save forecast CSV.

## Report Bus Integration

```python
from ml_utils import save_agent_report
save_agent_report("forecaster", {
    "status": "completed",
    "findings": {
        "best_model": "prophet", "horizon": 30, "cv_folds": 5,
        "metrics": {"mape": 4.32, "rmse": 12.1, "smape": 4.15, "coverage": 93.2},
    },
    "recommendations": [
        {"text": "Evaluate residual autocorrelation with ts-evaluate", "target_agent": "forecast-evaluator"}
    ],
    "artifacts": [".claude/ts_forecast_report.json", "forecasts/forecast.csv"]
})
```

## Full Specification

Usage: `/ts-forecast <data_path> [--model prophet|arima|ets|nbeats|tft|auto] [--horizon 30] [--cv-folds 5]`

Delegated agent: `forecaster`

See `commands/ts-forecast.md` for the complete workflow.
