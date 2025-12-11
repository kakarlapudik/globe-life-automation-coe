"""API Session Management for RAPTOR Framework

Provides session management and request chaining capabilities.
"""

from typing import Dict, Any, Optional, List
from raptor.api.client import ApiClient, ApiResponse
from raptor.api.auth import AuthManager


class ApiSession:
    """Manages API sessions with request chaining and state management."""
    
    def __init__(
        self,
        base_url: str = "",
        default_headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True
    ):
        """
        Initialize API session.
        
        Args:
            base_url: Base URL for all requests
            default_headers: Default headers for all requests
            timeout: Default timeout for requests
            verify_ssl: Whether to verify SSL certificates
        """
        self.client = ApiClient(
            base_url=base_url,
            default_headers=default_headers,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
        
        # Session state
        self.variables: Dict[str, Any] = {}
        self.last_response: Optional[ApiResponse] = None
    
    def set_variable(self, name: str, value: Any) -> 'ApiSession':
        """Set a session variable."""
        self.variables[name] = value
        return self
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a session variable."""
        return self.variables.get(name, default)
    
    def extract_from_response(
        self,
        json_path: str,
        variable_name: str
    ) -> 'ApiSession':
        """
        Extract value from last response and store as variable.
        
        Args:
            json_path: JSON path to extract (dot notation)
            variable_name: Name to store the extracted value
            
        Returns:
            Self for chaining
        """
        if not self.last_response:
            raise ValueError("No response available to extract from")
        
        try:
            json_data = self.last_response.json()
            current = json_data
            path_parts = json_path.split('.')
            
            for part in path_parts:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, list):
                    current = current[int(part)]
            
            self.set_variable(variable_name, current)
            
        except Exception as e:
            raise ValueError(f"Failed to extract '{json_path}': {str(e)}")
        
        return self
    
    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> ApiResponse:
        """Make GET request and store response."""
        self.last_response = self.client.get(
            endpoint=endpoint,
            headers=headers,
            params=params,
            timeout=timeout
        )
        return self.last_response
    
    def post(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> ApiResponse:
        """Make POST request and store response."""
        self.last_response = self.client.post(
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            json_data=json_data,
            files=files,
            timeout=timeout
        )
        return self.last_response
    
    def put(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> ApiResponse:
        """Make PUT request and store response."""
        self.last_response = self.client.put(
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            json_data=json_data,
            timeout=timeout
        )
        return self.last_response
    
    def patch(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> ApiResponse:
        """Make PATCH request and store response."""
        self.last_response = self.client.patch(
            endpoint=endpoint,
            headers=headers,
            params=params,
            data=data,
            json_data=json_data,
            timeout=timeout
        )
        return self.last_response
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> ApiResponse:
        """Make DELETE request and store response."""
        self.last_response = self.client.delete(
            endpoint=endpoint,
            headers=headers,
            params=params,
            timeout=timeout
        )
        return self.last_response
    
    def set_auth(self, auth_manager: AuthManager) -> 'ApiSession':
        """Set authentication for the session."""
        self.client.set_auth(auth_manager)
        return self
    
    def set_header(self, name: str, value: str) -> 'ApiSession':
        """Set default header for the session."""
        self.client.set_header(name, value)
        return self
    
    def remove_header(self, name: str) -> 'ApiSession':
        """Remove default header from the session."""
        self.client.remove_header(name)
        return self
    
    def clear_variables(self) -> 'ApiSession':
        """Clear all session variables."""
        self.variables.clear()
        return self
    
    def close(self) -> None:
        """Close the session."""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
