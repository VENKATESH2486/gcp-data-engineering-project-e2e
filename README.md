# GCP Data Engineering Project

This repository contains a sample data engineering project structure for ingesting customer data with Airflow and transforming data through Bronze, Silver, and Gold layers.

## Structure

- `dags/` - Airflow DAG definitions
- `data/` - Source CSV data files
- `sql/` - Transformation SQL scripts
- `utils/` - Helper modules for validation and configuration
- `requirements.txt` - Python dependencies
- `architecture.png` - Architecture diagram placeholder

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update `utils/config.py` with your environment settings.
3. Add DAGs to your Airflow `dags` folder and deploy.
