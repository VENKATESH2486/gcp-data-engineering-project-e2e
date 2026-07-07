"""
Service module for data ingestion operations.

This module provides service-layer functions for handling
data ingestion tasks, including customer data processing.
"""

import logging

logger = logging.getLogger(__name__)


def validate_customer_file(
    bucket_name: str,
    object_name: str,
) -> bool:
    """
    Service function to validate customer file from GCS.
    
    This function orchestrates the validation of a customer CSV file
    stored in Google Cloud Storage. It performs the following steps:
    1. Downloads the CSV file from GCS
    2. Validates data quality (schema, nulls, duplicates, formats)
    3. Raises appropriate errors if validation fails
    
    Args:
        bucket_name (str): Name of the GCS bucket containing the file
        object_name (str): Path to the CSV file in GCS (e.g., "raw/customer.csv")
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValueError: If any validation checks fail (missing columns, invalid data, etc.)
        Exception: If GCS download fails or other unexpected errors occur
        
    Example:
        >>> validate_customer_file("my-bucket", "raw/customers.csv")
        True
    """
    from utils.gcs_utils import download_csv_from_gcs
    from utils.validations import validate_customer_dataframe
    
    logger.info(f"Service: Starting customer file validation for gs://{bucket_name}/{object_name}")
    
    try:
        # Download CSV file from GCS
        logger.info("Service: Downloading customer file from GCS")
        df = download_csv_from_gcs(bucket_name, object_name)
        
        # Validate the customer dataframe
        logger.info("Service: Performing data quality validations")
        validate_customer_dataframe(df)
        
        logger.info("Service: Customer file validation completed successfully")
        return True
        
    except Exception:
        logger.exception(
            "Customer file validation failed for gs://%s/%s",
            bucket_name,
            object_name,
        )
        raise