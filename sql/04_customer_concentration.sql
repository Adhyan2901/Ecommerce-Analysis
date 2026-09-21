-- Q4: Revenue concentration across customers (spend quintiles)
-- Rules: delivered orders, Jan 2017 - Aug 2018; revenue = price + freight (R$)
-- A customer is customer_unique_id (customer_id changes with every order)
WITH customer_revenue AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(oi.price + oi.freight_value)::numeric AS revenue
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
    GROUP BY c.customer_unique_id
),
bucketed AS (
    SELECT
        *,
        NTILE(5) OVER (ORDER BY revenue DESC) AS spend_quintile
    FROM customer_revenue
)
SELECT
    spend_quintile,
    COUNT(*) AS customers,
    ROUND(SUM(revenue), 0) AS revenue,
    ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS pct_of_revenue,
    ROUND(100.0 * SUM(SUM(revenue)) OVER (ORDER BY spend_quintile)
          / SUM(SUM(revenue)) OVER (), 1) AS cumulative_pct,
    ROUND(AVG(revenue), 2) AS avg_spend,
    ROUND(MIN(revenue), 2) AS min_spend,
    ROUND(MAX(revenue), 2) AS max_spend,
    ROUND(AVG(orders), 2) AS avg_orders
FROM bucketed
GROUP BY spend_quintile
ORDER BY spend_quintile;