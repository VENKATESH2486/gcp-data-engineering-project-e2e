INSERT INTO `{project_id}.audit.pipeline_run_log`
(
    run_id,
    dag_id,
    pipeline_name,

    execution_date,

    source_file,

    bronze_table,
    silver_table,
    gold_table,

    bronze_row_count,
    silver_row_count,
    gold_row_count,

    status,

    start_time,
    end_time,

    duration_seconds,

    processed_at
)

SELECT

    '{run_id}',

    '{dag_id}',

    'Customer Ingestion Pipeline',

    TIMESTAMP('{execution_date}'),

    '{source_file}',

    '{bronze_table}',

    '{silver_table}',

    '{gold_table}',

    (
        SELECT COUNT(*)
        FROM `{project_id}.{dataset}.{bronze_table}`
    ),

    (
        SELECT COUNT(*)
        FROM `{project_id}.{dataset}.{silver_table}`
    ),

    (
        SELECT COUNT(*)
        FROM `{project_id}.{dataset}.{gold_table}`
    ),

    'SUCCESS',

    TIMESTAMP('{start_time}'),

    CURRENT_TIMESTAMP(),

    TIMESTAMP_DIFF(
        CURRENT_TIMESTAMP(),
        TIMESTAMP('{start_time}'),
        SECOND
    ),

    CURRENT_TIMESTAMP();