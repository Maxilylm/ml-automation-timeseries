---
name: ts-backtest
description: "Backtesting with expanding or sliding window temporal cross-validation. Multi-model comparison with Diebold-Mariano tests."
aliases: [backtest, temporal cross-validation, time series cv, ts cv, walk-forward]
extends: ml-automation
user_invocable: true
---

# Time Series Backtest

Run rigorous backtesting on time series forecasting models using expanding or sliding window cross-validation. Trains and evaluates across multiple folds, computes per-fold and aggregate metrics (MAPE, RMSE, SMAPE, coverage), analyzes accuracy degradation over forecast horizon, and performs statistical model comparison (Diebold-Mariano test) when using auto mode.

## Full Specification

See `commands/ts-backtest.md` for the complete workflow.
