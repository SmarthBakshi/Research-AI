import sys
sys.path.append("/opt/researchai")

import os 
from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from services.processing.extractors.hybrid_extractor import HybridPdfExtractor
from services.processing.ocr.tesseract_ocr import TesseractOCR
from services.processing.normalization.text_normaliser import TextNormalizer
from services.processing.chunking.chunker import Chunker
from services.processing.db_write.db_writer import write_chunks_to_db
from services.ingestion.arxiv.minio_utils import list_files, download_file

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="process_pdfs",
    default_args=default_args,
    schedule=None,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=4,
    description="Extract text from PDFs, chunk, and store in DB",
    tags=["researchai", "processing", "pc24"]
) as dag:

    @task(execution_timeout=timedelta(minutes=10))
    def process_each_pdf(key: str):
        print(f"🧪 STARTING: {key}")
        try:
            # Step 1: Initialize components
            print("🔧 Initializing components...")
            extractor = HybridPdfExtractor()
            ocr = TesseractOCR()
            normalizer = TextNormalizer(remove_latex=True)
            chunker = Chunker()

            # Step 2: Download PDF from MinIO
            print(f"📥 Downloading PDF from MinIO: {key}")
            pdf_path = download_file(bucket_name="researchai", object_name=key)
            print(f"✅ PDF downloaded to: {pdf_path}")

            # Step 3: Try PDF-based text extraction
            print("🔍 Trying primary PDF text extraction...")
            result = extractor.extract(pdf_path)
            used_ocr = False

            # Extract text from ExtractResult object
            text = None
            if result is None:
                text = None
            elif hasattr(result, "full_text"):
                # ExtractResult object has full_text property
                text = result.full_text
                used_ocr = any(page.source == "ocr" for page in result.pages) if hasattr(result, "pages") else False
            elif hasattr(result, "text"):
                text = result.text
                used_ocr = getattr(result, "used_ocr", False) or False
            elif isinstance(result, (tuple, list)) and result:
                text = result[0]
            else:
                # Fallback: convert to string (this should NOT happen normally)
                text = str(result) if result else None

            if not text:
                print("⚠️ Primary extraction returned empty. Trying OCR...")
                ocr_result = ocr.extract(pdf_path)
                if hasattr(ocr_result, "full_text"):
                    # OCR also returns ExtractResult with full_text
                    text = ocr_result.full_text
                    used_ocr = True
                elif hasattr(ocr_result, "text"):
                    text = ocr_result.text
                    used_ocr = True
                else:
                    text = str(ocr_result) if ocr_result else None
                    used_ocr = True

            if not text:
                error_msg = f"❌ Could not extract any text from {key}"
                print(error_msg)
                raise ValueError(error_msg)

            print("🧹 Normalizing extracted text...")
            normalized = normalizer.clean(text)

            print("📦 Chunking normalized text...")
            chunks = chunker.chunk(normalized, source_file=key)

            print(f"🗃 Writing {len(chunks)} chunks to database...")
            write_chunks_to_db(chunks)

            if os.path.exists(pdf_path):
                try:        
                    os.remove(pdf_path)
                    print(f"✅ Deleted local file: {pdf_path}")
                except Exception as cleanup_err:
                    print(f"⚡️ Failed to delete {pdf_path}: {cleanup_err}") 
            
            # after successful DB write
            success_msg = f"✅ Processed {key} successfully with {len(chunks)} chunks."
            print(success_msg)

            metrics = {
                "key": key,
                "status": "success",
                "num_chunks": len(chunks),
                "used_ocr": used_ocr,
                "timestamp": datetime.utcnow().isoformat()
            }
            return metrics


        except Exception as e:
            error_msg = f"🔥 ERROR while processing {key}: {str(e)}"
            print(error_msg)

            # ✏️ Temporary quarantine log (can be replaced with DB insert)
            quarantine_path = "/opt/airflow/logs/quarantine_keys.txt"
            with open(quarantine_path, "a") as f:
                f.write(f"{datetime.utcnow().isoformat()},{key},{str(e)}\n")

            raise


    @task()
    def list_pdf_keys():
        bucket = os.getenv("MINIO_BUCKET", "researchai")
        files = list_files(bucket)
        print(f"Found {len(files)} files in bucket '{bucket}'")
        return files
# trigger parse

    # ✅ Correct dynamic mapping
    keys = list_pdf_keys()
    process_each_pdf.expand(key=keys)
