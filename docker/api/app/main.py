"""
ResearchAI FastAPI Backend

Provides REST API endpoints for:
- Health checking
- Document search and retrieval
- Question answering with RAG
- System statistics

Author: ResearchAI Team
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

# Add services to path for imports
sys.path.insert(0, '/app')
sys.path.insert(0, '/opt/researchai')

try:
    from services.embedding.huggingface_embedder import HuggingFaceEmbedder
    from services.search.opensearch_store import OpenSearchStore
except ImportError:
    # Fallback for development
    HuggingFaceEmbedder = None
    OpenSearchStore = None

# ==================== Configuration ====================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://researchai:researchai@postgres:5432/researchai_app")
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/e5-base-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "ollama"

# Parse OpenSearch URL
opensearch_host = OPENSEARCH_URL.replace("http://", "").replace("https://", "").split(":")[0]
opensearch_port = int(OPENSEARCH_URL.split(":")[-1]) if ":" in OPENSEARCH_URL else 9200

# ==================== FastAPI App ====================

app = FastAPI(
    title="ResearchAI API",
    description="RAG system for scientific papers from arXiv",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Global State ====================

embedder = None
search_store = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global embedder, search_store

    if HuggingFaceEmbedder:
        try:
            embedder = HuggingFaceEmbedder(model_name=EMBEDDING_MODEL)
            print(f"✅ Loaded embedding model: {EMBEDDING_MODEL}")
        except Exception as e:
            print(f"⚠️  Could not load embedder: {e}")

    if OpenSearchStore:
        try:
            search_store = OpenSearchStore(
                host=opensearch_host,
                port=opensearch_port,
                index_name="chunks"
            )
            print(f"✅ Connected to OpenSearch at {opensearch_host}:{opensearch_port}")
        except Exception as e:
            print(f"⚠️  Could not connect to OpenSearch: {e}")

# ==================== Request/Response Models ====================

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, bool]

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    search_type: str = Field(default="hybrid", description="Type of search: 'dense', 'hybrid'")

class SearchResult(BaseModel):
    chunk_text: str
    source_file: str
    chunk_index: int
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    search_type: str
    count: int

class AskRequest(BaseModel):
    question: str = Field(..., description="Question to ask about the research papers")
    k: int = Field(default=5, ge=1, le=20, description="Number of context chunks to retrieve")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    search_type: str = Field(default="hybrid", description="Search type: 'dense' or 'hybrid'")

class Citation(BaseModel):
    source_file: str
    chunk_index: int
    excerpt: str

class AskResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
    retrieved_chunks: int
    model: str

class StatsResponse(BaseModel):
    total_chunks: int
    indexed_chunks: int
    unique_papers: int
    index_name: str

# ==================== Endpoints ====================

@app.get("/healthz", response_model=HealthResponse)
async def healthz():
    """Health check endpoint with service status"""
    services = {
        "embedder": embedder is not None,
        "opensearch": search_store is not None,
    }

    # Check LLM provider availability
    if LLM_PROVIDER == "openai":
        services["llm"] = bool(OPENAI_API_KEY)
        services["llm_provider"] = "openai"
    else:
        # Check Ollama availability
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{OLLAMA_URL}/api/tags")
                services["llm"] = response.status_code == 200
                services["llm_provider"] = "ollama"
        except Exception:
            services["llm"] = False
            services["llm_provider"] = "ollama"

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "services": services
    }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for relevant document chunks using vector or hybrid search.

    - **query**: Text query to search for
    - **k**: Number of results to return (1-20)
    - **search_type**: 'dense' for pure vector search, 'hybrid' for BM25+vector
    """
    if not embedder or not search_store:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search services not initialized"
        )

    try:
        # Generate query embedding
        query_embedding = embedder.embed_batch([request.query])[0]

        # Perform search
        if request.search_type == "dense":
            raw_results = search_store.search_dense(query_embedding, k=request.k)
        elif request.search_type == "hybrid":
            raw_results = search_store.search_hybrid(
                query_vector=query_embedding,
                query_text=request.query,
                k=request.k
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="search_type must be 'dense' or 'hybrid'"
            )

        # Format results
        results = []
        for hit in raw_results:
            source = hit.get("_source", {})
            results.append(SearchResult(
                chunk_text=source.get("chunk_text", ""),
                source_file=source.get("source_file", ""),
                chunk_index=source.get("chunk_index", 0),
                score=hit.get("_score", 0.0)
            ))

        return SearchResponse(
            query=request.query,
            results=results,
            search_type=request.search_type,
            count=len(results)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Answer a question using RAG (Retrieval-Augmented Generation).

    Steps:
    1. Retrieve relevant chunks from OpenSearch
    2. Build context from top-k chunks
    3. Generate answer using LLM (Ollama)
    4. Return answer with citations
    """
    if not embedder or not search_store:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search services not initialized"
        )

    try:
        # Step 1: Retrieve relevant chunks
        query_embedding = embedder.embed_batch([request.question])[0]

        if request.search_type == "hybrid":
            raw_results = search_store.search_hybrid(
                query_vector=query_embedding,
                query_text=request.question,
                k=request.k
            )
        else:
            raw_results = search_store.search_dense(query_embedding, k=request.k)

        # Step 2: Build context and citations
        context_parts = []
        citations = []

        for i, hit in enumerate(raw_results):
            source = hit.get("_source", {})
            chunk_text = source.get("chunk_text", "")
            source_file = source.get("source_file", "")
            chunk_index = source.get("chunk_index", 0)

            context_parts.append(f"[{i+1}] {chunk_text}")
            citations.append(Citation(
                source_file=source_file,
                chunk_index=chunk_index,
                excerpt=chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
            ))

        context = "\n\n".join(context_parts)

        # Step 3: Generate answer using LLM
        prompt = f"""You are a helpful research assistant. Answer the user's question based on the provided research paper excerpts. Be concise and cite your sources using [1], [2], etc.

Research Paper Excerpts:
{context}

Question: {request.question}

Answer:"""

        model_used = ""

        try:
            if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
                # Use OpenAI API
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {OPENAI_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": OPENAI_MODEL,
                            "messages": [
                                {"role": "system", "content": "You are a helpful research assistant."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": request.temperature,
                            "max_tokens": 1000
                        }
                    )

                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"OpenAI API error: {response.text}"
                        )

                    openai_response = response.json()
                    answer = openai_response["choices"][0]["message"]["content"].strip()
                    model_used = OPENAI_MODEL

            else:
                # Use Ollama
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{OLLAMA_URL}/api/generate",
                        json={
                            "model": LLM_MODEL,
                            "prompt": prompt,
                            "temperature": request.temperature,
                            "stream": False
                        }
                    )

                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="LLM service unavailable"
                        )

                    llm_response = response.json()
                    answer = llm_response.get("response", "").strip()
                    model_used = LLM_MODEL

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="LLM request timed out"
            )
        except httpx.ConnectError:
            # Fallback if LLM is not available
            answer = f"Based on {len(citations)} relevant research papers, I found information related to your question. However, the LLM service is currently unavailable. Please check the retrieved citations below."
            model_used = "fallback"

        return AskResponse(
            question=request.question,
            answer=answer,
            citations=citations,
            retrieved_chunks=len(citations),
            model=model_used
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )

@app.get("/stats", response_model=StatsResponse)
async def stats():
    """Get system statistics about indexed documents"""
    import psycopg2

    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://"))
        cur = conn.cursor()

        # Get total chunks
        cur.execute("SELECT COUNT(*) FROM chunks")
        total_chunks = cur.fetchone()[0]

        # Get indexed chunks
        cur.execute("SELECT COUNT(*) FROM chunks WHERE indexed_at IS NOT NULL")
        indexed_chunks = cur.fetchone()[0]

        # Get unique papers
        cur.execute("SELECT COUNT(DISTINCT source_file) FROM chunks")
        unique_papers = cur.fetchone()[0]

        conn.close()

        return StatsResponse(
            total_chunks=total_chunks,
            indexed_chunks=indexed_chunks,
            unique_papers=unique_papers,
            index_name="chunks"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "ResearchAI API",
        "version": "1.0.0",
        "description": "RAG system for scientific papers from arXiv",
        "endpoints": {
            "health": "/healthz",
            "docs": "/docs",
            "search": "/search",
            "ask": "/ask",
            "stats": "/stats"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
