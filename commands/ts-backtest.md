# /ts-backtest

Backtesting with expanding or sliding window temporal cross-validation.

## Usage

```
/ts-backtest <data_path> [--model prophet|arima|ets|auto] [--horizon 30] [--folds 5] [--strategy expanding|sliding] [--window-size <int>] [--date-col <col>] [--value-col <col>]
```

- `data_path`: path to CSV/Parquet file with time series data
- `--model`: forecasting model (default: auto)
- `--horizon`: forecast horizon per fold (default: 30)
- `--folds`: number of CV folds (default: 5)
- `--strategy`: cross-validation strategy (default: expanding)
- `--window-size`: training window size for sliding strategy (default: 3x horizon)
- `--date-col`: datetime column name (auto-detected if not specified)
- `--value-col`: value column name (auto-detected if not specified)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `timeseries_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/timeseries_utils.py`
3. Verify data file exists and is readable
4. Check sufficient data: need at least `--window-size + --folds * --horizon` data points

### Stage 1: Data Preparation

1. Load and parse data (detect date and value columns)
2. Handle missing values
3. Validate data length is sufficient for requested folds and horizon
4. Report: data shape, requested configuration, feasibility check

### Stage 2: Cross-Validation Split Generation

Based on `--strategy`:

**Expanding Window:**
1. Compute cutoff dates: space `--folds` cutoffs evenly across the last 50% of data
2. For each fold:
   - Training: all data from start to cutoff
   - Test: `--horizon` periods after cutoff
3. Verify no data leakage between train and test

**Sliding Window:**
1. Compute cutoff dates (same as expanding)
2. For each fold:
   - Training: `--window-size` periods ending at cutoff
   - Test: `--horizon` periods after cutoff
3. Verify minimum training size

Report: fold table (training start, training end, test start, test end, training size)

### Stage 3: Model Training and Forecasting per Fold

For each fold (1 to `--folds`):

1. Extract training and test partitions
2. Train model on training partition:
   - Prophet: fit with auto seasonality
   - ARIMA: run auto_arima on training data
   - ETS: select and fit best exponential smoothing model
   - Auto: train all three, pick best per-fold or use same model across folds
3. Generate forecast for `--horizon` periods
4. Compute forecast metrics against test partition:
   - MAPE, RMSE, SMAPE, MAE, coverage (if intervals available)
5. Store: fold number, metrics, forecast values, actual values
6. Report progress: fold N/total complete

### Stage 4: Aggregate Results

1. Compute aggregate metrics across folds:
   - Mean and std for each metric (MAPE, RMSE, SMAPE, MAE, coverage)
   - Median metrics (robust to single bad fold)
2. Analyze metric stability:
   - Coefficient of variation across folds
   - Identify worst fold and investigate
3. Analyze accuracy degradation over horizon:
   - Compute metrics by forecast step (step 1, step 2, ..., step H)
   - Does error grow with horizon? Linear or exponential degradation?
4. Report: aggregate table, stability analysis, horizon degradation

### Stage 5: Model Comparison (if --model auto)

1. Compile per-model results across all folds:
   - Prophet: mean MAPE, RMSE across folds
   - ARIMA: mean MAPE, RMSE across folds
   - ETS: mean MAPE, RMSE across folds
2. Statistical comparison:
   - Paired test (Diebold-Mariano) between best two models
   - Check if difference is statistically significant
3. Select winner based on mean MAPE (with tie-breaking by RMSE)
4. Report: model comparison table, statistical test results, winner

### Stage 6: Report

```python
from ml_utils import save_agent_report
save_agent_report("forecaster", {
    "status": "completed",
    "backtest_type": strategy,
    "folds": n_folds,
    "horizon": horizon,
    "model": best_model_name,
    "per_fold_results": [
        {"fold": i, "train_size": n, "mape": m, "rmse": r, "smape": s, "coverage": c}
        for each fold
    ],
    "aggregate_metrics": {
        "mean_mape": mean_mape,
        "std_mape": std_mape,
        "mean_rmse": mean_rmse,
        "std_rmse": std_rmse,
        "mean_coverage": mean_coverage
    },
    "horizon_degradation": horizon_metrics,
    "model_comparison": model_comparison,
    "recommendations": recommendations
})
```

Save backtest results to `reports/backtest_results.csv` with columns: fold, date, actual, forecast, lower_95, upper_95.
Print: per-fold metrics table, aggregate metrics, model comparison (if auto), horizon degradation summary.
