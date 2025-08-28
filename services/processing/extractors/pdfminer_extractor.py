# services/processing/extractors/pdfminer_extractor.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict
from dataclasses import asdict
from .base import PdfExtractor, ExtractResult, PageText

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from pypdf import PdfReader

class PdfMinerExtractor(PdfExtractor):
    """Primary text extractor using pdfminer.six; fast, no external binaries."""

    def __init__(self, min_chars_per_page: int = 20):
        self.min_chars = min_chars_per_page

    def _read_metadata(self, path: Path) -> Dict[str, str]:
        md: Dict[str, str] = {}
        try:
            reader = PdfReader(str(path))
            info = reader.metadata or {}
            # Normalize to str
            for k, v in info.items():
                md[str(k).strip("/")] = str(v)
            md["num_pages"] = str(len(reader.pages))
        except Exception as e:
            md["metadata_error"] = str(e)
        return md

    def extract(self, path: Path) -> ExtractResult:
        res = ExtractResult(path=path, metadata=self._read_metadata(path))
        try:
            for i, layout in enumerate(extract_pages(str(path)), start=1):
                chunks: List[str] = []
                for element in layout:
                    if isinstance(element, LTTextContainer):
                        chunks.append(element.get_text())
                page_text = "".join(chunks).strip()
                res.pages.append(PageText(
                    page_number=i,
                    text=page_text,
                    source="pdfminer",
                    confidence=None
                ))
        except Exception as e:
            res.errors.append(f"pdfminer_failed: {e}")

        # Mark obviously-empty pages (for OCR fallback to decide on)
        for p in res.pages:
            if len(p.text) < self.min_chars:
                # encode a hint in the errors list per page (non-fatal)
                res.errors.append(f"page_{p.page_number}_sparse_pdf_text")

        return res
