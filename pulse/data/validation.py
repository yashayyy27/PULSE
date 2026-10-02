"""Fail-closed source validation with auditable, per-rule results."""

import pandas as pd

PRIMARY_KEYS = {
    "dim_date": "date_id",
    "dim_location": "location_id",
    "dim_product": "product_id",
    "dim_customer": "customer_id",
    "dim_channel": "channel_id",
    "dim_promotion": "promotion_id",
    "dim_employee": "employee_id",
    "fact_sales": "sale_id",
    "fact_labour": "labour_id",
    "fact_inventory": "inventory_id",
    "fact_operating_costs": "cost_id",
    "fact_promotions": "spend_id",
    "fact_feedback": "feedback_id",
}


def validate(tables):
    results = []

    def rule(name, failures, detail):
        results.append(
            {
                "rule": name,
                "failures": int(failures),
                "status": "PASS" if failures == 0 else "FAIL",
                "detail": detail,
            }
        )

    for name, key in PRIMARY_KEYS.items():
        frame = tables[name]
        rule(f"{name}: nonempty", int(frame.empty), "Empty source tables cannot publish")
        rule(f"{name}: nulls", frame.isna().sum().sum(), "Every source column is required")
        rule(f"{name}: unique key", frame[key].duplicated().sum(), key)
        for column in frame.columns:
            target = "dim_" + column.removesuffix("_id")
            if column == "sale_id" and name == "fact_feedback":
                target = "fact_sales"
            if column.endswith("_id") and column != key and target in tables:
                rule(
                    f"{name}: {column} FK",
                    (~frame[column].isin(tables[target][column])).sum(),
                    target,
                )
        if "date_id" in frame:
            parsed = pd.to_datetime(frame.date_id, errors="coerce")
            rule(f"{name}: valid dates", parsed.isna().sum(), "ISO calendar dates")
        for column in frame.select_dtypes(include="number"):
            rule(
                f"{name}: {column} nonnegative",
                (
                    (frame[column] < 0)
                    | ~frame[column].map(lambda x: float("-inf") < x < float("inf"))
                ).sum(),
                "Negative or infinite source value",
            )
    sales = tables["fact_sales"]
    rule(
        "sales: ledger bounds",
        (sales.discount + sales.refund > sales.list_sales + 0.001).sum(),
        "Discount plus refund <= list sales",
    )
    rule(
        "sales: daypart",
        (~sales.daypart.isin(["Morning", "Lunch", "Evening"])).sum(),
        "Controlled vocabulary",
    )
    rule(
        "sales: plausible extremes",
        ((sales.quantity > 20) | (sales.list_sales > 1000) | (sales.quantity <= 0)).sum(),
        "Prototype source contract: 1–20 units, <= A$1,000",
    )
    products = tables["dim_product"]
    rule(
        "products: category",
        (~products.category.isin(["Kitchen", "Drinks", "Pantry"])).sum(),
        "Controlled vocabulary",
    )
    rule(
        "customers: segment",
        (
            ~tables["dim_customer"].segment.isin(["Guest", "Regular", "Convenience", "Occasional"])
        ).sum(),
        "Controlled vocabulary",
    )
    rule(
        "locations: state",
        (~tables["dim_location"].state.isin(["NSW", "VIC", "QLD", "WA", "SA", "ACT"])).sum(),
        "Fictional operating footprint",
    )
    rule("feedback: rating", (~tables["fact_feedback"].rating.between(1, 5)).sum(), "1–5")
    rule("inventory: availability", (~tables["fact_inventory"].available.isin([0, 1])).sum(), "0/1")
    rule(
        "inventory: stock consistency",
        (
            (tables["fact_inventory"].available == 0)
            & (tables["fact_inventory"].closing_units != 0)
        ).sum(),
        "Unavailable means zero units",
    )
    labour = tables["fact_labour"]
    rule("labour: hours", (~labour.hours.between(0.01, 16)).sum(), "0–16 hours per employee/day")
    employee_map = tables["dim_employee"].set_index("employee_id").location_id
    rule(
        "labour: employee assignment",
        (labour.employee_id.map(employee_map) != labour.location_id).sum(),
        "Employee belongs to paid location",
    )
    rule(
        "feedback: unique response",
        tables["fact_feedback"].sale_id.duplicated().sum(),
        "At most one response per order",
    )
    calendar = tables["dim_date"]
    all_dates = pd.date_range(calendar.date_id.min(), calendar.date_id.max()).strftime("%Y-%m-%d")
    rule(
        "calendar: no missing periods",
        len(set(all_dates) - set(calendar.date_id)),
        "Continuous daily calendar",
    )
    expected_days = len(calendar) * len(tables["dim_location"])
    for name in ["fact_labour", "fact_inventory", "fact_operating_costs", "fact_promotions"]:
        frame = tables[name]
        covered = frame[["date_id", "location_id"]].drop_duplicates()
        rule(
            f"{name}: store/day coverage",
            abs(len(covered) - expected_days),
            "All stores, all calendar days",
        )
    inventory = tables["fact_inventory"]
    rule(
        "inventory: natural key",
        inventory.duplicated(["date_id", "location_id", "product_id"]).sum(),
        "One daily observation per SKU",
    )
    rule(
        "inventory: SKU coverage",
        abs(len(inventory) - expected_days * len(products)),
        "Every product/store/day",
    )
    for name in ["fact_operating_costs", "fact_promotions"]:
        rule(
            f"{name}: natural key",
            tables[name].duplicated(["date_id", "location_id"]).sum(),
            "One store/day row",
        )
    assignment = tables["fact_promotions"]
    if not assignment.duplicated(["date_id", "location_id"]).any():
        reconciled = sales[["date_id", "location_id", "promotion_id"]].merge(
            assignment[["date_id", "location_id", "promotion_id"]],
            on=["date_id", "location_id"],
            how="left",
            suffixes=("_sale", "_assigned"),
            validate="many_to_one",
        )
        rule(
            "promotions: order assignment",
            (reconciled.promotion_id_sale != reconciled.promotion_id_assigned).sum(),
            "Order discount offer must match the store/day campaign spend assignment",
        )
    return pd.DataFrame(results)
