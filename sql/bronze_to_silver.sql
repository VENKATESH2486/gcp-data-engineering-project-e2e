-- ============================================================================
-- Bronze to Silver Transformation: Customer Data Cleaning & Standardization
-- ============================================================================
-- Purpose: Transform raw customer data into clean, business-ready format
-- Transformations:
--   1. Trim whitespace from all string fields
--   2. Normalize email casing (lowercase)
--   3. Standardize city and country names (title case)
--   4. Cast dates explicitly to DATE type
--   5. Remove duplicates using ROW_NUMBER() window function
-- ============================================================================

CREATE OR REPLACE TABLE `{project_id}.{dataset}.{silver_table}` 
PARTITION BY created_date
CLUSTER BY customer_id
AS
WITH cleaned AS (
  -- =========================================================================
  -- CTE 1: Data Cleaning & Standardization
  -- =========================================================================
  SELECT
    -- Primary Key (unchanged)
    customer_id,
    
    -- Customer Name Fields (trimmed & title-cased)
    TRIM(first_name) AS first_name,
    TRIM(last_name) AS last_name,
    
    -- Email (normalized to lowercase, trimmed)
    LOWER(TRIM(email)) AS email,
    
    -- Location Fields (standardized format)
    INITCAP(TRIM(city)) AS city,
    INITCAP(TRIM(country)) AS country,
    
    -- Dates (explicitly cast to DATE and TIMESTAMP)
    created_at AS created_date,
    TIMESTAMP(created_at) AS created_timestamp,
    
    -- Metadata
    CURRENT_TIMESTAMP() AS processed_at
  FROM
    `{project_id}.{dataset}.{bronze_table}`
),
ranked AS (
  -- =========================================================================
  -- CTE 2: Deduplication using ROW_NUMBER window function
  -- =========================================================================
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY customer_id
      ORDER BY created_timestamp DESC
    ) AS row_num
  FROM
    cleaned
)
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    city,
    country,
    created_date,
    created_timestamp,
    processed_at
FROM ranked
WHERE row_num = 1
;