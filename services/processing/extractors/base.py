# services/processing/extractors/base.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Iterable
from abc import ABC, abstractmethod
from pathlib import Path

@dataclass
class PageText:
    page_number: int           # 1-based
    text: str
    source: str                # "pdfminer" | "ocr" | "manual" | etc.
    confidence: Optional[float] = None   # for OCR

@dataclass
class ExtractResult:
    path: Path
    pages: List[PageText] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n".join(p.text for p in sorted(self.pages, key=lambda x: x.page_number))

class PdfExtractor(ABC):
    """Abstract base for all PDF extractors."""

    @abstractmethod
    def extract(self, path: Path) -> ExtractResult:
        """Extract per-page text + metadata from a PDF at `path`."""
        raise NotImplementedError
