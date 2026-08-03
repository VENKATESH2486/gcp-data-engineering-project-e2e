from airflow.models import Variable

SENDGRID_API_KEY = Variable.get("SENDGRID_API_KEY")
ALERT_EMAIL_FROM = Variable.get("ALERT_EMAIL")

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

# ---------------------------------------------------------------------------
# Email alert settings (SendGrid)
# Update these values before deploying.
# ---------------------------------------------------------------------------

# Cloud Composer Airflow UI base URL (used to build deep-links in alert emails)
AIRFLOW_BASE_URL = (
    "https://fb9e7f83d40f48b2b5767a907e00d339-dot-us-central1.composer.googleusercontent.com"
)

# Alert recipient(s) — comma-separated for multiple addresses
ALERT_EMAIL_TO   = "venkateshvenky2486@gmail.com"
