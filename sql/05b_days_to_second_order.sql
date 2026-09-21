-- Q5b: Repeat rate and time from first to second order
-- Rules: delivered orders, Jan 2017 - Aug 2018
-- Mature-cohort rate: only customers whose first order is at least ~90 days
-- before the end of the window (first order before 2018-06-03), so every
-- customer in that group had a full 90 days to come back.
WITH delivered AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp AS purchased_at
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
),
numbered AS (
    SELECT
        customer_unique_id,
        purchased_at,
        ROW_NUMBER() OVER (
            PARTITION BY customer_unique_id
            ORDER BY purchased_at, order_id
        ) AS order_num
    FROM delivered
),
first_second AS (
    SELECT
        customer_unique_id,
        MIN(purchased_at) FILTER (WHERE order_num = 1) AS first_order,
        MIN(purchased_at) FILTER (WHERE order_num = 2) AS second_order
    FROM numbered
    GROUP BY customer_unique_id
)
SELECT
    COUNT(*) AS customers,
    COUNT(second_order) AS repeat_customers,
    ROUND(100.0 * COUNT(second_order) / COUNT(*), 2) AS repeat_rate_pct,
    ROUND(100.0 * COUNT(*) FILTER (
              WHERE first_order < '2018-06-03'
                AND second_order < first_order + INTERVAL '90 days')
          / NULLIF(COUNT(*) FILTER (WHERE first_order < '2018-06-03'), 0),
          2) AS repeat_90d_pct_mature_cohort,
    ROUND(100.0 * COUNT(*) FILTER (
              WHERE second_order::date = first_order::date)
          / NULLIF(COUNT(second_order), 0), 1) AS pct_repeats_same_day,
    ROUND(100.0 * COUNT(*) FILTER (
              WHERE second_order <= first_order + INTERVAL '30 days')
          / NULLIF(COUNT(second_order), 0), 1) AS pct_repeats_within_30d,
    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (
              ORDER BY EXTRACT(EPOCH FROM (second_order - first_order)) / 86400
          ))::numeric, 0) AS median_days_to_second
FROM first_second;