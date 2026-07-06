from datetime import datetime
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)

PROJECT_ID = "enduring-coil-501604-u1"
BUCKET_NAME = "de-pipeline-venkatesh-501604"
DATASET = "retail"
TABLE = "bronze_customers"

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
        object="raw/customer.csv",
        google_cloud_conn_id="google_cloud_default",
        poke_interval=60,
        timeout=60 * 60,
    )

    load_customers = GCSToBigQueryOperator(
        task_id="load_customers_to_bigquery",
        bucket=BUCKET_NAME,
        source_objects=["raw/customer.csv"],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET}.{TABLE}",
        source_format="CSV",
        skip_leading_rows=1,
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )
    
    archive_customer_file = GCSToGCSOperator(
        task_id="archive_customer_file",
        source_bucket=BUCKET_NAME,
        source_object="raw/customer.csv",
        destination_bucket=BUCKET_NAME,
        destination_object="archive/customer.csv",
        move_object=True,
    )

    end = EmptyOperator(
        task_id="end"
    )

    start >> wait_for_customer_file >> load_customers >> archive_customer_file >> end