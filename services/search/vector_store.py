from abc import ABC, abstractmethod

class VectorStore(ABC):
    @abstractmethod
    def upsert(self, docs: list[dict]):
        """Upsert documents with embeddings and metadata."""
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search using vector/hybrid query and return top-k results."""
        pass
