# Project Overview

## What This Project Is

An end-to-end GCP data engineering portfolio project that demonstrates a production-style batch data pipeline using Google Cloud Platform services. The project ingests synthetic customer data, validates and transforms it through a medallion architecture, and loads it into BigQuery for analytics.

It is a **learning and portfolio project** — the goal is to demonstrate proficiency with real GCP tooling, not to serve a live business use case.

---

## Main Goals & Objectives

- Demonstrate an end-to-end data pipeline on GCP using industry-standard tools
- Implement a **medallion architecture** (Bronze → Silver → Gold) in BigQuery
- Orchestrate the pipeline using **Apache Airflow** (Cloud Composer)
- Validate data quality before loading into BigQuery
- Send email alerts on pipeline success/failure via SendGrid
- Archive processed files after a successful run
- Practice CI/CD for DAG deployment via GitHub Actions (`.github/`)

---

## Data Flow

```
scripts/generate_customers.py
        │
        ▼
data/customer.csv  (synthetic data, ~20,000 rows by default)
        │
        ▼  (manual or automated upload)
GCS bucket: de-pipeline-venkatesh-501604
        raw/customer.csv
        │
        ▼
Airflow DAG: customer_ingestion
        │
        ├─ GCSObjectExistenceSensor  — wait for file to land
        ├─ validate_customer_file    — schema + data quality checks
        ├─ GCSToBigQueryOperator     — raw CSV → bronze_customers
        ├─ BigQueryInsertJobOperator — bronze → silver (cleaning SQL)
        ├─ BigQueryInsertJobOperator — silver → gold (aggregation SQL)
        ├─ BigQueryInsertJobOperator — audit log entry
        └─ GCSToGCSOperator          — move file raw/ → archive/
```

---

## Key Modules

| Path | Purpose |
|---|---|
| `scripts/generate_customers.py` | Generates synthetic customer CSV using Faker. Accepts `--rows` arg (default: 20,009). |
| `data/customer.csv` | Local sample data used for development/testing. |
| `dags/customer_ingestion.py` | Main Airflow DAG — orchestrates the full pipeline. |
| `utils/config.py` | Central config: GCP project ID, bucket, dataset, table names, folder paths, validation constants. |
| `utils/validations.py` | Data quality validation logic (required columns, email regex, primary key checks). |
| `utils/gcs_utils.py` | GCS helper utilities (download, upload, etc.). |
| `utils/sql_utils.py` | `load_sql()` helper that reads `.sql` files from `sql/`. |
| `utils/email_utils.py` | SendGrid alert helpers: `notify_failure`, `notify_success`. |
| `services/ingestion_service.py` | `validate_customer_file()` — orchestrates validation logic, called by the DAG. |
| `sql/bronze_to_silver.sql` | SQL: cleans and deduplicates raw bronze data into silver layer. |
| `sql/silver_to_gold.sql` | SQL: aggregates silver data into gold summary table. |
| `sql/audit_success.sql` | SQL: writes an audit record after a successful pipeline run. |
| `cloud_functions/trigger_composer/` | Cloud Function that triggers the Composer DAG (e.g., on GCS file arrival). |

---

## GCP Resources

| Resource | Value |
|---|---|
| Project ID | `enduring-coil-501604-u1` |
| GCS Bucket | `de-pipeline-venkatesh-501604` |
| BigQuery Dataset | `retail` |
| BigQuery Location | `US` |
| Airflow Connection | `google_cloud_default` |
| Bronze Table | `bronze_customers` |
| Silver Table | `silver_customers` |
| Gold Table | `gold_customer_summary` |
| Raw GCS folder | `raw/` |
| Archive GCS folder | `archive/` |
| Failed GCS folder | `failed/` |

---

## Customer Data Schema

Required columns (validated before load):

| Column | Type | Notes |
|---|---|---|
| `customer_id` | Integer | Primary key |
| `first_name` | String | |
| `last_name` | String | |
| `email` | String | Validated against regex |
| `created_at` | Date (`YYYY-MM-DD`) | |
| `city` | String | One of 11 cities across India, USA, UK, Germany, Australia |
| `country` | String | |

---

## Alerts

- Pipeline success and failure notifications are sent via **SendGrid**
- API key and sender email are read from **Airflow Variables** (`SENDGRID_API_KEY`, `ALERT_EMAIL`)
- Alert recipient: `venkateshvenky2486@gmail.com`
- Airflow UI deep-links are included in alert emails using `AIRFLOW_BASE_URL` in `config.py`

---

## Stakeholders

This is a solo portfolio project. No external stakeholders.
