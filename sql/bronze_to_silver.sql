-- Bronze to Silver transformation SQL
-- Use this script to clean and standardize raw data
CREATE OR REPLACE TABLE `enduring-coil-501604-u1.retail.silver_customers` AS
SELECT
    customer_id,
    TRIM(first_name) AS first_name,
    TRIM(last_name) AS last_name,
    LOWER(TRIM(email)) AS email,
    INITCAP(TRIM(city)) AS city,
    UPPER(TRIM(country)) AS country,
    DATE(created_at) AS created_at
FROM
    `enduring-coil-501604-u1.retail.bronze_customers`

QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY created_at DESC
) = 1;