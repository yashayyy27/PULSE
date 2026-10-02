"""Scope-aware ledgers, period comparisons and deterministic evidence."""

import pandas as pd

from pulse.metrics.registry import calculate, ratio
from pulse.runtime import query, read_sql

ADDITIVE = [
    "list_sales",
    "discounts",
    "refunds",
    "transactions",
    "units",
    "cogs",
    "channel_fees",
    "labour_cost",
    "labour_hours",
    "overhead",
    "campaign_spend",
    "stockouts",
    "inventory_checks",
    "refunded_transactions",
    "rating_sum",
    "responses",
]
DIMENSIONS = {
    "State": "l.state",
    "Region": "l.region",
    "Location": "l.name",
    "Category": "p.category",
    "Product": "p.name",
    "Channel": "ch.name",
    "Daypart": "s.daypart",
    "Weekday": "d.weekday",
    "Customer segment": "c.segment",
    "Promotion": "pr.name",
}


def latest_week(path=None):
    """Never compare an incomplete trailing week with seven-day baselines."""
    end = pd.Timestamp(query("SELECT MAX(date_id) d FROM dim_date", path=path).iloc[0, 0])
    sunday = end - pd.Timedelta(days=(end.dayofweek + 1) % 7)
    return ((sunday - pd.Timedelta(days=6)).strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d"))


def previous_period(start, end):
    duration = pd.Timestamp(end) - pd.Timestamp(start) + pd.Timedelta(days=1)
    return (
        (pd.Timestamp(start) - duration).strftime("%Y-%m-%d"),
        (pd.Timestamp(start) - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
    )


def ledger(start, end, location=None, path=None):
    sums = ",".join(f"COALESCE(SUM({key}),0) {key}" for key in ADDITIVE)
    row = (
        query(
            f"SELECT {sums} FROM mart_daily WHERE date_id BETWEEN ? AND ? AND (? IS NULL OR location_id=?)",
            (start, end, location, location),
            path,
        )
        .iloc[0]
        .to_dict()
    )
    result = calculate(row)
    customers = query(
        """WITH visits AS (SELECT customer_id,COUNT(*) orders FROM fact_sales
        WHERE date_id BETWEEN ? AND ? AND customer_id<>0 AND (? IS NULL OR location_id=?)
        GROUP BY customer_id) SELECT COUNT(*) customer_count,
        COALESCE(SUM(CASE WHEN orders>=2 THEN 1 ELSE 0 END),0) repeat_customers FROM visits""",
        (start, end, location, location),
        path,
    ).iloc[0]
    result["customer_count"] = int(customers.customer_count)
    result["repeat_rate"] = ratio(customers.repeat_customers, customers.customer_count)
    return result


def daily(path=None, location=None):
    sums = ",".join(f"SUM({key}) {key}" for key in ADDITIVE)
    frame = query(
        f"SELECT date_id,{sums} FROM mart_daily WHERE (? IS NULL OR location_id=?) GROUP BY date_id ORDER BY date_id",
        (location, location),
        path,
    )
    return pd.DataFrame(
        [{"date_id": row["date_id"], **calculate(row)} for row in frame.to_dict("records")]
    )


def bridge(before, after):
    """Exact list-sales volume/basket bridge plus ledger costs; sums to profit delta.

    Volume uses previous list AOV; basket uses current order volume. Product mix,
    pricing and quantity effects are combined in basket; no unsupported separation.
    """
    old_aov = ratio(before["list_sales"], before["transactions"])
    if pd.isna(old_aov):
        volume, basket = 0.0, after["list_sales"] - before["list_sales"]
    else:
        volume = (after["transactions"] - before["transactions"]) * old_aov
        basket = after["list_sales"] - before["list_sales"] - volume
    rows = [
        {"contributor": "Order volume", "impact": volume},
        {"contributor": "Basket / price / product mix", "impact": basket},
    ]
    for key, label in [
        ("discounts", "Discounting"),
        ("refunds", "Refunds"),
        ("cogs", "Product cost"),
        ("labour_cost", "Labour cost"),
        ("channel_fees", "Channel fees"),
        ("overhead", "Overhead"),
        ("campaign_spend", "Campaign spend"),
    ]:
        rows.append({"contributor": label, "impact": before[key] - after[key]})
    return pd.DataFrame(rows)


def contributions(start, end, dimension="Location", location=None, path=None):
    if dimension not in DIMENSIONS:
        raise ValueError("Unsupported dimension")
    prior_start, prior_end = previous_period(start, end)
    return query(
        read_sql("dimensional_contribution.sql").format(dimension=DIMENSIONS[dimension]),
        {
            "current_start": start,
            "current_end": end,
            "prior_start": prior_start,
            "prior_end": prior_end,
            "location": location,
        },
        path,
    )


def investigate(start, end, location=None, path=None):
    prior = previous_period(start, end)
    before, after = ledger(*prior, location, path), ledger(start, end, location, path)
    return {
        "before": before,
        "after": after,
        "bridge": bridge(before, after),
        "start": start,
        "end": end,
        "prior_start": prior[0],
        "prior_end": prior[1],
    }
