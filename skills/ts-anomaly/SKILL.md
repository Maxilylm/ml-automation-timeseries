---
name: ts-anomaly
description: "Detect anomalies in time series using statistical (Z-score, IQR) and ML methods (Isolation Forest, LOF). Includes changepoint detection."
aliases: [anomaly detection, time series anomaly, outlier detection, ts outlier]
extends: ml-automation
user_invocable: true
---

# Time Series Anomaly Detection

Detect anomalies and outliers in time series data. Supports statistical methods (Z-score, modified Z-score, IQR, Grubbs), ML methods (Isolation Forest, LOF), and changepoint detection (PELT, CUSUM). Decomposes the series first to avoid flagging seasonal peaks as anomalies. Classifies anomalies by type (spike, dip, level shift, variance change).

## When to Use

- Identifying outliers or unexpected events in temporal data before modeling
- Detecting level shifts or structural breaks that affect forecast accuracy
- Running automated quality checks on incoming time series feeds
- Choosing between statistical and ML-based detection for a given dataset

## Workflow

1. **Env Check** - Verify required libraries (scikit-learn, statsmodels, ruptures as needed); install missing packages.
2. **Data Loading** - Read the dataset, parse dates, sort chronologically, and perform STL decomposition to isolate the residual component.
3. **Anomaly Detection** - Apply the selected `--method` (or `auto` to run all and ensemble) on the residual series using the specified `--threshold`.
4. **Anomaly Classification** - Label each detected anomaly by type: spike, dip, level shift, or variance change.
5. **Changepoint Detection** - Run PELT/CUSUM on the full series to detect structural breaks independent of the anomaly method.
6. **Summary Report** - List anomalies with timestamps, values, severity scores, and type labels; save annotated plot and report JSON.

## Report Bus Integration

```python
from ml_utils import save_agent_report
save_agent_report("anomaly-detector", {
    "status": "completed",
    "findings": {
        "method": "isolation_forest", "threshold": 3.0,
        "anomalies_found": 12,
        "types": {"spike": 5, "dip": 3, "level_shift": 2, "variance_change": 2},
        "changepoints": ["2024-03-15", "2024-09-01"],
    },
    "recommendations": [
        {"text": "Treat level shifts as regime changes in forecasting", "target_agent": "forecaster"}
    ],
    "artifacts": [".claude/ts_anomaly_report.json"]
})
```

## Full Specification

Usage: `/ts-anomaly <data_path> [--method zscore|iqr|isolation_forest|lof|auto] [--threshold 3.0]`

Delegated agent: `anomaly-detector`

See `commands/ts-anomaly.md` for the complete workflow.
