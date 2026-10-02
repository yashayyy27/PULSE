"""Deterministic synthetic source system; embedded behaviours are generator-only."""

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pulse.runtime import settings

TOWNS = [
    "Parramatta",
    "Newcastle",
    "Wollongong",
    "Penrith",
    "Orange",
    "Albury",
    "Richmond",
    "Geelong",
    "Ballarat",
    "Bendigo",
    "Footscray",
    "Frankston",
    "Toowoomba",
    "Cairns",
    "Townsville",
    "Ipswich",
    "Redcliffe",
    "Mackay",
    "Fremantle",
    "Joondalup",
    "Bunbury",
    "Mandurah",
    "Albany",
    "Midland",
    "Norwood",
    "Glenelg",
    "Mount Barker",
    "Prospect",
    "Whyalla",
    "Port Lincoln",
    "Braddon",
    "Belconnen",
    "Woden",
    "Tuggeranong",
    "Gungahlin",
    "Kingston",
]


def frames(seed=20251006, small=False):
    """One sale row is one order containing a single SKU and 1–3 units.

    This deliberately simplifies a POS basket. No genuine customer/employee data.
    Demand seasonality, product mix, campaign selection and operational failures
    interact; analytics are never given the generator's behaviour labels.
    """
    rng = np.random.default_rng(seed)
    cfg = settings()
    n = 6 if small else cfg["locations"]
    dates = pd.date_range(cfg["start"], cfg["end"])
    if small:
        dates = dates[-210:]
    locations = pd.DataFrame(
        {
            "location_id": np.arange(1, n + 1),
            "name": TOWNS[:n],
            "state": np.repeat(["NSW", "VIC", "QLD", "WA", "SA", "ACT"], 6)[:n],
        }
    )
    locations["region"] = locations.state + " district"
    products = pd.DataFrame(
        {
            "product_id": np.arange(1, 13),
            "name": [
                "Harvest bowl",
                "Roast vegetable bowl",
                "Rye sandwich",
                "Chicken sandwich",
                "Flat white",
                "Long black",
                "Tea",
                "Cold brew",
                "Granola",
                "Sourdough",
                "Brownie",
                "Seasonal tart",
            ],
            "category": np.repeat(["Kitchen", "Drinks", "Pantry"], 4),
            "list_price": [18, 17, 13, 16, 5, 4.5, 4, 6, 12, 9, 6, 8],
            "unit_cost": [6, 5, 4, 5.5, 1.1, 0.8, 0.6, 1.5, 5, 3.5, 1.8, 2.8],
        }
    )
    channels = pd.DataFrame(
        {
            "channel_id": [1, 2, 3],
            "name": ["In store", "Click & collect", "Delivery"],
            "fee_rate": [0, 0.025, 0.22],
        }
    )
    customers = pd.DataFrame(
        {
            "customer_id": np.arange(24001),
            "segment": ["Guest"] + np.tile(["Regular", "Convenience", "Occasional"], 8000).tolist(),
        }
    )
    promotions = pd.DataFrame(
        {
            "promotion_id": [0, 1, 2],
            "name": ["None", "Lunch bundle", "Pantry discovery"],
            "discount_rate": [0, 0.22, 0.12],
        }
    )
    employees = pd.DataFrame(
        {
            "employee_id": np.arange(1, n * 4 + 1),
            "location_id": np.repeat(np.arange(1, n + 1), 4),
            "role": np.tile(["Lead", "Team", "Team", "Team"], n),
        }
    )
    calendar = pd.DataFrame(
        {
            "date_id": dates.strftime("%Y-%m-%d"),
            "month": dates.strftime("%Y-%m"),
            "weekday": dates.dayofweek,
            "week_start": (dates - pd.to_timedelta(dates.dayofweek, unit="d")).strftime("%Y-%m-%d"),
        }
    )
    day_idx = np.repeat(np.arange(len(dates)), n)
    loc = np.tile(np.arange(1, n + 1), len(dates))
    date_values = calendar.date_id.to_numpy()[day_idx]
    progress = np.clip((day_idx - (len(dates) - 150)) / 150, 0, 1)
    seasonal = 1 + 0.12 * np.sin(2 * np.pi * dates.dayofyear.to_numpy()[day_idx] / 365.25)
    weekend = np.where(dates.dayofweek.to_numpy()[day_idx] >= 5, 1.18, 1)
    base = rng.uniform(31, 47, n)[loc - 1]
    demand = base * seasonal * weekend
    demand *= np.where(loc <= 3, 1 - 0.40 * progress, 1)
    campaign = ((day_idx % 28) < 5) & (loc % 4 == 0)
    demand *= np.where(campaign, 1.14, 1)
    count = rng.poisson(demand)
    rows = np.repeat(np.arange(len(loc)), count)
    size = len(rows)
    sloc, sday = loc[rows], day_idx[rows]
    sku = rng.choice(
        np.arange(1, 13),
        size=size,
        p=[0.12, 0.09, 0.10, 0.12, 0.12, 0.07, 0.04, 0.07, 0.05, 0.06, 0.08, 0.08],
    )
    mix_change = (sloc % 7 == 0) & (rng.random(size) < 0.4 * progress[rows])
    sku[mix_change] = 9
    # Product availability is generated independently at store/day/product grain.
    inv_rows = np.repeat(np.arange(len(loc)), 12)
    inv_sku = np.tile(np.arange(1, 13), len(loc))
    inv_loc = loc[inv_rows]
    inv_progress = progress[inv_rows]
    outage_probability = 0.015 + np.where(
        (inv_loc % 5 == 0) & (inv_sku <= 4), 0.45 * inv_progress, 0
    )
    unavailable = rng.random(len(inv_rows)) < outage_probability
    availability = (~unavailable).reshape(len(loc), 12)
    unavailable_sale = ~availability[rows, sku - 1]
    # Substitute unavailable products; lost demand is represented by fewer orders.
    sku[unavailable_sale] = 6
    lost = unavailable_sale & (rng.random(size) < 0.35)
    keep = ~lost
    rows, sloc, sday, sku = rows[keep], sloc[keep], sday[keep], sku[keep]
    size = len(rows)
    channel = rng.choice([1, 2, 3], size=size, p=[0.67, 0.18, 0.15])
    switch = (sloc % 6 == 0) & (rng.random(size) < 0.35 * progress[rows])
    channel[switch] = 3
    cust = rng.integers(1, 24001, size)
    cust[rng.random(size) < 0.28] = 0
    # Deteriorating regular participation, with guest substitution.
    regular_decline = (cust % 3 == 1) & (sloc <= 5) & (rng.random(size) < 0.60 * progress[rows])
    cust[regular_decline] = 0
    promo = np.where(campaign[rows], 1, 0)
    promo[(sloc % 9 == 0) & (sday % 30 < 4)] = 2
    qty = rng.choice([1, 2, 3], size=size, p=[0.37, 0.51, 0.12])
    qty[(sloc % 8 == 0) & (rng.random(size) < 0.45 * progress[rows])] = 1
    list_sales = np.round(products.list_price.to_numpy()[sku - 1] * qty, 2)
    discount = np.round(list_sales * promotions.discount_rate.to_numpy()[promo], 2)
    refund_prob = 0.009 + np.where(sloc % 11 == 0, 0.065 * progress[rows], 0)
    refund = np.where(rng.random(size) < refund_prob, list_sales - discount, 0)
    cost_factor = 1 + np.where(sloc % 7 == 0, 0.28 * progress[rows], 0.04 * progress[rows])
    cogs = np.round(products.unit_cost.to_numpy()[sku - 1] * qty * cost_factor, 2)
    fees = np.round((list_sales - discount - refund) * channels.fee_rate.to_numpy()[channel - 1], 2)
    sales = pd.DataFrame(
        {
            "sale_id": np.arange(1, size + 1),
            "date_id": calendar.date_id.to_numpy()[sday],
            "location_id": sloc,
            "product_id": sku,
            "customer_id": cust,
            "channel_id": channel,
            "promotion_id": promo,
            "daypart": rng.choice(["Morning", "Lunch", "Evening"], size, p=[0.24, 0.51, 0.25]),
            "quantity": qty,
            "list_sales": list_sales,
            "discount": discount,
            "refund": refund,
            "cogs": cogs,
            "channel_fee": fees,
        }
    )
    labour_rows = np.repeat(np.arange(len(loc)), 2)
    hours = (3.1 + count[labour_rows] * 0.024) * rng.uniform(0.94, 1.06, len(labour_rows))
    hours *= np.where(loc[labour_rows] % 4 == 1, 1 + 0.30 * progress[labour_rows], 1)
    hours *= np.where(
        (loc[labour_rows] % 4 == 1) & (day_idx[labour_rows] >= len(dates) - 21), 1.20, 1
    )
    hours = np.round(hours, 2)
    labour = pd.DataFrame(
        {
            "labour_id": np.arange(1, len(labour_rows) + 1),
            "date_id": date_values[labour_rows],
            "location_id": loc[labour_rows],
            "employee_id": (loc[labour_rows] - 1) * 4 + np.tile([1, 2], len(loc)),
            "hours": hours,
            "labour_cost": np.round(hours * np.where(np.arange(len(hours)) % 2 == 0, 34, 30), 2),
        }
    )
    inventory = pd.DataFrame(
        {
            "inventory_id": np.arange(1, len(inv_rows) + 1),
            "date_id": date_values[inv_rows],
            "location_id": inv_loc,
            "product_id": inv_sku,
            "available": (~unavailable).astype(int),
            "closing_units": np.where(unavailable, 0, rng.integers(3, 50, len(inv_rows))),
        }
    )
    costs = pd.DataFrame(
        {
            "cost_id": np.arange(1, len(loc) + 1),
            "date_id": date_values,
            "location_id": loc,
            "overhead": np.round(68 + loc * 0.7 + rng.uniform(0, 12, len(loc)), 2),
        }
    )
    spend = pd.DataFrame(
        {
            "spend_id": np.arange(1, len(loc) + 1),
            "date_id": date_values,
            "location_id": loc,
            "promotion_id": np.where(
                (loc % 9 == 0) & (day_idx % 30 < 4), 2, np.where(campaign, 1, 0)
            ),
            "campaign_spend": np.where(
                (loc % 9 == 0) & (day_idx % 30 < 4), 18, np.where(campaign, 32, 0)
            ),
        }
    )
    respondents = rng.choice(size, max(1, int(size * 0.065)), replace=False)
    frows = rows[respondents]
    satisfaction = rng.normal(4.2 - np.where(loc[frows] <= 3, 0.9 * progress[frows], 0), 0.65)
    feedback = pd.DataFrame(
        {
            "feedback_id": np.arange(1, len(respondents) + 1),
            "sale_id": sales.sale_id.to_numpy()[respondents],
            "rating": np.clip(np.rint(satisfaction), 1, 5).astype(int),
        }
    )
    return {
        "dim_date": calendar,
        "dim_location": locations,
        "dim_product": products,
        "dim_customer": customers,
        "dim_channel": channels,
        "dim_promotion": promotions,
        "dim_employee": employees,
        "fact_sales": sales,
        "fact_labour": labour,
        "fact_inventory": inventory,
        "fact_operating_costs": costs,
        "fact_promotions": spend,
        "fact_feedback": feedback,
    }


def write_raw(target: Path, seed=20251006, small=False):
    target.mkdir(parents=True, exist_ok=True)
    tables = frames(seed, small)
    for name, frame in tables.items():
        with (target / f"{name}.csv.gz").open("wb") as raw:
            with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
                compressed.write(frame.to_csv(index=False).encode())
    (target / "manifest.json").write_text(
        json.dumps(
            {
                "synthetic": True,
                "seed": seed,
                "small": small,
                "rows": {k: len(v) for k, v in tables.items()},
            },
            indent=2,
        )
    )
    return tables
