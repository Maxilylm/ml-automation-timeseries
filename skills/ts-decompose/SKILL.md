---
name: ts-decompose
description: "Decompose time series into trend, seasonal, and residual components using STL, classical, or MSTL methods."
aliases: [decompose, time series decomposition, seasonal decomposition, stl]
extends: ml-automation
user_invocable: true
---

# Time Series Decompose

Decompose a time series into trend, seasonal, and residual components. Supports STL (robust to outliers), classical (additive/multiplicative), and MSTL (multiple seasonalities). Auto-detects seasonal period and model type. Analyzes each component: trend direction and changepoints, seasonal amplitude and stability, and residual white noise properties.

## Full Specification

See `commands/ts-decompose.md` for the complete workflow.
