from pathlib import Path
from services.processing.extractors.pdfminer_extractor import PdfMinerExtractor

def test_pdfminer_extract_smoke(tmp_path: Path):
    # Use a tiny fixture PDF you already have, or generate one if needed
    sample = Path("data/fixtures/simple.pdf")
    if not sample.exists():
        # Skip gracefully if fixture not present
        return
    ext = PdfMinerExtractor()
    out = ext.extract(sample)
    assert out.pages, "No pages extracted"
    assert isinstance(out.full_text, str)
