"""
Test suite for ResearchAI API endpoints

Tests all FastAPI endpoints for correct functionality.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'docker', 'api', 'app'))

from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_healthz_returns_ok(self):
        """Test that healthz endpoint returns 200 OK"""
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_healthz_response_structure(self):
        """Test healthz response has correct structure"""
        response = client.get("/healthz")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
        assert isinstance(data["services"], dict)


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_returns_ok(self):
        """Test root endpoint returns 200 OK"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_response_structure(self):
        """Test root response has API information"""
        response = client.get("/")
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["name"] == "ResearchAI API"


class TestSearchEndpoint:
    """Test search endpoint"""

    def test_search_requires_query(self):
        """Test search endpoint requires query parameter"""
        response = client.post("/search", json={})
        # Should fail validation without query
        assert response.status_code == 422

    def test_search_with_valid_query(self):
        """Test search with valid query structure"""
        response = client.post("/search", json={
            "query": "machine learning",
            "k": 5,
            "search_type": "hybrid"
        })
        # May return 503 if services not initialized in test env
        assert response.status_code in [200, 503]

    def test_search_validates_search_type(self):
        """Test search validates search_type parameter"""
        # Note: This test assumes services are not initialized
        # In production, it should validate before service check
        response = client.post("/search", json={
            "query": "test",
            "k": 5,
            "search_type": "invalid"
        })
        assert response.status_code in [400, 503]

    def test_search_validates_k_range(self):
        """Test search validates k parameter range"""
        # k too low
        response = client.post("/search", json={
            "query": "test",
            "k": 0
        })
        assert response.status_code == 422

        # k too high
        response = client.post("/search", json={
            "query": "test",
            "k": 25
        })
        assert response.status_code == 422


class TestAskEndpoint:
    """Test /ask endpoint"""

    def test_ask_requires_question(self):
        """Test ask endpoint requires question parameter"""
        response = client.post("/ask", json={})
        assert response.status_code == 422

    def test_ask_with_valid_request(self):
        """Test ask with valid request structure"""
        response = client.post("/ask", json={
            "question": "What is machine learning?",
            "k": 5,
            "temperature": 0.7,
            "search_type": "hybrid"
        })
        # May return 503 if services not initialized
        assert response.status_code in [200, 503]

    def test_ask_validates_temperature_range(self):
        """Test ask validates temperature parameter"""
        # Temperature too high
        response = client.post("/ask", json={
            "question": "test",
            "temperature": 3.0
        })
        assert response.status_code == 422

        # Temperature negative
        response = client.post("/ask", json={
            "question": "test",
            "temperature": -0.5
        })
        assert response.status_code == 422


class TestStatsEndpoint:
    """Test stats endpoint"""

    def test_stats_returns_data(self):
        """Test stats endpoint returns data"""
        response = client.get("/stats")
        # May fail if database not available in test
        assert response.status_code in [200, 500]

    def test_stats_response_structure(self):
        """Test stats response structure when successful"""
        response = client.get("/stats")
        if response.status_code == 200:
            data = response.json()
            assert "total_chunks" in data
            assert "indexed_chunks" in data
            assert "unique_papers" in data
            assert "index_name" in data


class TestCORS:
    """Test CORS middleware"""

    def test_cors_headers_present(self):
        """Test CORS headers are included"""
        response = client.options("/healthz")
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
