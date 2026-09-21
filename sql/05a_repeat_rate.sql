-- Q5a: How many customers ordered once, twice, or 3+ times?
-- Rules: delivered orders, Jan 2017 - Aug 2018
-- Customer = customer_unique_id (customer_id changes with every order)
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS orders
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp >= '2017-01-01'
      AND o.order_purchase_timestamp <  '2018-09-01'
    GROUP BY c.customer_unique_id
)
SELECT
    CASE WHEN orders = 1 THEN '1 order'
         WHEN orders = 2 THEN '2 orders'
         ELSE '3+ orders' END AS order_bucket,
    COUNT(*) AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_customers,
    SUM(orders) AS orders,
    ROUND(100.0 * SUM(orders) / SUM(SUM(orders)) OVER (), 2) AS pct_of_orders
FROM customer_orders
GROUP BY 1
ORDER BY 1;