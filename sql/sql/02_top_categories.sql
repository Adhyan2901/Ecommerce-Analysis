-- Q2: Top 10 product categories by revenue and share of total
-- Rules: delivered orders only; revenue = item price + freight (R$)
-- Window: Jan 2017 - Aug 2018 (same as Q1)
WITH category_revenue AS (
    SELECT
        COALESCE(t.product_category_name_english,
                 p.product_category_name,
                 'unknown') AS category,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(oi.price + oi.freight_value)::numeric AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN product_category_name_translation t
           ON t.product_category_name = p.product_category_name
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
    GROUP BY 1
)
SELECT
    category,
    orders,
    ROUND(revenue, 2) AS revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS pct_of_total,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC)
          / SUM(revenue) OVER (), 1) AS cumulative_pct
FROM category_revenue
ORDER BY revenue DESC
LIMIT 10;