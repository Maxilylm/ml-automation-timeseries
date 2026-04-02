"""
Time series utilities for the spark-timeseries extension plugin.

Requires ml_utils.py from the spark core plugin to be present
in the same directory (copied via Stage 0 of time series commands).
"""

import math
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

try:
    from ml_utils import save_agent_report, load_agent_report  # re-exported
except ImportError:
    save_agent_report = None  # type: ignore[assignment]
    load_agent_report = None  # type: ignore[assignment]


# --- Relevance Detection ---

DATETIME_COLUMN_PATTERNS = [
    r"date", r"time", r"timestamp", r"dt", r"datetime",
    r"created_at", r"updated_at", r"period", r"month", r"year",
    r"day", r"week", r"hour",
]

TIMESERIES_FILE_PATTERNS = [
    "*.csv", "*.parquet", "*.tsv",
]


def detect_timeseries_relevance(project_path="."):
    """Check if project has time series indicators for relevance gating.

    Checks: datetime columns in CSV/Parquet files, regular frequency data,
    time-indexed datasets, temporal keywords in column names.

    Args:
        project_path: root directory of the project

    Returns:
        dict with 'is_timeseries': bool, 'indicators': list of found indicators
    """
    indicators = []
    project = Path(project_path)

    # Check for CSV files with datetime columns
    csv_files = list(project.glob("**/*.csv"))[:20]  # limit scan
    for csv_file in csv_files:
        try:
            # Read just the header line
            with open(csv_file) as f:
                header = f.readline().strip().lower()
            columns = [c.strip().strip('"').strip("'") for c in header.split(",")]
            for col in columns:
                for pattern in DATETIME_COLUMN_PATTERNS:
                    if re.search(pattern, col, re.IGNORECASE):
                        indicators.append(f"datetime column '{col}' in {csv_file.name}")
                        break
        except (UnicodeDecodeError, PermissionError):
            continue

    # Check for Parquet files (common for time series)
    parquet_files = list(project.glob("**/*.parquet"))[:10]
    if parquet_files:
        indicators.append(f"{len(parquet_files)} Parquet files found")

    # Check Python files for time series library imports
    ts_libraries = {
        "prophet", "statsmodels", "pmdarima", "sktime",
        "neuralforecast", "pytorch_forecasting", "darts",
        "tbats", "arch", "ruptures",
    }
    py_files = list(project.glob("**/*.py"))[:50]
    for py_file in py_files:
        try:
            content = py_file.read_text()
            for lib in ts_libraries:
                if f"import {lib}" in content or f"from {lib}" in content:
                    indicators.append(f"{lib} import in {py_file.name}")
                    break
        except (UnicodeDecodeError, PermissionError):
            continue

    # Check requirements for time series packages
    for req_file in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]:
        req_path = project / req_file
        if req_path.exists():
            try:
                content = req_path.read_text().lower()
                for pkg in ts_libraries:
                    if pkg in content:
                        indicators.append(f"{pkg} in {req_file}")
            except (UnicodeDecodeError, PermissionError):
                continue

    # Check for forecast/timeseries directories
    for ts_dir in ["forecasts", "timeseries", "time_series", "temporal"]:
        if (project / ts_dir).is_dir():
            indicators.append(f"Directory: {ts_dir}/")

    return {
        "is_timeseries": len(indicators) > 0,
        "indicators": indicators,
    }


# --- Forecast Metrics ---

def compute_forecast_metrics(actual: List[float], forecast: List[float],
                             lower: Optional[List[float]] = None,
                             upper: Optional[List[float]] = None) -> Dict[str, float]:
    """Compute standard forecast accuracy metrics.

    Args:
        actual: list of actual values
        forecast: list of forecast values
        lower: optional lower prediction interval bounds
        upper: optional upper prediction interval bounds

    Returns:
        dict with MAPE, RMSE, MAE, SMAPE, bias, and optionally coverage
    """
    assert len(actual) == len(forecast), "Actual/forecast length mismatch"
    n = len(actual)

    # MAE
    abs_errors = [abs(a - f) for a, f in zip(actual, forecast)]
    mae = sum(abs_errors) / n

    # RMSE
    sq_errors = [(a - f) ** 2 for a, f in zip(actual, forecast)]
    rmse = math.sqrt(sum(sq_errors) / n)

    # MAPE (exclude zeros in actual)
    mape_values = []
    for a, f in zip(actual, forecast):
        if abs(a) > 1e-10:
            mape_values.append(abs(a - f) / abs(a))
    mape = (sum(mape_values) / len(mape_values) * 100) if mape_values else float("inf")

    # SMAPE
    smape_values = []
    for a, f in zip(actual, forecast):
        denom = abs(a) + abs(f)
        if denom > 1e-10:
            smape_values.append(2 * abs(a - f) / denom)
    smape = (sum(smape_values) / len(smape_values) * 100) if smape_values else float("inf")

    # Bias (mean error)
    errors = [f - a for a, f in zip(actual, forecast)]
    bias = sum(errors) / n

    result = {
        "mape": round(mape, 4),
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "smape": round(smape, 4),
        "bias": round(bias, 4),
        "n": n,
    }

    # Coverage (if prediction intervals provided)
    if lower is not None and upper is not None:
        assert len(lower) == n and len(upper) == n
        covered = sum(1 for a, lo, hi in zip(actual, lower, upper) if lo <= a <= hi)
        result["coverage"] = round(covered / n * 100, 2)
        result["avg_interval_width"] = round(
            sum(hi - lo for lo, hi in zip(lower, upper)) / n, 4
        )

    return result


# --- Temporal Train/Test Split ---

def temporal_train_test_split(dates: List, values: List,
                              horizon: int,
                              strategy: str = "expanding",
                              n_folds: int = 5,
                              window_size: Optional[int] = None
                              ) -> List[Dict[str, Any]]:
    """Create temporal cross-validation splits.

    Args:
        dates: list of datetime values (sorted ascending)
        values: list of corresponding values
        horizon: forecast horizon (number of steps)
        strategy: 'expanding' or 'sliding'
        n_folds: number of CV folds
        window_size: training window size for sliding strategy

    Returns:
        list of dicts with 'train_dates', 'train_values',
        'test_dates', 'test_values', 'fold' keys
    """
    n = len(dates)
    assert n == len(values), "Dates/values length mismatch"
    assert n >= horizon * (n_folds + 1), (
        f"Insufficient data: need >= {horizon * (n_folds + 1)} points, "
        f"got {n}"
    )

    # Compute cutoff indices
    # Space folds evenly across the last 50% of data
    min_train = n // 2
    max_cutoff = n - horizon
    cutoff_step = (max_cutoff - min_train) // n_folds

    folds = []
    for fold_idx in range(n_folds):
        cutoff = min_train + fold_idx * cutoff_step

        if strategy == "expanding":
            train_start = 0
        elif strategy == "sliding":
            ws = window_size or (horizon * 3)
            train_start = max(0, cutoff - ws)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        train_end = cutoff
        test_start = cutoff
        test_end = min(cutoff + horizon, n)

        folds.append({
            "fold": fold_idx + 1,
            "train_dates": dates[train_start:train_end],
            "train_values": values[train_start:train_end],
            "test_dates": dates[test_start:test_end],
            "test_values": values[test_start:test_end],
            "train_size": train_end - train_start,
            "test_size": test_end - test_start,
        })

    return folds


# --- Seasonality Detection ---

def detect_seasonality(values: List[float],
                       max_period: int = 365,
                       candidate_periods: Optional[List[int]] = None
                       ) -> List[Dict[str, Any]]:
    """Detect seasonal periods in a time series using autocorrelation.

    Args:
        values: list of numeric values (evenly spaced)
        max_period: maximum period to check
        candidate_periods: specific periods to test (default: [7, 12, 24, 52, 365])

    Returns:
        list of dicts with 'period', 'acf_value', 'strength' sorted by strength desc
    """
    if candidate_periods is None:
        candidate_periods = [7, 12, 24, 52, 365]

    n = len(values)
    mean_val = sum(values) / n
    variance = sum((v - mean_val) ** 2 for v in values) / n

    if variance < 1e-10:
        return []

    # Filter candidates that are feasible given data length
    candidates = [p for p in candidate_periods if p < n // 2 and p <= max_period]

    results = []
    for period in candidates:
        # Compute autocorrelation at this lag
        acf_val = _autocorrelation(values, period, mean_val, variance)

        # Compute seasonal strength by averaging values at each position
        n_cycles = n // period
        if n_cycles < 2:
            continue

        seasonal_means = []
        for pos in range(period):
            pos_values = [values[i] for i in range(pos, n, period)]
            seasonal_means.append(sum(pos_values) / len(pos_values))

        # Seasonal strength: variance of seasonal means / total variance
        seasonal_mean_overall = sum(seasonal_means) / len(seasonal_means)
        seasonal_variance = sum(
            (m - seasonal_mean_overall) ** 2 for m in seasonal_means
        ) / len(seasonal_means)
        strength = seasonal_variance / variance if variance > 0 else 0

        results.append({
            "period": period,
            "acf_value": round(acf_val, 4),
            "strength": round(strength, 4),
        })

    # Sort by strength descending
    results.sort(key=lambda x: x["strength"], reverse=True)

    # Filter weak seasonality (strength < 0.01)
    results = [r for r in results if r["strength"] >= 0.01]

    return results


def _autocorrelation(values: List[float], lag: int,
                     mean_val: float, variance: float) -> float:
    """Compute autocorrelation at a specific lag."""
    n = len(values)
    if lag >= n or variance < 1e-10:
        return 0.0
    covariance = sum(
        (values[i] - mean_val) * (values[i + lag] - mean_val)
        for i in range(n - lag)
    ) / n
    return covariance / variance


# --- Stationarity Testing ---

def test_stationarity(values: List[float],
                      significance: float = 0.05) -> Dict[str, Any]:
    """Test time series stationarity using simplified variance ratio test.

    For full ADF/KPSS, use statsmodels. This provides a quick heuristic.

    Args:
        values: list of numeric values
        significance: significance level (default: 0.05)

    Returns:
        dict with 'is_stationary', 'rolling_mean_trend', 'rolling_var_trend',
        'recommended_d', 'method'
    """
    n = len(values)
    if n < 20:
        return {
            "is_stationary": None,
            "reason": "Insufficient data (need >= 20 observations)",
            "recommended_d": 0,
            "method": "heuristic",
        }

    # Split into segments and compare means/variances
    segment_size = n // 4
    segments = [
        values[i * segment_size:(i + 1) * segment_size]
        for i in range(4)
    ]

    segment_means = [sum(s) / len(s) for s in segments]
    segment_vars = [
        sum((v - m) ** 2 for v in s) / len(s)
        for s, m in zip(segments, segment_means)
    ]

    # Check if means are trending
    mean_range = max(segment_means) - min(segment_means)
    overall_std = math.sqrt(sum((v - sum(values) / n) ** 2 for v in values) / n)
    mean_trend = mean_range > 2 * overall_std / math.sqrt(segment_size)

    # Check if variance is changing
    var_range = max(segment_vars) - min(segment_vars)
    mean_var = sum(segment_vars) / len(segment_vars)
    var_trend = var_range > mean_var if mean_var > 0 else False

    is_stationary = not mean_trend and not var_trend

    # Recommend differencing
    recommended_d = 0
    if mean_trend:
        recommended_d = 1
    if var_trend and not mean_trend:
        recommended_d = 1  # may need log transform first

    return {
        "is_stationary": is_stationary,
        "rolling_mean_trend": mean_trend,
        "rolling_var_trend": var_trend,
        "recommended_d": recommended_d,
        "method": "heuristic (use statsmodels for ADF/KPSS)",
        "segment_means": [round(m, 4) for m in segment_means],
        "segment_vars": [round(v, 4) for v in segment_vars],
    }


# --- ACF/PACF Computation ---

def compute_acf_pacf(values: List[float],
                     max_lags: Optional[int] = None
                     ) -> Dict[str, Any]:
    """Compute autocorrelation (ACF) and partial autocorrelation (PACF).

    Args:
        values: list of numeric values
        max_lags: maximum number of lags (default: min(40, len/2))

    Returns:
        dict with 'acf' (list), 'pacf' (list), 'confidence_bound',
        'significant_acf_lags', 'significant_pacf_lags'
    """
    n = len(values)
    if max_lags is None:
        max_lags = min(40, n // 2)

    mean_val = sum(values) / n
    variance = sum((v - mean_val) ** 2 for v in values) / n

    if variance < 1e-10:
        return {
            "acf": [1.0] + [0.0] * max_lags,
            "pacf": [1.0] + [0.0] * max_lags,
            "confidence_bound": 0.0,
            "significant_acf_lags": [],
            "significant_pacf_lags": [],
        }

    # Compute ACF
    acf = [1.0]  # lag 0
    for lag in range(1, max_lags + 1):
        acf_val = _autocorrelation(values, lag, mean_val, variance)
        acf.append(round(acf_val, 4))

    # Compute PACF using Durbin-Levinson recursion
    pacf = _durbin_levinson(acf, max_lags)

    # 95% confidence bound
    conf_bound = round(1.96 / math.sqrt(n), 4)

    # Significant lags
    sig_acf = [lag for lag in range(1, len(acf)) if abs(acf[lag]) > conf_bound]
    sig_pacf = [lag for lag in range(1, len(pacf)) if abs(pacf[lag]) > conf_bound]

    return {
        "acf": acf,
        "pacf": pacf,
        "confidence_bound": conf_bound,
        "significant_acf_lags": sig_acf,
        "significant_pacf_lags": sig_pacf,
    }


def _durbin_levinson(acf: List[float], max_lags: int) -> List[float]:
    """Compute PACF from ACF using Durbin-Levinson algorithm."""
    pacf = [1.0]  # lag 0

    if max_lags < 1 or len(acf) < 2:
        return pacf

    # Lag 1
    pacf.append(round(acf[1], 4))

    if max_lags < 2:
        return pacf

    # phi[k][j] stores the k-th order AR coefficient for lag j
    phi_prev = [0.0, acf[1]]

    for k in range(2, max_lags + 1):
        if k >= len(acf):
            pacf.append(0.0)
            continue

        # Compute phi_kk
        numerator = acf[k] - sum(
            phi_prev[j] * acf[k - j] for j in range(1, k)
        )
        denominator = 1.0 - sum(
            phi_prev[j] * acf[j] for j in range(1, k)
        )

        if abs(denominator) < 1e-10:
            pacf.append(0.0)
            phi_prev = phi_prev + [0.0]
            continue

        phi_kk = numerator / denominator
        pacf.append(round(phi_kk, 4))

        # Update phi coefficients
        phi_new = [0.0] * (k + 1)
        phi_new[k] = phi_kk
        for j in range(1, k):
            phi_new[j] = phi_prev[j] - phi_kk * phi_prev[k - j]
        phi_prev = phi_new

    return pacf
