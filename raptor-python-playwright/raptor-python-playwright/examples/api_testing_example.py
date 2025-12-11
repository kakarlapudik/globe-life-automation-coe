"""API Testing Examples for RAPTOR Framework

Demonstrates comprehensive API testing capabilities.
"""

from raptor.api import ApiClient, ApiSession, AuthManager, ApiAssertions, JsonSchemaValidator


def example_basic_api_request():
    """Example: Basic API request."""
    print("\n=== Basic API Request ===")
    
    # Create API client
    client = ApiClient(base_url="https://jsonplaceholder.typicode.com")
    
    # Make GET request
    response = client.get("/posts/1")
    
    # Check response
    print(f"Status: {response.status_code}")
    print(f"Response time: {response.elapsed_time:.3f}s")
    print(f"Data: {response.json()}")
    
    client.close()


def example_authentication():
    """Example: API authentication."""
    print("\n=== API Authentication ===")
    
    # Create auth manager
    auth = AuthManager()
    
    # Set Bearer token authentication
    auth.set_bearer_auth("your-api-token-here")
    
    # Create client with authentication
    client = ApiClient(
        base_url="https://api.example.com",
        auth_manager=auth
    )
    
    # Make authenticated request
    response = client.get("/user/profile")
    print(f"Status: {response.status_code}")
    
    client.close()


def example_fluent_assertions():
    """Example: Fluent assertions."""
    print("\n=== Fluent Assertions ===")
    
    client = ApiClient(base_url="https://jsonplaceholder.typicode.com")
    assertions = ApiAssertions()
    
    # Make request
    response = client.get("/posts/1")
    
    # Chain assertions
    try:
        assertions.that(response) \
            .is_ok() \
            .has_valid_json() \
            .has_json_path("userId", 1) \
            .has_json_path("title") \
            .response_time_less_than(2.0)
        
        print("All assertions passed!")
    except Exception as e:
        print(f"Assertion failed: {e}")
    
    client.close()


def example_json_schema_validation():
    """Example: JSON schema validation."""
    print("\n=== JSON Schema Validation ===")
    
    client = ApiClient(base_url="https://jsonplaceholder.typicode.com")
    schema_validator = JsonSchemaValidator()
    assertions = ApiAssertions()
    
    # Define JSON schema
    post_schema = {
        "type": "object",
        "properties": {
            "userId": {"type": "integer"},
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "body": {"type": "string"}
        },
        "required": ["userId", "id", "title", "body"]
    }
    
    # Add schema
    schema_validator.add_schema("post", post_schema)
    
    # Make request and validate
    response = client.get("/posts/1")
    
    try:
        assertions.that(response).matches_schema("post")
        print("Schema validation passed!")
    except Exception as e:
        print(f"Schema validation failed: {e}")
    
    client.close()


def example_session_management():
    """Example: Session management with request chaining."""
    print("\n=== Session Management ===")
    
    with ApiSession(base_url="https://jsonplaceholder.typicode.com") as session:
        # Create a post
        create_response = session.post(
            "/posts",
            json_data={
                "title": "Test Post",
                "body": "This is a test",
                "userId": 1
            }
        )
        
        # Extract post ID from response
        session.extract_from_response("id", "post_id")
        post_id = session.get_variable("post_id")
        
        print(f"Created post with ID: {post_id}")
        
        # Get the created post
        get_response = session.get(f"/posts/{post_id}")
        print(f"Retrieved post: {get_response.json()}")
        
        # Update the post
        update_response = session.put(
            f"/posts/{post_id}",
            json_data={
                "title": "Updated Post",
                "body": "This is updated",
                "userId": 1
            }
        )
        print(f"Updated post: {update_response.json()}")
        
        # Delete the post
        delete_response = session.delete(f"/posts/{post_id}")
        print(f"Delete status: {delete_response.status_code}")


def example_data_driven_testing():
    """Example: Data-driven API testing."""
    print("\n=== Data-Driven Testing ===")
    
    client = ApiClient(base_url="https://jsonplaceholder.typicode.com")
    assertions = ApiAssertions()
    
    # Test data
    post_ids = [1, 2, 3, 4, 5]
    
    for post_id in post_ids:
        response = client.get(f"/posts/{post_id}")
        
        try:
            assertions.that(response) \
                .is_ok() \
                .has_json_path("id", post_id) \
                .has_json_path("userId") \
                .has_json_path("title") \
                .has_json_path("body")
            
            print(f"✓ Post {post_id} validation passed")
        except Exception as e:
            print(f"✗ Post {post_id} validation failed: {e}")
    
    client.close()


def example_async_api_testing():
    """Example: Async API testing."""
    print("\n=== Async API Testing ===")
    
    import asyncio
    from raptor.api.client import AsyncApiClient
    
    async def test_multiple_endpoints():
        client = AsyncApiClient(base_url="https://jsonplaceholder.typicode.com")
        
        # Make concurrent requests
        tasks = [
            client.get("/posts/1"),
            client.get("/posts/2"),
            client.get("/posts/3"),
            client.get("/users/1"),
            client.get("/users/2")
        ]
        
        responses = await asyncio.gather(*tasks)
        
        for i, response in enumerate(responses):
            print(f"Response {i+1}: Status {response.status_code}, Time {response.elapsed_time:.3f}s")
    
    # Run async test
    asyncio.run(test_multiple_endpoints())


def example_error_handling():
    """Example: Error handling."""
    print("\n=== Error Handling ===")
    
    client = ApiClient(base_url="https://jsonplaceholder.typicode.com")
    assertions = ApiAssertions()
    
    # Test 404 error
    response = client.get("/posts/999999")
    
    try:
        assertions.that(response).is_not_found()
        print("404 error handled correctly")
    except Exception as e:
        print(f"Error handling failed: {e}")
    
    # Test with invalid endpoint
    try:
        response = client.get("/invalid-endpoint")
        assertions.that(response).is_not_found()
        print("Invalid endpoint handled correctly")
    except Exception as e:
        print(f"Error: {e}")
    
    client.close()


def example_file_upload():
    """Example: File upload."""
    print("\n=== File Upload ===")
    
    client = ApiClient(base_url="https://httpbin.org")
    
    # Prepare file
    files = {
        'file': ('test.txt', b'Hello, World!', 'text/plain')
    }
    
    # Upload file
    response = client.post("/post", files=files)
    
    print(f"Upload status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    client.close()


if __name__ == "__main__":
    print("RAPTOR API Testing Examples")
    print("=" * 50)
    
    example_basic_api_request()
    example_authentication()
    example_fluent_assertions()
    example_json_schema_validation()
    example_session_management()
    example_data_driven_testing()
    example_async_api_testing()
    example_error_handling()
    example_file_upload()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
