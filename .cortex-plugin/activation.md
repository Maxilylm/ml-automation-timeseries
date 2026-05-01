---
name: spark-timeseries
description: >
  Suggest enabling the spark-timeseries plugin when the user asks about time
  series analysis, forecasting, Prophet, ARIMA, SARIMA, neural forecasting,
  seasonality decomposition, temporal cross-validation, anomaly detection in
  time series, or trend analysis. Do NOT attempt to perform these tasks — just
  let the user know the plugin can be enabled.
---

# spark-timeseries (disabled plugin)

This plugin is installed but not enabled. It provides time series analysis
and forecasting automation within Cortex Code, integrated with the spark-core
workflow.

## Agents (3)

- **anomaly-detector** — Time series anomaly detection and alerting
- **forecaster** — Demand forecasting, Prophet, ARIMA, neural forecasting
- **timeseries-analyst** — Trend, seasonality, and stationarity analysis

## Skills (6)

- **ts-analyze** — Analyze time series data for trends, seasonality, and stationarity
- **ts-anomaly** — Detect anomalies in time series with statistical and ML methods
- **ts-backtest** — Run temporal cross-validation and backtesting
- **ts-decompose** — Decompose time series into trend, seasonal, and residual components
- **ts-evaluate** — Evaluate forecasting models with proper temporal metrics
- **ts-forecast** — Generate forecasts with Prophet, ARIMA, or neural models

## Requires

- spark-core plugin

## Enable

    cortex plugin enable spark-timeseries

Do NOT attempt to perform time series tasks through this plugin's skills while it is disabled.
