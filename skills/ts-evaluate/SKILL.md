---
name: ts-evaluate
description: "Evaluate forecast accuracy with MAPE, RMSE, SMAPE, coverage, and Winkler score. Includes error pattern analysis."
aliases: [forecast evaluation, forecast accuracy, ts metrics, forecast metrics]
extends: ml-automation
user_invocable: true
---

# Time Series Evaluate

Evaluate forecast accuracy against actuals. Computes point forecast metrics (MAPE, RMSE, MAE, SMAPE, MASE, bias), interval forecast metrics (coverage, width, Winkler score), and error pattern analysis (autocorrelation, systematic bias by calendar, degradation over horizon). Identifies worst predictions and recommends improvements.

## Full Specification

See `commands/ts-evaluate.md` for the complete workflow.
