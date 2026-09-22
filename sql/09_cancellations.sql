-- Q9: Cancellation, unavailable, and in-progress rates by purchase month
-- Rules: ALL order statuses, Jan 2017 - Aug 2018 (by purchase date).
-- canceled     = order_status 'canceled'
-- unavailable  = order_status 'unavailable'
-- in_progress  = shipped, invoiced, processing, created, approved
-- Status is a snapshot from when the data was extracted.
WITH orders_window AS (
    SELECT
        order_id,
        order_status,
        DATE_TRUNC('month', order_purchase_timestamp) AS month
    FROM orders
    WHERE order_purchase_timestamp >= '2017-01-01'
      AND order_purchase_timestamp <  '2018-09-01'
)
SELECT
    COALESCE(TO_CHAR(month, 'YYYY-MM'), 'TOTAL') AS month_label,
    COUNT(*) AS orders,
    COUNT(*) FILTER (WHERE order_status = 'delivered') AS delivered,
    COUNT(*) FILTER (WHERE order_status = 'canceled') AS canceled,
    ROUND(100.0 * COUNT(*) FILTER (WHERE order_status = 'canceled') / COUNT(*), 2) AS canceled_pct,
    COUNT(*) FILTER (WHERE order_status = 'unavailable') AS unavailable,
    ROUND(100.0 * COUNT(*) FILTER (WHERE order_status = 'unavailable') / COUNT(*), 2) AS unavailable_pct,
    COUNT(*) FILTER (WHERE order_status NOT IN ('delivered', 'canceled', 'unavailable')) AS in_progress,
    ROUND(100.0 * COUNT(*) FILTER (WHERE order_status NOT IN ('delivered', 'canceled', 'unavailable'))
          / COUNT(*), 2) AS in_progress_pct
FROM orders_window
GROUP BY ROLLUP (month)
ORDER BY month NULLS LAST;