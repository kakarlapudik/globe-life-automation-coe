"""API Assertions for RAPTOR Framework

Provides REST Assured-like assertion methods for API testing.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union
from raptor.api.client import ApiResponse
from raptor.api.validator import ResponseValidator, JsonSchemaValidator, ValidationResult


class AssertionError(Exception):
    """Custom assertion error for API testing."""
    pass


class ApiAssertions:
    """Provides fluent assertion methods for API responses."""
    
    def __init__(self):
        self.validator = ResponseValidator()
        self.schema_validator = JsonSchemaValidator()
        self.response: Optional[ApiResponse] = None
    
    def that(self, response: ApiResponse) -> 'ApiAssertions':
        """Set the response to assert against."""
        self.response = response
        return self
    
    def _ensure_response(self) -> ApiResponse:
        """Ensure response is set."""
        if self.response is None:
            raise AssertionError("No response set. Use .that(response) first.")
        return self.response
    
    def _assert_validation_result(self, result: ValidationResult, custom_message: str = "") -> 'ApiAssertions':
        """Assert validation result is successful."""
        if not result.is_valid:
            message = custom_message or result.message
            raise AssertionError(message)
        return self
    
    # Status Code Assertions
    
    def has_status_code(self, expected_code: int) -> 'ApiAssertions':
        """Assert response has specific status code."""
        response = self._ensure_response()
        result = self.validator.validate_status_code(response, expected_code)
        return self._assert_validation_result(result)
    
    def has_status_code_in_range(self, min_code: int, max_code: int) -> 'ApiAssertions':
        """Assert response status code is within range."""
        response = self._ensure_response()
        result = self.validator.validate_status_code_in_range(response, min_code, max_code)
        return self._assert_validation_result(result)
    
    def is_success(self) -> 'ApiAssertions':
        """Assert response has success status code (2xx)."""
        response = self._ensure_response()
        result = self.validator.validate_success_status(response)
        return self._assert_validation_result(result)
    
    def is_ok(self) -> 'ApiAssertions':
        """Assert response has 200 OK status."""
        return self.has_status_code(200)
    
    def is_created(self) -> 'ApiAssertions':
        """Assert response has 201 Created status."""
        return self.has_status_code(201)
    
    def is_accepted(self) -> 'ApiAssertions':
        """Assert response has 202 Accepted status."""
        return self.has_status_code(202)
    
    def is_no_content(self) -> 'ApiAssertions':
        """Assert response has 204 No Content status."""
        return self.has_status_code(204)
    
    def is_bad_request(self) -> 'ApiAssertions':
        """Assert response has 400 Bad Request status."""
        return self.has_status_code(400)
    
    def is_unauthorized(self) -> 'ApiAssertions':
        """Assert response has 401 Unauthorized status."""
        return self.has_status_code(401)
    
    def is_forbidden(self) -> 'ApiAssertions':
        """Assert response has 403 Forbidden status."""
        return self.has_status_code(403)
    
    def is_not_found(self) -> 'ApiAssertions':
        """Assert response has 404 Not Found status."""
        return self.has_status_code(404)
    
    def is_internal_server_error(self) -> 'ApiAssertions':
        """Assert response has 500 Internal Server Error status."""
        return self.has_status_code(500)
    
    # Header Assertions
    
    def has_header(self, header_name: str) -> 'ApiAssertions':
        """Assert response has specific header."""
        response = self._ensure_response()
        result = self.validator.validate_header_exists(response, header_name)
        return self._assert_validation_result(result)
    
    def has_header_with_value(self, header_name: str, expected_value: str) -> 'ApiAssertions':
        """Assert response header has specific value."""
        response = self._ensure_response()
        result = self.validator.validate_header_value(response, header_name, expected_value)
        return self._assert_validation_result(result)
    
    def has_content_type(self, expected_type: str) -> 'ApiAssertions':
        """Assert response has specific content type."""
        response = self._ensure_response()
        result = self.validator.validate_content_type(response, expected_type)
        return self._assert_validation_result(result)
    
    def is_json(self) -> 'ApiAssertions':
        """Assert response is JSON."""
        return self.has_content_type("application/json")
    
    def is_xml(self) -> 'ApiAssertions':
        """Assert response is XML."""
        return self.has_content_type("application/xml")
    
    def is_html(self) -> 'ApiAssertions':
        """Assert response is HTML."""
        return self.has_content_type("text/html")
    
    def is_text(self) -> 'ApiAssertions':
        """Assert response is plain text."""
        return self.has_content_type("text/plain")
    
    # Content Assertions
    
    def has_valid_json(self) -> 'ApiAssertions':
        """Assert response is valid JSON."""
        response = self._ensure_response()
        result = self.validator.validate_json_response(response)
        return self._assert_validation_result(result)
    
    def contains_text(self, text: str, case_sensitive: bool = True) -> 'ApiAssertions':
        """Assert response contains specific text."""
        response = self._ensure_response()
        result = self.validator.validate_text_contains(response, text, case_sensitive)
        return self._assert_validation_result(result)
    
    def matches_regex(self, pattern: str, flags: int = 0) -> 'ApiAssertions':
        """Assert response matches regex pattern."""
        response = self._ensure_response()
        result = self.validator.validate_text_matches_regex(response, pattern, flags)
        return self._assert_validation_result(result)
    
    def is_empty(self) -> 'ApiAssertions':
        """Assert response body is empty."""
        response = self._ensure_response()
        if response.text.strip():
            raise AssertionError(f"Expected empty response, got: {response.text[:100]}...")
        return self
    
    def is_not_empty(self) -> 'ApiAssertions':
        """Assert response body is not empty."""
        response = self._ensure_response()
        if not response.text.strip():
            raise AssertionError("Expected non-empty response, got empty response")
        return self
    
    # JSON Assertions
    
    def has_json_path(self, json_path: str, expected_value: Any = None) -> 'ApiAssertions':
        """Assert JSON path exists and optionally has expected value."""
        response = self._ensure_response()
        result = self.validator.validate_json_path(response, json_path, expected_value)
        return self._assert_validation_result(result)
    
    def json_path_equals(self, json_path: str, expected_value: Any) -> 'ApiAssertions':
        """Assert JSON path equals expected value."""
        return self.has_json_path(json_path, expected_value)
    
    def json_path_contains(self, json_path: str, expected_item: Any) -> 'ApiAssertions':
        """Assert JSON path (array) contains expected item."""
        response = self._ensure_response()
        
        # First check if path exists
        path_result = self.validator.validate_json_path(response, json_path)
        if not path_result.is_valid:
            raise AssertionError(path_result.message)
        
        # Get the value at path
        try:
            json_data = response.json()
            current = json_data
            path_parts = json_path.split('.')
            
            for part in path_parts:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, list):
                    current = current[int(part)]
            
            if not isinstance(current, list):
                raise AssertionError(f"JSON path '{json_path}' is not an array")
            
            if expected_item not in current:
                raise AssertionError(
                    f"JSON path '{json_path}' does not contain '{expected_item}'"
                )
            
        except Exception as e:
            raise AssertionError(f"Error checking JSON path '{json_path}': {str(e)}")
        
        return self
    
    def json_path_has_size(self, json_path: str, expected_size: int) -> 'ApiAssertions':
        """Assert JSON path (array/object) has expected size."""
        response = self._ensure_response()
        
        # First check if path exists
        path_result = self.validator.validate_json_path(response, json_path)
        if not path_result.is_valid:
            raise AssertionError(path_result.message)
        
        # Get the value at path and check size
        try:
            json_data = response.json()
            current = json_data
            path_parts = json_path.split('.')
            
            for part in path_parts:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, list):
                    current = current[int(part)]
            
            if isinstance(current, (list, dict, str)):
                actual_size = len(current)
                if actual_size != expected_size:
                    raise AssertionError(
                        f"JSON path '{json_path}' has size {actual_size}, expected {expected_size}"
                    )
            else:
                raise AssertionError(f"JSON path '{json_path}' is not a collection")
        
        except AssertionError:
            raise
        except Exception as e:
            raise AssertionError(f"Error checking JSON path '{json_path}': {str(e)}")
        
        return self
    
    # Schema Assertions
    
    def matches_schema(self, schema: Union[str, Dict[str, Any]]) -> 'ApiAssertions':
        """Assert response matches JSON schema."""
        response = self._ensure_response()
        result = self.schema_validator.validate_response(response, schema)
        return self._assert_validation_result(result)
    
    # Performance Assertions
    
    def response_time_less_than(self, max_time: float) -> 'ApiAssertions':
        """Assert response time is less than specified time."""
        response = self._ensure_response()
        result = self.validator.validate_response_time(response, max_time)
        return self._assert_validation_result(result)
    
    def response_size_less_than(self, max_size: int) -> 'ApiAssertions':
        """Assert response size is less than specified size."""
        response = self._ensure_response()
        result = self.validator.validate_response_size(response, max_size)
        return self._assert_validation_result(result)
