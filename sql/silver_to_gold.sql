CREATE OR REPLACE TABLE
`{project_id}.{dataset}.{gold_table}`
PARTITION BY processing_date
CLUSTER BY country
AS

SELECT
    country,
    city,

    COUNT(*) AS customer_count,

    MIN(created_date) AS first_customer,
    MAX(created_date) AS latest_customer,

    CURRENT_TIMESTAMP() AS processed_at,
    CURRENT_DATE() AS processing_date

FROM
    `{project_id}.{dataset}.{silver_table}`

GROUP BY
    country,
    city
;