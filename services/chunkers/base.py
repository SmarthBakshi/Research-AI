from abc import ABC, abstractmethod
from typing import List

class TextChunker(ABC):
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """Split the input text into meaningful chunks."""
        pass
