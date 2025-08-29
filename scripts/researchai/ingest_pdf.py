from services.ingestion.arxiv.client import ArxivClient
from services.ingestion.arxiv.config import ArxivConfig
from services.ingestion.arxiv.runner import ingest_pdfs_from_metadata

config = ArxivConfig()
client = ArxivClient(config)

xml = client.fetch()
metadata = client.parse_metadata(xml)

ingest_pdfs_from_metadata(metadata)
