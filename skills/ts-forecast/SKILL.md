---
name: ts-forecast
description: "Train forecasting models (Prophet, ARIMA, ETS, N-BEATS, TFT) with temporal cross-validation and automatic model selection."
aliases: [forecast, time series forecast, predict time series, ts predict]
extends: ml-automation
user_invocable: true
---

# Time Series Forecast

Train and evaluate forecasting models on time series data. Supports Prophet, ARIMA/SARIMA, exponential smoothing, N-BEATS, and Temporal Fusion Transformer. Runs temporal cross-validation with expanding or sliding windows, computes MAPE/RMSE/SMAPE/coverage per fold, and selects the best model automatically when using auto mode.

## Full Specification

See `commands/ts-forecast.md` for the complete workflow.
