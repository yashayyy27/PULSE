"""Single-period what-if ledger with explicit independent assumptions."""

from dataclasses import dataclass
import math

from pulse.metrics.registry import calculate


@dataclass(frozen=True)
class Assumptions:
    price_change: float = 0
    transaction_change: float = 0
    basket_change: float = 0
    hours_change: float = 0
    wage_change: float = 0
    retention_change: float = 0
    promotion_uptake_change: float = 0
    discount_rate: float | None = None
    product_margin: float | None = None


def simulate(baseline, assumptions=Assumptions()):
    b = dict(baseline)
    for key in [
        "list_sales",
        "discounts",
        "refunds",
        "transactions",
        "cogs",
        "channel_fees",
        "labour_hours",
        "labour_cost",
        "overhead",
        "campaign_spend",
    ]:
        if key not in b or not math.isfinite(b[key]) or b[key] < 0:
            raise ValueError("Baseline needs finite nonnegative ledger inputs")
    if b["list_sales"] <= 0 or b["transactions"] <= 0 or b["labour_hours"] <= 0:
        raise ValueError("Positive sales, orders and hours required")
    for field in [
        "price_change",
        "transaction_change",
        "basket_change",
        "hours_change",
        "wage_change",
        "retention_change",
        "promotion_uptake_change",
    ]:
        value = getattr(assumptions, field)
        if not math.isfinite(value) or not -0.5 <= value <= 0.5:
            raise ValueError(f"{field} must be between -50% and +50%")
    rate = (
        b["discounts"] / b["list_sales"]
        if assumptions.discount_rate is None
        else assumptions.discount_rate
    )
    if not math.isfinite(rate) or not 0 <= rate <= 0.8:
        raise ValueError("Discount rate must be 0–80%")
    # Uptake change is additional order share receiving 22% discount; no automatic lift.
    rate += assumptions.promotion_uptake_change * 0.22
    if not 0 <= rate <= 0.8:
        raise ValueError("Effective discount rate must remain 0–80%")
    repeat_share = b.get("repeat_rate", 0)
    if not math.isfinite(repeat_share):
        repeat_share = 0
    volume = (1 + assumptions.transaction_change) * (
        1 + assumptions.retention_change * repeat_share
    )
    basket = 1 + assumptions.basket_change
    out = b.copy()
    out["transactions"] = b["transactions"] * volume
    out["list_sales"] = b["list_sales"] * volume * basket * (1 + assumptions.price_change)
    out["discounts"] = out["list_sales"] * rate
    # Preserve refund share of post-discount sales and channel fee share of net sales.
    refund_share = (
        b["refunds"] / (b["list_sales"] - b["discounts"]) if b["list_sales"] > b["discounts"] else 0
    )
    out["refunds"] = (out["list_sales"] - out["discounts"]) * refund_share
    revenue = out["list_sales"] - out["discounts"] - out["refunds"]
    out["channel_fees"] = revenue * b["channel_fees"] / b["revenue"] if b["revenue"] else 0
    out["cogs"] = b["cogs"] * volume * basket
    if assumptions.product_margin is not None:
        margin = assumptions.product_margin
        if not math.isfinite(margin) or not 0 <= margin <= 0.95:
            raise ValueError("Product margin must be 0–95%")
        # Margin applies to pre-price list sales, preserving the independent price lever.
        out["cogs"] = b["list_sales"] * volume * basket * (1 - margin)
    out["labour_hours"] = b["labour_hours"] * (1 + assumptions.hours_change)
    out["labour_cost"] = (
        b["labour_cost"] * (1 + assumptions.hours_change) * (1 + assumptions.wage_change)
    )
    return calculate(out)


ASSUMPTION_TEXT = (
    "Single-period scenario, not a forecast. Price has no automatic elasticity; supply a demand change. "
    "Basket changes scale units and product cost; price changes do not. Loaded wage and hours multiply. "
    "Retention change scales volume by the observed repeat-customer share (an imperfect proxy for repeat-order share). "
    "Promotion uptake changes discount share by 22% times uptake change; no assumed incremental orders. "
    "Product margin means margin on pre-discount, pre-price list sales. Refund and channel-fee rates, "
    "campaign spend and overhead stay fixed in their stated units. Feasibility, service and customer response are untested."
)
