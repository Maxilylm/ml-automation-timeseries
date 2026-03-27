# /ts-forecast

Train forecasting models with temporal cross-validation. Supports Prophet, ARIMA, exponential smoothing, and neural methods.

## Usage

```
/ts-forecast <data_path> [--model prophet|arima|ets|nbeats|tft|auto] [--horizon 30] [--date-col <col>] [--value-col <col>] [--cv-folds 5]
```

- `data_path`: path to CSV/Parquet file with time series data
- `--model`: forecasting model (default: auto — tries multiple and selects best)
- `--horizon`: forecast horizon in data frequency units (default: 30)
- `--date-col`: datetime column name (auto-detected if not specified)
- `--value-col`: value column name (auto-detected if not specified)
- `--cv-folds`: number of temporal cross-validation folds (default: 5)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `timeseries_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/timeseries_utils.py`
3. Verify data file exists and is readable
4. Check required packages based on `--model`:
   - prophet: `prophet`
   - arima: `statsmodels`
   - ets: `statsmodels`
   - nbeats: `neuralforecast` or `pytorch-forecasting`
   - tft: `pytorch-forecasting`

### Stage 1: Data Preparation

1. Load and parse data (detect date and value columns)
2. Handle missing values (forward fill or interpolation based on gap analysis)
3. Detect frequency and validate regularity
4. Split data: training set and holdout set (last `--horizon` points)
5. Report: data shape, frequency, train/test split sizes, basic stats

### Stage 2: Model Training

Based on `--model`:

**Prophet:**
1. Initialize Prophet with auto-detected seasonality
2. Add country holidays (if detectable from date range)
3. Fit on training data
4. Generate forecast for horizon
5. Extract components (trend, seasonality, holidays)

**ARIMA/SARIMA:**
1. Run auto_arima to select optimal (p,d,q)(P,D,Q,m) order
2. Fit SARIMAX model
3. Run residual diagnostics (Ljung-Box, normality)
4. Generate forecast with confidence intervals

**Exponential Smoothing (ETS):**
1. Test additive vs. multiplicative seasonality
2. Test damped vs. undamped trend
3. Select best model via AIC
4. Fit and forecast

**N-BEATS:**
1. Prepare data in neural forecast format
2. Configure N-BEATS architecture (generic or interpretable)
3. Train with early stopping
4. Generate probabilistic forecast

**TFT (Temporal Fusion Transformer):**
1. Prepare data with static and time-varying features
2. Configure TFT with attention and variable selection
3. Train with learning rate finder and early stopping
4. Generate forecast with prediction intervals

**Auto (default):**
1. Train Prophet, ARIMA, and ETS in parallel
2. Run temporal cross-validation on each
3. Select model with best average MAPE across folds

### Stage 3: Temporal Cross-Validation

1. Create `--cv-folds` expanding window splits:
   - Each fold uses all data up to cutoff as training
   - Forecast `--horizon` steps ahead
   - Cutoffs spaced evenly across the last 50% of data
2. For each fold:
   - Train model on training partition
   - Forecast horizon steps
   - Compute metrics: MAPE, RMSE, SMAPE, MAE
   - Compute coverage of 95% prediction intervals
3. Report: per-fold metrics table, aggregate metrics (mean and std)

### Stage 4: Holdout Evaluation

1. Generate forecast on holdout set using model trained on full training data
2. Compute metrics: MAPE, RMSE, SMAPE, MAE, coverage
3. Compute residual diagnostics:
   - Mean residual (bias check)
   - Residual autocorrelation (Ljung-Box)
   - Residual normality (Shapiro-Wilk)
4. Report: holdout metrics, residual diagnostics, forecast vs. actual comparison

### Stage 5: Forecast Generation

1. Retrain best model on full dataset (train + holdout)
2. Generate future forecast for `--horizon` periods
3. Save forecast to `forecasts/forecast_output.csv`:
   - Columns: date, forecast, lower_95, upper_95
4. Save model artifact to `models/`

### Stage 6: Report

```python
from ml_utils import save_agent_report
save_agent_report("forecaster", {
    "status": "completed",
    "model": model_name,
    "model_config": model_config,
    "cv_results": {
        "folds": cv_folds_detail,
        "mean_mape": mean_mape,
        "mean_rmse": mean_rmse,
        "mean_smape": mean_smape,
        "mean_coverage": mean_coverage
    },
    "holdout_metrics": holdout_metrics,
    "residual_diagnostics": residual_diagnostics,
    "forecast_file": "forecasts/forecast_output.csv",
    "model_file": model_path,
    "recommendations": recommendations
})
```

Print: model summary, cross-validation results table, holdout metrics, forecast preview (first 10 periods).
