from airflow.decorators import dag, task
from datetime import datetime
from pathlib import Path
import json
import logging

from services.ingestion.arxiv.runner import ingest_pdfs_from_metadata

@dag(
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["arxiv", "minio"],
    description="Ingest arXiv PDFs into MinIO using metadata JSON"
)
def ingest_arxiv_pdf():
    """
    DAG to read arXiv metadata and download/upload corresponding PDFs to MinIO.
    """

    @task
    def read_metadata() -> list[dict]:
        """
        Read the metadata JSON file containing arXiv paper entries.

        :returns: List of metadata dictionaries
        :rtype: list[dict]
        """
        metadata_path = Path("/opt/researchai/data/arxiv/metadata.json")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        logging.info(f"📄 Reading metadata from {metadata_path}")
        with metadata_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @task
    def ingest(metadata: list[dict]) -> None:
        """
        Ingest PDFs from arXiv metadata and store them in MinIO.

        :param metadata: List of arXiv paper metadata
        :type metadata: list[dict]
        """
        logging.info(f"🚀 Starting ingestion for {len(metadata)} records")
        ingest_pdfs_from_metadata(metadata)

    metadata = read_metadata()
    ingest(metadata)

dag = ingest_arxiv_pdf()
