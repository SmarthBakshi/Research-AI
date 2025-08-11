# ResearchAI

Production-grade RAG over research papers (infra-first, modular, testable).

## Quickstart
1) Copy `.env.example` → `.env` and fill values.
2) `docker compose up -d`
3) `./scripts/healthcheck.sh`

Services:
- API http://localhost:8000/docs
- Airflow http://localhost:8080
- OpenSearch http://localhost:9200
- MinIO http://localhost:9001
- UI http://localhost:7860
