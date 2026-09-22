-- Q8: Installments vs order value (credit card orders only)
-- Rules: delivered orders, Jan 2017 - Aug 2018 (R$)
-- Only orders paid entirely by credit card (no voucher/boleto mixed in).
-- installments = installments of the largest card payment in the order.
-- Order value = item price + freight from order_items, NOT the amount paid,
-- because installment interest can inflate payment_value.
-- Both CTEs return ONE row per order, so the join cannot multiply rows.
WITH card_orders AS (
    SELECT
        order_id,
        SUM(payment_value)::numeric AS order_paid,
        (ARRAY_AGG(payment_installments
                   ORDER BY payment_value DESC, payment_sequential))[1] AS installments
    FROM order_payments
    GROUP BY order_id
    HAVING COUNT(DISTINCT payment_type) = 1
       AND MIN(payment_type) = 'credit_card'
),
item_value AS (
    SELECT
        order_id,
        SUM(price + freight_value)::numeric AS items_total
    FROM order_items
    GROUP BY order_id
),
joined AS (
    SELECT
        c.installments,
        c.order_paid,
        iv.items_total
    FROM card_orders c
    JOIN item_value iv ON iv.order_id = c.order_id
    JOIN orders o ON o.order_id = c.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
)
SELECT
    CASE WHEN installments <= 1  THEN '1. Paid in full (1)'
         WHEN installments <= 3  THEN '2. 2-3 installments'
         WHEN installments <= 6  THEN '3. 4-6 installments'
         WHEN installments <= 9  THEN '4. 7-9 installments'
         ELSE                         '5. 10+ installments' END AS installment_bucket,
    COUNT(*) AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_orders,
    ROUND(AVG(items_total), 2) AS avg_order_value,
    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY items_total))::numeric, 2) AS median_order_value,
    ROUND(AVG(order_paid), 2) AS avg_paid,
    ROUND(100.0 * (SUM(order_paid) / SUM(items_total) - 1), 1) AS paid_over_items_pct
FROM joined
GROUP BY 1
ORDER BY 1;