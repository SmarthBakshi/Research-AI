from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
from pathlib import Path

from services.ingestion.arxiv.minio_utils import ingest_pdfs_from_metadata

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

def run_ingestion():
    metadata_path = Path("/opt/researchai/data/arxiv/metadata.json")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    with metadata_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)
    ingest_pdfs_from_metadata(metadata)

with DAG(
    dag_id="ingest_arxiv_pdf",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Download and store arXiv PDFs into MinIO",
    tags=["arxiv", "minio", "ingestion"]
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_arxiv_pdfs",
        python_callable=run_ingestion,
    )
