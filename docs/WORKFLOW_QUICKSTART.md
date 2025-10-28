# ⚡ ResearchAI Workflow Quick Start

## 🎯 What Does This System Do?

ResearchAI is a **RAG (Retrieval-Augmented Generation) pipeline** that:

1. 📥 **Ingests** scientific papers from arXiv
2. 📄 **Extracts** text from PDF files
3. ✂️ **Chunks** text into searchable pieces
4. 🧠 **Embeds** chunks into vector representations
5. 🔍 **Indexes** for fast semantic search
6. 💬 **Answers** questions using retrieved context + LLM

---

## 🔄 The Three-Stage Pipeline

### Stage 1: Ingest PDFs 📥

**What happens:**
```
arXiv metadata → Download PDFs → Store in MinIO
```

**How to run:**
1. Add paper metadata to `data/arxiv/metadata.json`
2. Go to Airflow UI: http://localhost:8080
3. Enable and trigger: `ingest_arxiv_pdf`

**What it does:**
- Reads your metadata file
- Downloads each PDF from arXiv
- Uploads to MinIO with hash-based naming
- Skips duplicates automatically

**Where data goes:**
- MinIO bucket: `researchai/raw/pdfs/{hash}.pdf`

---

### Stage 2: Process PDFs 📄

**What happens:**
```
PDFs → Extract text → Clean → Chunk → Store in PostgreSQL
```

**How to run:**
1. After Stage 1 completes
2. Enable and trigger: `process_pdfs`

**What it does:**
- Downloads each PDF from MinIO
- Extracts text using smart hybrid approach:
  - First tries fast PDF text extraction
  - Falls back to OCR for scanned pages
- Normalizes text (removes LaTeX, fixes spacing)
- Chunks into 300-word pieces with 50-word overlap
- Stores chunks in PostgreSQL

**Where data goes:**
- PostgreSQL table: `chunks`
- Columns: `source_file`, `chunk_index`, `chunk_text`

**Runs in parallel:** Processes 4 PDFs at once

---

### Stage 3: Embed & Index 🧠

**What happens:**
```
Chunks → Generate embeddings → Index in OpenSearch
```

**How to run:**
1. After Stage 2 completes
2. Enable and trigger: `embed_and_index`

**What it does:**
- Loads unindexed chunks from PostgreSQL (100 at a time)
- Generates 768-dimensional embeddings using `intfloat/e5-base-v2`
- Uploads to OpenSearch with vector support
- Marks chunks as indexed

**Where data goes:**
- OpenSearch index: `chunks`
- Fields: `chunk_text`, `embedding`, `chunk_index`, `source_file`

**Note:** Run multiple times if you have > 100 chunks

---

## 🚀 Complete Workflow Example

### Prerequisites
```bash
# 1. Start all services
make build-up

# 2. Wait for health checks (1-2 minutes)
docker compose ps
```

### Step-by-Step Execution

**1️⃣ Prepare your data:**
```bash
# Edit data/arxiv/metadata.json
cat > data/arxiv/metadata.json << 'EOF'
[
  {
    "id": "2301.00001",
    "title": "Example Paper",
    "authors": ["John Doe"]
  },
  {
    "id": "2301.00002",
    "title": "Another Paper",
    "authors": ["Jane Smith"]
  }
]
EOF
```

**2️⃣ Run Stage 1 - Ingest:**
```
Browser → http://localhost:8080
Login: admin / admin
DAGs → ingest_arxiv_pdf → Toggle ON → Trigger DAG (▶️)
Wait for completion (~2-5 minutes for 2 papers)
```

**Expected output:**
```
✅ Task: read_metadata (Success)
✅ Task: ingest (Success)
```

**Verify:**
```bash
# Check MinIO console
# http://localhost:9001 (minio / minio123)
# Navigate to: researchai → raw/pdfs/
# Should see: {hash1}.pdf, {hash2}.pdf
```

**3️⃣ Run Stage 2 - Process:**
```
DAGs → process_pdfs → Toggle ON → Trigger DAG (▶️)
Wait for completion (~5-10 minutes for 2 papers)
```

**Expected output:**
```
✅ Task: list_pdf_keys (Success)
✅ Task: process_each_pdf[0] (Success)
✅ Task: process_each_pdf[1] (Success)
```

**Verify:**
```bash
# Check database
docker exec -it researchai-postgres psql -U researchai -d researchai_app

# Run query:
SELECT COUNT(*) FROM chunks;
# Should show: number of chunks created

SELECT source_file, chunk_index, LEFT(chunk_text, 100)
FROM chunks
LIMIT 5;
# Should show: sample chunks
```

**4️⃣ Run Stage 3 - Embed:**
```
DAGs → embed_and_index → Toggle ON → Trigger DAG (▶️)
Wait for completion (~2-5 minutes for first 100 chunks)

If you have > 100 chunks:
  → Trigger again
  → Repeat until all chunks indexed
```

**Expected output:**
```
✅ Task: load_unindexed_chunks (Success)
✅ Task: embed_chunks (Success)
✅ Task: upsert_to_opensearch (Success)
✅ Task: mark_indexed (Success)
```

**Verify:**
```bash
# Check OpenSearch
curl -X GET "localhost:9200/chunks/_count"
# Should return: {"count": N, ...}

# Search test
curl -X POST "localhost:9200/chunks/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"match": {"chunk_text": "machine learning"}}}'
```

---

## 🎬 Monitoring & Logs

### Airflow UI (http://localhost:8080)

**DAG View:**
- See all DAGs and their status
- Green = success, Red = failed, Yellow = running

**Task Logs:**
1. Click on DAG name
2. Click "Graph" view
3. Click on a task box
4. Click "Logs" button
5. Read detailed execution logs

### Service Logs

```bash
# Real-time logs
docker compose logs -f airflow
docker compose logs -f api
docker compose logs -f postgres

# All logs
make logs

# Service status
docker compose ps
```

---

## 🔍 Understanding the Data

### Data Flow Diagram

```
┌─────────────┐
│ metadata.   │
│ json        │
└──────┬──────┘
       │ Stage 1: Ingest
       ▼
┌─────────────┐
│ MinIO       │
│ raw/pdfs/   │
│ {hash}.pdf  │
└──────┬──────┘
       │ Stage 2: Process
       ▼
┌─────────────┐
│ PostgreSQL  │
│ chunks      │
│ table       │
└──────┬──────┘
       │ Stage 3: Embed
       ▼
┌─────────────┐
│ OpenSearch  │
│ chunks      │
│ index       │
└─────────────┘
```

### Data Transformations

**Input (metadata.json):**
```json
{
  "id": "2301.00001",
  "title": "Deep Learning for NLP"
}
```

**After Stage 1 (MinIO):**
```
File: raw/pdfs/a1b2c3d4e5f6...pdf
Size: 2.3 MB
Content: Binary PDF data
```

**After Stage 2 (PostgreSQL):**
```
source_file: a1b2c3d4e5f6...pdf
chunk_index: 0
chunk_text: "Abstract: This paper presents a novel approach..."
```

**After Stage 3 (OpenSearch):**
```json
{
  "chunk_text": "Abstract: This paper presents...",
  "embedding": [0.023, -0.145, 0.678, ...], // 768 dimensions
  "chunk_index": 0,
  "source_file": "a1b2c3d4e5f6...pdf"
}
```

---

## 🛠️ Common Tasks

### Add More Papers

**Option 1: Append to metadata.json**
```bash
# Add new entries to data/arxiv/metadata.json
# Re-run Stage 1
# System automatically skips duplicates
```

**Option 2: Use scripts**
```bash
# Future: automated arXiv search and ingestion
python scripts/researchai/ingest_metadata.py --query "machine learning"
```

### Reprocess Failed PDFs

```bash
# Check quarantine log
cat /opt/airflow/logs/quarantine_keys.txt

# Remove from quarantine (if fixed)
# Re-run Stage 2
```

### Search Your Index

```bash
# Basic keyword search
curl -X POST "localhost:9200/chunks/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"match": {"chunk_text": "your search term"}}}'

# Vector search (requires embedding your query first)
# Use the API endpoint (coming in M5)
```

### Clear All Data

```bash
# Stop everything
make down

# Clear all volumes
docker compose down -v

# Restart
make build-up
```

---

## ⚠️ Troubleshooting

### DAG not appearing?

```bash
# Check Python syntax
docker exec -it researchai-airflow python -m py_compile /opt/airflow/dags/your_dag.py

# Refresh DAGs
docker compose restart airflow
```

### Task stuck in "running"?

```bash
# Check logs
docker compose logs airflow | tail -100

# Kill stuck task
docker exec -it researchai-airflow airflow tasks clear [dag_id] [task_id]
```

### Out of disk space?

```bash
# Check Docker disk usage
docker system df

# Clean up
make clean  # Removes unused images/containers
```

### OpenSearch out of memory?

```bash
# In docker-compose.yml, increase memory:
OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g  # Instead of 1g
```

---

## 📊 What to Expect

### Performance Benchmarks (Local Development)

| Stage | Papers | Time | Rate |
|-------|--------|------|------|
| Stage 1: Ingest | 10 | ~5 min | 2 PDF/min |
| Stage 2: Process | 10 | ~20 min | 0.5 PDF/min |
| Stage 3: Embed | 100 chunks | ~3 min | 33 chunks/min |

**Bottlenecks:**
- Stage 2: OCR is slow (CPU-bound)
- Stage 3: Embedding generation (can use GPU)

### Resource Usage

| Service | CPU | Memory | Disk |
|---------|-----|--------|------|
| Airflow | ~10% | ~500 MB | 1 GB |
| PostgreSQL | ~5% | ~200 MB | 500 MB |
| OpenSearch | ~20% | ~1.5 GB | 2 GB |
| MinIO | ~5% | ~100 MB | Varies |

**Total:** ~4 GB RAM minimum, 8 GB recommended

---

## 🎓 Learning Resources

### Understanding the Pipeline

1. **Watch the DAGs run:** Airflow UI Graph view is very visual
2. **Read the logs:** Each task shows what it's doing
3. **Inspect the data:** Connect to databases and see transformations
4. **Experiment:** Try small datasets first (2-3 papers)

### Key Concepts

**RAG (Retrieval-Augmented Generation):**
- Retrieve relevant documents
- Augment LLM prompt with context
- Generate grounded answer

**Vector Embeddings:**
- Convert text to numbers (vectors)
- Similar text → similar vectors
- Enable semantic search

**Chunking:**
- Split long documents into pieces
- Enable fine-grained retrieval
- Balance between context and precision

---

## 🚦 Next Steps

After completing the pipeline:

1. **✅ Test search:** Use OpenSearch API
2. **✅ Connect API:** Implement `/ask` endpoint (M5)
3. **✅ Add LLM:** Integrate Ollama for generation
4. **✅ Build UI:** Enhance Gradio interface
5. **✅ Monitor:** Add observability with Langfuse

---

## 📞 Getting Help

- **Documentation:** See `docs/CODEBASE_GUIDE.md` for deep dive
- **Issues:** https://github.com/SmarthBakshi/Research-AI/issues
- **Logs:** Always check `docker compose logs -f [service]`

---

**Remember:** Start small (2-3 papers), verify each stage, then scale up!

**Last Updated:** 2025-10-28
