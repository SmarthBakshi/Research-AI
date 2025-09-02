import os
import json
from typing import List, Dict, Any, Optional
from opensearchpy import OpenSearch


class OpenSearchStore:
    """
    Handles vector-based and hybrid search using OpenSearch.
    Supports:
    - Index creation with knn_vector field
    - Upserting embedded chunks
    - Dense kNN search
    - Hybrid BM25 + vector search
    """

    def __init__(
        self,
        host: str = os.getenv("OPENSEARCH_HOST", "localhost"),
        port: int = int(os.getenv("OPENSEARCH_PORT", 9200)),
        index_name: str = os.getenv("OPENSEARCH_INDEX_NAME", "chunks"),
        dim: int = 768,
    ):
        self.host = host
        self.port = port
        self.index_name = index_name
        self.dim = dim

        self.client = OpenSearch(
            hosts=[{"host": self.host, "port": self.port}],
            use_ssl=False,
            verify_certs=False,
            timeout=30,
        )

    def create_index(self):
        """
        Creates a vector-capable index in OpenSearch for semantic and BM25 search.
        This includes both a `knn_vector` field and a `text` field for hybrid search.
        """
        if self.client.indices.exists(index=self.index_name):
            print(f"Index '{self.index_name}' already exists.")
            return

        index_body = {
            "settings": {
                "index": {
                    "knn": True
                }
            },
            "mappings": {
                "properties": {
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": self.dim,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "nmslib"
                        }
                    },
                    "chunk_text": {"type": "text"},
                    "chunk_index": {"type": "integer"},
                    "source_file": {"type": "keyword"},
                }
            }
        }

        self.client.indices.create(index=self.index_name, body=index_body)
        print(f"Created index '{self.index_name}' with vector and text support.")

    def upsert_documents(self, docs: List[Dict[str, Any]]):
        """
        Upserts a batch of documents with embeddings and metadata.

        :param docs: List of dicts with keys: chunk_text, embedding, chunk_index, source_file
        """
        bulk_lines = ""

        for doc in docs:
            doc_id = f"{doc['source_file']}_{doc['chunk_index']}"
            action = {"index": {"_index": self.index_name, "_id": doc_id}}
            bulk_lines += json.dumps(action) + "\n"
            bulk_lines += json.dumps(doc) + "\n"

        response = self.client.bulk(body=bulk_lines)
        if response.get("errors"):
            print("Bulk insert errors:", response)
        else:
            print(f"✅ Upserted {len(docs)} documents into '{self.index_name}'.")

    def search_dense(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs dense kNN search on vector index.

        :param query_vector: List of floats (embedding)
        :param k: Top-K results to return
        :return: List of matching documents
        """
        body = {
            "size": k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_vector,
                        "k": k
                    }
                }
            }
        }
        response = self.client.search(index=self.index_name, body=body)
        return response.get("hits", {}).get("hits", [])

    def search_hybrid(
        self,
        query_vector: List[float],
        query_text: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Performs hybrid search: BM25 match + vector kNN.

        :param query_vector: Embedding vector
        :param query_text: Text query (BM25)
        :param k: Number of results
        :return: Ranked search results
        """
        body = {
            "size": k,
            "query": {
                "bool": {
                    "must": [
                        {"match": {"chunk_text": query_text}}
                    ],
                    "should": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_vector,
                                    "k": k
                                }
                            }
                        }
                    ]
                }
            }
        }

        response = self.client.search(index=self.index_name, body=body)
        return response.get("hits", {}).get("hits", [])
