import re
from typing import List
from .base import TextChunker

class HeadingAwareChunker(TextChunker):
    def chunk(self, text: str) -> List[str]:
        # Regex pattern to identify section headings
        pattern = re.compile(r"(?:^|\n)(\d{1,2}(?:\.\d+)*\.?\s+.+?)(?=\n\d{1,2}(?:\.\d+)*\.?\s+|$)", re.MULTILINE)
        matches = pattern.findall(text)
        return [m.strip() for m in matches if len(m.strip()) > 50]
