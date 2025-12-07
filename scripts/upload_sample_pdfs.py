#!/usr/bin/env python3
"""
Quick script to download sample AI/ML papers from arXiv and upload to GCS
"""
import os
import requests
from google.cloud import storage

# Sample arXiv papers (AI/ML themed)
SAMPLE_PAPERS = [
    "2103.14030",  # CLIP (OpenAI)
    "1706.03762",  # Attention Is All You Need (Transformers)
    "2005.14165",  # GPT-3
    "2010.11929",  # ViT (Vision Transformer)
    "1810.04805",  # BERT
]

BUCKET_NAME = "researchai-pdfs-eu"
DATA_DIR = "/Users/smarthbakshi/Desktop/projects/Research-AI/data/arxiv"

def download_arxiv_pdf(arxiv_id, output_dir):
    """Download PDF from arXiv"""
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    output_path = os.path.join(output_dir, f"{arxiv_id}.pdf")

    if os.path.exists(output_path):
        print(f"✓ {arxiv_id}.pdf already exists")
        return output_path

    print(f"Downloading {arxiv_id}.pdf...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✓ Downloaded {arxiv_id}.pdf")
    return output_path

def upload_to_gcs(local_path, bucket_name):
    """Upload file to Google Cloud Storage"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob_name = os.path.basename(local_path)
    blob = bucket.blob(blob_name)

    if blob.exists():
        print(f"✓ {blob_name} already exists in GCS")
        return

    print(f"Uploading {blob_name} to gs://{bucket_name}/...")
    blob.upload_from_filename(local_path)
    print(f"✓ Uploaded {blob_name}")

def main():
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"📥 Downloading {len(SAMPLE_PAPERS)} sample papers from arXiv...")

    for arxiv_id in SAMPLE_PAPERS:
        try:
            # Download PDF
            local_path = download_arxiv_pdf(arxiv_id, DATA_DIR)

            # Upload to GCS
            upload_to_gcs(local_path, BUCKET_NAME)

        except Exception as e:
            print(f"❌ Error processing {arxiv_id}: {e}")
            continue

    print(f"\n✅ Done! Uploaded papers to gs://{BUCKET_NAME}/")
    print(f"   Local copies in: {DATA_DIR}")

if __name__ == "__main__":
    main()
