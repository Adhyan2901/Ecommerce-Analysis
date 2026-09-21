-- 00_exploration.sql
-- Data validation checks run after loading the Olist data

-- 1. Row counts per table
SELECT 'orders' AS tbl, COUNT(*) FROM orders
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL SELECT 'geolocation', COUNT(*) FROM geolocation;

-- 2. customer_id vs customer_unique_id (customer_id is per order)
SELECT COUNT(DISTINCT customer_id) AS customer_ids,
       COUNT(DISTINCT customer_unique_id) AS real_customers
FROM customers;

-- 3. Order statuses, duplicate checks, and date range in one labelled table
SELECT 'status: ' || order_status AS check_name, COUNT(*)::text AS result
FROM orders
GROUP BY order_status

UNION ALL
SELECT 'orders with >1 payment row', COUNT(*)::text
FROM (SELECT order_id FROM order_payments GROUP BY order_id HAVING COUNT(*) > 1) t

UNION ALL
SELECT 'orders with >1 review', COUNT(*)::text
FROM (SELECT order_id FROM order_reviews GROUP BY order_id HAVING COUNT(*) > 1) t

UNION ALL
SELECT 'first order date', MIN(order_purchase_timestamp)::text FROM orders

UNION ALL
SELECT 'last order date', MAX(order_purchase_timestamp)::text FROM orders;

-- 4. Check exact column names (some are misspelled in the source data)
SELECT * FROM products LIMIT 5;