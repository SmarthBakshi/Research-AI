from services.ingestion.arxiv.client import ArxivClient
from services.ingestion.arxiv.config import ArxivConfig

def test_arxiv_client_init():
    config = ArxivConfig(base_url="https://export.arxiv.org/api/query")
    client = ArxivClient(config)
    assert client.config.base_url == "https://export.arxiv.org/api/query"
