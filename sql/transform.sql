-- Aggregate EACH source to location/day BEFORE joining. Never multiply payroll by orders.
CREATE TABLE mart_daily AS
WITH s AS (
 SELECT date_id, location_id, COUNT(*) transactions, SUM(quantity) units,
 SUM(list_sales) list_sales, SUM(discount) discounts, SUM(refund) refunds,
 SUM(CASE WHEN refund>0 THEN 1 ELSE 0 END) refunded_transactions,
 SUM(list_sales-discount-refund) revenue, SUM(cogs) cogs, SUM(channel_fee) channel_fees,
 COUNT(DISTINCT CASE WHEN customer_id<>0 THEN customer_id END) customers
 FROM fact_sales GROUP BY date_id,location_id
), l AS (
 SELECT date_id,location_id,SUM(hours) labour_hours,SUM(labour_cost) labour_cost
 FROM fact_labour GROUP BY date_id,location_id
), i AS (
 SELECT date_id,location_id,SUM(1-available) stockouts,COUNT(*) inventory_checks
 FROM fact_inventory GROUP BY date_id,location_id
), f AS (
 SELECT s.date_id,s.location_id,SUM(f.rating) rating_sum,COUNT(*) responses
 FROM fact_feedback f JOIN fact_sales s USING(sale_id) GROUP BY s.date_id,s.location_id
)
SELECT d.date_id,d.month,d.week_start,d.weekday,x.location_id,x.name,x.state,x.region,
 COALESCE(s.transactions,0) transactions,COALESCE(s.units,0) units,
 COALESCE(s.list_sales,0) list_sales,COALESCE(s.discounts,0) discounts,COALESCE(s.refunds,0) refunds,
 COALESCE(s.refunded_transactions,0) refunded_transactions,COALESCE(s.revenue,0) revenue,
 COALESCE(s.cogs,0) cogs,COALESCE(s.channel_fees,0) channel_fees,
 COALESCE(s.customers,0) customers,l.labour_hours,l.labour_cost,i.stockouts,i.inventory_checks,
 COALESCE(f.rating_sum,0) rating_sum,COALESCE(f.responses,0) responses,
 o.overhead,p.campaign_spend,
 COALESCE(s.revenue-s.cogs,0) gross_profit,
 COALESCE(s.revenue-s.cogs-s.channel_fees,0)-l.labour_cost-o.overhead-p.campaign_spend operating_profit
FROM dim_date d CROSS JOIN dim_location x
LEFT JOIN s ON s.date_id=d.date_id AND s.location_id=x.location_id
JOIN l ON l.date_id=d.date_id AND l.location_id=x.location_id
JOIN i ON i.date_id=d.date_id AND i.location_id=x.location_id
LEFT JOIN f ON f.date_id=d.date_id AND f.location_id=x.location_id
JOIN fact_operating_costs o ON o.date_id=d.date_id AND o.location_id=x.location_id
JOIN fact_promotions p ON p.date_id=d.date_id AND p.location_id=x.location_id;
CREATE UNIQUE INDEX daily_key ON mart_daily(location_id,date_id);

CREATE VIEW mart_monthly AS
WITH monthly AS (
 SELECT month,location_id,name,state,SUM(revenue) revenue,SUM(transactions) transactions,
 SUM(gross_profit) gross_profit,SUM(operating_profit) operating_profit,
 SUM(labour_cost) labour_cost,SUM(labour_hours) labour_hours
 FROM mart_daily GROUP BY month,location_id
)
SELECT *, LAG(revenue) OVER(PARTITION BY location_id ORDER BY month) previous_revenue,
 revenue-LAG(revenue) OVER(PARTITION BY location_id ORDER BY month) revenue_variance,
 AVG(revenue) OVER(PARTITION BY location_id ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) rolling_3m_revenue,
 DENSE_RANK() OVER(PARTITION BY month ORDER BY operating_profit) profit_attention_rank
FROM monthly;

-- Anonymous guest ID 0 is never interpreted as a real customer.
CREATE TABLE mart_customer_month AS
SELECT customer_id,substr(date_id,1,7) month,COUNT(*) orders,
 SUM(list_sales-discount-refund) revenue
FROM fact_sales WHERE customer_id<>0 GROUP BY customer_id,substr(date_id,1,7);
CREATE UNIQUE INDEX customer_month_key ON mart_customer_month(customer_id,month);
CREATE INDEX customer_month_period ON mart_customer_month(month);
CREATE TABLE mart_retention AS
WITH active AS (SELECT month,COUNT(*) active_customers FROM mart_customer_month GROUP BY month),
 retained AS (
 SELECT a.month,COUNT(*) retained_customers FROM mart_customer_month a
 JOIN mart_customer_month b ON a.customer_id=b.customer_id
 AND b.month=strftime('%Y-%m',date(a.month||'-01','+1 month')) GROUP BY a.month
)
SELECT a.month,a.active_customers,COALESCE(r.retained_customers,0) retained_customers,
 CASE WHEN a.month<(SELECT MAX(month) FROM mart_customer_month)
 THEN 1.0*COALESCE(r.retained_customers,0)/a.active_customers ELSE NULL END retention
FROM active a LEFT JOIN retained r USING(month);
CREATE TABLE mart_cohorts AS
WITH first_month AS (SELECT customer_id,MIN(month) cohort FROM mart_customer_month GROUP BY customer_id),
 sizes AS (SELECT cohort,COUNT(*) cohort_size FROM first_month GROUP BY cohort)
SELECT c.cohort,m.month,s.cohort_size,COUNT(*) active_customers,
 1.0*COUNT(*)/s.cohort_size retention
FROM first_month c JOIN mart_customer_month m USING(customer_id)
JOIN sizes s USING(cohort) GROUP BY c.cohort,m.month;
