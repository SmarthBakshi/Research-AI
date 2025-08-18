from airflow.decorators import dag, task
from datetime import datetime
from pathlib import Path
import json
import logging
from typing import List, Dict, Any

from services.ingestion.arxiv.runner import ingest_pdfs_from_metadata

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dag(
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["arxiv", "minio"],
    description="DAG to download and store arXiv PDFs into MinIO using metadata."
)
def ingest_arxiv_pdf():s
    """
    DAG to ingest arXiv PDFs into MinIO using metadata stored as JSON.
    """

    @task
    def read_metadata() -> List[Dict[str, Any]]:
        """
        Read arXiv metadata from a JSON file.

        :returns: List of metadata dictionaries for each arXiv entry.
        :rtype: List[Dict[str, Any]]
        :raises FileNotFoundError: If the metadata file is not found.
        """
        metadata_path = Path("/opt/researchai/data/arxiv/metadata.json")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        with metadata_path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)

        logger.info(f"✅ Loaded {len(metadata)} metadata entries from {metadata_path}")
        return metadata

    @task
    def ingest(metadata: List[Dict[str, Any]]) -> None:
        """
        Ingest PDFs for each arXiv entry using the metadata.

        :param metadata: List of dictionaries, each representing one arXiv paper's metadata.
        :type metadata: List[Dict[str, Any]]
        """
        logger.info("🚀 Starting ingestion of PDFs...")
        ingest_pdfs_from_metadata(metadata)
        logger.info("✅ Finished ingesting all PDFs.")

    metadata = read_metadata()
    ingest(metadata)

dag = ingest_arxiv_pdf()
