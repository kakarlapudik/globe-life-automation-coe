---
inclusion: manual
---

# Python Lambda Backend Standards

This document defines coding standards and best practices for building backend Lambda functions and APIs using Python for the AI Test Automation Platform.

## Project Structure

### Recommended Directory Structure
```
src/
├── handlers/           # Lambda function handlers
│   ├── test_execution/
│   │   ├── execute_test.py
│   │   ├── get_test_results.py
│   │   └── schedule_test.py
│   ├── test_data/
│   │   ├── generate_data.py
│   │   ├── validate_data.py
│   │   └── manage_data.py
│   ├── ai_analysis/
│   │   ├── analyze_results.py
│   │   ├── predict_failures.py
│   │   └── optimize_tests.py
│   └── auth/
│       ├── authenticate.py
│       └── authorize.py
├── services/           # Business logic services
│   ├── test_service.py
│   ├── data_service.py
│   ├── ai_service.py
│   ├── notification_service.py
│   └── integration_service.py
├── repositories/       # Data access layer
│   ├── test_repository.py
│   ├── user_repository.py
│   ├── result_repository.py
│   └── data_repository.py
├── models/             # Data models and schemas
│   ├── test_case.py
│   ├── test_result.py
│   ├── test_data.py
│   ├── user.py
│   └── ai_prediction.py
├── utils/              # Utility functions
│   ├── logger.py
│   ├── validator.py
│   ├── encryption.py
│   ├── date_utils.py
│   └── constants.py
├── middleware/         # Lambda middleware
│   ├── auth.py
│   ├── validation.py
│   ├── error_handler.py
│   └── cors.py
├── config/             # Configuration files
│   ├── database.py
│   ├── aws.py
│   ├── environment.py
│   └── secrets.py
└── tests/              # Test files
    ├── unit/
    ├── integration/
    └── fixtures/
```

## Coding Standards

### Python Best Practices
Use modern Python features and follow PEP 8 guidelines for clean, maintainable code.

**Examples:**
```python
# Good: Use type hints
from typing import Dict, List, Optional
from datetime import datetime

def process_test_results(
    test_id: str,
    results: List[Dict[str, any]]
) -> Dict[str, any]:
    """Process test execution results."""
    return {
        'test_id': test_id,
        'total_tests': len(results),
        'passed': sum(1 for r in results if r['status'] == 'passed')
    }

# Good: Use dataclasses for models
from dataclasses import dataclass, field

@dataclass
class TestCase:
    """Test case model."""
    test_id: str
    name: str
    description: str
    status: str = 'pending'
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)

# Good: Use context managers
import boto3
from contextlib import contextmanager

@contextmanager
def dynamodb_connection():
    """Context manager for DynamoDB connection."""
    dynamodb = boto3.resource('dynamodb')
    try:
        yield dynamodb
    finally:
        # Cleanup if needed
        pass

# Good: Use list/dict comprehensions
test_names = [test['name'] for test in tests if test['status'] == 'active']
test_map = {test['id']: test for test in tests}

# Good: Use f-strings for formatting
log_message = f"Processing test {test_id} with status {status}"

# Good: Async/await for async operations
import asyncio
import aioboto3

async def get_test_data(test_id: str) -> Dict[str, any]:
    """Get test data asynchronously."""
    try:
        async with aioboto3.Session().resource('dynamodb') as dynamodb:
            table = await dynamodb.Table('TestCases')
            response = await table.get_item(Key={'test_id': test_id})
            return response.get('Item', {})
    except Exception as error:
        logger.error(f'Failed to get test data: {test_id}', exc_info=True)
        raise
```

### Lambda Handler Pattern
```python
import json
import logging
from typing import Dict, Any
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for test execution.
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        API Gateway response
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        test_id = body.get('test_id')
        
        # Validate input
        if not test_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'test_id is required'
                })
            }
        
        # Execute business logic
        result = execute_test(test_id)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'data': result,
                'meta': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'request_id': context.request_id
                }
            })
        }
        
    except ValueError as error:
        logger.error('Validation error', exc_info=True)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(error)})
        }
        
    except Exception as error:
        logger.error('Internal server error', exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
```

### Service Layer Pattern
```python
from typing import List, Dict, Optional
import boto3
from botocore.exceptions import ClientError

class TestService:
    """Service for test execution operations."""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('TestCases')
        self.logger = logging.getLogger(__name__)
    
    def execute_test(self, test_id: str) -> Dict[str, any]:
        """
        Execute a test case.
        
        Args:
            test_id: Test case identifier
            
        Returns:
            Test execution result
            
        Raises:
            ValueError: If test_id is invalid
            RuntimeError: If execution fails
        """
        try:
            # Get test case
            test_case = self._get_test_case(test_id)
            
            if not test_case:
                raise ValueError(f'Test case not found: {test_id}')
            
            # Execute test
            result = self._run_test(test_case)
            
            # Store result
            self._store_result(test_id, result)
            
            return result
            
        except ClientError as error:
            self.logger.error(f'DynamoDB error: {error}', exc_info=True)
            raise RuntimeError('Failed to execute test') from error
    
    def _get_test_case(self, test_id: str) -> Optional[Dict[str, any]]:
        """Get test case from database."""
        response = self.table.get_item(Key={'test_id': test_id})
        return response.get('Item')
    
    def _run_test(self, test_case: Dict[str, any]) -> Dict[str, any]:
        """Run test execution logic."""
        # Implementation here
        pass
    
    def _store_result(self, test_id: str, result: Dict[str, any]) -> None:
        """Store test result."""
        # Implementation here
        pass
```

### Repository Pattern
```python
from typing import List, Dict, Optional
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr

class TestRepository:
    """Repository for test case data access."""
    
    def __init__(self, table_name: str = 'TestCases'):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
    
    def find_by_id(self, test_id: str) -> Optional[Dict[str, any]]:
        """Find test case by ID."""
        response = self.table.get_item(Key={'test_id': test_id})
        return response.get('Item')
    
    def find_by_status(self, status: str) -> List[Dict[str, any]]:
        """Find test cases by status."""
        response = self.table.query(
            IndexName='StatusIndex',
            KeyConditionExpression=Key('status').eq(status)
        )
        return response.get('Items', [])
    
    def create(self, test_case: Dict[str, any]) -> Dict[str, any]:
        """Create new test case."""
        test_case['created_at'] = datetime.utcnow().isoformat()
        test_case['updated_at'] = datetime.utcnow().isoformat()
        
        self.table.put_item(Item=test_case)
        return test_case
    
    def update(self, test_id: str, updates: Dict[str, any]) -> Dict[str, any]:
        """Update test case."""
        updates['updated_at'] = datetime.utcnow().isoformat()
        
        update_expression = 'SET ' + ', '.join(f'#{k} = :{k}' for k in updates.keys())
        expression_attribute_names = {f'#{k}': k for k in updates.keys()}
        expression_attribute_values = {f':{k}': v for k, v in updates.items()}
        
        response = self.table.update_item(
            Key={'test_id': test_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        return response.get('Attributes', {})
    
    def delete(self, test_id: str) -> None:
        """Delete test case."""
        self.table.delete_item(Key={'test_id': test_id})
```

## Error Handling

### Custom Exceptions
```python
class TestAutomationError(Exception):
    """Base exception for test automation errors."""
    pass

class TestNotFoundError(TestAutomationError):
    """Test case not found."""
    pass

class TestExecutionError(TestAutomationError):
    """Test execution failed."""
    pass

class DataValidationError(TestAutomationError):
    """Data validation failed."""
    pass

# Usage
def get_test_case(test_id: str) -> Dict[str, any]:
    """Get test case or raise error."""
    test_case = repository.find_by_id(test_id)
    
    if not test_case:
        raise TestNotFoundError(f'Test case not found: {test_id}')
    
    return test_case
```

### Error Handler Decorator
```python
from functools import wraps
import json

def handle_errors(func):
    """Decorator for error handling in Lambda functions."""
    @wraps(func)
    def wrapper(event, context):
        try:
            return func(event, context)
        except TestNotFoundError as error:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': str(error)})
            }
        except DataValidationError as error:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(error)})
            }
        except Exception as error:
            logger.error('Unexpected error', exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Internal server error'})
            }
    return wrapper

@handle_errors
def lambda_handler(event, context):
    """Lambda handler with error handling."""
    # Implementation
    pass
```

## Logging

### Structured Logging
```python
from aws_lambda_powertools import Logger
import json

logger = Logger(service="test-automation")

# Good: Structured logging with context
logger.info("Test execution started", extra={
    "test_id": test_id,
    "user_id": user_id,
    "environment": "production"
})

# Good: Log with correlation ID
logger.append_keys(correlation_id=context.request_id)
logger.info("Processing test request")

# Good: Log errors with context
try:
    execute_test(test_id)
except Exception as error:
    logger.error(
        "Test execution failed",
        extra={
            "test_id": test_id,
            "error_type": type(error).__name__,
            "error_message": str(error)
        },
        exc_info=True
    )
```

## Testing

### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from handlers.test_execution import execute_test

@pytest.fixture
def mock_dynamodb():
    """Mock DynamoDB resource."""
    with patch('boto3.resource') as mock:
        yield mock

def test_execute_test_success(mock_dynamodb):
    """Test successful test execution."""
    # Arrange
    test_id = 'test-123'
    expected_result = {'status': 'passed', 'duration': 1.5}
    
    mock_table = Mock()
    mock_table.get_item.return_value = {
        'Item': {'test_id': test_id, 'name': 'Test Case 1'}
    }
    mock_dynamodb.return_value.Table.return_value = mock_table
    
    # Act
    result = execute_test.execute(test_id)
    
    # Assert
    assert result['status'] == 'passed'
    mock_table.get_item.assert_called_once()

def test_execute_test_not_found(mock_dynamodb):
    """Test execution with non-existent test."""
    # Arrange
    test_id = 'invalid-test'
    mock_table = Mock()
    mock_table.get_item.return_value = {}
    mock_dynamodb.return_value.Table.return_value = mock_table
    
    # Act & Assert
    with pytest.raises(TestNotFoundError):
        execute_test.execute(test_id)
```

### Integration Tests
```python
import boto3
import pytest
from moto import mock_dynamodb

@pytest.fixture
def dynamodb_table():
    """Create mock DynamoDB table."""
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        table = dynamodb.create_table(
            TableName='TestCases',
            KeySchema=[
                {'AttributeName': 'test_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'test_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield table

def test_create_test_case_integration(dynamodb_table):
    """Integration test for creating test case."""
    # Arrange
    repository = TestRepository('TestCases')
    test_case = {
        'test_id': 'test-123',
        'name': 'Integration Test',
        'status': 'active'
    }
    
    # Act
    result = repository.create(test_case)
    
    # Assert
    assert result['test_id'] == 'test-123'
    assert 'created_at' in result
    
    # Verify in database
    stored = repository.find_by_id('test-123')
    assert stored is not None
    assert stored['name'] == 'Integration Test'
```

## Performance Optimization

### Connection Reuse
```python
import boto3

# Good: Reuse connections across invocations
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TestCases')

def lambda_handler(event, context):
    """Handler reuses connection."""
    # Use table connection
    response = table.get_item(Key={'test_id': event['test_id']})
    return response
```

### Batch Operations
```python
def batch_create_tests(test_cases: List[Dict[str, any]]) -> None:
    """Create multiple test cases in batch."""
    with table.batch_writer() as batch:
        for test_case in test_cases:
            batch.put_item(Item=test_case)

def batch_get_tests(test_ids: List[str]) -> List[Dict[str, any]]:
    """Get multiple test cases in batch."""
    response = dynamodb.batch_get_item(
        RequestItems={
            'TestCases': {
                'Keys': [{'test_id': test_id} for test_id in test_ids]
            }
        }
    )
    return response['Responses']['TestCases']
```

## Security Best Practices

### Input Validation
```python
from pydantic import BaseModel, validator, Field
from typing import Optional

class TestCaseInput(BaseModel):
    """Input validation for test case."""
    test_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: int = Field(default=1, ge=1, le=5)
    
    @validator('test_id')
    def validate_test_id(cls, v):
        """Validate test ID format."""
        if not v.isalnum() and '-' not in v:
            raise ValueError('test_id must be alphanumeric with hyphens')
        return v

# Usage
def create_test_case(data: dict) -> Dict[str, any]:
    """Create test case with validation."""
    try:
        validated_data = TestCaseInput(**data)
        return repository.create(validated_data.dict())
    except ValidationError as error:
        raise DataValidationError(str(error))
```

### Secrets Management
```python
import boto3
import json
from functools import lru_cache

@lru_cache(maxsize=1)
def get_secret(secret_name: str) -> Dict[str, any]:
    """Get secret from AWS Secrets Manager with caching."""
    client = boto3.client('secretsmanager')
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as error:
        logger.error(f'Failed to get secret: {secret_name}', exc_info=True)
        raise

# Usage
def connect_to_external_api():
    """Connect using secrets."""
    secrets = get_secret('test-automation/api-keys')
    api_key = secrets['api_key']
    # Use api_key
```

## Dependencies Management

### requirements.txt
```txt
# AWS SDK
boto3==1.28.0
botocore==1.31.0

# Lambda Powertools
aws-lambda-powertools==2.25.0

# Data validation
pydantic==2.4.0

# HTTP client
httpx==0.25.0

# Testing
pytest==7.4.0
pytest-cov==4.1.0
pytest-asyncio==0.21.0
moto==4.2.0

# Code quality
black==23.9.0
flake8==6.1.0
mypy==1.5.0
pylint==2.17.0
```

### Layer Management
```python
# Create Lambda layer for common dependencies
# layer/python/lib/python3.11/site-packages/
# - boto3
# - aws_lambda_powertools
# - pydantic
```

This Python Lambda standards document provides a comprehensive guide for building the AI Test Automation Platform backend with Python, following AWS best practices and modern Python development patterns.
