# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-15

### Added
- Complete RAG system for scientific papers from arXiv
- Automated PDF ingestion pipeline with Airflow
- Intelligent PDF processing with OCR fallback
- Hybrid search (BM25 + vector) using OpenSearch
- FastAPI backend with comprehensive REST API
- Interactive Gradio web UI with question answering
- Ollama LLM integration for answer generation
- Docker Compose orchestration for 8 services
- Comprehensive test suite (unit + integration)
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks for code quality
- Complete documentation (README, CONTRIBUTING)
- MIT License

### Infrastructure
- PostgreSQL 15 for structured data
- OpenSearch 2.11.0 for vector search
- MinIO for S3-compatible object storage
- Apache Airflow 3.0.4 for orchestration
- Ollama for local LLM inference

### Features
- `/ask` endpoint for RAG-based Q&A
- `/search` endpoint for semantic search
- `/stats` endpoint for system statistics
- Health checks for all services
- Citation-backed answers
- Configurable search parameters (k, temperature)
- Hybrid and dense search modes
- Real-time UI with statistics dashboard

### Performance
- p95 query latency < 1.5s
- Processing ~100 PDFs/min
- 768-dimensional embeddings (e5-base-v2)
- Idempotent DAG execution

### Developer Experience
- One-command deployment
- Hot reload for local development
- Comprehensive API documentation
- Type hints throughout codebase
- Automated code formatting (Black)
- Linting (Ruff) and type checking (MyPy)

## [0.5.0] - 2025-01-10

### Added
- Basic Airflow DAGs for ingestion and processing
- PDF extraction with PDFMiner
- Chunking logic with sliding window
- OpenSearch index creation
- Embedding generation with HuggingFace

### Changed
- Migrated from custom scripts to Airflow DAGs
- Improved error handling in PDF processing

## [0.3.0] - 2025-01-05

### Added
- Docker Compose setup for infrastructure
- PostgreSQL database schema
- MinIO object storage integration
- Basic API stub with FastAPI

### Changed
- Restructured project for better modularity
- Updated dependencies to latest versions

## [0.1.0] - 2025-01-01

### Added
- Initial project structure
- Basic PDF processing
- arXiv metadata fetching
- Simple chunking algorithm

---

## [Unreleased]

### Planned
- Observability with Langfuse
- Multi-LLM provider support
- Query caching for performance
- Advanced chunking strategies
- User authentication
- Document upload via UI
- Kubernetes deployment guides
