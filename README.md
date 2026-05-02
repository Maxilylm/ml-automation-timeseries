# spark-timeseries

Time series analysis and forecasting extension for [ml-automation](https://github.com/BLEND360/ml-automation-core).

## Prerequisites

- [ml-automation](https://github.com/BLEND360/ml-automation-core) core plugin (>= v1.8.0)
- Claude Code CLI
- Time series libraries as needed: `statsmodels`, `prophet`, `scikit-learn`, `neuralforecast`

## Installation

```bash
claude plugin add /path/to/spark-timeseries
```

## What's Included

### Agents

| Agent | Purpose |
|---|---|
| `timeseries-analyst` | Pattern analysis, seasonality, stationarity, ACF/PACF, decomposition |
| `forecaster` | Prophet, ARIMA, ETS, N-BEATS, TFT with temporal cross-validation |
| `anomaly-detector` | Statistical and ML anomaly detection, changepoint detection |

### Commands

| Command | Purpose |
|---|---|
| `/ts-analyze` | Comprehensive time series EDA |
| `/ts-forecast` | Train forecasting models with temporal CV |
| `/ts-anomaly` | Detect anomalies in time series |
| `/ts-decompose` | Decompose into trend, seasonal, residual |
| `/ts-evaluate` | Evaluate forecast accuracy (MAPE, RMSE, SMAPE, coverage) |
| `/ts-backtest` | Backtesting with expanding/sliding window CV |

## Getting Started

```bash
# Analyze time series patterns
/ts-analyze sales_data.csv --date-col date --value-col revenue

# Train a forecasting model
/ts-forecast sales_data.csv --model prophet --horizon 30 --cv-folds 5

# Detect anomalies
/ts-anomaly sensor_data.csv --method auto --threshold 3.0

# Decompose into components
/ts-decompose monthly_data.csv --method stl --model auto

# Evaluate forecast accuracy
/ts-evaluate forecasts/output.csv --actual actuals.csv

# Run backtesting
/ts-backtest sales_data.csv --model auto --horizon 30 --folds 5 --strategy expanding
```

## How It Integrates

When installed alongside the core plugin:

1. **Automatic routing** -- Tasks mentioning time series, forecasting, seasonality, or temporal analysis are routed to time series agents
2. **Core workflow hooks** -- When running `/team-coldstart`:
   - `timeseries-analyst` fires at `after-eda` to detect and analyze temporal patterns
   - `forecaster` fires at `after-training` to evaluate forecasting model quality
3. **Core agent reuse** -- Commands use eda-analyst, developer, ml-theory-advisor from core

## License

MIT
