import logging

import pandas as pd
from typing import List

from utils.config import (
    CUSTOMER_REQUIRED_COLUMNS,
    PRIMARY_KEY,
    EMAIL_COLUMN,
    DATE_COLUMN,
    EMAIL_REGEX
)

logger = logging.getLogger(__name__)

def validate_empty_dataframe(df: pd.DataFrame) -> None:
    """
    Validates that the DataFrame is not empty.

    """

    logger.info("Validating DataFrame is not empty")
    if df.empty:
        logger.error("Validation failed: DataFrame is empty")
        raise ValueError("The DataFrame is empty. No data to process.")
    logger.info("DataFrame is not empty")

def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
    """
    Validates that the DataFrame contains all required columns.
    """

    logger.info("Validating required columns: %s", required_columns)
    # provide explicit typing for the comprehension result to satisfy type checkers
    missing_columns: List[str] = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error("Validation failed: missing columns: %s", missing_columns)
        raise ValueError(f"The following required columns are missing: {', '.join(missing_columns)}")
    logger.info("All required columns are present")

def validate_primary_key(df: pd.DataFrame, primary_key: str) -> None:
    """
    Validates that the primary key column exists and contains no NULL values.
    """

    logger.info("Validating primary key column: %s", primary_key)
    if primary_key not in df.columns:
        logger.error("Validation failed: primary key column '%s' is missing", primary_key)
        raise ValueError(
            f"Primary key '{primary_key}' column is missing."
        )

    if df[primary_key].isnull().any():
        logger.error("Validation failed: primary key column '%s' contains NULL values", primary_key)
        raise ValueError(
            f"Primary key '{primary_key}' contains NULL values."
        )
    logger.info("Primary key column '%s' is valid", primary_key)
        
def validate_duplicates(df: pd.DataFrame, primary_key: str) -> None:
    """
    Validates duplicate values in the primary key column.

    Raises:
        ValueError
    """
    logger.info("Validating duplicate values for primary key: %s", primary_key)
    duplicate_count = df[primary_key].duplicated().sum()

    if duplicate_count > 0:
        duplicate_ids = (df[df.duplicated(primary_key, keep=False)][primary_key].unique().tolist())

        logger.error(
            "Validation failed: found %s duplicate values for %s",
            duplicate_count,
            primary_key,
        )
        logger.error(
            "Duplicate customer IDs found: %s",
            duplicate_ids,
        )
        
        raise ValueError(
            f"Found {duplicate_count} duplicate "
            f"{primary_key} values."
        )
    logger.info("No duplicate values found for primary key: %s", primary_key)
    
def validate_email(df: pd.DataFrame, email_column: str) -> None:
    """
    Validates the email column for proper format.
    """

    logger.info("Validating email column: %s", email_column)
    if email_column not in df.columns:
        logger.error("Validation failed: email column '%s' is missing", email_column)
        raise ValueError(f"The email column '{email_column}' is missing from the DataFrame.")

    # explicit type annotation to help type checkers
    invalid_emails: pd.DataFrame = df[~df[email_column].fillna("").str.fullmatch(EMAIL_REGEX)]

    if not invalid_emails.empty:
        logger.error("Validation failed: found %s invalid email rows", len(invalid_emails))
        # log a few examples to aid debugging
        try:
            examples = invalid_emails[email_column].head(5).tolist()
        except Exception:
            examples = []
        logger.error("Invalid email examples: %s", examples)
        raise ValueError(f"Found {len(invalid_emails)} invalid email records.")
    logger.info("Email validation passed")

def validate_date_format(df: pd.DataFrame, date_column: str) -> None:
    """
    Validates the date column for proper format.
    """

    logger.info("Validating date column: %s", date_column)
    if date_column not in df.columns:
        logger.error("Validation failed: date column '%s' is missing", date_column)
        raise ValueError(f"The date column '{date_column}' is missing from the DataFrame.")

    parsed_dates = pd.to_datetime(df[date_column],format="%Y-%m-%d",errors="coerce",)
    invalid_dates = df[parsed_dates.isna()]

    if not invalid_dates.empty:
        logger.error("Invalid dates detected: %s rows", len(invalid_dates))
        raise ValueError(f"{len(invalid_dates)} invalid dates found")
    logger.info("Date validation passed for column: %s", date_column)
    
def validate_customer_dataframe(df: pd.DataFrame) -> bool:
    """
    Validates the entire customer DataFrame for data quality.

    Args:
        df (pd.DataFrame): The customer DataFrame to validate.

    Returns:
        bool: True if validation passes, False otherwise.
    """

    logger.info(
        "Starting customer DataFrame validation with %s rows and %s columns",
        len(df),
        len(df.columns),
    )
    
    validate_empty_dataframe(df)
    validate_required_columns(df, CUSTOMER_REQUIRED_COLUMNS)
    validate_primary_key(df, PRIMARY_KEY)
    validate_duplicates(df, PRIMARY_KEY)
    validate_email(df, EMAIL_COLUMN)
    validate_date_format(df, DATE_COLUMN)
    logger.info("Customer DataFrame validation completed successfully")
    return True

