-- Silver to Gold transformation SQL
-- Use this script to aggregate and prepare final analytics tables

SELECT
    customer_id,
    COUNT(order_id) AS order_count,
    SUM(quantity * price) AS total_spent
FROM silver.orders
JOIN silver.products USING (product_id)
GROUP BY customer_id;
