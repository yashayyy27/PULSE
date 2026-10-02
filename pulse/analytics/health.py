"""Transparent stakeholder-assumed targets and configurable importance weights."""

import math

from pulse.runtime import settings

TARGETS = {
    "operating_margin": 0.15,
    "satisfaction": 4.2,
    "labour_pct": 0.33,
    "inventory_availability": 0.98,
}


def health(metrics, weights=None):
    weights = settings()["health_weights"] if weights is None else weights
    if set(weights) != {"Financial", "Customer", "Operations", "Inventory"}:
        raise ValueError("Four health dimensions required")
    if any(not math.isfinite(v) or v < 0 for v in weights.values()) or sum(weights.values()) <= 0:
        raise ValueError("Weights must be finite, nonnegative and have a positive sum")
    values = {
        "Financial": metrics["operating_margin"] / 0.15,
        "Customer": metrics["satisfaction"] / 4.2,
        "Operations": 0.33 / metrics["labour_pct"] if metrics["labour_pct"] > 0 else math.nan,
        "Inventory": metrics["inventory_availability"] / 0.98,
    }
    scores = {
        key: min(100, max(0, value * 100)) if math.isfinite(value) else math.nan
        for key, value in values.items()
    }
    total = sum(weights.values())
    overall = sum(scores[key] * value / total for key, value in weights.items() if value > 0)
    return {
        "overall": overall,
        "scores": scores,
        "normalised_weights": {k: v / total for k, v in weights.items()},
        "targets": TARGETS,
        "method": "Ratio to target, capped 0–100; inverse ratio for labour share. Fictional stakeholder targets; not a predictive risk score.",
    }
