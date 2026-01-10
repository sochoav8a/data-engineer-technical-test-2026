from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from airflow.operators.python import PythonOperator

from airflow import DAG


def _run_pipeline() -> None:
    repo_root = Path(os.environ.get("REPO_ROOT", "/opt/airflow/repo"))
    data_dir = repo_root / "data"
    output_dir = repo_root / "output"
    sqlite_path = output_dir / "extractions.db"

    from pipeline.config import Settings
    from pipeline.pipeline import run_pipeline

    settings = Settings()
    run_pipeline(
        data_dir=data_dir,
        output_dir=output_dir,
        sqlite_path=sqlite_path,
        settings=settings,
    )


with DAG(
    dag_id="ni43_extraction",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ni43", "extraction"],
) as dag:
    PythonOperator(task_id="extract_pdfs", python_callable=_run_pipeline)
