import logging
from utils.gcs_utils import download_csv_from_gcs
from utils.validations import validate_customer_dataframe

logger = logging.getLogger(__name__)


def validate_customer_file(
    bucket_name: str,
    object_name: str,
) -> bool:
    """
    Download file from GCS, read CSV, and validate dataframe.
    
    Args:
        bucket_name (str): Name of the GCS bucket
        object_name (str): Path to the CSV file in GCS
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValueError: If validation fails
    """
    logger.info(
        "Starting customer file validation for gs://%s/%s",
        bucket_name,
        object_name,
    )
    
    try:
        # Download CSV from GCS
        df = download_csv_from_gcs(
            bucket_name,
            object_name,
        )

        # Validate the dataframe
        validate_customer_dataframe(df)
        
        logger.info("Customer file validation completed successfully")
        return True
    except Exception as e:
        logger.error(f"Customer file validation failed: {str(e)}")
        raise
