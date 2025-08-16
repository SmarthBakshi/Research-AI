from services.ingestion.arxiv.client import ArxivClient
from services.ingestion.arxiv.config import ArxivConfig
from services.ingestion.arxiv.writer import MinIOWriter
from dotenv import load_dotenv

load_dotenv()

config = ArxivConfig()
client = ArxivClient(config)
writer = MinIOWriter()

print("📡 Fetching from Arxiv...")
xml = client.fetch()
metadata = client.parse_metadata(xml)
print(f"📝 Parsed {len(metadata)} entries.")

writer.write_metadata(metadata)
print("✅ Metadata written to MinIO.")