"""Explainable, one-sided weekly warnings; no generator labels or seeded IDs."""

import numpy as np
import pandas as pd

from pulse.analytics.core import ADDITIVE, latest_week
from pulse.metrics.registry import calculate
from pulse.runtime import query, settings

METRICS = {
    "revenue": -1,
    "gross_profit": -1,
    "operating_profit": -1,
    "labour_pct": 1,
    "refund_rate": 1,
    "stockout_rate": 1,
    "satisfaction": -1,
}


def robust_warning(actual, history, direction, minimum_deviation=0.08, threshold=2.5):
    history = np.asarray(history, dtype=float)
    history = history[np.isfinite(history)]
    if len(history) < 8 or not np.isfinite(actual):
        return None
    median = float(np.median(history))
    scale = max(1.4826 * float(np.median(np.abs(history - median))), abs(median) * 0.03, 1e-6)
    denominator = max(abs(median), scale)
    adverse = direction * (actual - median)
    if adverse / denominator < minimum_deviation or adverse / scale < threshold:
        return None
    return {
        "baseline": median,
        "expected_low": median - 2.5 * scale,
        "expected_high": median + 2.5 * scale,
        "variance": actual - median,
        "variance_pct": (actual - median) / denominator,
        "robust_z": (actual - median) / scale,
    }


def detect(path=None):
    cfg = settings()["alerts"]
    start, end = latest_week(path)
    lookback = (pd.Timestamp(start) - pd.Timedelta(weeks=cfg["baseline_weeks"])).strftime(
        "%Y-%m-%d"
    )
    sums = ",".join(f"SUM({key}) {key}" for key in ADDITIVE)
    weeks = query(
        f"SELECT location_id,name,week_start,COUNT(*) days,{sums} FROM mart_daily WHERE date_id BETWEEN ? AND ? GROUP BY location_id,week_start ORDER BY location_id,week_start",
        (lookback, end),
        path,
    )
    rows = []
    for _, group in weeks.groupby("location_id"):
        group = group[group.days == 7]
        current = group[group.week_start == start]
        history = group[group.week_start < start].tail(8)
        if current.empty or len(history) < 8:
            continue
        now = calculate(current.iloc[0].to_dict())
        past = [calculate(row) for row in history.to_dict("records")]
        for metric, direction in METRICS.items():
            evidence = robust_warning(
                now[metric],
                [row[metric] for row in past],
                direction,
                cfg["minimum_deviation"],
                cfg["robust_z"],
            )
            if evidence is None:
                continue
            impact = (
                max(0, evidence["baseline"] - now[metric])
                if metric in ["operating_profit", "gross_profit"]
                else 0
            )
            if metric == "revenue":
                margin = max(0, float(np.nanmedian([row["gross_margin"] for row in past])))
                impact = max(0, evidence["baseline"] - now[metric]) * margin
            if metric == "labour_pct":
                impact = max(0, now[metric] - evidence["baseline"]) * now["revenue"]
            if (
                metric in ["operating_profit", "revenue", "gross_profit", "labour_pct"]
                and impact < cfg["minimum_profit_exposure"]
            ):
                continue
            rows.append(
                {
                    "severity": "CRITICAL" if impact >= cfg["critical_exposure"] else "WARNING",
                    "kpi": metric,
                    "location_id": int(current.iloc[0].location_id),
                    "entity": current.iloc[0]["name"],
                    "actual": now[metric],
                    **evidence,
                    "estimated_profit_exposure": impact,
                    "period_start": start,
                    "timestamp": end,
                    "evidence": "8 complete prior weeks; adverse deviation and robust z exceed thresholds",
                    "method": "Median/MAD with 3% baseline scale floor; one-sided; unadjusted for holidays",
                    "investigation": "Compare period profit bridge, channel/product mix, payroll and stock availability",
                }
            )
    columns = [
        "severity",
        "kpi",
        "location_id",
        "entity",
        "actual",
        "baseline",
        "expected_low",
        "expected_high",
        "variance",
        "variance_pct",
        "robust_z",
        "estimated_profit_exposure",
        "period_start",
        "timestamp",
        "evidence",
        "method",
        "investigation",
    ]
    return pd.DataFrame(rows, columns=columns).sort_values(
        "estimated_profit_exposure", ascending=False
    )


def exposure_summary(alerts):
    """Company exposure uses only operating-profit warnings, once per store.

    Different KPI warnings overlap. Other warning estimates must never be added.
    """
    return float(
        alerts.loc[alerts.kpi == "operating_profit"]
        .drop_duplicates("location_id")
        .estimated_profit_exposure.sum()
    )
