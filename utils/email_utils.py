"""
Email alert utilities for Airflow DAG callbacks.

Provides notify_failure and notify_success to be wired as
on_failure_callback / on_success_callback on the DAG.

Required entries in utils/config.py:
    AIRFLOW_BASE_URL   – Cloud Composer UI base URL (for deep-links)
    ALERT_EMAIL_TO     – recipient address(es), comma-separated
    ALERT_EMAIL_FROM   – verified sender address (must match SendGrid sender identity)
    SENDGRID_API_KEY   – SendGrid API key (keep secret, never commit the real value)
"""

import logging
from datetime import datetime, timezone

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To

from utils.config import (
    AIRFLOW_BASE_URL,
    ALERT_EMAIL_FROM,
    ALERT_EMAIL_TO,
    SENDGRID_API_KEY,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _dag_run_url(context: dict) -> str:
    """Build a direct Airflow UI link for the current DAG run."""
    dag_id = context["dag"].dag_id
    run_id = context["dag_run"].run_id
    return (
        f"{AIRFLOW_BASE_URL}/dags/{dag_id}/grid"
        f"?dag_run_id={run_id}&tab=details"
    )


def _send_email(subject: str, html_body: str) -> None:
    """Send an HTML email via SendGrid."""
    recipients = [To(a.strip()) for a in ALERT_EMAIL_TO.split(",") if a.strip()]

    message = Mail(
        from_email=ALERT_EMAIL_FROM,
        to_emails=recipients,
        subject=subject,
        html_content=html_body,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(
            "Alert email sent via SendGrid → status %s | subject: %s",
            response.status_code,
            subject,
        )
    except Exception:
        logger.exception("Failed to send alert email via SendGrid")


# ---------------------------------------------------------------------------
# HTML email builders
# ---------------------------------------------------------------------------

def _failure_html(context: dict) -> str:
    dag_id   = context["dag"].dag_id
    task_id  = context["task_instance"].task_id
    run_id   = context["dag_run"].run_id
    ts       = context.get("ts", datetime.now(timezone.utc).isoformat())
    exc      = context.get("exception", "Unknown error")
    conf     = context["dag_run"].conf or {}
    src_file = conf.get("object", "N/A")
    url      = _dag_run_url(context)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body        {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }}
    .card       {{ background: #ffffff; border-radius: 8px; max-width: 560px; margin: 0 auto;
                  border-top: 4px solid #e53935; padding: 28px 32px; }}
    h2          {{ margin: 0 0 6px; color: #e53935; font-size: 20px; }}
    .subtitle   {{ color: #555; font-size: 13px; margin-bottom: 24px; }}
    table       {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    td          {{ padding: 9px 12px; border-bottom: 1px solid #eee; vertical-align: top; }}
    td:first-child {{ color: #555; white-space: nowrap; width: 120px; font-weight: 600; }}
    td:last-child  {{ color: #1a1a1a; word-break: break-all; }}
    .error-box  {{ background: #fff3f3; border-left: 3px solid #e53935; padding: 10px 14px;
                  border-radius: 0 4px 4px 0; font-size: 13px; color: #c62828; margin: 18px 0; }}
    .btn        {{ display: inline-block; margin-top: 20px; padding: 10px 22px;
                  background: #1976d2; color: #fff !important; text-decoration: none;
                  border-radius: 5px; font-size: 14px; font-weight: 600; }}
    .footer     {{ text-align: center; color: #aaa; font-size: 11px; margin-top: 24px; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>&#10060; Customer Pipeline Failed</h2>
    <p class="subtitle">An error occurred during the pipeline run. Please investigate.</p>

    <table>
      <tr><td>Pipeline</td>    <td>{dag_id}</td></tr>
      <tr><td>Task</td>        <td>{task_id}</td></tr>
      <tr><td>Run ID</td>      <td>{run_id}</td></tr>
      <tr><td>File</td>        <td>{src_file}</td></tr>
      <tr><td>Timestamp</td>   <td>{ts}</td></tr>
    </table>

    <div class="error-box">
      <strong>Error:</strong> {exc}
    </div>

    <a class="btn" href="{url}">View in Airflow &#8594;</a>

    <p class="footer">Automated alert &mdash; Customer Ingestion Pipeline</p>
  </div>
</body>
</html>"""


def _success_html(context: dict) -> str:
    dag_id   = context["dag"].dag_id
    run_id   = context["dag_run"].run_id
    ts       = context.get("ts", datetime.now(timezone.utc).isoformat())
    conf     = context["dag_run"].conf or {}
    src_file = conf.get("object", "N/A")
    url      = _dag_run_url(context)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body        {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }}
    .card       {{ background: #ffffff; border-radius: 8px; max-width: 560px; margin: 0 auto;
                  border-top: 4px solid #43a047; padding: 28px 32px; }}
    h2          {{ margin: 0 0 6px; color: #2e7d32; font-size: 20px; }}
    .subtitle   {{ color: #555; font-size: 13px; margin-bottom: 24px; }}
    table       {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    td          {{ padding: 9px 12px; border-bottom: 1px solid #eee; vertical-align: top; }}
    td:first-child {{ color: #555; white-space: nowrap; width: 120px; font-weight: 600; }}
    td:last-child  {{ color: #1a1a1a; word-break: break-all; }}
    .btn        {{ display: inline-block; margin-top: 20px; padding: 10px 22px;
                  background: #1976d2; color: #fff !important; text-decoration: none;
                  border-radius: 5px; font-size: 14px; font-weight: 600; }}
    .footer     {{ text-align: center; color: #aaa; font-size: 11px; margin-top: 24px; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>&#9989; Customer Pipeline Succeeded</h2>
    <p class="subtitle">The pipeline completed successfully.</p>

    <table>
      <tr><td>Pipeline</td>    <td>{dag_id}</td></tr>
      <tr><td>Run ID</td>      <td>{run_id}</td></tr>
      <tr><td>File</td>        <td>{src_file}</td></tr>
      <tr><td>Timestamp</td>   <td>{ts}</td></tr>
    </table>

    <a class="btn" href="{url}">View in Airflow &#8594;</a>

    <p class="footer">Automated alert &mdash; Customer Ingestion Pipeline</p>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Public callbacks — assigned to DAG on_failure_callback / on_success_callback
# ---------------------------------------------------------------------------

def notify_failure(context: dict) -> None:
    """
    Airflow on_failure_callback.

    Called by Airflow when any task in the DAG fails.
    Sends an HTML email with the failing task, run ID, error message,
    source file path, and a direct link to the Airflow UI run.
    """
    dag_id  = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    subject = f"\u274c Airflow | {dag_id} | {task_id} FAILED"
    _send_email(subject, _failure_html(context))


def notify_success(context: dict) -> None:
    """
    Airflow on_success_callback.

    Called by Airflow when the DAG completes successfully.
    Sends a confirmation HTML email with run details and a link to Airflow.
    """
    dag_id  = context["dag"].dag_id
    subject = f"\u2705 Airflow | {dag_id} | Pipeline succeeded"
    _send_email(subject, _success_html(context))
