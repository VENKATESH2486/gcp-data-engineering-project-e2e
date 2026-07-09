from datetime import datetime
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)

from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryInsertJobOperator,
)

from utils.config import (
    PROJECT_ID,
    BUCKET_NAME,
    DATASET,
    BRONZE_CUSTOMERS_TABLE,
    RAW_FOLDER,
    ARCHIVE_FOLDER,
    GOOGLE_CONN_ID,
    CUSTOMER_FILE ,
    SILVER_CUSTOMERS_TABLE,
    GOLD_CUSTOMER_SUMMARY_TABLE,
    BQ_LOCATION,
)
from utils.sql_utils import load_sql
from services.ingestion_service import validate_customer_file
from datetime import timedelta

default_args = {
    "owner": "venkatesh",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

DEFAULT_OBJECT = f"{RAW_FOLDER}/{CUSTOMER_FILE}"
OBJECT_NAME = "{{ dag_run.conf.get('object', '" + DEFAULT_OBJECT + "') }}"

DEFAULT_BUCKET = BUCKET_NAME
BUCKET = "{{ dag_run.conf.get('bucket', '" + DEFAULT_BUCKET + "') }}"

ARCHIVE_OBJECT = "{{ dag_run.conf.get('object', '" + DEFAULT_OBJECT + "').replace('raw/', 'archive/') }}"

with DAG(
    dag_id="customer_ingestion",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=[
        "gcp",
        "medallion",
        "customer",
        "bigquery",
    ],
    default_args=default_args,
) as dag:

    start = EmptyOperator(
        task_id="start"
    )

    wait_for_customer_file = GCSObjectExistenceSensor(
        task_id="wait_for_customer_file",
        bucket=BUCKET,
        object=OBJECT_NAME,
        google_cloud_conn_id=GOOGLE_CONN_ID,
        poke_interval=60,
        timeout=60 * 60,
    )

    validate_customer = PythonOperator(
        task_id="validate_customer_file",
        python_callable=validate_customer_file,
        op_kwargs={
            "bucket_name": BUCKET,
            "object_name": OBJECT_NAME,
        },
    )

    load_customers = GCSToBigQueryOperator(
        task_id="load_customers_to_bigquery",
        bucket=BUCKET,
        source_objects=[OBJECT_NAME],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET}.{BRONZE_CUSTOMERS_TABLE}",
        source_format="CSV",
        skip_leading_rows=1,
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )

    bronze_to_silver = BigQueryInsertJobOperator(
        task_id="bronze_to_silver",
        configuration={
            "query": {
                "query": load_sql("bronze_to_silver.sql").format(
                project_id=PROJECT_ID,
                dataset=DATASET,
                bronze_table=BRONZE_CUSTOMERS_TABLE,
                silver_table=SILVER_CUSTOMERS_TABLE
            ),
                "useLegacySql": False,
            }
        },
        location=BQ_LOCATION,
    )

    silver_to_gold = BigQueryInsertJobOperator(
        task_id="silver_to_gold",
        configuration={
            "query": {
                "query": load_sql("silver_to_gold.sql").format(
                project_id=PROJECT_ID,
                dataset=DATASET,
                silver_table=SILVER_CUSTOMERS_TABLE,
                gold_table=GOLD_CUSTOMER_SUMMARY_TABLE
            ),
                "useLegacySql": False,
            }
        },
        location=BQ_LOCATION,
    )

    archive_customer_file = GCSToGCSOperator(
        task_id="archive_customer_file",
        source_bucket=BUCKET,
        source_object=OBJECT_NAME,
        destination_bucket=BUCKET,
        destination_object=ARCHIVE_OBJECT,
        move_object=True,
    )

    audit_pipeline = BigQueryInsertJobOperator(
        task_id="audit_pipeline",

        configuration={
            "query": {
                "query": load_sql("audit_success.sql").format(
                    project_id=PROJECT_ID,
                    dataset=DATASET,

                    bronze_table=BRONZE_CUSTOMERS_TABLE,
                    silver_table=SILVER_CUSTOMERS_TABLE,
                    gold_table=GOLD_CUSTOMER_SUMMARY_TABLE,

                    source_file=OBJECT_NAME,
                ),
                "useLegacySql": False,
            }
        },

        location=BQ_LOCATION,
    )

    end = EmptyOperator(
        task_id="end"
    )

    start >> wait_for_customer_file >> validate_customer >> load_customers >> bronze_to_silver >> silver_to_gold >> audit_pipeline >> archive_customer_file >> end