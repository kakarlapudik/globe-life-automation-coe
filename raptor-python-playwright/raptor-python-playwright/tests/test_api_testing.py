"""Unit tests for API Testing Module"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from raptor.api import ApiClient, ApiSession, AuthManager, ApiAssertions, JsonSchemaValidator
from raptor.api.client import ApiResponse, ApiRequest
from raptor.api.auth import BasicAuth, BearerAuth, ApiKeyAuth


class TestApiClient:
    """Tests for ApiClient."""
    
    def test_client_initialization(self):
        """Test API client initialization."""
        client = ApiClient(
            base_url="https://api.example.com",
            timeout=60.0,
            verify_ssl=False
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.timeout == 60.0
        assert client.verify_ssl is False
    
    @patch('raptor.api.client.requests.Session')
    def test_get_request(self, mock_session):
        """Test GET request."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = b'{"key": "value"}'
        mock_response.text = '{"key": "value"}'
        mock_response.json.return_value = {"key": "value"}
        mock_response.url = "https://api.example.com/test"
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Test
        client = ApiClient(base_url="https://api.example.com")
        response = client.get("/test")
        
        assert response.status_code == 200
        assert response.json_data == {"key": "value"}
    
    def test_build_url(self):
        """Test URL building."""
        client = ApiClient(base_url="https://api.example.com")
        
        # Test with relative path
        url = client._build_url("/users")
        assert url == "https://api.example.com/users"
        
        # Test with absolute URL
        url = client._build_url("https://other.com/api")
        assert url == "https://other.com/api"


class TestAuthentication:
    """Tests for authentication methods."""
    
    def test_basic_auth(self):
        """Test Basic authentication."""
        auth = BasicAuth("user", "pass")
        headers = auth.get_auth_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")
    
    def test_bearer_auth(self):
        """Test Bearer token authentication."""
        auth = BearerAuth("test-token")
        headers = auth.get_auth_headers()
        
        assert headers["Authorization"] == "Bearer test-token"
    
    def test_api_key_auth(self):
        """Test API key authentication."""
        auth = ApiKeyAuth("my-api-key", "X-API-Key")
        headers = auth.get_auth_headers()
        
        assert headers["X-API-Key"] == "my-api-key"
    
    def test_auth_manager(self):
        """Test AuthManager."""
        auth_manager = AuthManager()
        
        # Test setting different auth methods
        auth_manager.set_basic_auth("user", "pass")
        assert auth_manager.is_authenticated()
        
        auth_manager.set_bearer_auth("token")
        headers = auth_manager.get_auth_headers()
        assert "Authorization" in headers


class TestApiAssertions:
    """Tests for API assertions."""
    
    def test_status_code_assertion(self):
        """Test status code assertion."""
        response = ApiResponse(
            status_code=200,
            headers={},
            content=b"",
            text=""
        )
        
        assertions = ApiAssertions()
        
        # Should pass
        assertions.that(response).has_status_code(200)
        
        # Should fail
        with pytest.raises(Exception):
            assertions.that(response).has_status_code(404)
    
    def test_json_path_assertion(self):
        """Test JSON path assertion."""
        response = ApiResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            content=b'{"user": {"name": "John", "age": 30}}',
            text='{"user": {"name": "John", "age": 30}}',
            json_data={"user": {"name": "John", "age": 30}}
        )
        
        assertions = ApiAssertions()
        
        # Should pass
        assertions.that(response).has_json_path("user.name", "John")
        assertions.that(response).has_json_path("user.age", 30)
        
        # Should fail
        with pytest.raises(Exception):
            assertions.that(response).has_json_path("user.name", "Jane")
    
    def test_fluent_assertions(self):
        """Test fluent assertion chaining."""
        response = ApiResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            content=b'{"status": "success"}',
            text='{"status": "success"}',
            json_data={"status": "success"},
            elapsed_time=0.5
        )
        
        assertions = ApiAssertions()
        
        # Chain multiple assertions
        assertions.that(response) \
            .is_ok() \
            .has_valid_json() \
            .has_json_path("status", "success") \
            .response_time_less_than(1.0)


class TestJsonSchemaValidator:
    """Tests for JSON schema validation."""
    
    def test_add_schema(self):
        """Test adding JSON schema."""
        validator = JsonSchemaValidator()
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        validator.add_schema("user", schema)
        assert "user" in validator.list_schemas()
    
    def test_validate_response(self):
        """Test response validation against schema."""
        validator = JsonSchemaValidator()
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        
        validator.add_schema("person", schema)
        
        # Valid response
        valid_response = ApiResponse(
            status_code=200,
            headers={},
            content=b'{"name": "John", "age": 30}',
            text='{"name": "John", "age": 30}',
            json_data={"name": "John", "age": 30}
        )
        
        result = validator.validate_response(valid_response, "person")
        assert result.is_valid
        
        # Invalid response
        invalid_response = ApiResponse(
            status_code=200,
            headers={},
            content=b'{"name": "John"}',
            text='{"name": "John"}',
            json_data={"name": "John"}
        )
        
        result = validator.validate_response(invalid_response, "person")
        assert not result.is_valid


class TestApiSession:
    """Tests for API session management."""
    
    def test_session_variables(self):
        """Test session variable management."""
        session = ApiSession()
        
        # Set and get variables
        session.set_variable("user_id", 123)
        assert session.get_variable("user_id") == 123
        
        # Get with default
        assert session.get_variable("missing", "default") == "default"
        
        # Clear variables
        session.clear_variables()
        assert session.get_variable("user_id") is None
    
    @patch('raptor.api.client.requests.Session')
    def test_extract_from_response(self, mock_session):
        """Test extracting values from response."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b'{"user": {"id": 123, "name": "John"}}'
        mock_response.text = '{"user": {"id": 123, "name": "John"}}'
        mock_response.json.return_value = {"user": {"id": 123, "name": "John"}}
        mock_response.url = "https://api.example.com/user"
        
        mock_session_instance = Mock()
        mock_session_instance.request.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Test
        session = ApiSession(base_url="https://api.example.com")
        session.get("/user")
        session.extract_from_response("user.id", "user_id")
        
        assert session.get_variable("user_id") == 123


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
