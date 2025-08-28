import pytest
from unittest.mock import patch
from services.ingestion.arxiv.client import ArxivClient

@pytest.fixture
def arxiv_client():
    return ArxivClient()

def test_fetch_returns_expected_metadata(arxiv_client):
    # Minimal arXiv-like entry; adapt to your normalizer if fields differ
    sample_entries = [
        {
            "id": "http://arxiv.org/abs/1234.5678",
            "title": "Sample Paper",
            "summary": "This is a summary.",
            "authors": [{"name": "Alice"}],
            "published": "2021-01-01T00:00:00Z",
            "updated": "2021-01-01T00:00:00Z",
            "links": [
                {"href": "http://arxiv.org/pdf/1234.5678.pdf", "type": "application/pdf"}
            ],
        }
    ]

    # Patch the symbol where it's used inside your client module
    with patch("services.ingestion.arxiv.client.arxiv.query") as mock_query:
        mock_query.return_value = sample_entries

        result = arxiv_client.fetch("quantum")

    assert isinstance(result, list)
    assert result and result[0]["title"] == "Sample Paper"
    assert result[0]["authors"] == ["Alice"]  # assuming your client flattens author names
    assert "pdf_url" in result[0] and result[0]["pdf_url"].endswith(".pdf")


def test_fetch_handles_empty_results(arxiv_client):
    with patch("services.ingestion.arxiv.client.arxiv.query") as mock_query:
        mock_query.return_value = []
        result = arxiv_client.fetch("nothing-should-match")
    assert result == []


def test_fetch_retries_then_succeeds(arxiv_client):
    # Optional: only if your client implements backoff/retry
    # Simulate one transient failure (raise) then success
    side_effects = [RuntimeError("429 rate limit"), [{"id": "http://arxiv.org/abs/1", "title": "ok", "summary": "", "authors":[{"name":"A"}], "published":"2021-01-01T00:00:00Z", "updated":"2021-01-01T00:00:00Z", "links":[{"href":"http://arxiv.org/pdf/1.pdf","type":"application/pdf"}]}]]
    with patch("services.ingestion.arxiv.client.arxiv.query", side_effect=side_effects):
        out = arxiv_client.fetch("quantum")
    assert len(out) == 1
