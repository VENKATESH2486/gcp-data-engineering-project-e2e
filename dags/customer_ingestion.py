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
)
from utils.sql_utils import load_sql
from services.ingestion_service import validate_customer_file

with DAG(
    dag_id="customer_ingestion",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["gcp", "bigquery", "bronze"],
) as dag:

    start = EmptyOperator(
        task_id="start"
    )

    wait_for_customer_file = GCSObjectExistenceSensor(
        task_id="wait_for_customer_file",
        bucket=BUCKET_NAME,
        object=f"{RAW_FOLDER}/{CUSTOMER_FILE}",
        google_cloud_conn_id=GOOGLE_CONN_ID,
        poke_interval=60,
        timeout=60 * 60,
    )

    validate_customer = PythonOperator(
        task_id="validate_customer_file",
        python_callable=validate_customer_file,
        op_kwargs={
            "bucket_name": BUCKET_NAME,
            "object_name": f"{RAW_FOLDER}/{CUSTOMER_FILE}",
        },
    )

    load_customers = GCSToBigQueryOperator(
        task_id="load_customers_to_bigquery",
        bucket=BUCKET_NAME,
        source_objects=[f"{RAW_FOLDER}/{CUSTOMER_FILE}"],
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
                "query": load_sql("bronze_to_silver.sql"),
                "useLegacySql": False,
            }
        },
        location="US",
    )
    archive_customer_file = GCSToGCSOperator(
        task_id="archive_customer_file",
        source_bucket=BUCKET_NAME,
        source_object=f"{RAW_FOLDER}/{CUSTOMER_FILE}",
        destination_bucket=BUCKET_NAME,
        destination_object=f"{ARCHIVE_FOLDER}/{CUSTOMER_FILE}",
        move_object=True,
    )

    end = EmptyOperator(
        task_id="end"
    )

    workflow = start >> wait_for_customer_file >> validate_customer >> load_customers >> bronze_to_silver >> archive_customer_file >> end