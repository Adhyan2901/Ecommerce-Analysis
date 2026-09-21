-- Q6: Does late delivery lower review scores?
-- Rules: delivered orders, Jan 2017 - Aug 2018, with a delivery date and
-- at least one review. One review per order (the latest), because 547
-- orders have more than one review.
-- delay_days = actual delivery date - estimated delivery date (negative = early)
WITH latest_review AS (
    SELECT order_id, review_score
    FROM (
        SELECT
            order_id,
            review_score,
            ROW_NUMBER() OVER (
                PARTITION BY order_id
                ORDER BY review_answer_timestamp DESC NULLS LAST, review_id DESC
            ) AS rn
        FROM order_reviews
    ) r
    WHERE rn = 1
),
order_delay AS (
    SELECT
        o.order_id,
        (o.order_delivered_customer_date::date
         - o.order_estimated_delivery_date::date) AS delay_days,
        lr.review_score
    FROM orders o
    JOIN latest_review lr ON lr.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
)
SELECT
    CASE WHEN delay_days <= -8 THEN '1. Early by 8+ days'
         WHEN delay_days <= -1 THEN '2. Early by 1-7 days'
         WHEN delay_days = 0   THEN '3. On the estimated date'
         WHEN delay_days <= 3  THEN '4. Late by 1-3 days'
         WHEN delay_days <= 7  THEN '5. Late by 4-7 days'
         ELSE '6. Late by 8+ days' END AS delivery_bucket,
    COUNT(*) AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_orders,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(100.0 * COUNT(*) FILTER (WHERE review_score <= 2) / COUNT(*), 1) AS pct_1_2_stars,
    ROUND(100.0 * COUNT(*) FILTER (WHERE review_score = 5) / COUNT(*), 1) AS pct_5_stars
FROM order_delay
GROUP BY 1
ORDER BY 1;