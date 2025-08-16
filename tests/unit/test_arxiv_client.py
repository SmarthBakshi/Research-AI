from services.ingestion.arxiv.client import ArxivClient
from services.ingestion.arxiv.config import ArxivConfig

cfg = ArxivConfig()
client = ArxivClient(cfg)

raw = client.fetch()
parsed = client.parse_metadata(raw)

print(parsed[:2])  # Preview first two
