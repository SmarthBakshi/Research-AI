import os 
from airflow import DAG
from airflow.decorators import task
from datetime import datetime
from services.processing.extractors.base import PdfExtractor
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
    description="Extract text from PDFs, chunk, and store in DB",
    tags=["researchai", "processing", "pc24"]
) as dag:

    @task()
    def process_each_pdf(key: str):
        print(f"🧪 STARTING: {key}")
        try:
            # Step 1: Initialize components
            print("🔧 Initializing components...")
            extractor = PdfExtractor()
            ocr = TesseractOCR()
            normalizer = TextNormalizer(remove_latex=True)
            chunker = Chunker()

            # Step 2: Download PDF from MinIO
            print(f"📥 Downloading PDF from MinIO: {key}")
            pdf_path = download_file(bucket_name="researchai", object_name=key)
            print(f"✅ PDF downloaded to: {pdf_path}")

            # Step 3: Try PDF-based text extraction
            print("🔍 Trying primary PDF text extraction...")
            text = extractor.extract(pdf_path)
            if not text:
                print("⚠️ Primary extraction failed. Trying OCR...")
                text = ocr.extract(pdf_path)

            if not text:
                error_msg = f"❌ Could not extract any text from {key}"
                print(error_msg)
                raise ValueError(error_msg)

            print("🧹 Normalizing extracted text...")
            normalized = normalizer.clean(text)

            print("📦 Chunking normalized text...")
            chunks = chunker.chunk(normalized, source=key)

            print(f"🗃 Writing {len(chunks)} chunks to database...")
            write_chunks_to_db(chunks)

            success_msg = f"✅ Processed {key} successfully with {len(chunks)} chunks."
            print(success_msg)
            return {
                "key": key,
                "status": "success",
                "num_chunks": len(chunks)
            }

        except Exception as e:
            error_msg = f"🔥 ERROR while processing {key}: {str(e)}"
            print(error_msg)
            raise  # Let Airflow handle retries


    @task()
    def list_pdf_keys():
        bucket = os.getenv("MINIO_BUCKET", "researchai")
        files = list_files(bucket)
        print(f"Found {len(files)} files in bucket '{bucket}'")
        return files

    # ✅ Correct dynamic mapping
    keys = list_pdf_keys()
    process_each_pdf.expand(key=keys)
