-- Q7: Payment method mix and average order value
-- Rules: delivered orders, Jan 2017 - Aug 2018 (R$)
-- Payments are aggregated to ONE row per order before anything else,
-- because 2,961 orders have more than one payment row.
-- main_method = the payment type covering the largest part of the order.
-- order_paid = total of all payment rows for the order.
WITH pay AS (
    SELECT
        order_id,
        SUM(payment_value)::numeric AS order_paid,
        COUNT(DISTINCT payment_type) AS methods_used,
        (ARRAY_AGG(payment_type ORDER BY payment_value DESC, payment_sequential))[1] AS main_method
    FROM order_payments
    GROUP BY order_id
)
SELECT
    p.main_method,
    COUNT(*) AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_orders,
    ROUND(SUM(p.order_paid), 0) AS total_paid,
    ROUND(100.0 * SUM(p.order_paid) / SUM(SUM(p.order_paid)) OVER (), 1) AS pct_of_paid,
    ROUND(AVG(p.order_paid), 2) AS avg_order_value,
    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY p.order_paid))::numeric, 2) AS median_order_value,
    ROUND(100.0 * COUNT(*) FILTER (WHERE p.methods_used > 1) / COUNT(*), 1) AS pct_multi_method
FROM pay p
JOIN orders o ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp <  '2018-09-01'
GROUP BY p.main_method
ORDER BY orders DESC;