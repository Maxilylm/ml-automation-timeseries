---
name: ts-anomaly
description: "Detect anomalies in time series using statistical (Z-score, IQR) and ML methods (Isolation Forest, LOF). Includes changepoint detection."
aliases: [anomaly detection, time series anomaly, outlier detection, ts outlier]
extends: ml-automation
user_invocable: true
---

# Time Series Anomaly Detection

Detect anomalies and outliers in time series data. Supports statistical methods (Z-score, modified Z-score, IQR, Grubbs), ML methods (Isolation Forest, LOF), and changepoint detection (PELT, CUSUM). Decomposes the series first to avoid flagging seasonal peaks as anomalies. Classifies anomalies by type (spike, dip, level shift, variance change).

## Full Specification

See `commands/ts-anomaly.md` for the complete workflow.
