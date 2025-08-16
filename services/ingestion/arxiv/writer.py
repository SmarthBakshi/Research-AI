import os
import json
import boto3
import hashlib
from datetime import datetime
from botocore.client import Config
from services.ingestion.arxiv.minio_utils import ensure_bucket_exists
from dotenv import load_dotenv

load_dotenv()

class MinIOWriter:
    def __init__(self):
        self.bucket = os.getenv("MINIO_BUCKET", "researchai")
        self.s3 = boto3.client(
            "s3",
            endpoint_url=f"http://localhost:{os.getenv('MINIO_API_PORT', '9000')}",
            aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
            aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        ensure_bucket_exists(self.bucket, self.s3)

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def write_metadata(self, metadata: list[dict], prefix: str = "raw/arxiv/") -> str:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        body = json.dumps(metadata, indent=2)
        hash_val = self._hash_content(body)
        key = f"{prefix}metadata-{timestamp}-{hash_val[:8]}.json"

        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=body,
            ContentType="application/json",
        )
        print(f"✅ Uploaded metadata to MinIO: {key}")
        return key
