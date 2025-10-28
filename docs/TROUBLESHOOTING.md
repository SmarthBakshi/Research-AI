# 🔧 ResearchAI Troubleshooting & FAQ

## 🆘 Common Issues & Solutions

### Installation & Setup Issues

#### Issue: `docker compose up` fails with "Cannot connect to Docker daemon"

**Symptoms:**
```
ERROR: Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solution:**
```bash
# Start Docker daemon
sudo systemctl start docker

# Or on macOS
open -a Docker

# Verify Docker is running
docker --version
docker ps
```

---

#### Issue: Services fail to start with "port already in use"

**Symptoms:**
```
ERROR: for airflow Cannot start service airflow: driver failed programming external connectivity on endpoint researchai-airflow: Bind for 0.0.0.0:8080 failed: port is already allocated
```

**Solution:**
```bash
# Find what's using the port
lsof -i :8080  # Linux/macOS
netstat -ano | findstr :8080  # Windows

# Kill the process or change port in .env
echo "AIRFLOW_PORT=8081" >> .env

# Or stop the conflicting service
sudo systemctl stop apache2  # if port 8080 is used by Apache
```

---

#### Issue: MinIO container fails with "Access Denied"

**Symptoms:**
```
ERROR: Unable to write to directory /data - Access Denied
```

**Solution:**
```bash
# Fix permissions on volume
docker compose down
sudo chown -R 1000:1000 ./volumes/minio  # if using bind mount

# Or use Docker volume (recommended)
# Already configured in docker-compose.yml
docker volume ls
docker volume inspect research-ai_minio
```

---

### Airflow Issues

#### Issue: DAGs not showing up in Airflow UI

**Symptoms:**
- Airflow UI loads but shows no DAGs
- DAG appears as "broken" with import errors

**Solution:**

1. **Check DAG syntax:**
```bash
# Test DAG file
docker exec -it researchai-airflow python -c "
from airflow.models import DagBag
dagbag = DagBag('/opt/airflow/dags')
print('Errors:', dagbag.import_errors)
"
```

2. **Verify file permissions:**
```bash
ls -la dags/
# Should be readable by user 50000 (airflow user)
```

3. **Check DAG processor logs:**
```bash
docker compose logs airflow | grep "DAG Processor"
docker compose logs airflow | grep ERROR
```

4. **Manually refresh DAGs:**
```bash
docker exec -it researchai-airflow airflow dags list
docker compose restart airflow
```

---

#### Issue: Task fails with "Import Error: No module named 'services'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'services'
```

**Solution:**

1. **Verify volume mounts:**
```bash
docker exec -it researchai-airflow ls -la /opt/researchai/services
# Should show your service modules
```

2. **Check PYTHONPATH:**
```bash
docker exec -it researchai-airflow env | grep PYTHONPATH
# Should include /opt/researchai
```

3. **Fix in docker-compose.yml:**
```yaml
airflow:
  environment:
    PYTHONPATH: /opt/researchai
  volumes:
    - ./services:/opt/researchai/services:delegated
```

4. **Restart Airflow:**
```bash
make restart-airflow
```

---

#### Issue: Airflow task stuck in "running" state

**Symptoms:**
- Task shows "running" for hours
- No logs being produced
- Task doesn't respond to manual interventions

**Solution:**

1. **Check if process is actually running:**
```bash
docker exec -it researchai-airflow ps aux | grep airflow
```

2. **Clear the task:**
```bash
docker exec -it researchai-airflow airflow tasks clear \
  --yes \
  ingest_arxiv_pdf \
  read_metadata \
  2024-01-01
```

3. **Restart scheduler:**
```bash
docker compose restart airflow
```

4. **If zombie task:**
```bash
docker exec -it researchai-airflow airflow tasks clear \
  --yes \
  --only-failed \
  ingest_arxiv_pdf
```

---

### Database Issues

#### Issue: PostgreSQL connection refused

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Solution:**

1. **Check if PostgreSQL is running:**
```bash
docker compose ps postgres
# Should show "Up (healthy)"
```

2. **Verify connection details:**
```bash
# From .env
cat .env | grep POSTGRES

# Test connection
docker exec -it researchai-postgres psql -U researchai -d researchai_app -c "SELECT 1;"
```

3. **Check health:**
```bash
docker exec -it researchai-postgres pg_isready -U researchai
```

4. **View logs:**
```bash
docker compose logs postgres | tail -50
```

5. **If database doesn't exist:**
```bash
docker exec -it researchai-postgres psql -U researchai -d postgres
CREATE DATABASE researchai_app;
\q
```

---

#### Issue: "chunks table does not exist"

**Symptoms:**
```
psycopg2.errors.UndefinedTable: relation "chunks" does not exist
```

**Solution:**

The table should be auto-created by the DAG. If not:

```bash
# Connect to database
docker exec -it researchai-postgres psql -U researchai -d researchai_app

# Create table manually
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    source_file VARCHAR NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    indexed_at TIMESTAMP
);

# Verify
\dt
SELECT COUNT(*) FROM chunks;
```

---

### MinIO Issues

#### Issue: "Access Key Id you provided does not exist"

**Symptoms:**
```
botocore.exceptions.ClientError: An error occurred (InvalidAccessKeyId)
```

**Solution:**

1. **Verify credentials in .env:**
```bash
cat .env | grep MINIO
```

2. **Check MinIO console:**
```
http://localhost:9001
Login: minio / minio123
```

3. **Recreate access keys:**
```bash
# In MinIO console
# Administrator → Access Keys → Create Access Key
```

4. **Update environment:**
```bash
# Update .env
AWS_ACCESS_KEY_ID=your_new_key
AWS_SECRET_ACCESS_KEY=your_new_secret

# Restart services
docker compose restart airflow api
```

---

#### Issue: Bucket does not exist

**Symptoms:**
```
botocore.exceptions.ClientError: An error occurred (NoSuchBucket)
```

**Solution:**

1. **Create bucket via console:**
```
http://localhost:9001 → Buckets → Create Bucket → "researchai"
```

2. **Or via code (auto-creation):**
```python
# Already implemented in services/ingestion/arxiv/minio_utils.py
ensure_bucket_exists("researchai", s3_client)
```

---

### OpenSearch Issues

#### Issue: OpenSearch container keeps restarting

**Symptoms:**
```
opensearch container exits immediately
Error: max virtual memory areas vm.max_map_count [65530] is too low
```

**Solution:**

**Linux:**
```bash
# Increase vm.max_map_count
sudo sysctl -w vm.max_map_count=262144

# Make permanent
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
```

**macOS/Windows:**
```bash
# Already handled by Docker Desktop
# If issue persists, increase Docker memory to 4GB+
```

---

#### Issue: "index_not_found_exception"

**Symptoms:**
```
opensearchpy.exceptions.NotFoundError: index_not_found_exception
```

**Solution:**

1. **Create index:**
```bash
# Via Python script
docker exec -it researchai-api python -c "
from services.search.opensearch_store import OpenSearchStore
store = OpenSearchStore()
store.create_index()
"
```

2. **Or via API:**
```bash
curl -X PUT "localhost:9200/chunks" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "index": {
      "knn": true
    }
  },
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 768
      },
      "chunk_text": {"type": "text"}
    }
  }
}'
```

---

### Pipeline Execution Issues

#### Issue: PDF extraction returns empty text

**Symptoms:**
```
⚠️ Primary extraction returned empty. Trying OCR...
❌ Could not extract any text from {key}
```

**Causes & Solutions:**

1. **Scanned/Image-only PDF:**
   - Expected behavior, OCR should kick in
   - Check Tesseract is installed:
   ```bash
   docker exec -it researchai-airflow tesseract --version
   ```

2. **Corrupted PDF:**
   ```bash
   # Download and inspect manually
   docker exec -it researchai-airflow python -c "
   from services.ingestion.arxiv.minio_utils import download_file
   path = download_file('researchai', 'raw/pdfs/{hash}.pdf')
   print(path)
   "
   
   # Try opening in PDF viewer
   ```

3. **Password-protected PDF:**
   - Not currently supported
   - Add to quarantine and skip

---

#### Issue: Chunking creates too many/too few chunks

**Symptoms:**
- 5-page paper generates 500 chunks
- 50-page paper generates 5 chunks

**Solution:**

Adjust chunking parameters:

```python
# In services/processing/chunking/chunker.py
class Chunker:
    def __init__(self, chunk_size=300, overlap=50):
        # Increase chunk_size for fewer chunks
        self.chunk_size = 500  # was 300
        
        # Decrease for more granular chunks
        self.chunk_size = 150
        
        # Adjust overlap (should be 10-20% of chunk_size)
        self.overlap = 100  # for chunk_size=500
```

Then reprocess PDFs:
```bash
# Clear chunks table
docker exec -it researchai-postgres psql -U researchai -d researchai_app -c "TRUNCATE chunks;"

# Re-run process_pdfs DAG
```

---

#### Issue: Embedding generation is too slow

**Symptoms:**
- `embed_chunks` task takes > 10 minutes
- CPU usage at 100%

**Solutions:**

1. **Reduce batch size:**
```python
# In dags/embed_and_index.py
LIMIT 50;  # Instead of 100
```

2. **Use GPU (if available):**
```python
# In services/embedding/huggingface_embedder.py
self.model = SentenceTransformer(
    model_name,
    device='cuda'  # Instead of 'cpu'
)
```

3. **Use smaller model:**
```python
# In dags/embed_and_index.py
embedder = HuggingFaceEmbedder("sentence-transformers/all-MiniLM-L6-v2")
# Faster but 384-dim instead of 768-dim
```

4. **Use quantized model:**
```python
embedder = HuggingFaceEmbedder(
    "sentence-transformers/all-MiniLM-L6-v2",
    quantize=True
)
```

---

## ❓ Frequently Asked Questions

### General Questions

**Q: What is RAG?**

A: Retrieval-Augmented Generation. A technique where:
1. Relevant documents are retrieved from a knowledge base
2. Retrieved context is added to the LLM prompt
3. LLM generates an answer grounded in the retrieved facts
4. Reduces hallucinations and provides citations

---

**Q: How much disk space do I need?**

A: Depends on dataset size:
- **Minimal (10 papers):** ~5 GB
- **Small (100 papers):** ~20 GB
- **Medium (1,000 papers):** ~150 GB
- **Large (10,000 papers):** ~1.5 TB

Breakdown:
- PDFs: ~1-2 MB per paper (MinIO)
- Chunks: ~500 KB per paper (PostgreSQL)
- Vectors: ~300 KB per paper (OpenSearch)

---

**Q: Can I use this for non-arXiv papers?**

A: Yes! Just modify the ingestion:
1. Place PDFs in MinIO manually
2. Run `process_pdfs` DAG
3. System will process any PDF

Or create a custom ingestion DAG for your source.

---

**Q: Why do I need both PostgreSQL and OpenSearch?**

A: Different purposes:
- **PostgreSQL:** Structured data (metadata, chunk text, relations)
- **OpenSearch:** Fast vector search + BM25 keyword search

You could use just one, but hybrid is more powerful.

---

**Q: Can I run this without Docker?**

A: Yes, but not recommended. You'd need to:
1. Install Python 3.10+
2. Install PostgreSQL, OpenSearch, MinIO locally
3. Install Airflow
4. Configure all connections manually
5. Manage dependencies

Docker makes it much easier.

---

### Performance Questions

**Q: How fast is the ingestion pipeline?**

A: Benchmarks (local development):
- **Ingestion:** ~2 PDFs/minute
- **Processing:** ~0.5 PDFs/minute (OCR is slow)
- **Embedding:** ~33 chunks/minute

Bottleneck: PDF extraction (especially OCR)

---

**Q: How can I speed up processing?**

A:
1. **Increase parallelism:**
   ```python
   # In dags/process_pdfs.py
   max_active_tasks=8  # Instead of 4
   ```

2. **Use GPU for OCR:**
   - Not currently implemented
   - Would require custom OCR engine

3. **Skip OCR for text-based PDFs:**
   - Already implemented (hybrid approach)

4. **Distribute to multiple workers:**
   - Use CeleryExecutor instead of LocalExecutor
   - Add more Airflow workers

---

**Q: What's the query latency?**

A: Current target: p95 < 1.5 seconds

Breakdown:
- Embedding query: ~50ms
- OpenSearch retrieval: ~100ms
- LLM generation: ~1-2s (depends on model)
- Total: ~1.2-2.2s

To improve:
- Use faster embedding model
- Cache frequent queries
- Use smaller LLM or GPU acceleration

---

### Development Questions

**Q: How do I add a new embedding model?**

A:
```python
# In services/embedding/custom_embedder.py
from .embedder import Embedder

class CustomEmbedder(Embedder):
    def __init__(self, model_name):
        # Your implementation
        pass
    
    def embed_text(self, text):
        # Your implementation
        pass

# In dags/embed_and_index.py
from services.embedding.custom_embedder import CustomEmbedder
embedder = CustomEmbedder("your-model-name")
```

---

**Q: How do I add a new chunking strategy?**

A:
```python
# In services/chunkers/semantic_chunker.py
class SemanticChunker:
    def chunk(self, text, source_file):
        # Your implementation
        # Split based on semantic boundaries
        pass

# In dags/process_pdfs.py
from services.chunkers.semantic_chunker import SemanticChunker
chunker = SemanticChunker()
```

---

**Q: How do I add custom metadata fields?**

A:
1. **Modify database schema:**
```sql
ALTER TABLE chunks ADD COLUMN author TEXT;
ALTER TABLE chunks ADD COLUMN publish_date DATE;
```

2. **Update db_writer.py:**
```python
class Chunk(Base):
    # ... existing fields ...
    author = Column(String)
    publish_date = Column(Date)
```

3. **Update processing pipeline:**
```python
chunks.append({
    "source_file": source_file,
    "chunk_text": chunk_text,
    "author": metadata.get("author"),
    "publish_date": metadata.get("date")
})
```

---

### Deployment Questions

**Q: Is this production-ready?**

A: Not yet. Current state:
- ✅ Core pipeline works
- ✅ Docker containerized
- ✅ Modular architecture
- ⚠️ No authentication
- ⚠️ No HTTPS
- ⚠️ Default credentials
- ⚠️ No monitoring
- ⚠️ Not optimized for scale

For production:
1. Enable security features
2. Add authentication/authorization
3. Set up monitoring (Langfuse)
4. Use managed services (RDS, OpenSearch Service)
5. Implement CI/CD
6. Add comprehensive tests

---

**Q: How do I deploy to AWS/GCP/Azure?**

A: Several options:

**Option 1: Docker Compose on VM**
```bash
# Provision VM (t3.xlarge or larger)
# Install Docker
# Clone repo
# Configure .env with production settings
docker compose -f docker-compose.prod.yml up -d
```

**Option 2: Kubernetes**
```bash
# Convert docker-compose to K8s manifests
kompose convert

# Or use Helm charts (future)
helm install researchai ./charts/researchai
```

**Option 3: Managed Services**
- Airflow → AWS MWAA / Cloud Composer
- PostgreSQL → RDS / Cloud SQL
- OpenSearch → Amazon OpenSearch / Elastic Cloud
- MinIO → S3 / Cloud Storage
- API → ECS / Cloud Run

---

**Q: How much does it cost to run?**

A: **Development (local):** $0

**Production (AWS estimate):**
- EC2 t3.xlarge: ~$150/month
- RDS PostgreSQL: ~$50/month
- OpenSearch domain: ~$200/month
- S3 storage (1TB): ~$25/month
- Data transfer: ~$50/month
- **Total: ~$475/month** (for moderate usage)

Can reduce with:
- Reserved instances
- Spot instances for batch jobs
- S3 Intelligent-Tiering
- OpenSearch reserved instances

---

## 🐞 Debug Mode

### Enable Verbose Logging

**Airflow:**
```yaml
# In docker-compose.yml
environment:
  AIRFLOW__LOGGING__LOGGING_LEVEL: DEBUG
```

**API:**
```python
# In docker/api/app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**OpenSearch:**
```bash
# Check cluster health
curl -X GET "localhost:9200/_cluster/health?pretty"

# Check node stats
curl -X GET "localhost:9200/_nodes/stats?pretty"

# Enable slow query log
curl -X PUT "localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "transient": {
    "logger.index.search.slowlog": "DEBUG"
  }
}'
```

---

### Useful Debug Commands

**Check container resource usage:**
```bash
docker stats
```

**Inspect specific container:**
```bash
docker inspect researchai-airflow
docker exec -it researchai-airflow bash
```

**View container logs in real-time:**
```bash
docker compose logs -f --tail=100 airflow
```

**Test individual components:**
```bash
# Test PDF extraction
docker exec -it researchai-airflow python -c "
from services.processing.extractors.hybrid_extractor import HybridPdfExtractor
ext = HybridPdfExtractor()
result = ext.extract('/path/to/test.pdf')
print(result.text[:500])
"

# Test embedding
docker exec -it researchai-airflow python -c "
from services.embedding.huggingface_embedder import HuggingFaceEmbedder
emb = HuggingFaceEmbedder('intfloat/e5-base-v2')
vec = emb.embed(['test text'])
print(len(vec[0]))  # Should be 768
"
```

---

## 📞 Getting More Help

### Resources

- **Documentation:** `/docs` directory
- **GitHub Issues:** https://github.com/SmarthBakshi/Research-AI/issues
- **Discussions:** https://github.com/SmarthBakshi/Research-AI/discussions

### Reporting Bugs

When reporting an issue, include:

1. **System info:**
   ```bash
   uname -a
   docker --version
   docker compose version
   ```

2. **Error logs:**
   ```bash
   docker compose logs airflow > logs.txt
   ```

3. **Configuration:**
   ```bash
   cat .env  # Redact passwords!
   ```

4. **Steps to reproduce**
5. **Expected vs actual behavior**

### Contributing

See main README.md for contribution guidelines.

---

## 🔄 Version History

### v0.1.0 (Current)
- ✅ Core pipeline implementation
- ✅ Docker containerization
- ✅ Airflow DAGs
- ✅ Hybrid PDF extraction
- ✅ OpenSearch integration

### v0.2.0 (Planned)
- [ ] /ask API endpoint
- [ ] LLM integration
- [ ] Enhanced UI
- [ ] Langfuse observability

### v1.0.0 (Future)
- [ ] Production-ready security
- [ ] Comprehensive tests
- [ ] CI/CD pipeline
- [ ] Deployment guides

---

**Last Updated:** 2025-10-28

**Need help?** Open an issue or start a discussion on GitHub!
