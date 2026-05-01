# spark-timeseries — Cortex Code Extension

Time series analysis and forecasting. Prophet, ARIMA, neural forecasting, seasonality decomposition, temporal cross-validation, and anomaly detection. Requires spark-core installed.

## Available Agents

| Agent | When to use |
|---|---|
| `timeseries-analyst` | User wants to explore time series data, check stationarity, decompose seasonality/trend, or understand temporal patterns |
| `forecaster` | User wants to build a forecast model using Prophet, ARIMA, or neural approaches, or run temporal cross-validation |
| `anomaly-detector` | User wants to detect anomalies or outliers in time series data |

## Available Skills

| Skill | Trigger |
|---|---|
| `/ts-analyze` | "analyze this time series", "check stationarity", "explore temporal data", "time series EDA" |
| `/ts-forecast` | "forecast this series", "predict future values", "build a Prophet model", "ARIMA forecast" |
| `/ts-anomaly` | "detect anomalies", "find outliers in time series", "flag unusual spikes" |
| `/ts-decompose` | "decompose seasonality", "extract trend", "seasonal decomposition" |
| `/ts-evaluate` | "evaluate forecast accuracy", "MAPE, RMSE for my forecast", "backtest results" |
| `/ts-backtest` | "backtest the forecast", "walk-forward validation", "temporal cross-validation" |

## Routing

- Time series EDA, stationarity, decomposition → `timeseries-analyst`
- Forecasting models → `forecaster`
- Anomaly / outlier detection → `anomaly-detector`
- Fallback → spark-core orchestrator
