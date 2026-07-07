import logging
import pandas as pd
from google.cloud import storage
from io import BytesIO

logger = logging.getLogger(__name__)


def download_csv_from_gcs(bucket_name: str, object_name: str) -> pd.DataFrame:
    """
    Download a CSV file from Google Cloud Storage and return as DataFrame.
    
    Args:
        bucket_name (str): Name of the GCS bucket
        object_name (str): Path to the object in GCS
        
    Returns:
        pd.DataFrame: The CSV file as a pandas DataFrame
        
    Raises:
        Exception: If the download or read fails
    """
    logger.info(f"Downloading CSV from gs://{bucket_name}/{object_name}")
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        
        # Download file to bytes
        file_content = blob.download_as_bytes()
        
        # Read CSV from bytes
        df = pd.read_csv(BytesIO(file_content))
        logger.info(f"Successfully downloaded and read CSV. Shape: {df.shape}")
        
        return df
    except Exception as e:
        logger.error(f"Failed to download CSV from GCS: {str(e)}")
        raise


def upload_file_to_gcs(bucket_name: str, object_name: str, file_path: str) -> None:
    """
    Upload a file to Google Cloud Storage.
    
    Args:
        bucket_name (str): Name of the GCS bucket
        object_name (str): Path where the object should be stored in GCS
        file_path (str): Local file path to upload
        
    Raises:
        Exception: If the upload fails
    """
    logger.info(f"Uploading file from {file_path} to gs://{bucket_name}/{object_name}")
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        
        blob.upload_from_filename(file_path)
        logger.info(f"Successfully uploaded file to gs://{bucket_name}/{object_name}")
    except Exception as e:
        logger.error(f"Failed to upload file to GCS: {str(e)}")
        raise

def get_storage_client():
    return storage.Client()

def move_file(
    source_bucket: str, 
    source_object: str, 
    dest_bucket: str, 
    dest_object: str
) -> None:
    """
    Move (copy then delete) a file within or between GCS buckets.
    
    Args:
        source_bucket (str): Source bucket name
        source_object (str): Source object path
        dest_bucket (str): Destination bucket name
        dest_object (str): Destination object path
        
    Raises:
        Exception: If the move operation fails
    """
    logger.info(f"Moving gs://{source_bucket}/{source_object} to gs://{dest_bucket}/{dest_object}")
    
    try:
        storage_client = get_storage_client()
        source_bucket_obj = storage_client.bucket(source_bucket)
        source_blob = source_bucket_obj.blob(source_object)
        
        dest_bucket_obj = storage_client.bucket(dest_bucket)
        
        # Copy the blob
        source_bucket_obj.copy_blob(source_blob, dest_bucket_obj, dest_object)
        logger.info(f"Copied blob to gs://{dest_bucket}/{dest_object}")
        
        # Delete the original
        source_blob.delete()
        logger.info(f"Deleted original blob from gs://{source_bucket}/{source_object}")
        logger.info("Move operation completed successfully")
    except Exception as e:
        logger.error(f"Failed to move file in GCS: {str(e)}")
        raise