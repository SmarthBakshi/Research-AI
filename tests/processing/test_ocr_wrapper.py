from pathlib import Path
import pytest
from services.processing.ocr.tesseract_ocr import TesseractOCR, TesseractConfig

@pytest.mark.skip(reason="Needs tesseract+poppler installed in CI/host")
def test_tesseract_ocr_smoke():
    pdf = Path("data/fixtures/scanned.pdf")
    if not pdf.exists():
        return
    ocr = TesseractOCR(TesseractConfig(lang="eng", dpi=200))
    res = ocr.ocr_pdf_pages(pdf, pages=[1])
    assert res and isinstance(res[0][1], str)
