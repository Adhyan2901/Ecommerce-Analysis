-- Q1: Monthly revenue, revenue per order, and MoM growth
-- Rules: delivered orders only; revenue = item price + freight (R$)
-- Window: Jan 2017 - Aug 2018 (earlier and later months are too small or empty)
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(oi.price + oi.freight_value)::numeric AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
    GROUP BY 1
)
SELECT
    month::date AS month,
    orders,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue / orders, 2) AS revenue_per_order,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
        1
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;