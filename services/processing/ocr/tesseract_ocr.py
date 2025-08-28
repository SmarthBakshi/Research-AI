from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

@dataclass
class TesseractConfig:
    lang: str = "eng"
    psm: int = 3             # page segmentation mode
    oem: int = 3             # OCR engine mode
    dpi: int = 300
    poppler_path: Optional[str] = None   # if poppler isn't on PATH (macOS: brew install poppler)

class TesseractOCR:
    def __init__(self, cfg: Optional[TesseractConfig] = None):
        self.cfg = cfg or TesseractConfig()

    def _tess_cmd(self) -> str:
        return f"--oem {self.cfg.oem} --psm {self.cfg.psm}"

    def ocr_pdf_pages(
        self,
        pdf_path: Path,
        pages: Iterable[int],
    ) -> List[Tuple[int, str, float]]:
        """
        OCR only `pages` (1-based). Returns list of (page_number, text, confidence_est).
        """
        # pdf2image pages are 1-based if we pass first_page/last_page
        first = min(pages)
        last  = max(pages)
        images: List[Image.Image] = convert_from_path(
            str(pdf_path),
            dpi=self.cfg.dpi,
            first_page=first,
            last_page=last,
            poppler_path=self.cfg.poppler_path,
        )
        # Map back to the exact requested pages
        requested = set(pages)
        out: List[Tuple[int, str, float]] = []
        for idx, img in enumerate(images, start=first):
            if idx not in requested:
                continue
            data = pytesseract.image_to_data(
                img, lang=self.cfg.lang, config=self._tess_cmd(), output_type=pytesseract.Output.DICT
            )
            text = pytesseract.image_to_string(img, lang=self.cfg.lang, config=self._tess_cmd())
            # crude average confidence over non-empty tokens
            confs = [float(c) for c in data.get("conf", []) if c not in ("-1", "", None)]
            conf = sum(confs) / len(confs) / 100.0 if confs else 0.0
            out.append((idx, text.strip(), conf))
        return out
