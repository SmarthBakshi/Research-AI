from typing import List
from .base import TextChunker

class SlidingWindowChunker(TextChunker):
    def __init__(self, window_size: int = 200, stride: int = 100):
        self.window_size = window_size
        self.stride = stride

    def chunk(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.stride):
            chunk = words[i:i + self.window_size]
            if len(chunk) < 50:
                continue
            chunks.append(" ".join(chunk))
        return chunks
