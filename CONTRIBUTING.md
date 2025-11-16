# Contributing to ResearchAI

Thank you for your interest in contributing to ResearchAI! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Poetry (for dependency management)
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Research-AI.git
cd Research-AI

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d
```

### Install Pre-commit Hooks

```bash
# Install pre-commit
poetry add --group dev pre-commit

# Install hooks
pre-commit install
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-chunking-strategy`
- `fix/opensearch-connection-timeout`
- `docs/update-readme`
- `refactor/improve-embedding-performance`

### Commit Messages

Follow conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add /ask endpoint for RAG queries

Implements the question-answering endpoint that combines
retrieval and LLM generation. Includes hybrid search support.

Closes #123
```

```
fix(processing): handle PDFs with missing metadata

Added error handling for PDFs without title or author fields.

Fixes #456
```

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_api.py

# Run with coverage
poetry run pytest --cov=services --cov-report=html

# Run integration tests
poetry run pytest tests/integration/
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the AAA pattern (Arrange, Act, Assert)

**Example:**

```python
def test_chunker_handles_empty_text():
    """Test that chunker handles empty text gracefully"""
    # Arrange
    chunker = SlidingWindowChunker(chunk_size=300)
    text = ""

    # Act
    chunks = chunker.chunk_text(text)

    # Assert
    assert len(chunks) == 0
```

## Pull Request Process

1. **Update documentation**: Ensure README and docstrings are updated
2. **Run tests**: All tests must pass
3. **Update CHANGELOG**: Add your changes to CHANGELOG.md
4. **Ensure CI passes**: GitHub Actions must pass
5. **Request review**: Tag maintainers for review
6. **Address feedback**: Make requested changes promptly

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Pre-commit hooks pass
```

## Code Style

### Python

We use:
- **Black** for code formatting (100 char line length)
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format code
black services/ dags/ tests/

# Lint code
ruff check services/ dags/ tests/

# Type check
mypy services/ dags/
```

### Docstrings

Use Google-style docstrings:

```python
def process_pdf(pdf_path: str, chunk_size: int = 300) -> List[str]:
    """
    Process a PDF and return text chunks.

    Args:
        pdf_path: Path to the PDF file
        chunk_size: Maximum words per chunk

    Returns:
        List of text chunks

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If chunk_size is invalid

    Example:
        >>> chunks = process_pdf("paper.pdf", chunk_size=500)
        >>> len(chunks)
        42
    """
    pass
```

### Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional

def embed_texts(
    texts: List[str],
    model_name: Optional[str] = None
) -> List[List[float]]:
    pass
```

## Project Structure

```
Research-AI/
├── services/          # Core business logic
│   ├── chunkers/      # Text chunking strategies
│   ├── embedding/     # Embedding generation
│   ├── ingestion/     # Data ingestion
│   ├── processing/    # PDF processing
│   └── search/        # Search and retrieval
├── dags/              # Airflow DAGs
├── tests/             # Test suite
├── docker/            # Service dockerfiles
└── scripts/           # Utility scripts
```

## Areas for Contribution

### High Priority

- [ ] Add more chunking strategies (semantic, hierarchical)
- [ ] Implement observability with Langfuse
- [ ] Add support for more LLM providers (OpenAI, Anthropic)
- [ ] Improve PDF extraction accuracy
- [ ] Add query caching for better performance

### Documentation

- [ ] Add architecture diagrams
- [ ] Create video tutorials
- [ ] Write deployment guides
- [ ] Add API examples

### Testing

- [ ] Increase test coverage
- [ ] Add performance benchmarks
- [ ] Create end-to-end tests

## Questions?

- Open an issue for bugs or feature requests
- Join our discussions for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to ResearchAI!
