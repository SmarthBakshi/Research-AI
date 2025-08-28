from __future__ import annotations
from pathlib import Path
from typing import List
from .base import PdfExtractor, ExtractResult, PageText
from .pdfminer_extractor import PdfMinerExtractor
from ..ocr.tesseract_ocr import TesseractOCR, TesseractConfig

class HybridPdfExtractor(PdfExtractor):
    def __init__(self, min_chars_per_page: int = 20, ocr_cfg: TesseractConfig | None = None):
        self.pdf = PdfMinerExtractor(min_chars_per_page=min_chars_per_page)
        self.ocr = TesseractOCR(cfg=ocr_cfg)

    def extract(self, path: Path) -> ExtractResult:
        res = self.pdf.extract(path)
        # find sparse pages flagged during pdfminer pass
        sparse_pages: List[int] = []
        for err in res.errors:
            if err.startswith("page_") and err.endswith("_sparse_pdf_text"):
                pno = int(err.split("_")[1])
                sparse_pages.append(pno)

        if not sparse_pages:
            return res

        try:
            ocred = {p: (t, c) for p, t, c in self.ocr.ocr_pdf_pages(path, sparse_pages)}
            for p in res.pages:
                if p.page_number in ocred:
                    text, conf = ocred[p.page_number]
                    # Replace only if OCR actually found text
                    if len(text) > len(p.text):
                        p.text = text
                        p.source = "ocr"
                        p.confidence = conf
        except Exception as e:
            res.errors.append(f"ocr_failed: {e}")

        return res
