import os
import json
import boto3
import hashlib
import requests
from datetime import datetime
from botocore.client import Config
from botocore.exceptions import ClientError
from services.ingestion.arxiv.minio_utils import ensure_bucket_exists
from dotenv import load_dotenv

load_dotenv()

class MinIOWriter:
    def __init__(self):
        self.bucket = os.getenv("MINIO_BUCKET", "researchai")
        
        # Dynamically set endpoint depending on context
        endpoint_url = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
        
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
            aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        ensure_bucket_exists(self.bucket, self.s3)


    def _hash_content(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def write_metadata(self, metadata: list[dict], prefix: str = "raw/arxiv/") -> str:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        body = json.dumps(metadata, indent=2).encode("utf-8")
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

    def write_pdf(self, pdf_url: str) -> str:
        response = requests.get(pdf_url)
        response.raise_for_status()
        content = response.content

        content_hash = self._hash_content(content)
        key = f"raw/pdfs/{content_hash}.pdf"

        # Skip upload if already exists
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            print(f"⚠️ PDF already exists in MinIO: {key}")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.s3.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=content,
                    ContentType="application/pdf",
                )
                print(f"✅ Uploaded PDF to MinIO: {key}")
            else:
                raise  # re-raise unexpected errors

        return content_hash
