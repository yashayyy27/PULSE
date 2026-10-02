-- Observational same-store, same-weekday comparison. Campaign timing and demand confound this estimate.
WITH days AS (
 SELECT s.location_id,s.date_id,d.weekday,
 SUM(s.list_sales-s.discount-s.refund-s.cogs-s.channel_fee) contribution,
 MAX(CASE WHEN s.promotion_id>0 THEN 1 ELSE 0 END) promoted
 FROM fact_sales s JOIN dim_date d USING(date_id)
 WHERE s.date_id BETWEEN date(:start,'-56 days') AND :end GROUP BY s.location_id,s.date_id
), baseline AS (
 SELECT location_id,weekday,AVG(contribution) baseline_contribution,COUNT(*) reference_days
 FROM days WHERE promoted=0 AND date_id<:start GROUP BY location_id,weekday HAVING COUNT(*)>=3
)
SELECT pr.name,COUNT(*) campaign_days,MIN(b.reference_days) min_reference_days,SUM(fp.campaign_spend) spend,
 SUM(a.contribution-b.baseline_contribution) associated_incremental_contribution,
 (SUM(a.contribution-b.baseline_contribution)-SUM(fp.campaign_spend)) / NULLIF(SUM(fp.campaign_spend),0) promotion_roi
FROM fact_promotions fp JOIN dim_promotion pr USING(promotion_id)
JOIN days a ON a.location_id=fp.location_id AND a.date_id=fp.date_id
JOIN baseline b ON b.location_id=a.location_id AND b.weekday=a.weekday
WHERE fp.promotion_id>0 AND fp.date_id BETWEEN :start AND :end
GROUP BY pr.name;
