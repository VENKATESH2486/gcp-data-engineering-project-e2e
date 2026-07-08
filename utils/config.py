# utils/config.py

PROJECT_ID = "enduring-coil-501604-u1"

BUCKET_NAME = "de-pipeline-venkatesh-501604"

DATASET = "retail"

BQ_LOCATION = "US"
BRONZE_CUSTOMERS_TABLE = "bronze_customers"
SILVER_CUSTOMERS_TABLE = "silver_customers"
GOLD_CUSTOMER_SUMMARY_TABLE = "gold_customer_summary"

RAW_FOLDER = "raw"
ARCHIVE_FOLDER = "archive"
FAILED_FOLDER = "failed"
CUSTOMER_FILE  = "customer.csv"

GOOGLE_CONN_ID = "google_cloud_default"


CUSTOMER_REQUIRED_COLUMNS = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "created_at",
]

PRIMARY_KEY = "customer_id"

EMAIL_COLUMN = "email"

DATE_COLUMN = "created_at"
EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"