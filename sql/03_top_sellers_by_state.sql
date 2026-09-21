-- Q3: Top 3 sellers by revenue within each seller state
-- Rules: delivered orders only; revenue = item price + freight (R$)
-- Window: Jan 2017 - Aug 2018 (same as Q1 and Q2)
WITH seller_revenue AS (
    SELECT
        s.seller_state,
        s.seller_id,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(oi.price + oi.freight_value)::numeric AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN sellers s ON s.seller_id = oi.seller_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
    GROUP BY s.seller_state, s.seller_id
),
ranked AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY seller_state ORDER BY revenue DESC) AS state_rank,
        SUM(revenue) OVER (PARTITION BY seller_state) AS state_revenue
    FROM seller_revenue
)
SELECT
    seller_state,
    state_rank,
    seller_id,
    orders,
    ROUND(revenue, 2) AS revenue,
    ROUND(100.0 * revenue / state_revenue, 1) AS pct_of_state_revenue
FROM ranked
WHERE state_rank <= 3
ORDER BY state_revenue DESC, seller_state, state_rank;