# 📚 ResearchAI Codebase & Workflow Guide

## 🎯 Overview

ResearchAI is an end-to-end **Retrieval-Augmented Generation (RAG) system** designed to ingest, process, embed, and semantically search scientific papers from arXiv. This guide explains the entire codebase structure, workflow, and component interactions.

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                   (Gradio UI - Port 7860)                        │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER                                   │
│                  (FastAPI - Port 8000)                           │
│            Endpoints: /healthz, /ask (planned)                   │
└────────┬──────────────────────────────────────┬─────────────────┘
         │                                       │
         ▼                                       ▼
┌────────────────────┐              ┌──────────────────────────┐
│  RETRIEVAL LAYER   │              │   GENERATION LAYER       │
│   (OpenSearch)     │              │  (LLM via Ollama)        │
│  - Vector Search   │              │  - Prompt Construction   │
│  - BM25 Search     │              │  - Answer Generation     │
│  - Hybrid Search   │              │                          │
└────────────────────┘              └──────────────────────────┘
         ▲                                       
         │                                       
┌────────┴────────────────────────────────────────────────────────┐
│                  PROCESSING PIPELINE                             │
│                  (Airflow DAGs)                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ 1. Ingest    │→ │ 2. Process   │→ │ 3. Embed & Index     │ │
│  │    PDFs      │  │    PDFs      │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└──────────┬───────────────┬────────────────────┬────────────────┘
           │               │                    │
           ▼               ▼                    ▼
┌──────────────┐  ┌──────────────┐   ┌─────────────────┐
│    MinIO     │  │  PostgreSQL  │   │   OpenSearch    │
│ (PDF Store)  │  │ (Metadata &  │   │ (Vector Index)  │
│              │  │  Chunks)     │   │                 │
└──────────────┘  └──────────────┘   └─────────────────┘
```

---

## 📂 Repository Structure

```
Research-AI/
├── api/                          # API service code
│   ├── README.md
│   └── __init__.py
│
├── core/                         # Core library code
│   └── src/researchai_core/
│
├── dags/                         # Airflow DAG definitions
│   ├── ingest_arxiv.py          # DAG 1: Download PDFs from arXiv
│   ├── process_pdfs.py          # DAG 2: Extract & chunk text
│   └── embed_and_index.py       # DAG 3: Generate embeddings & index
│
├── services/                     # Modular service components
│   ├── chunkers/                # Text chunking strategies
│   │   ├── base.py
│   │   ├── heading_aware.py
│   │   └── sliding_window.py
│   │
│   ├── embedding/               # Embedding generation
│   │   ├── embedder.py         # Abstract base class
│   │   └── huggingface_embedder.py
│   │
│   ├── ingestion/              # Data ingestion from arXiv
│   │   └── arxiv/
│   │       ├── client.py       # arXiv API client
│   │       ├── config.py
│   │       ├── minio_utils.py  # MinIO helper functions
│   │       ├── runner.py       # Ingestion orchestration
│   │       └── writer.py       # Write to MinIO
│   │
│   ├── processing/             # PDF processing pipeline
│   │   ├── extractors/        # PDF text extraction
│   │   │   ├── base.py
│   │   │   ├── hybrid_extractor.py  # Smart PDF + OCR
│   │   │   └── pdfminer_extractor.py
│   │   ├── chunking/          # Text chunking
│   │   │   └── chunker.py
│   │   ├── db_write/          # Database operations
│   │   │   └── db_writer.py
│   │   ├── normalization/     # Text cleaning
│   │   │   └── text_normaliser.py
│   │   └── ocr/               # OCR fallback
│   │       └── tesseract_ocr.py
│   │
│   └── search/                 # Search & retrieval
│       ├── opensearch_store.py # OpenSearch client
│       └── vector_store.py
│
├── docker/                      # Docker configurations
│   ├── api/                    # API service Dockerfile
│   │   ├── Dockerfile
│   │   └── app/main.py
│   └── ui/                     # UI service Dockerfile
│       ├── Dockerfile
│       └── app.py
│
├── infra/                       # Infrastructure configs
│   └── airflow/
│       └── Dockerfile
│
├── scripts/                     # Utility scripts
│   └── researchai/
│       ├── embedder_test.py
│       ├── ingest_metadata.py
│       └── ingest_pdf.py
│
├── tests/                       # Test suite
│   ├── ingestion/
│   ├── processing/
│   └── unit/
│
├── data/                        # Data directory
│   └── arxiv/
│       └── metadata.json       # arXiv paper metadata
│
├── docs/                        # Documentation
│   ├── architecture.gif
│   └── CODEBASE_GUIDE.md       # This file
│
├── docker-compose.yml           # Service orchestration
├── pyproject.toml              # Python dependencies
├── Makefile                    # Common commands
└── README.md                   # Project README
```

---

## 🔄 Complete Data Flow Workflow

### Phase 1: Ingestion (DAG: `ingest_arxiv_pdf`)

**File:** `dags/ingest_arxiv.py`

**Purpose:** Download PDFs from arXiv and store them in MinIO

**Flow:**
```
1. read_metadata()
   ├─ Reads: /opt/researchai/data/arxiv/metadata.json
   └─ Returns: List of paper metadata dicts

2. ingest(metadata)
   ├─ For each paper in metadata:
   │  ├─ Extract arXiv ID
   │  ├─ Construct PDF URL: https://arxiv.org/pdf/{arxiv_id}.pdf
   │  ├─ Download PDF content
   │  ├─ Calculate SHA256 hash
   │  ├─ Upload to MinIO: raw/pdfs/{hash}.pdf
   │  └─ Skip if already exists
   └─ Returns: List of ingestion results
```

**Key Components:**
- `services/ingestion/arxiv/runner.py`: Orchestrates ingestion
- `services/ingestion/arxiv/writer.py`: MinIOWriter class
  - Uses boto3 to interact with MinIO (S3-compatible API)
  - Implements content-addressable storage (filename = hash of content)
  - Idempotent: checks if PDF exists before uploading

**Storage Location:**
- MinIO bucket: `researchai`
- Path pattern: `raw/pdfs/{sha256_hash}.pdf`

---

### Phase 2: Processing (DAG: `process_pdfs`)

**File:** `dags/process_pdfs.py`

**Purpose:** Extract text from PDFs, normalize, chunk, and store in PostgreSQL

**Flow:**
```
1. list_pdf_keys()
   ├─ Connects to MinIO
   ├─ Lists all files in bucket 'researchai'
   └─ Returns: List of PDF keys

2. process_each_pdf(key)  [Dynamic task mapping - runs in parallel]
   │
   ├─ Step 1: Download PDF from MinIO
   │  └─ services/ingestion/arxiv/minio_utils.download_file()
   │
   ├─ Step 2: Extract Text (Hybrid approach)
   │  ├─ Primary: HybridPdfExtractor.extract()
   │  │  ├─ Uses PdfMinerExtractor first
   │  │  │  └─ services/processing/extractors/pdfminer_extractor.py
   │  │  ├─ Detects "sparse" pages (< 20 chars/page)
   │  │  └─ Falls back to OCR for sparse pages
   │  │     └─ services/processing/ocr/tesseract_ocr.py
   │  └─ Fallback: Full OCR if primary fails
   │
   ├─ Step 3: Normalize Text
   │  └─ TextNormalizer.clean()
   │     └─ services/processing/normalization/text_normaliser.py
   │     ├─ Removes LaTeX commands
   │     ├─ Fixes spacing issues
   │     ├─ Removes special characters
   │     └─ Normalizes whitespace
   │
   ├─ Step 4: Chunk Text
   │  └─ Chunker.chunk()
   │     └─ services/processing/chunking/chunker.py
   │     ├─ Sliding window approach
   │     ├─ Default: 300 words per chunk
   │     ├─ Overlap: 50 words
   │     └─ Returns: List of {source_file, chunk_index, chunk_text}
   │
   ├─ Step 5: Store in PostgreSQL
   │  └─ write_chunks_to_db()
   │     └─ services/processing/db_write/db_writer.py
   │     ├─ Table: chunks
   │     ├─ Columns: id, source_file, chunk_index, chunk_text, created_at
   │     └─ Uses SQLAlchemy ORM
   │
   └─ Step 6: Cleanup
      └─ Delete local PDF file
```

**Key Components:**

1. **HybridPdfExtractor** (`services/processing/extractors/hybrid_extractor.py`)
   - Intelligent extraction: tries PDF text first, falls back to OCR
   - Returns ExtractResult object with text, pages, and error flags

2. **TextNormalizer** (`services/processing/normalization/text_normaliser.py`)
   - Cleans and standardizes extracted text
   - Removes LaTeX artifacts, fixes spacing, normalizes unicode

3. **Chunker** (`services/processing/chunking/chunker.py`)
   - Sliding window chunking strategy
   - Configurable chunk size and overlap
   - Preserves context across chunks

4. **Database Writer** (`services/processing/db_write/db_writer.py`)
   - SQLAlchemy-based PostgreSQL client
   - Auto-creates tables if they don't exist
   - Stores chunks with metadata

**Error Handling:**
- Failed PDFs logged to: `/opt/airflow/logs/quarantine_keys.txt`
- Includes timestamp, key, and error message
- Task execution timeout: 10 minutes

**Parallelization:**
- Uses Airflow dynamic task mapping
- `max_active_tasks=4`: Process 4 PDFs concurrently
- Each PDF is a separate task instance

---

### Phase 3: Embedding & Indexing (DAG: `embed_and_index`)

**File:** `dags/embed_and_index.py`

**Purpose:** Generate embeddings for chunks and index them in OpenSearch

**Flow:**
```
1. load_unindexed_chunks()
   ├─ Query PostgreSQL: SELECT chunks WHERE indexed_at IS NULL
   ├─ LIMIT 100 (batch size)
   └─ Returns: List of {chunk_id, chunk_text, source_file, chunk_index}

2. embed_chunks(chunks)
   ├─ Initialize: HuggingFaceEmbedder("intfloat/e5-base-v2")
   │  └─ services/embedding/huggingface_embedder.py
   │  └─ Model: 768-dimensional embeddings
   ├─ Extract text from all chunks
   ├─ Generate embeddings (batch processing)
   └─ Returns: chunks + embeddings

3. upsert_to_opensearch(chunks)
   ├─ Initialize: OpenSearchStore
   │  └─ services/search/opensearch_store.py
   ├─ Bulk upload to OpenSearch
   │  ├─ Index: 'chunks'
   │  ├─ Document ID: {source_file}_{chunk_index}
   │  └─ Fields: chunk_text, embedding, chunk_index, source_file
   └─ Returns: List of chunk_ids

4. mark_indexed(chunk_ids)
   ├─ UPDATE chunks SET indexed_at = NOW()
   └─ WHERE chunk_id IN (chunk_ids)
```

**Key Components:**

1. **HuggingFaceEmbedder** (`services/embedding/huggingface_embedder.py`)
   - Uses sentence-transformers library
   - Default model: `intfloat/e5-base-v2`
   - Generates 768-dimensional dense vectors
   - Batch processing for efficiency

2. **OpenSearchStore** (`services/search/opensearch_store.py`)
   - Vector database client
   - Supports three search modes:
     - **Dense Search**: Pure kNN vector similarity
     - **BM25 Search**: Traditional keyword search
     - **Hybrid Search**: Combined vector + BM25
   - Index configuration:
     - `knn_vector` field with HNSW algorithm
     - `cosinesimil` space type
     - `nmslib` engine

**Database Schema Updates:**
```sql
-- chunks table includes:
indexed_at TIMESTAMP  -- NULL = not indexed, NOT NULL = indexed
```

**Batch Processing:**
- Processes 100 chunks per DAG run
- Prevents memory overflow
- Allows incremental indexing

---

## 🎨 Component Deep Dive

### 1. PDF Text Extraction

**Architecture:**
```
HybridPdfExtractor (hybrid_extractor.py)
    │
    ├─► PdfMinerExtractor (pdfminer_extractor.py)
    │   ├─ Library: pdfminer.six
    │   ├─ Extracts: Structured PDF text
    │   ├─ Works on: Text-based PDFs
    │   └─ Detects: Sparse pages (< min_chars_per_page)
    │
    └─► TesseractOCR (tesseract_ocr.py)
        ├─ Library: pytesseract + pdf2image
        ├─ Extracts: Text from images
        ├─ Works on: Scanned PDFs, images
        └─ Returns: Text + confidence score
```

**Strategy:**
1. Try PdfMiner first (fast, works for 90% of papers)
2. Identify pages with < 20 characters (likely scanned/image)
3. Run OCR only on sparse pages (hybrid approach)
4. If PdfMiner returns nothing, run full OCR

**Return Type:**
```python
@dataclass
class ExtractResult:
    text: str                  # Full extracted text
    pages: List[PageText]      # Per-page details
    errors: List[str]          # Error messages
    used_ocr: bool            # Whether OCR was used
```

---

### 2. Text Chunking Strategies

**Current Implementation:** Sliding Window

**Code:** `services/processing/chunking/chunker.py`

```python
class Chunker:
    def __init__(self, chunk_size=300, overlap=50):
        self.chunk_size = 300    # words per chunk
        self.overlap = 50        # overlapping words
```

**Algorithm:**
```
Input: "word1 word2 word3 ... wordN"

Chunk 1: words[0:300]
Chunk 2: words[250:550]    # 50-word overlap with chunk 1
Chunk 3: words[500:800]
...
```

**Why Overlap?**
- Preserves context across chunk boundaries
- Improves retrieval accuracy
- Prevents splitting of related concepts

**Alternative Chunkers** (in codebase but not used):
- `heading_aware.py`: Chunks based on document structure
- `sliding_window.py`: Pure sliding window

---

### 3. Embedding Generation

**Model:** `intfloat/e5-base-v2`

**Characteristics:**
- Type: Dense vector embeddings
- Dimensions: 768
- Library: HuggingFace sentence-transformers
- Training: Contrastive learning on diverse text

**Usage Pattern:**
```python
embedder = HuggingFaceEmbedder("intfloat/e5-base-v2")
embeddings = embedder.embed(["text1", "text2", ...])
# Returns: [[0.1, 0.2, ...], [0.3, 0.4, ...]]
```

**Performance Considerations:**
- Batch processing: More efficient than one-by-one
- GPU acceleration: Not currently configured (CPU only)
- Model loading: Cached after first use

---

### 4. Search & Retrieval

**OpenSearch Index Schema:**
```json
{
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib"
        }
      },
      "chunk_text": {"type": "text"},
      "chunk_index": {"type": "integer"},
      "source_file": {"type": "keyword"}
    }
  }
}
```

**Search Methods:**

1. **Dense kNN Search:**
   ```python
   store.search_dense(query_vector, k=5)
   ```
   - Pure semantic similarity
   - Uses cosine similarity
   - Fast approximate nearest neighbors (HNSW)

2. **Hybrid Search:**
   ```python
   store.search_hybrid(query_vector, query_text, k=5)
   ```
   - Combines BM25 keyword matching + vector similarity
   - More robust than either alone
   - Better handles specific terms + semantic meaning

---

## 🐳 Docker Services

### Service Dependency Graph

```
postgres
    ├─► airflow-init
    │       └─► airflow
    ├─► api
    └─► (app database)

opensearch
    └─► api

minio
    ├─► api
    └─► airflow (for PDF storage)

api
    └─► ui
```

### Service Details

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **postgres** | postgres:15 | 5435→5432 | Two databases: `researchai_app` + `researchai_airflow` |
| **opensearch** | opensearchproject/opensearch:2.11.0 | 9200 | Vector search engine |
| **minio** | minio/minio | 9000 (API), 9001 (Console) | S3-compatible object storage |
| **airflow** | researchai-airflow:2.9.0 | 8080 | DAG orchestration |
| **api** | custom | 8000 | FastAPI backend |
| **ui** | custom | 7860 | Gradio interface |

### Volume Mounts (Airflow Container)

```yaml
volumes:
  - ./data:/opt/airflow/data              # Metadata files
  - ./dags:/opt/airflow/dags              # DAG definitions
  - ./services:/opt/researchai/services   # Service modules
  - ./scripts:/opt/researchai/scripts     # Utility scripts
```

**Why?**
- Changes to DAGs/services reflected immediately
- No rebuild required for code changes
- Facilitates development workflow

---

## 🚀 Development Workflow

### Setting Up the Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SmarthBakshi/Research-AI
   cd Research-AI
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start services:**
   ```bash
   make build-up
   # or
   docker compose up -d --build
   ```

4. **Access interfaces:**
   - Airflow UI: http://localhost:8080
   - MinIO Console: http://localhost:9001
   - API Docs: http://localhost:8000/docs
   - Gradio UI: http://localhost:7860

### Running the Pipeline

**Step 1: Prepare Metadata**
```bash
# Place your arXiv metadata in:
data/arxiv/metadata.json

# Format:
[
  {
    "id": "2401.12345",
    "title": "Paper Title",
    "authors": [...],
    ...
  }
]
```

**Step 2: Trigger Ingestion DAG**
1. Go to Airflow UI (http://localhost:8080)
2. Login: admin/admin
3. Enable DAG: `ingest_arxiv_pdf`
4. Trigger manually
5. Monitor progress in the DAG graph view

**Step 3: Trigger Processing DAG**
1. Enable DAG: `process_pdfs`
2. Trigger manually
3. Watch parallel task execution
4. Check logs if any task fails

**Step 4: Trigger Embedding DAG**
1. Enable DAG: `embed_and_index`
2. Trigger manually
3. May need to run multiple times (100 chunks per run)

### Common Development Tasks

**Run tests:**
```bash
make test
# or
pytest -v tests/
```

**Lint code:**
```bash
make lint
# or
ruff check .
```

**Format code:**
```bash
make format
# or
black .
```

**Rebuild specific service:**
```bash
make rebuild-airflow
make rebuild-api
make rebuild-ui
```

**Check service logs:**
```bash
docker compose logs -f airflow
docker compose logs -f api
```

**Connect to PostgreSQL:**
```bash
docker exec -it researchai-postgres psql -U researchai -d researchai_app
```

**Browse MinIO:**
```bash
# Web UI: http://localhost:9001
# Login: minio / minio123
```

---

## 🧪 Testing Strategy

### Test Organization

```
tests/
├── ingestion/
│   ├── test_arxiv_client.py        # arXiv API client tests
│   └── test_ingest_arxiv_dag.py    # DAG logic tests
│
├── processing/
│   ├── test_pdf_extractor.py       # PDF extraction tests
│   ├── test_ocr_wrapper.py         # OCR functionality tests
│   ├── test_chunkers.py            # Chunking strategy tests
│   ├── test_text_normaliser.py     # Text normalization tests
│   └── test_db_writer.py           # Database writing tests
│
└── unit/
    └── test_arxiv_client.py        # Unit tests
```

### Running Tests

```bash
# All tests
pytest -v tests/

# Specific module
pytest tests/processing/test_chunkers.py

# With coverage
pytest --cov=services tests/
```

---

## 🔧 Configuration

### Environment Variables

**PostgreSQL:**
```bash
POSTGRES_USER=researchai
POSTGRES_PASSWORD=researchai
APP_DB=researchai_app              # Application database
AIRFLOW_DB=researchai_airflow      # Airflow metadata database
```

**OpenSearch:**
```bash
OPENSEARCH_PORT=9200
OPENSEARCH_HOST=opensearch
DISABLE_SECURITY_PLUGIN=true       # For development only
```

**MinIO:**
```bash
MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=minio123
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_BUCKET=researchai
```

**Airflow:**
```bash
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW_ADMIN_USER=admin
AIRFLOW_ADMIN_PWD=admin
AIRFLOW_ADMIN_EMAIL=admin@example.com
```

### Changing Configuration

1. **Chunking parameters:**
   Edit `services/processing/chunking/chunker.py`:
   ```python
   def __init__(self, chunk_size=300, overlap=50):
   ```

2. **Embedding model:**
   Edit `dags/embed_and_index.py`:
   ```python
   embedder = HuggingFaceEmbedder("intfloat/e5-base-v2")
   # Change to your preferred model
   ```

3. **Batch size:**
   Edit `dags/embed_and_index.py`:
   ```sql
   LIMIT 100;  -- Change batch size
   ```

4. **Parallel tasks:**
   Edit `dags/process_pdfs.py`:
   ```python
   max_active_tasks=4  # Increase for more parallelism
   ```

---

## 🎯 Current Status & Roadmap

### ✅ Implemented (M1-M4)

- [x] Docker infrastructure with all services
- [x] MinIO object storage for PDFs
- [x] PostgreSQL for metadata and chunks
- [x] Airflow DAGs for pipeline orchestration
- [x] PDF ingestion from arXiv
- [x] Hybrid text extraction (PDF + OCR)
- [x] Text normalization and chunking
- [x] HuggingFace embedding generation
- [x] OpenSearch indexing with kNN support
- [x] Basic API skeleton
- [x] Basic UI skeleton

### 🚧 In Progress (M5)

- [ ] Implement `/ask` endpoint in FastAPI
- [ ] Integrate retrieval with LLM (Ollama)
- [ ] Prompt engineering for RAG
- [ ] Response generation pipeline
- [ ] Citation tracking

### 📋 Planned (M6)

- [ ] Langfuse integration for observability
- [ ] Latency monitoring (p95 < 1.5s target)
- [ ] User feedback collection
- [ ] Quality metrics (hit@k, token usage)
- [ ] Comprehensive test coverage
- [ ] CI/CD pipeline
- [ ] Production deployment guide

---

## 🔍 Key Design Decisions

### 1. Why Hybrid PDF Extraction?

**Problem:** Scientific PDFs come in two forms:
- Text-based PDFs (LaTeX-generated): Easy to extract
- Scanned PDFs (old papers): Require OCR

**Solution:** HybridPdfExtractor
- Try fast text extraction first
- Detect problematic pages
- Apply OCR selectively
- **Result:** Best of both worlds - speed + accuracy

### 2. Why Content-Addressable Storage?

**Problem:** Same PDF might be ingested multiple times

**Solution:** Hash-based filenames
```python
filename = f"{sha256(pdf_content)}.pdf"
```
- Same content = same filename
- Automatic deduplication
- No database lookup needed

### 3. Why Sliding Window Chunking?

**Problem:** Fixed-size chunks might split related text

**Solution:** Overlapping chunks
- Context preserved across boundaries
- Better retrieval accuracy
- Slight storage overhead (acceptable trade-off)

### 4. Why OpenSearch over Alternatives?

**Comparison:**
| Feature | OpenSearch | Pinecone | Weaviate |
|---------|-----------|----------|----------|
| Open Source | ✅ | ❌ | ✅ |
| Hybrid Search | ✅ | ❌ | ✅ |
| Self-Hosted | ✅ | ❌ | ✅ |
| BM25 + Vector | ✅ | ❌ | ✅ |

**Decision:** OpenSearch for hybrid search + self-hosting

### 5. Why Airflow for Orchestration?

**Alternatives:** Prefect, Dagster, Temporal

**Airflow Advantages:**
- Mature ecosystem
- Strong DAG visualization
- Built-in retry/failure handling
- Dynamic task mapping
- Large community

---

## 🐛 Troubleshooting

### Common Issues

**1. Airflow DAG not appearing:**
```bash
# Check DAG syntax
docker exec -it researchai-airflow airflow dags list

# View DAG errors
docker compose logs airflow | grep ERROR
```

**2. MinIO connection failed:**
```bash
# Check MinIO is running
curl http://localhost:9000/minio/health/ready

# Verify credentials in .env
echo $MINIO_ROOT_USER
echo $MINIO_ROOT_PASSWORD
```

**3. PostgreSQL connection refused:**
```bash
# Check postgres is healthy
docker compose ps postgres

# Test connection
docker exec -it researchai-postgres psql -U researchai -d researchai_app -c "SELECT 1;"
```

**4. OpenSearch not starting (Apple Silicon):**
```yaml
# In docker-compose.yml, uncomment:
opensearch:
  platform: linux/amd64
```

**5. Out of memory during embedding:**
```python
# In embed_and_index.py, reduce batch size:
LIMIT 50;  # Instead of 100
```

### Debug Mode

**Enable Airflow debug logs:**
```yaml
# In docker-compose.yml:
environment:
  AIRFLOW__LOGGING__LOGGING_LEVEL: DEBUG
```

**Check DAG execution logs:**
```bash
# Via UI: Airflow → DAGs → [DAG name] → Graph → [Task] → Logs

# Via CLI:
docker exec -it researchai-airflow airflow tasks test ingest_arxiv_pdf read_metadata 2024-01-01
```

---

## 📚 Additional Resources

### Key Technologies

- **Airflow:** https://airflow.apache.org/docs/
- **OpenSearch:** https://opensearch.org/docs/latest/
- **MinIO:** https://min.io/docs/minio/linux/index.html
- **HuggingFace Embeddings:** https://huggingface.co/docs/transformers/
- **FastAPI:** https://fastapi.tiangolo.com/

### Related Papers

- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)
- "Dense Passage Retrieval for Open-Domain Question Answering" (Karpukhin et al., 2020)
- "Text and Code Embeddings by Contrastive Pre-Training" (Wang et al., 2022)

### Community

- GitHub Issues: https://github.com/SmarthBakshi/Research-AI/issues
- Discussions: https://github.com/SmarthBakshi/Research-AI/discussions

---

## 🤝 Contributing

### Code Style

- **Formatter:** Black (line length 100)
- **Linter:** Ruff
- **Type Hints:** Encouraged but not required

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Run linter: `make lint`
6. Format code: `make format`
7. Submit PR with description

### Commit Message Convention

```
<type>(<scope>): <subject>

Examples:
feat(dags): add metadata validation step
fix(extractor): handle empty PDF pages
docs(readme): update installation steps
test(chunker): add overlap boundary tests
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👥 Credits

**Author:** Smarth Bakshi (bakshismarth.20@gmail.com)

**Contributors:** [See GitHub contributors page]

---

**Last Updated:** 2025-10-28
