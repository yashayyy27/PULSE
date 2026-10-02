# Data dictionary and source contracts

> Portfolio simulation: Wattle & Rye, stakeholders, statements and data are fictional. No real interviews, sign-offs or achieved benefits are claimed.


AUD excluding GST; all keys synthetic. Source PK/FK/check definitions are authoritative in [schema](../../sql/schema.sql). Sale cost is captured at transaction time. No genuine PII.

## dim_date
Grain: **one calendar day**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| date_id | TEXT | PK | ISO business date; FK to calendar in dated facts |
| month | TEXT | required | YYYY-MM reporting period |
| weekday | INTEGER | required | Monday 0 through Sunday 6 |
| week_start | TEXT | required | ISO Monday of week |

## dim_location
Grain: **one fictional store**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| location_id | INTEGER | PK | Synthetic location identifier |
| name | TEXT | required | fictional entity display name |
| state | TEXT | required | NSW, VIC, QLD, WA, SA or ACT |
| region | TEXT | required | fictional state district |

## dim_product
Grain: **one SKU**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| product_id | INTEGER | PK | Synthetic product identifier |
| name | TEXT | required | fictional entity display name |
| category | TEXT | required | Kitchen, Drinks or Pantry |
| list_price | REAL | required | AUD unit price excluding GST |
| unit_cost | REAL | required | AUD reference unit product cost |

## dim_customer
Grain: **one anonymous synthetic customer; 0 means guest**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| customer_id | INTEGER | PK | Synthetic customer identifier |
| segment | TEXT | required | Regular, Convenience, Occasional or Guest |

## dim_channel
Grain: **one channel**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| channel_id | INTEGER | PK | Synthetic channel identifier |
| name | TEXT | required | fictional entity display name |
| fee_rate | REAL | required | channel fee fraction of net sales |

## dim_promotion
Grain: **one offer; 0 means none**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| promotion_id | INTEGER | PK | Synthetic promotion identifier |
| name | TEXT | required | fictional entity display name |
| discount_rate | REAL | required | offer fraction of list sales |

## dim_employee
Grain: **one fictional employee**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| employee_id | INTEGER | PK | Synthetic employee identifier |
| location_id | INTEGER | required | Synthetic location identifier |
| role | TEXT | required | fictional employee role |

## fact_sales
Grain: **one order with one featured SKU and 1–3 units**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| sale_id | INTEGER | PK | Synthetic sale identifier |
| date_id | TEXT | required | ISO business date; FK to calendar in dated facts |
| location_id | INTEGER | required | Synthetic location identifier |
| product_id | INTEGER | required | Synthetic product identifier |
| customer_id | INTEGER | required | Synthetic customer identifier |
| channel_id | INTEGER | required | Synthetic channel identifier |
| promotion_id | INTEGER | required | Synthetic promotion identifier |
| daypart | TEXT | required | Morning, Lunch or Evening |
| quantity | INTEGER | required | units in the single-SKU order |
| list_sales | REAL | required | AUD gross list amount |
| discount | REAL | required | AUD discount amount |
| refund | REAL | required | AUD revenue reversed; does not reverse COGS |
| cogs | REAL | required | AUD sale-captured product cost |
| channel_fee | REAL | required | AUD fee on net revenue |

## fact_labour
Grain: **one paid employee/day**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| labour_id | INTEGER | PK | Synthetic labour identifier |
| date_id | TEXT | required | ISO business date; FK to calendar in dated facts |
| location_id | INTEGER | required | Synthetic location identifier |
| employee_id | INTEGER | required | Synthetic employee identifier |
| hours | REAL | required | loaded paid hours per employee/day |
| labour_cost | REAL | required | AUD loaded payroll |

## fact_inventory
Grain: **one store/SKU/day snapshot**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| inventory_id | INTEGER | PK | Synthetic inventory identifier |
| date_id | TEXT | required | ISO business date; FK to calendar in dated facts |
| location_id | INTEGER | required | Synthetic location identifier |
| product_id | INTEGER | required | Synthetic product identifier |
| available | INTEGER | required | daily SKU check: 0 unavailable, 1 available |
| closing_units | INTEGER | required | synthetic units remaining |

## fact_operating_costs
Grain: **one store/day overhead**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| cost_id | INTEGER | PK | Synthetic cost identifier |
| date_id | TEXT | required | ISO business date; FK to calendar in dated facts |
| location_id | INTEGER | required | Synthetic location identifier |
| overhead | REAL | required | AUD store/day fixed operating overhead |

## fact_promotions
Grain: **one store/day campaign assignment/spend, including none**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| spend_id | INTEGER | PK | Synthetic spend identifier |
| date_id | TEXT | required | ISO business date; FK to calendar in dated facts |
| location_id | INTEGER | required | Synthetic location identifier |
| promotion_id | INTEGER | required | Synthetic promotion identifier |
| campaign_spend | REAL | required | AUD store/day campaign spend |

## fact_feedback
Grain: **one voluntary order response; at most one per order**.

| Column | SQLite type | Key / required | Business meaning |
|---|---|---|---|
| feedback_id | INTEGER | PK | Synthetic feedback identifier |
| sale_id | INTEGER | required | Synthetic sale identifier |
| rating | INTEGER | required | voluntary satisfaction response from 1 to 5 |

`mart_daily`: store/day additive ledger; source facts aggregate independently. `mart_monthly`: store/month plus LAG, ranking and trailing three-month average (first months have shorter windows). `mart_customer_month`: identified customer/month activity. `mart_retention`: company monthly transition; final month NULL. `mart_cohorts`: first-observed cohort/month activity.

[Lineage](15-data-flow.md) · [ERD and architecture](../ARCHITECTURE.md) · [KPI definitions](12-kpi-dictionary.md)