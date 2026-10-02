"""Conditional operational exposure estimates, separated from observed ledger."""

from pulse.runtime import query


def stockout_opportunity(start, end, location=None, path=None, substitution=0.5):
    if not 0 <= substitution <= 1:
        raise ValueError("Substitution must be 0–1")
    # Match store/SKU/weekday within the selected interval, using only available days.
    sql = """WITH sales AS (
        SELECT date_id,location_id,product_id,SUM(list_sales-discount-refund) revenue,
        SUM(list_sales-discount-refund-cogs) profit FROM fact_sales
        WHERE date_id BETWEEN :start AND :end GROUP BY date_id,location_id,product_id
    ), observations AS (
        SELECT i.*,d.weekday,COALESCE(s.revenue,0) revenue,COALESCE(s.profit,0) profit
        FROM fact_inventory i JOIN dim_date d USING(date_id)
        LEFT JOIN sales s ON s.date_id=i.date_id AND s.location_id=i.location_id AND s.product_id=i.product_id
        WHERE i.date_id BETWEEN :start AND :end AND (:location IS NULL OR i.location_id=:location)
    ), reference AS (
        SELECT location_id,product_id,weekday,AVG(revenue) expected_sales,AVG(profit) expected_profit,COUNT(*) sample_days
        FROM observations WHERE available=1 GROUP BY location_id,product_id,weekday
    )
    SELECT p.name product,p.category,COUNT(*) outage_days,
        SUM(CASE WHEN r.sample_days>=3 THEN r.expected_sales ELSE 0 END) reference_sales,
        SUM(CASE WHEN r.sample_days>=3 THEN r.expected_profit ELSE 0 END) reference_profit,
        SUM(CASE WHEN r.sample_days>=3 THEN 1 ELSE 0 END) supported_outage_days
    FROM observations o JOIN dim_product p USING(product_id)
    LEFT JOIN reference r ON r.location_id=o.location_id AND r.product_id=o.product_id AND r.weekday=o.weekday
    WHERE o.available=0 GROUP BY p.name,p.category"""
    frame = query(sql, {"start": start, "end": end, "location": location}, path)
    frame["estimated_revenue_opportunity"] = frame.reference_sales * (1 - substitution)
    frame["estimated_gross_profit_opportunity"] = frame.reference_profit * (1 - substitution)
    return frame


def annualise(weekly_exposure):
    return {
        "estimated_weekly_exposure": weekly_exposure,
        "conditional_annualised_exposure": weekly_exposure * 52,
        "assumption": "Same weekly gap persists for 52 weeks; no recovery, seasonality or management response. Not a forecast.",
    }
