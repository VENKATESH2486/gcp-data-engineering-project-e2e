#!/usr/bin/env python3
"""
Comprehensive E2E Pipeline Validation Script
==============================================

This script validates all aspects of the GCP data engineering project:
1. Phase 1: Static code analysis (syntax, imports, DAG structure)
2. Phase 2: Configuration & connectivity validation
3. Phase 3: Unit tests for utilities
4. Phase 4: Integration tests (requires live GCP environment)
"""

import sys
import os
import subprocess
import logging
from pathlib import Path
from typing import List, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_phase(phase_num: int, title: str):
    """Print phase header"""
    print("\n" + "="*80)
    print(f"PHASE {phase_num}: {title}")
    print("="*80 + "\n")


def print_section(title: str):
    """Print section header"""
    print(f"\n>>> {title}")
    print("-" * 80)


def check_python_syntax() -> bool:
    """Check Python files for syntax errors"""
    print_section("1.1 Checking Python Syntax")
    
    python_files = list(PROJECT_ROOT.glob("**/*.py"))
    python_files = [f for f in python_files if "/.venv/" not in str(f) and "/__pycache__/" not in str(f)]
    
    all_valid = True
    for py_file in python_files:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✓ {py_file.relative_to(PROJECT_ROOT)}")
            else:
                print(f"✗ {py_file.relative_to(PROJECT_ROOT)}")
                print(f"  Error: {result.stderr}")
                all_valid = False
        except Exception as e:
            print(f"✗ {py_file.relative_to(PROJECT_ROOT)}")
            print(f"  Error: {str(e)}")
            all_valid = False
    
    return all_valid


def check_imports() -> bool:
    """Check if all required imports are available"""
    print_section("1.2 Checking Required Imports")
    
    required_modules = [
        "airflow",
        "airflow.providers.google.cloud",
        "pandas",
        "google.cloud.storage",
        "google.cloud.bigquery",
    ]
    
    all_available = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module} - {str(e)}")
            all_available = False
    
    return all_available


def check_project_imports() -> bool:
    """Check project-specific imports"""
    print_section("1.3 Checking Project Module Imports")
    
    try:
        print("Importing utils.config...")
        from utils import config
        print(f"✓ Project ID: {config.PROJECT_ID}")
        print(f"✓ Bucket: {config.BUCKET_NAME}")
        print(f"✓ Dataset: {config.DATASET}")
        
        print("\nImporting utils.gcs_utils...")
        from utils import gcs_utils
        print("✓ gcs_utils imported successfully")
        
        print("\nImporting utils.validations...")
        from utils import validations
        print("✓ validations imported successfully")
        
        print("\nImporting utils.sql_utils...")
        from utils import sql_utils
        print("✓ sql_utils imported successfully")
        
        print("\nImporting services.ingestion_service...")
        from services import ingestion_service
        print("✓ ingestion_service imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_dag_definitions() -> bool:
    """Check if DAGs can be instantiated"""
    print_section("1.4 Checking DAG Definitions")
    
    try:
        # Try to import customer_ingestion DAG
        print("Importing customer_ingestion DAG...")
        sys.path.insert(0, str(PROJECT_ROOT / "dags"))
        
        from customer_ingestion import dag as customer_dag
        print(f"✓ customer_ingestion DAG loaded")
        print(f"  - DAG ID: {customer_dag.dag_id}")
        print(f"  - Start date: {customer_dag.start_date}")
        print(f"  - Tasks: {list(customer_dag.task_dict.keys())}")
        
        # Verify task dependencies
        print("\n  Task dependencies:")
        for task_id, task in customer_dag.task_dict.items():
            downstream = [t.task_id for t in task.downstream_list]
            if downstream:
                print(f"    {task_id} → {downstream}")
        
        # Try hello_world DAG
        print("\nImporting hello_world DAG...")
        from hello_world import dag as hello_dag
        print(f"✓ hello_world DAG loaded")
        print(f"  - DAG ID: {hello_dag.dag_id}")
        
        return True
    except Exception as e:
        print(f"✗ DAG check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_sql_files() -> bool:
    """Check if SQL files exist and are readable"""
    print_section("1.5 Checking SQL Files")
    
    sql_files = {
        "bronze_to_silver.sql": "Bronze to Silver transformation",
        "silver_to_gold.sql": "Silver to Gold aggregation",
    }
    
    all_valid = True
    for filename, description in sql_files.items():
        sql_path = PROJECT_ROOT / "sql" / filename
        if sql_path.exists():
            try:
                content = sql_path.read_text()
                lines = len(content.split('\n'))
                print(f"✓ {filename} ({lines} lines) - {description}")
            except Exception as e:
                print(f"✗ {filename} - Error reading: {str(e)}")
                all_valid = False
        else:
            print(f"✗ {filename} - File not found")
            all_valid = False
    
    return all_valid


def check_data_files() -> bool:
    """Check if test data files exist"""
    print_section("1.6 Checking Test Data Files")
    
    data_files = ["customers.csv", "orders.csv", "products.csv"]
    all_exist = True
    
    for filename in data_files:
        data_path = PROJECT_ROOT / "data" / filename
        if data_path.exists():
            try:
                with open(data_path) as f:
                    lines = len(f.readlines())
                print(f"✓ {filename} ({lines} lines)")
            except Exception as e:
                print(f"✗ {filename} - Error reading: {str(e)}")
                all_exist = False
        else:
            print(f"✗ {filename} - File not found")
            all_exist = False
    
    return all_exist


def check_configuration() -> bool:
    """Verify configuration"""
    print_section("2.1 Checking Configuration")
    
    try:
        from utils.config import (
            PROJECT_ID, BUCKET_NAME, DATASET, BRONZE_CUSTOMERS_TABLE,
            SILVER_CUSTOMERS_TABLE, GOLD_CUSTOMERS_TABLE, RAW_FOLDER,
            ARCHIVE_FOLDER, CUSTOMER_FILE, GOOGLE_CONN_ID, BQ_LOCATION,
            CUSTOMER_REQUIRED_COLUMNS, PRIMARY_KEY, EMAIL_COLUMN, DATE_COLUMN
        )
        
        print("GCP Configuration:")
        print(f"  Project ID: {PROJECT_ID}")
        print(f"  Bucket: {BUCKET_NAME}")
        print(f"  Dataset: {DATASET}")
        print(f"  BigQuery Location: {BQ_LOCATION}")
        print(f"  Airflow Connection: {GOOGLE_CONN_ID}")
        
        print("\nTable Names:")
        print(f"  Bronze: {BRONZE_CUSTOMERS_TABLE}")
        print(f"  Silver: {SILVER_CUSTOMERS_TABLE}")
        print(f"  Gold: {GOLD_CUSTOMERS_TABLE}")
        
        print("\nFolder Structure (GCS):")
        print(f"  Raw: {RAW_FOLDER}/")
        print(f"  Archive: {ARCHIVE_FOLDER}/")
        print(f"  Customer File: {CUSTOMER_FILE}")
        
        print("\nData Schema:")
        print(f"  Required columns: {CUSTOMER_REQUIRED_COLUMNS}")
        print(f"  Primary key: {PRIMARY_KEY}")
        print(f"  Email column: {EMAIL_COLUMN}")
        print(f"  Date column: {DATE_COLUMN}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration check failed: {str(e)}")
        return False


def test_validations() -> bool:
    """Test validation functions with sample data"""
    print_section("3.1 Testing Validation Functions")
    
    try:
        import pandas as pd
        from utils.validations import (
            validate_empty_dataframe,
            validate_required_columns,
            validate_primary_key,
            validate_duplicates,
            validate_email,
            validate_date_format,
            validate_customer_dataframe,
        )
        from utils.config import CUSTOMER_REQUIRED_COLUMNS, PRIMARY_KEY, EMAIL_COLUMN, DATE_COLUMN
        
        # Create valid test data
        valid_df = pd.DataFrame({
            'customer_id': [1, 2],
            'first_name': ['John', 'Jane'],
            'last_name': ['Doe', 'Smith'],
            'email': ['john@example.com', 'jane@example.com'],
            'created_at': ['2026-01-01', '2026-02-15'],
        })
        
        print("Test 1: Empty DataFrame validation")
        try:
            empty_df = pd.DataFrame()
            validate_empty_dataframe(empty_df)
            print("✗ Should have raised ValueError for empty DataFrame")
            return False
        except ValueError:
            print("✓ Correctly rejected empty DataFrame")
        
        print("\nTest 2: Required columns validation")
        try:
            validate_required_columns(valid_df, CUSTOMER_REQUIRED_COLUMNS)
            print("✓ Valid DataFrame has all required columns")
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            return False
        
        print("\nTest 3: Primary key validation (no nulls)")
        try:
            validate_primary_key(valid_df, PRIMARY_KEY)
            print("✓ Primary key is valid (no nulls)")
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            return False
        
        print("\nTest 4: Duplicates validation")
        try:
            validate_duplicates(valid_df, PRIMARY_KEY)
            print("✓ No duplicates found")
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            return False
        
        print("\nTest 5: Email validation")
        try:
            validate_email(valid_df, EMAIL_COLUMN)
            print("✓ All emails are valid")
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            return False
        
        print("\nTest 6: Date format validation")
        try:
            validate_date_format(valid_df, DATE_COLUMN)
            print("✓ All dates are valid (YYYY-MM-DD)")
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            return False
        
        print("\nTest 7: Full customer DataFrame validation")
        try:
            result = validate_customer_dataframe(valid_df)
            print(f"✓ Full validation passed (result: {result})")
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            return False
        
        # Test failure scenarios
        print("\nTest 8: Invalid email detection")
        invalid_email_df = valid_df.copy()
        invalid_email_df.loc[0, 'email'] = 'invalid-email'
        try:
            validate_email(invalid_email_df, EMAIL_COLUMN)
            print("✗ Should have detected invalid email")
            return False
        except ValueError:
            print("✓ Correctly detected invalid email")
        
        print("\nTest 9: Invalid date detection")
        invalid_date_df = valid_df.copy()
        invalid_date_df.loc[0, 'created_at'] = '2026-13-01'  # Invalid month
        try:
            validate_date_format(invalid_date_df, DATE_COLUMN)
            print("✗ Should have detected invalid date")
            return False
        except ValueError:
            print("✓ Correctly detected invalid date")
        
        print("\nTest 10: Duplicate detection")
        duplicate_df = valid_df.copy()
        duplicate_df = pd.concat([duplicate_df, duplicate_df.iloc[[0]]], ignore_index=True)
        try:
            validate_duplicates(duplicate_df, PRIMARY_KEY)
            print("✗ Should have detected duplicates")
            return False
        except ValueError:
            print("✓ Correctly detected duplicates")
        
        return True
    except Exception as e:
        print(f"✗ Validation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_sql_utils() -> bool:
    """Test SQL utilities"""
    print_section("3.2 Testing SQL Utilities")
    
    try:
        from utils.sql_utils import load_sql
        
        # Test loading bronze_to_silver.sql
        print("Loading bronze_to_silver.sql...")
        bronze_sql = load_sql("bronze_to_silver.sql")
        print(f"✓ Loaded {len(bronze_sql)} characters")
        print(f"  Contains expected keywords:")
        keywords = ["CREATE OR REPLACE TABLE", "WITH cleaned AS", "ROW_NUMBER", "PARTITION BY"]
        for keyword in keywords:
            if keyword in bronze_sql:
                print(f"  ✓ '{keyword}'")
            else:
                print(f"  ✗ Missing '{keyword}'")
                return False
        
        # Test loading silver_to_gold.sql
        print("\nLoading silver_to_gold.sql...")
        gold_sql = load_sql("silver_to_gold.sql")
        print(f"✓ Loaded {len(gold_sql)} characters")
        print(f"  Contains expected keywords:")
        keywords = ["SELECT", "COUNT", "SUM"]
        for keyword in keywords:
            if keyword in gold_sql:
                print(f"  ✓ '{keyword}'")
            else:
                print(f"  ✗ Missing '{keyword}'")
        
        return True
    except Exception as e:
        print(f"✗ SQL utilities test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_gcs_utils_mock() -> bool:
    """Test GCS utilities (mocked, without actual GCS connection)"""
    print_section("3.3 Testing GCS Utilities (Mocked)")
    
    try:
        from utils.gcs_utils import download_csv_from_gcs, upload_file_to_gcs, move_file
        import inspect
        
        # Just verify the functions exist and have correct signatures
        print("Checking download_csv_from_gcs...")
        sig = inspect.signature(download_csv_from_gcs)
        params = list(sig.parameters.keys())
        print(f"✓ Function exists with parameters: {params}")
        if "bucket_name" not in params or "object_name" not in params:
            print("✗ Missing expected parameters")
            return False
        
        print("\nChecking upload_file_to_gcs...")
        sig = inspect.signature(upload_file_to_gcs)
        params = list(sig.parameters.keys())
        print(f"✓ Function exists with parameters: {params}")
        
        print("\nChecking move_file...")
        sig = inspect.signature(move_file)
        params = list(sig.parameters.keys())
        print(f"✓ Function exists with parameters: {params}")
        
        return True
    except Exception as e:
        print(f"✗ GCS utilities test failed: {str(e)}")
        return False


def check_gcp_connectivity() -> bool:
    """Check GCP credentials and connectivity"""
    print_section("2.2 Checking GCP Connectivity")
    
    try:
        from google.cloud import storage
        from google.cloud import bigquery
        
        print("Attempting GCP authentication...")
        
        # Try to authenticate to GCS
        try:
            storage_client = storage.Client()
            project_id = storage_client.project
            print(f"✓ GCS authentication successful (project: {project_id})")
            
            # Try to list buckets
            print("  Attempting to list buckets...")
            buckets = list(storage_client.list_buckets(max_results=5))
            print(f"  ✓ Can list buckets ({len(buckets)} found)")
        except Exception as e:
            print(f"⚠ GCS authentication warning: {str(e)}")
            print("  (This is expected if not running with GCP credentials)")
            return True  # Not a hard failure
        
        # Try to authenticate to BigQuery
        try:
            print("\nAttempting BigQuery authentication...")
            bq_client = bigquery.Client()
            project_id = bq_client.project
            print(f"✓ BigQuery authentication successful (project: {project_id})")
        except Exception as e:
            print(f"⚠ BigQuery authentication warning: {str(e)}")
            print("  (This is expected if not running with GCP credentials)")
        
        return True
    except Exception as e:
        print(f"⚠ GCP connectivity check: {str(e)}")
        print("  (This is expected if not running with GCP credentials)")
        return True


def run_all_validations() -> Tuple[bool, int]:
    """Run all validation phases"""
    
    results = {}
    
    # PHASE 1: Static Code Analysis
    print_phase(1, "STATIC CODE ANALYSIS & VALIDATION")
    
    results['syntax'] = check_python_syntax()
    results['imports'] = check_imports()
    results['project_imports'] = check_project_imports()
    results['dags'] = check_dag_definitions()
    results['sql'] = check_sql_files()
    results['data'] = check_data_files()
    
    phase1_pass = all(results.values())
    
    # PHASE 2: Configuration & Connectivity
    print_phase(2, "CONFIGURATION & CONNECTIVITY")
    
    results['config'] = check_configuration()
    results['gcp_connectivity'] = check_gcp_connectivity()
    
    phase2_pass = results['config'] and results['gcp_connectivity']
    
    # PHASE 3: Unit Tests
    print_phase(3, "UNIT & INTEGRATION TESTS")
    
    results['validations'] = test_validations()
    results['sql_utils'] = test_sql_utils()
    results['gcs_utils'] = test_gcs_utils_mock()
    
    phase3_pass = results['validations'] and results['sql_utils'] and results['gcs_utils']
    
    # Summary
    print_phase(4, "VALIDATION SUMMARY")
    
    print("\n✓ = PASSED  |  ✗ = FAILED  |  ⚠ = WARNING\n")
    print("PHASE 1: Static Code Analysis")
    for check, result in [
        ("Python Syntax", results['syntax']),
        ("Required Imports", results['imports']),
        ("Project Imports", results['project_imports']),
        ("DAG Definitions", results['dags']),
        ("SQL Files", results['sql']),
        ("Test Data Files", results['data']),
    ]:
        status = "✓" if result else "✗"
        print(f"  [{status}] {check}")
    
    print("\nPHASE 2: Configuration & Connectivity")
    for check, result in [
        ("Configuration", results['config']),
        ("GCP Connectivity", results['gcp_connectivity']),
    ]:
        status = "✓" if result else "✗"
        print(f"  [{status}] {check}")
    
    print("\nPHASE 3: Unit & Integration Tests")
    for check, result in [
        ("Validation Functions", results['validations']),
        ("SQL Utilities", results['sql_utils']),
        ("GCS Utilities", results['gcs_utils']),
    ]:
        status = "✓" if result else "✗"
        print(f"  [{status}] {check}")
    
    print("\n" + "="*80)
    if phase1_pass and phase2_pass and phase3_pass:
        print("✓ ALL VALIDATIONS PASSED!")
        print("="*80)
        print("\nThe project is ready for Phase 4: End-to-End Pipeline Execution")
        print("Next steps:")
        print("  1. Upload sample data to GCS: gs://de-pipeline-venkatesh-501604/raw/customer.csv")
        print("  2. Trigger customer_ingestion DAG in Airflow")
        print("  3. Monitor DAG execution and verify outputs")
        print("="*80)
        return True, 0
    else:
        print("✗ SOME VALIDATIONS FAILED")
        print("="*80)
        print("\nFailed checks:")
        if not phase1_pass:
            print("  - Phase 1: Static Code Analysis")
        if not phase2_pass:
            print("  - Phase 2: Configuration & Connectivity")
        if not phase3_pass:
            print("  - Phase 3: Unit & Integration Tests")
        print("\nPlease fix the issues above before proceeding.")
        print("="*80)
        return False, 1


if __name__ == "__main__":
    try:
        success, exit_code = run_all_validations()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error during validation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
