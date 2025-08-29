import re
from typing import List, Dict

class Chunker:
    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, source_file: str) -> List[Dict]:
        """
        Split text into overlapping chunks using a sliding window strategy.
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words).strip()

            if len(chunk_text) > 0:
                chunks.append({
                    "source_file": source_file,
                    "chunk_index": len(chunks),
                    "chunk_text": chunk_text
                })

        return chunks
