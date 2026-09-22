-- Q10: Cumulative revenue and 3-month rolling average
-- Rules: delivered orders, Jan 2017 - Aug 2018; revenue = price + freight (R$)
-- Same monthly base as Q1.
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
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
    ROUND(revenue, 0) AS revenue,
    ROUND(SUM(revenue) OVER (ORDER BY month), 0) AS cumulative_revenue,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY month)
          / SUM(revenue) OVER (), 1) AS cumulative_pct,
    CASE WHEN COUNT(*) OVER (ORDER BY month) >= 3
         THEN ROUND(AVG(revenue) OVER (
                  ORDER BY month
                  ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0)
    END AS rolling_3m_avg
FROM monthly
ORDER BY month;