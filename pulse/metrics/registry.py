"""One central registry powers documentation, UI definitions and metric calculation."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class KPI:
    name: str
    formula: str
    source: str
    owner: str
    interpretation: str
    limitation: str
    unit: str = "AUD"
    grain: str = "selected store(s)/period"
    technical_owner: str = "Analytics steward"
    refresh: str = "Each local pipeline run; daily proposed in production"


REGISTRY = {
    "revenue": KPI(
        "Revenue",
        "list_sales - discounts - refunds",
        "mart_daily / fact_sales",
        "Finance",
        "Net sales excluding GST",
        "Refund revenue reverses; product COGS remains",
    ),
    "transactions": KPI(
        "Transactions",
        "sum(transactions)",
        "fact_sales",
        "Operations",
        "Orders including fully refunded orders",
        "Single featured SKU per synthetic order",
        "count",
    ),
    "aov": KPI(
        "Average Order Value",
        "revenue / transactions",
        "fact_sales",
        "Commercial",
        "Net revenue per order",
        "Refunds and mix affect the ratio",
    ),
    "gross_profit": KPI(
        "Gross Profit",
        "revenue - cogs",
        "fact_sales",
        "Finance",
        "Revenue after sold-product cost",
        "Not operating profit",
    ),
    "gross_margin": KPI(
        "Gross Margin %",
        "gross_profit / revenue",
        "fact_sales",
        "Finance",
        "Gross profit share of net sales",
        "Undefined when net revenue is zero",
        "ratio",
    ),
    "operating_profit": KPI(
        "Operating Profit",
        "gross_profit - labour_cost - channel_fees - overhead - campaign_spend",
        "mart_daily",
        "Finance",
        "Controllable operating ledger profit",
        "Excludes depreciation, tax, financing and central office costs",
    ),
    "operating_margin": KPI(
        "Operating Margin %",
        "operating_profit / revenue",
        "mart_daily",
        "Finance",
        "Operating profit share",
        "Weighted from sums, not averaged ratios",
        "ratio",
    ),
    "labour_cost": KPI(
        "Labour Cost",
        "sum(labour_cost)",
        "fact_labour",
        "Operations",
        "Loaded hourly payroll",
        "Synthetic rates; no award-compliant roster",
    ),
    "labour_pct": KPI(
        "Labour %",
        "labour_cost / revenue",
        "mart_daily",
        "Operations",
        "Payroll share of sales",
        "Can increase from lower demand without more hours",
        "ratio",
    ),
    "sales_per_labour_hour": KPI(
        "Sales per Labour Hour",
        "revenue / labour_hours",
        "mart_daily",
        "Operations",
        "Sales productivity",
        "Does not measure service quality",
    ),
    "customer_count": KPI(
        "Customer Count",
        "count(distinct customer_id where customer_id != 0)",
        "fact_sales",
        "Marketing",
        "Identified customers in selected period",
        "Guests excluded; never sum daily distinct counts",
        "count",
    ),
    "repeat_rate": KPI(
        "Repeat Customer Rate",
        "identified customers with >=2 orders / identified customers",
        "fact_sales",
        "Marketing",
        "Repeat within the selected period",
        "Not next-month retention",
        "ratio",
    ),
    "retention": KPI(
        "Retention",
        "active customers in month M also active in M+1 / active in M",
        "mart_retention",
        "Marketing",
        "Adjacent-month identified-customer retention",
        "Latest month right-censored; global company scope",
        "ratio",
        "company/month transition",
    ),
    "churn": KPI(
        "Churn",
        "1 - retention",
        "mart_retention",
        "Marketing",
        "No return in next month",
        "Not permanent customer loss",
        "ratio",
        "company/month transition",
    ),
    "promotion_roi": KPI(
        "Promotion ROI",
        "(associated incremental contribution - spend) / spend",
        "promotion_analysis.sql",
        "Marketing / Finance",
        "Observational campaign economics",
        "Prior 56-day same-store weekday reference (>=3 days); selection and seasonality confound incrementality",
        "ratio",
        "company/campaign/period",
    ),
    "stockout_rate": KPI(
        "Stockout Rate",
        "stockouts / inventory_checks",
        "fact_inventory",
        "Supply chain",
        "Share of daily SKU checks unavailable",
        "Daily check does not capture outage duration",
        "ratio",
    ),
    "inventory_availability": KPI(
        "Inventory Availability",
        "1 - stockout_rate",
        "fact_inventory",
        "Supply chain",
        "Share of daily checks available",
        "SKU-weighted, not sales-weighted",
        "ratio",
    ),
    "refund_rate": KPI(
        "Refund Rate",
        "refunded_transactions / transactions",
        "fact_sales",
        "Finance",
        "Share of orders receiving a refund",
        "Counts orders, not refund dollars",
        "ratio",
    ),
    "satisfaction": KPI(
        "Customer Satisfaction",
        "rating_sum / responses",
        "fact_feedback",
        "Operations",
        "Mean response rating, 1–5",
        "Response selection bias; not all customers",
        "score",
    ),
}


def ratio(numerator, denominator):
    return float(numerator / denominator) if denominator else math.nan


def calculate(ledger):
    """Derived ratios always use additive sums at the requested scope."""
    x = dict(ledger)
    x["revenue"] = x["list_sales"] - x["discounts"] - x["refunds"]
    x["gross_profit"] = x["revenue"] - x["cogs"]
    x["operating_profit"] = (
        x["gross_profit"]
        - x["labour_cost"]
        - x["channel_fees"]
        - x["overhead"]
        - x["campaign_spend"]
    )
    for key, numerator, denominator in [
        ("aov", "revenue", "transactions"),
        ("gross_margin", "gross_profit", "revenue"),
        ("operating_margin", "operating_profit", "revenue"),
        ("labour_pct", "labour_cost", "revenue"),
        ("sales_per_labour_hour", "revenue", "labour_hours"),
        ("stockout_rate", "stockouts", "inventory_checks"),
        ("refund_rate", "refunded_transactions", "transactions"),
        ("satisfaction", "rating_sum", "responses"),
    ]:
        x[key] = ratio(x.get(numerator, 0), x.get(denominator, 0))
    x["inventory_availability"] = 1 - x["stockout_rate"]
    return x
