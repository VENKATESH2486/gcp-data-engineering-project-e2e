from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime

with DAG(
    dag_id="hello_world",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["demo"],
) as dag:

    start = EmptyOperator(task_id="start")

    end = EmptyOperator(task_id="end")

    start >> end