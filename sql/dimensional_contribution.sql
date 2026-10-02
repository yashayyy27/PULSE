-- Parameterised dates and store; dimension expression is chosen by a strict allow-list in Python.
-- Revenue contributions reconcile to company/store revenue movement. No causal interpretation.
WITH periods AS (
 SELECT {dimension} entity,
 SUM(CASE WHEN s.date_id BETWEEN :current_start AND :current_end
     THEN s.list_sales-s.discount-s.refund ELSE 0 END) current_revenue,
 SUM(CASE WHEN s.date_id BETWEEN :prior_start AND :prior_end
     THEN s.list_sales-s.discount-s.refund ELSE 0 END) prior_revenue
 FROM fact_sales s
 JOIN dim_location l USING(location_id) JOIN dim_product p USING(product_id)
 JOIN dim_channel ch USING(channel_id) JOIN dim_customer c USING(customer_id)
 JOIN dim_promotion pr USING(promotion_id) JOIN dim_date d USING(date_id)
 WHERE s.date_id BETWEEN :prior_start AND :current_end
 AND (:location IS NULL OR s.location_id=:location)
 GROUP BY {dimension}
)
SELECT *,current_revenue-prior_revenue contribution,
 DENSE_RANK() OVER(ORDER BY current_revenue-prior_revenue) attention_rank
FROM periods ORDER BY contribution;
