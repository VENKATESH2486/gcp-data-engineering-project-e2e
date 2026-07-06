-- Bronze to Silver transformation SQL
-- Use this script to clean and standardize raw data

SELECT
    customer_id,
    first_name,
    last_name,
    email,
    created_at
FROM bronze.customers;
