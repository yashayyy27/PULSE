# Governed KPI dictionary

> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.


Definitions are generated from `pulse/metrics/registry.py`; update code and regenerate rather than maintaining parallel formulas.

| Key / name | Formula | Source / grain | Business / technical owner | Refresh | Interpretation / limitation |
|---|---|---|---|---|---|
| revenue: Revenue | `list_sales - discounts - refunds` | mart_daily / fact_sales; selected store(s)/period | Finance / Analytics steward | Each local pipeline run; daily proposed in production | Net sales excluding GST. Refund revenue reverses; product COGS remains |
| transactions: Transactions | `sum(transactions)` | fact_sales; selected store(s)/period | Operations / Analytics steward | Each local pipeline run; daily proposed in production | Orders including fully refunded orders. Single featured SKU per synthetic order |
| aov: Average Order Value | `revenue / transactions` | fact_sales; selected store(s)/period | Commercial / Analytics steward | Each local pipeline run; daily proposed in production | Net revenue per order. Refunds and mix affect the ratio |
| gross_profit: Gross Profit | `revenue - cogs` | fact_sales; selected store(s)/period | Finance / Analytics steward | Each local pipeline run; daily proposed in production | Revenue after sold-product cost. Not operating profit |
| gross_margin: Gross Margin % | `gross_profit / revenue` | fact_sales; selected store(s)/period | Finance / Analytics steward | Each local pipeline run; daily proposed in production | Gross profit share of net sales. Undefined when net revenue is zero |
| operating_profit: Operating Profit | `gross_profit - labour_cost - channel_fees - overhead - campaign_spend` | mart_daily; selected store(s)/period | Finance / Analytics steward | Each local pipeline run; daily proposed in production | Controllable operating ledger profit. Excludes depreciation, tax, financing and central office costs |
| operating_margin: Operating Margin % | `operating_profit / revenue` | mart_daily; selected store(s)/period | Finance / Analytics steward | Each local pipeline run; daily proposed in production | Operating profit share. Weighted from sums, not averaged ratios |
| labour_cost: Labour Cost | `sum(labour_cost)` | fact_labour; selected store(s)/period | Operations / Analytics steward | Each local pipeline run; daily proposed in production | Loaded hourly payroll. Synthetic rates; no award-compliant roster |
| labour_pct: Labour % | `labour_cost / revenue` | mart_daily; selected store(s)/period | Operations / Analytics steward | Each local pipeline run; daily proposed in production | Payroll share of sales. Can increase from lower demand without more hours |
| sales_per_labour_hour: Sales per Labour Hour | `revenue / labour_hours` | mart_daily; selected store(s)/period | Operations / Analytics steward | Each local pipeline run; daily proposed in production | Sales productivity. Does not measure service quality |
| customer_count: Customer Count | `count(distinct customer_id where customer_id != 0)` | fact_sales; selected store(s)/period | Marketing / Analytics steward | Each local pipeline run; daily proposed in production | Identified customers in selected period. Guests excluded; never sum daily distinct counts |
| repeat_rate: Repeat Customer Rate | `identified customers with >=2 orders / identified customers` | fact_sales; selected store(s)/period | Marketing / Analytics steward | Each local pipeline run; daily proposed in production | Repeat within the selected period. Not next-month retention |
| retention: Retention | `active customers in month M also active in M+1 / active in M` | mart_retention; company/month transition | Marketing / Analytics steward | Each local pipeline run; daily proposed in production | Adjacent-month identified-customer retention. Latest month right-censored; global company scope |
| churn: Churn | `1 - retention` | mart_retention; company/month transition | Marketing / Analytics steward | Each local pipeline run; daily proposed in production | No return in next month. Not permanent customer loss |
| promotion_roi: Promotion ROI | `(associated incremental contribution - spend) / spend` | promotion_analysis.sql; company/campaign/period | Marketing / Finance / Analytics steward | Each local pipeline run; daily proposed in production | Observational campaign economics. Prior 56-day same-store weekday reference (>=3 days); selection and seasonality confound incrementality |
| stockout_rate: Stockout Rate | `stockouts / inventory_checks` | fact_inventory; selected store(s)/period | Supply chain / Analytics steward | Each local pipeline run; daily proposed in production | Share of daily SKU checks unavailable. Daily check does not capture outage duration |
| inventory_availability: Inventory Availability | `1 - stockout_rate` | fact_inventory; selected store(s)/period | Supply chain / Analytics steward | Each local pipeline run; daily proposed in production | Share of daily checks available. SKU-weighted, not sales-weighted |
| refund_rate: Refund Rate | `refunded_transactions / transactions` | fact_sales; selected store(s)/period | Finance / Analytics steward | Each local pipeline run; daily proposed in production | Share of orders receiving a refund. Counts orders, not refund dollars |
| satisfaction: Customer Satisfaction | `rating_sum / responses` | fact_feedback; selected store(s)/period | Operations / Analytics steward | Each local pipeline run; daily proposed in production | Mean response rating, 1–5. Response selection bias; not all customers |

Ratios use sums at scope, not averages of store ratios. Zero denominators produce missing values. Daily `customers` is informational only: period customer counts are recomputed distinctly. Retention/churn and campaign ROI have their declared company/month or campaign scope.

[Governance](27-data-governance.md) · [Data model](13-data-dictionary.md)