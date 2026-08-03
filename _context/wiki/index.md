# Wiki Index

This wiki captures the context, goals, and working preferences for the **GCP Data Engineering E2E Project**.
Read it at the start of a task when you need project or convention context — follow links only where relevant.

---

## Pages

| File | What's in it |
|---|---|
| [project.md](project.md) | Project overview, goals, architecture, key modules, and GCP resources |
| [preferences.md](preferences.md) | Working standards, coding style, and AI collaboration preferences |

---

## Quick Reference

- **Primary pipeline:** `dags/customer_ingestion.py`
- **Config:** `utils/config.py` — all GCP resource names, table names, and shared constants live here
- **Data flow:** `scripts/` → `data/` → GCS (raw/) → Airflow → BigQuery (bronze → silver → gold)
- **GCP Project ID:** `enduring-coil-501604-u1`
- **GCS Bucket:** `de-pipeline-venkatesh-501604`
- **BigQuery Dataset:** `retail`
