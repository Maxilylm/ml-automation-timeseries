# /ts-analyze

Comprehensive time series EDA: decomposition, stationarity tests, ACF/PACF, and seasonality detection.

## Usage

```
/ts-analyze <data_path> [--date-col <col>] [--value-col <col>] [--freq auto|D|W|M|H]
```

- `data_path`: path to CSV/Parquet file with time series data
- `--date-col`: name of datetime column (auto-detected if not specified)
- `--value-col`: name of value column (auto-detected if not specified)
- `--freq`: data frequency (default: auto-detect)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `timeseries_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/timeseries_utils.py`
3. Verify data file exists and is readable (CSV or Parquet)

### Stage 1: Data Loading and Validation

1. Load data from `data_path` (CSV or Parquet)
2. Auto-detect datetime column if `--date-col` not specified:
   - Check for columns with `datetime64` dtype
   - Check column names containing `date`, `time`, `timestamp`, `dt`
   - Try parsing string columns as dates
3. Auto-detect value column if `--value-col` not specified:
   - Select first numeric column that is not the date column
4. Parse dates, set as index, sort chronologically
5. Detect frequency if `--freq auto`:
   - Compute median gap between consecutive timestamps
   - Map to pandas frequency alias (H, D, W, M, Q, Y)
6. Report: row count, date range, frequency, missing values, basic stats (mean, std, min, max)

### Stage 2: Missing Value Analysis

1. Detect gaps in the time series (missing timestamps for the detected frequency)
2. Compute missing value percentage
3. Identify longest contiguous gap
4. Recommend imputation strategy:
   - < 5% missing: forward fill or linear interpolation
   - 5-20% missing: seasonal interpolation
   - > 20% missing: warn about data quality, suggest resampling to lower frequency
5. Report: gap count, gap lengths, imputation recommendation

### Stage 3: Decomposition

1. Perform STL decomposition (if sufficient data for seasonal period):
   - Extract trend, seasonal, and residual components
   - Compute seasonal strength: `1 - Var(residual) / Var(seasonal + residual)`
   - Compute trend strength: `1 - Var(residual) / Var(trend + residual)`
2. Perform classical decomposition (additive and multiplicative):
   - Compare residual variance to select best model type
3. Report: trend direction (increasing/decreasing/flat), seasonal period, seasonal strength, model type recommendation

### Stage 4: Stationarity Tests

1. Run ADF test (Augmented Dickey-Fuller):
   - Report: test statistic, p-value, critical values, decision
2. Run KPSS test:
   - Report: test statistic, p-value, critical values, decision
3. If non-stationary:
   - Test first difference
   - Test seasonal difference
   - Recommend differencing order (d, D for ARIMA)
4. Report: stationarity verdict, recommended differencing

### Stage 5: ACF/PACF Analysis

1. Compute ACF up to `min(40, len(series) // 2)` lags
2. Compute PACF up to `min(40, len(series) // 2)` lags
3. Identify significant lags (outside 95% confidence bands):
   - ACF significant lags suggest MA order or seasonal period
   - PACF significant lags suggest AR order
4. Report: significant ACF lags, significant PACF lags, suggested ARIMA orders (p, d, q)

### Stage 6: Seasonality Detection

1. Compute periodogram (spectral density):
   - Identify dominant frequencies
   - Convert to seasonal periods
2. Test candidate periods: 7 (weekly), 12 (monthly), 24 (hourly), 52 (weekly-yearly), 365 (daily-yearly)
3. For each detected period:
   - Compute seasonal strength
   - Compute seasonal subseries means
4. Report: detected periods with strength scores, calendar effects

### Stage 7: Report

```python
from ml_utils import save_agent_report
save_agent_report("timeseries-analyst", {
    "status": "completed",
    "data_summary": {
        "rows": row_count,
        "date_range": [start_date, end_date],
        "frequency": frequency,
        "missing_pct": missing_pct
    },
    "decomposition": {
        "model_type": model_type,
        "trend_direction": trend_direction,
        "seasonal_period": seasonal_period,
        "seasonal_strength": seasonal_strength,
        "trend_strength": trend_strength
    },
    "stationarity": {
        "adf_pvalue": adf_pvalue,
        "kpss_pvalue": kpss_pvalue,
        "is_stationary": is_stationary,
        "recommended_d": d,
        "recommended_D": D
    },
    "acf_pacf": {
        "significant_acf_lags": acf_lags,
        "significant_pacf_lags": pacf_lags,
        "suggested_arima_order": (p, d, q)
    },
    "seasonality": detected_periods,
    "recommendations": recommendations
})
```

Print summary table with all findings.
Print recommended next steps (forecasting model suggestions based on analysis).
