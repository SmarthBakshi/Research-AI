import os 
from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule
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
    schedule_interval=None,
    catchup=False,
    description="Extract text from PDFs, chunk, and store in DB",
    tags=["researchai", "processing", "pc24"]
) as dag:

    @task()
    def process_each_pdf(key: str):
        extractor = PdfExtractor()
        ocr = TesseractOCR()
        normalizer = TextNormalizer(remove_latex=True)
        chunker = Chunker()

        # Download from MinIO
        pdf_path = download_file(key)

        # Try primary extraction
        text = extractor.extract(pdf_path)
        if not text:
            text = ocr.extract(pdf_path)

        if not text:
            raise ValueError(f"❌ Could not extract text from {key}")

        normalized = normalizer.clean(text)
        chunks = chunker.chunk(normalized, source=key)
        write_chunks_to_db(chunks)

        return f"✅ Processed {key}"

    @task()
    def list_pdf_keys():
        bucket = os.getenv("MINIO_BUCKET", "researchai")
        return list_files(bucket)  

    # ✅ Correct dynamic mapping
    process_each_pdf.expand(key=list_pdf_keys())
