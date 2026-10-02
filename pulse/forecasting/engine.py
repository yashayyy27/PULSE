"""Transparent multi-step forecasts with validation-only selection and holdout."""

import numpy as np
import pandas as pd

MODELS = ["Seasonal naive", "Weekday mean (8 weeks)"]
METRICS = ["revenue", "transactions", "gross_profit", "labour_hours"]


def predict(history, model, horizon=28):
    """Forecast uses only input history; future actuals cannot enter recurrence."""
    values = np.asarray(history, dtype=float)
    if len(values) < 56 or not np.isfinite(values).all():
        raise ValueError("Forecast requires >=56 finite daily observations")
    if model not in MODELS or horizon <= 0:
        raise ValueError("Unsupported model or horizon")
    if model == MODELS[0]:
        return np.resize(values[-7:], horizon)
    # History is contiguous; align each future weekday with matching historical offsets.
    return np.asarray([np.mean(values[-56:][(i % 7) :: 7]) for i in range(horizon)])


def errors(actual, predicted):
    a, p = np.asarray(actual), np.asarray(predicted)
    mask = np.abs(a) > 1e-8
    return {
        "MAE": float(np.mean(np.abs(a - p))),
        "RMSE": float(np.sqrt(np.mean((a - p) ** 2))),
        "MAPE": float(np.mean(np.abs((a[mask] - p[mask]) / a[mask]))) if mask.any() else None,
    }


def forecast(frame, horizon=28):
    if horizon != 28:
        raise ValueError("Backtest design supports a 28-day horizon")
    frame = frame.sort_values("date_id").copy()
    dates = pd.to_datetime(frame.date_id)
    if len(frame) < 168 or not dates.diff().dropna().eq(pd.Timedelta(days=1)).all():
        raise ValueError("Need >=168 consecutive days for validation and holdout")
    summaries, predictions, backtests = [], [], []
    n = len(frame)
    origins = [n - 112, n - 84, n - 56]
    for metric in METRICS:
        values = frame[metric].to_numpy(float)
        validation = {}
        for model in MODELS:
            residuals = []
            for origin in origins:
                pred = predict(values[:origin], model, horizon)
                actual = values[origin : origin + horizon]
                residuals.append(actual - pred)
                for day, (a, p) in enumerate(zip(actual, pred), 1):
                    backtests.append(
                        {
                            "metric": metric,
                            "model": model,
                            "split": "validation",
                            "origin": str(dates.iloc[origin - 1].date()),
                            "horizon": day,
                            "actual": a,
                            "predicted": p,
                        }
                    )
            validation[model] = np.asarray(residuals)
        selected = min(MODELS, key=lambda m: np.mean(np.abs(validation[m])))
        # Final 28 days were not used in choosing the model.
        holdout = predict(values[:-horizon], selected, horizon)
        actual = values[-horizon:]
        # Calibration uses only pre-holdout residuals; small sample makes bands approximate.
        radius = np.quantile(np.abs(validation[selected]), 0.9, axis=0)
        stats = errors(actual, holdout)
        coverage = float(np.mean(np.abs(actual - holdout) <= radius))
        summaries.append(
            {
                "metric": metric,
                "selected_model": selected,
                **stats,
                "holdout_coverage": coverage,
                "nominal_coverage": 0.9,
                "calibration_origins": 3,
                "validation_naive_MAE": float(np.mean(np.abs(validation[MODELS[0]]))),
                "validation_mean_MAE": float(np.mean(np.abs(validation[MODELS[1]]))),
            }
        )
        for day, (a, p, r) in enumerate(zip(actual, holdout, radius), 1):
            backtests.append(
                {
                    "metric": metric,
                    "model": selected,
                    "split": "holdout",
                    "origin": str(dates.iloc[-horizon - 1].date()),
                    "horizon": day,
                    "actual": a,
                    "predicted": p,
                    "lower": max(0, p - r),
                    "upper": p + r,
                }
            )
        future = predict(values, selected, horizon)
        for day, (p, r) in enumerate(zip(future, radius), 1):
            predictions.append(
                {
                    "metric": metric,
                    "date_id": str((dates.iloc[-1] + pd.Timedelta(days=day)).date()),
                    "forecast": p,
                    "lower": max(0, p - r),
                    "upper": p + r,
                    "model": selected,
                }
            )
    return {
        "metrics": pd.DataFrame(summaries),
        "future": pd.DataFrame(predictions),
        "backtests": pd.DataFrame(backtests),
    }
