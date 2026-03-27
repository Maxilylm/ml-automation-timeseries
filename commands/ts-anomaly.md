# /ts-anomaly

Detect anomalies and outliers in time series data using statistical and ML methods.

## Usage

```
/ts-anomaly <data_path> [--method zscore|iqr|isolation_forest|lof|auto] [--threshold 3.0] [--date-col <col>] [--value-col <col>]
```

- `data_path`: path to CSV/Parquet file with time series data
- `--method`: anomaly detection method (default: auto — runs multiple and combines)
- `--threshold`: detection threshold (default: 3.0 for Z-score, 1.5 for IQR multiplier)
- `--date-col`: datetime column name (auto-detected if not specified)
- `--value-col`: value column name (auto-detected if not specified)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` — if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `timeseries_utils.py` exists in `src/` — if missing, copy from this plugin's `templates/timeseries_utils.py`
3. Verify data file exists and is readable
4. Check required packages based on `--method`:
   - isolation_forest/lof: `scikit-learn`

### Stage 1: Data Loading

1. Load and parse data (detect date and value columns)
2. Handle missing values (forward fill)
3. Compute baseline statistics: mean, std, median, MAD, IQR
4. Report: row count, date range, basic stats

### Stage 2: Decomposition-Based Preprocessing

1. Decompose series (STL) to separate trend, seasonal, residual
2. Compute anomaly scores on residual component (removes seasonal effects)
3. This ensures seasonal peaks are not flagged as anomalies

### Stage 3: Anomaly Detection

Based on `--method`:

**Z-Score:**
1. Compute Z-scores on residual component
2. Flag points where |Z| > `--threshold`
3. Report: flagged count, percentage

**Modified Z-Score (MAD-based):**
1. Compute Modified Z-scores using MAD (Median Absolute Deviation)
2. More robust to existing outliers than standard Z-score
3. Flag points where |Modified Z| > `--threshold`

**IQR Method:**
1. Compute Q1, Q3, IQR on residual component
2. Flag points below Q1 - threshold * IQR or above Q3 + threshold * IQR
3. Report: lower/upper bounds, flagged count

**Isolation Forest:**
1. Prepare features: value, lag-1, lag-7, rolling mean, rolling std
2. Fit Isolation Forest (contamination=auto or 0.05)
3. Score each point (-1 = anomaly, 1 = normal)
4. Report: contamination rate, anomaly count

**Local Outlier Factor (LOF):**
1. Prepare features: value, lag-1, lag-7, rolling mean, rolling std
2. Fit LOF with k=20 neighbors
3. Compute negative outlier factor scores
4. Flag points with LOF score below threshold
5. Report: anomaly count, score distribution

**Auto (default):**
1. Run Z-score, IQR, and Isolation Forest
2. Ensemble: flag points detected by >= 2 methods
3. Report: per-method counts, ensemble consensus count

### Stage 4: Changepoint Detection

1. Run PELT algorithm on the series:
   - Detect mean shifts and variance changes
   - Report: changepoint timestamps, magnitude of change
2. Run CUSUM on residuals:
   - Detect sustained shifts in mean
   - Report: shift points, cumulative sum chart data

### Stage 5: Contextual Analysis

1. For each detected anomaly:
   - Classify as: spike, dip, level shift, or variance change
   - Check proximity to other anomalies (clusters)
   - Check calendar context (holiday, weekend, month-end)
2. Group anomalies by type and temporal proximity
3. Report: anomaly classification breakdown, temporal clusters

### Stage 6: Report

```python
from ml_utils import save_agent_report
save_agent_report("anomaly-detector", {
    "status": "completed",
    "method": method,
    "threshold": threshold,
    "anomaly_count": anomaly_count,
    "anomaly_pct": anomaly_pct,
    "anomalies": [
        {"date": date, "value": value, "score": score, "type": anomaly_type}
        for each anomaly
    ][:50],
    "changepoints": changepoints,
    "anomaly_types": type_breakdown,
    "recommendations": recommendations
})
```

Save anomaly report to `reports/anomaly_report.csv` with columns: date, value, is_anomaly, anomaly_score, anomaly_type.
Print: anomaly summary, top 10 anomalies by score, changepoints, visualization recommendations.
