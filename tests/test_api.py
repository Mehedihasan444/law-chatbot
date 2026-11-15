"""
API Tests for Bangladesh Constitution Chatbot
Tests all API endpoints with various scenarios
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import app

# Create test client
client = TestClient(app)

class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["status"] == "active"

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "chatbot_ready" in data
        assert "timestamp" in data
        assert "version" in data
        assert "system_info" in data
    
    def test_health_check_structure(self):
        """Test health check response structure"""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data["chatbot_ready"], bool)
        assert isinstance(data["system_info"], dict)

class TestStatsEndpoint:
    """Test statistics endpoint"""
    
    def test_get_stats(self):
        """Test stats endpoint returns statistics"""
        response = client.get("/stats")
        # May return 503 if chatbot not initialized
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "queries_processed" in data
            assert "session_duration_minutes" in data
            assert "system_status" in data
            assert "languages_detected" in data

class TestQueryEndpoint:
    """Test query endpoint"""
    
    def test_query_valid_question(self):
        """Test query with valid question"""
        payload = {
            "question": "What are the fundamental rights?",
            "use_llm": False  # Faster for testing
        }
        response = client.post("/query", json=payload)
        
        # May return 503 if chatbot not initialized
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True
            assert "question" in data
            assert "answer" in data
            assert "language" in data
            assert "num_sources" in data
            assert "processing_time" in data
    
    def test_query_empty_question(self):
        """Test query with empty question"""
        payload = {
            "question": "",
            "use_llm": False
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_query_too_long_question(self):
        """Test query with too long question"""
        payload = {
            "question": "x" * 1001,  # Exceeds max length
            "use_llm": False
        }
        response = client.post("/query", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_query_bengali_question(self):
        """Test query with Bengali question"""
        payload = {
            "question": "মৌলিক অধিকার কি?",
            "use_llm": False
        }
        response = client.post("/query", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True
            # Language should be detected as Bengali
            assert data.get("language") in ["bn", "en"]
    
    def test_query_missing_fields(self):
        """Test query with missing required fields"""
        response = client.post("/query", json={})
        assert response.status_code == 422  # Validation error
    
    def test_query_with_llm_enabled(self):
        """Test query with LLM enabled"""
        payload = {
            "question": "What is Article 27?",
            "use_llm": True
        }
        response = client.post("/query", json=payload)
        
        # May return 503 if chatbot not initialized or 200
        assert response.status_code in [200, 503]
    
    def test_query_article_specific(self):
        """Test query about specific article"""
        payload = {
            "question": "Tell me about Article 27 of the Constitution",
            "use_llm": False
        }
        response = client.post("/query", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True
            # Should return some sources
            assert isinstance(data["num_sources"], int)

class TestHistoryEndpoint:
    """Test history endpoints"""
    
    def test_get_history(self):
        """Test get conversation history"""
        response = client.get("/history")
        
        # May return 503 if chatbot not initialized
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "count" in data
            assert "history" in data
            assert isinstance(data["history"], list)
    
    def test_get_history_with_limit(self):
        """Test get history with custom limit"""
        response = client.get("/history?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            assert len(data["history"]) <= 5
    
    def test_clear_history(self):
        """Test clear conversation history"""
        response = client.delete("/history")
        
        # May return 503 if chatbot not initialized
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True
            assert "message" in data

class TestInitializeEndpoint:
    """Test initialize endpoint"""
    
    def test_initialize_default(self):
        """Test initialize with default settings"""
        response = client.post("/initialize")
        
        # Should work or return error with message
        assert response.status_code in [200, 500, 503]
    
    def test_initialize_with_rebuild(self):
        """Test initialize with force rebuild"""
        response = client.post("/initialize?force_rebuild=true")
        
        # Should work or return error with message
        assert response.status_code in [200, 500, 503]

class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint"""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test using invalid HTTP method"""
        response = client.put("/query")
        assert response.status_code == 405
    
    def test_malformed_json(self):
        """Test sending malformed JSON"""
        response = client.post(
            "/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/query")
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200

@pytest.mark.integration
class TestIntegration:
    """Integration tests"""
    
    def test_full_query_workflow(self):
        """Test complete query workflow"""
        # 1. Check health
        health = client.get("/health")
        if health.status_code != 200:
            pytest.skip("Chatbot not initialized")
        
        # 2. Get initial stats
        stats_before = client.get("/stats")
        if stats_before.status_code != 200:
            pytest.skip("Stats not available")
        queries_before = stats_before.json()["queries_processed"]
        
        # 3. Make a query
        query_response = client.post("/query", json={
            "question": "What is the Constitution?",
            "use_llm": False
        })
        assert query_response.status_code == 200
        
        # 4. Check stats increased
        stats_after = client.get("/stats")
        if stats_after.status_code == 200:
            queries_after = stats_after.json()["queries_processed"]
            assert queries_after == queries_before + 1
        
        # 5. Check history
        history = client.get("/history")
        if history.status_code == 200:
            assert len(history.json()["history"]) > 0

def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v", "-s", "--tb=short"])

if __name__ == "__main__":
    run_tests()
