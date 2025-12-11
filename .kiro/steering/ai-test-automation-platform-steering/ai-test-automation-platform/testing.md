---
inclusion: manual
---

# Testing Guidelines

This document defines comprehensive testing guidelines for the AI Test Automation Platform, covering unit tests, integration tests, end-to-end tests, and property-based testing strategies.

## Testing Philosophy

### Test Pyramid Strategy

```
                    /\
                   /  \
                  / E2E \
                 /--------\
                /          \
               / Integration \
              /--------------\
             /                \
            /   Unit Tests     \
           /____________________\
```

**Distribution**:
- 70% Unit Tests - Fast, isolated, focused
- 20% Integration Tests - Component interactions
- 10% E2E Tests - Full user workflows

## Python Backend Testing

### Unit Testing Standards

#### Test Structure (AAA Pattern)
```python
# tests/unit/services/test_test_execution_service.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from services.test_execution_service import TestExecutionService
from models.test_case import TestCase
from exceptions import TestExecutionError

class TestTestExecutionService:
    """Unit tests for TestExecutionService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return TestExecutionService()
    
    @pytest.fixture
    def sample_test_case(self):
        """Create sample test case."""
        return TestCase(
            id="test_001",
            name="Sample Test",
            description="A sample test case",
            steps=[
                {"action": "navigate", "target": "https://example.com"},
                {"action": "click", "target": "#submit-button"}
            ],
            expected_results=["Page should load successfully"]
        )
    
    def test_execute_test_case_success(self, service, sample_test_case):
        """Test successful test case execution."""
        # Arrange
        expected_status = "PASSED"
        expected_duration = 10.5
        
        with patch.object(service, '_run_test_steps') as mock_run:
            mock_run.return_value = {
                "status": expected_status,
                "duration": expected_duration
            }
            
            # Act
            result = service.execute_test_case(sample_test_case)
            
            # Assert
            assert result.status == expected_status
            assert result.duration == expected_duration
            assert result.test_case_id == sample_test_case.id
            mock_run.assert_called_once_with(sample_test_case)
    
    def test_execute_test_case_with_invalid_input(self, service):
        """Test execution with invalid test case."""
        # Arrange
        invalid_test_case = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Test case cannot be None"):
            service.execute_test_case(invalid_test_case)
    
    @pytest.mark.asyncio
    async def test_execute_test_suite_async(self, service):
        """Test asynchronous test suite execution."""
        # Arrange
        suite_id = "suite_001"
        test_cases = [
            TestCase(id=f"test_{i}", name=f"Test {i}", description="", steps=[], expected_results=[])
            for i in range(3)
        ]
        
        with patch.object(service.repository, 'get_test_suite', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = test_cases
            
            with patch.object(service, '_execute_single_test', new_callable=AsyncMock) as mock_execute:
                mock_execute.return_value = Mock(status="PASSED")
                
                # Act
                results = await service.execute_test_suite_async(suite_id)
                
                # Assert
                assert len(results) == 3
                assert mock_execute.call_count == 3
```

#### Parametrized Testing
```python
@pytest.mark.parametrize("test_status,expected_metric", [
    ("PASSED", 1),
    ("FAILED", 0),
    ("ERROR", 0),
])
def test_calculate_success_rate(service, test_status, expected_metric):
    """Test success rate calculation for different statuses."""
    # Arrange
    results = [Mock(status=test_status) for _ in range(10)]
    
    # Act
    success_rate = service.calculate_success_rate(results)
    
    # Assert
    assert success_rate == expected_metric

@pytest.mark.parametrize("environment,expected_timeout", [
    ("development", 60),
    ("staging", 120),
    ("production", 300),
])
def test_get_environment_timeout(service, environment, expected_timeout):
    """Test environment-specific timeout configuration."""
    config = service.get_environment_config(environment)
    assert config["timeout"] == expected_timeout
```

### Integration Testing

#### DynamoDB Integration Tests
```python
# tests/integration/test_test_repository.py
import pytest
import boto3
from moto import mock_dynamodb

from repositories.test_repository import TestRepository
from models.test_case import TestCase

@pytest.fixture
def dynamodb_table():
    """Create mock DynamoDB table for testing."""
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        table = dynamodb.create_table(
            TableName='TestCases',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1SK', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'GSI1',
                    'KeySchema': [
                        {'AttributeName': 'GSI1PK', 'KeyType': 'HASH'},
                        {'AttributeName': 'GSI1SK', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield table

@pytest.mark.integration
class TestTestRepository:
    """Integration tests for TestRepository."""
    
    def test_create_and_retrieve_test_case(self, dynamodb_table):
        """Test creating and retrieving a test case."""
        # Arrange
        repository = TestRepository('TestCases')
        test_case = TestCase(
            id="test_001",
            name="Integration Test",
            description="Test case for integration testing",
            steps=[{"action": "navigate", "target": "https://example.com"}],
            expected_results=["Page loads successfully"]
        )
        
        # Act
        created = repository.create(test_case)
        retrieved = repository.find_by_id("test_001")
        
        # Assert
        assert created.id == test_case.id
        assert retrieved is not None
        assert retrieved.name == test_case.name
        assert len(retrieved.steps) == 1
    
    def test_query_by_status(self, dynamodb_table):
        """Test querying test cases by status."""
        # Arrange
        repository = TestRepository('TestCases')
        
        # Create test cases with different statuses
        for i in range(5):
            test_case = TestCase(
                id=f"test_{i}",
                name=f"Test {i}",
                description="",
                steps=[],
                expected_results=[],
                status="ACTIVE" if i % 2 == 0 else "INACTIVE"
            )
            repository.create(test_case)
        
        # Act
        active_tests = repository.find_by_status("ACTIVE")
        
        # Assert
        assert len(active_tests) == 3
        assert all(test.status == "ACTIVE" for test in active_tests)
```

#### API Integration Tests
```python
# tests/integration/test_api_endpoints.py
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app
from tests.fixtures import create_test_user, create_auth_token

@pytest.mark.integration
class TestAPIEndpoints:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers."""
        token = create_auth_token(user_id="test_user")
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_test_case_endpoint(self, client, auth_headers):
        """Test test case creation endpoint."""
        # Arrange
        test_case_data = {
            "name": "API Integration Test",
            "description": "Test case created via API",
            "steps": [
                {"action": "navigate", "target": "https://example.com"}
            ],
            "expected_results": ["Page should load"]
        }
        
        # Act
        response = client.post(
            "/api/v1/test-cases",
            json=test_case_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_case_data["name"]
        assert "id" in data
        assert "ai_complexity_score" in data
    
    def test_execute_test_suite_endpoint(self, client, auth_headers):
        """Test test suite execution endpoint."""
        # Arrange
        suite_id = "suite_001"
        execution_request = {
            "suite_id": suite_id,
            "environment": "staging",
            "parallel_execution": False
        }
        
        # Act
        response = client.post(
            "/api/v1/test-execution/execute-suite",
            json=execution_request,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        assert "results" in data
        assert "ai_insights" in data
```

### Property-Based Testing

#### Using Hypothesis for Property Tests
```python
# tests/property/test_test_case_properties.py
import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import composite

from models.test_case import TestCase
from services.test_execution_service import TestExecutionService

# Custom strategies
@composite
def test_case_strategy(draw):
    """Generate random valid test cases."""
    return TestCase(
        id=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        name=draw(st.text(min_size=1, max_size=100)),
        description=draw(st.text(max_size=500)),
        steps=draw(st.lists(
            st.fixed_dictionaries({
                'action': st.sampled_from(['navigate', 'click', 'type', 'wait']),
                'target': st.text(min_size=1, max_size=100)
            }),
            min_size=1,
            max_size=10
        )),
        expected_results=draw(st.lists(st.text(min_size=1, max_size=200), min_size=1, max_size=5))
    )

@pytest.mark.property
class TestTestCaseProperties:
    """Property-based tests for test case operations."""
    
    @given(test_case=test_case_strategy())
    def test_test_case_serialization_roundtrip(self, test_case):
        """Property: Serializing and deserializing should preserve test case data."""
        # Act
        serialized = test_case.to_dict()
        deserialized = TestCase.from_dict(serialized)
        
        # Assert
        assert deserialized.id == test_case.id
        assert deserialized.name == test_case.name
        assert len(deserialized.steps) == len(test_case.steps)
    
    @given(
        test_case=test_case_strategy(),
        tag=st.text(min_size=1, max_size=20)
    )
    def test_adding_tag_increases_tag_count(self, test_case, tag):
        """Property: Adding a tag should increase the tag count by 1."""
        # Arrange
        initial_count = len(test_case.tags)
        
        # Act
        test_case.add_tag(tag)
        
        # Assert
        assert len(test_case.tags) == initial_count + 1
        assert tag in test_case.tags
    
    @given(test_case=test_case_strategy())
    def test_estimated_duration_is_positive(self, test_case):
        """Property: Estimated duration should always be positive."""
        # Act
        duration = test_case.calculate_estimated_duration()
        
        # Assert
        assert duration > 0
```

## Vue.js Frontend Testing

### Component Unit Tests

#### Using Vitest and Vue Test Utils
```javascript
// tests/unit/components/TestCaseEditor.spec.js
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TestCaseEditor from '@/components/TestCaseEditor.vue'
import { useTestCaseStore } from '@/stores/testCase'

describe('TestCaseEditor', () => {
  let wrapper
  let store
  
  beforeEach(() => {
    // Setup Pinia
    setActivePinia(createPinia())
    store = useTestCaseStore()
    
    // Mount component
    wrapper = mount(TestCaseEditor, {
      props: {
        testCaseId: null
      }
    })
  })
  
  it('renders the component', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('form').exists()).toBe(true)
  })
  
  it('validates required fields', async () => {
    // Arrange
    const submitButton = wrapper.find('button[type="submit"]')
    
    // Act
    await submitButton.trigger('click')
    
    // Assert
    expect(wrapper.vm.errors.name).toBeTruthy()
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })
  
  it('creates test case on valid submission', async () => {
    // Arrange
    const createSpy = vi.spyOn(store, 'createTestCase')
    
    await wrapper.find('#test-name').setValue('New Test Case')
    await wrapper.find('#test-description').setValue('Test description')
    
    // Act
    await wrapper.find('form').trigger('submit')
    
    // Assert
    expect(createSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'New Test Case',
        description: 'Test description'
      })
    )
  })
  
  it('emits cancel event when cancel button clicked', async () => {
    // Act
    await wrapper.find('button.btn-secondary').trigger('click')
    
    // Assert
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })
})
```

#### Testing Composables
```javascript
// tests/unit/composables/useTestExecution.spec.js
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useTestExecution } from '@/composables/useTestExecution'
import { testService } from '@/services/testService'

vi.mock('@/services/testService')

describe('useTestExecution', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  
  it('initializes with idle status', () => {
    const { executionStatus } = useTestExecution()
    expect(executionStatus.value).toBe('idle')
  })
  
  it('executes test suite successfully', async () => {
    // Arrange
    const mockResults = [
      { test_id: 'test_001', status: 'PASSED' },
      { test_id: 'test_002', status: 'PASSED' }
    ]
    testService.executeTestSuite.mockResolvedValue(mockResults)
    
    const { executeTestSuite, executionStatus, results } = useTestExecution()
    
    // Act
    await executeTestSuite('suite_001')
    
    // Assert
    expect(executionStatus.value).toBe('completed')
    expect(results.value).toEqual(mockResults)
    expect(testService.executeTestSuite).toHaveBeenCalledWith('suite_001')
  })
  
  it('handles execution errors', async () => {
    // Arrange
    const error = new Error('Execution failed')
    testService.executeTestSuite.mockRejectedValue(error)
    
    const { executeTestSuite, executionStatus, error: executionError } = useTestExecution()
    
    // Act
    await executeTestSuite('suite_001')
    
    // Assert
    expect(executionStatus.value).toBe('error')
    expect(executionError.value).toBe(error.message)
  })
})
```

### Integration Tests

#### Component Integration Tests
```javascript
// tests/integration/TestExecutionFlow.spec.js
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TestSuiteRunner from '@/components/test-execution/TestSuiteRunner.vue'
import TestResultsPanel from '@/components/test-execution/TestResultsPanel.vue'
import AIInsightsCard from '@/components/test-execution/AIInsightsCard.vue'

describe('Test Execution Flow Integration', () => {
  let wrapper
  
  beforeEach(() => {
    setActivePinia(createPinia())
    
    wrapper = mount(TestSuiteRunner, {
      global: {
        components: {
          TestResultsPanel,
          AIInsightsCard
        }
      }
    })
  })
  
  it('completes full test execution workflow', async () => {
    // Arrange - Select test suite
    const suiteSelect = wrapper.find('select')
    await suiteSelect.setValue('suite_001')
    
    // Act - Execute test suite
    const executeButton = wrapper.find('button')
    await executeButton.trigger('click')
    
    // Wait for execution to complete
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Assert - Results are displayed
    expect(wrapper.findComponent(TestResultsPanel).exists()).toBe(true)
    expect(wrapper.findComponent(AIInsightsCard).exists()).toBe(true)
  })
})
```

### End-to-End Tests

#### Using Playwright
```javascript
// tests/e2e/test-execution.spec.js
import { test, expect } from '@playwright/test'

test.describe('Test Execution Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login')
    await page.fill('#email', 'test@example.com')
    await page.fill('#password', 'password123')
    await page.click('button[type="submit"]')
    
    // Wait for dashboard
    await page.waitForURL('/dashboard')
  })
  
  test('user can execute a test suite', async ({ page }) => {
    // Navigate to test execution
    await page.click('text=Test Execution')
    await page.waitForURL('/test-execution')
    
    // Select test suite
    await page.selectOption('select#test-suite', 'suite_001')
    
    // Execute test suite
    await page.click('button:has-text("Execute Suite")')
    
    // Wait for execution to complete
    await page.waitForSelector('.test-results-panel', { timeout: 30000 })
    
    // Verify results are displayed
    const resultsPanel = page.locator('.test-results-panel')
    await expect(resultsPanel).toBeVisible()
    
    // Verify AI insights are shown
    const aiInsights = page.locator('.ai-insights-card')
    await expect(aiInsights).toBeVisible()
    
    // Verify summary metrics
    const passedCount = page.locator('.metric-passed')
    await expect(passedCount).toContainText(/\d+/)
  })
  
  test('user can view test execution history', async ({ page }) => {
    // Navigate to test history
    await page.click('text=Test History')
    await page.waitForURL('/test-history')
    
    // Verify history table is displayed
    const historyTable = page.locator('table.test-history')
    await expect(historyTable).toBeVisible()
    
    // Verify at least one execution is shown
    const rows = historyTable.locator('tbody tr')
    await expect(rows).toHaveCount({ min: 1 })
    
    // Click on an execution to view details
    await rows.first().click()
    
    // Verify details modal opens
    const detailsModal = page.locator('.execution-details-modal')
    await expect(detailsModal).toBeVisible()
  })
})
```

## Test Data Management

### Test Fixtures
```python
# tests/fixtures/test_data.py
import pytest
from datetime import datetime, timezone

@pytest.fixture
def sample_test_cases():
    """Provide sample test cases for testing."""
    return [
        {
            "id": "test_001",
            "name": "Login Test",
            "description": "Test user login functionality",
            "steps": [
                {"action": "navigate", "target": "/login"},
                {"action": "type", "target": "#email", "value": "user@example.com"},
                {"action": "type", "target": "#password", "value": "password123"},
                {"action": "click", "target": "button[type='submit']"}
            ],
            "expected_results": ["User should be redirected to dashboard"]
        },
        {
            "id": "test_002",
            "name": "Create Test Case",
            "description": "Test creating a new test case",
            "steps": [
                {"action": "navigate", "target": "/test-cases/new"},
                {"action": "type", "target": "#name", "value": "New Test"},
                {"action": "click", "target": "button[type='submit']"}
            ],
            "expected_results": ["Test case should be created successfully"]
        }
    ]

@pytest.fixture
def mock_ai_insights():
    """Provide mock AI insights for testing."""
    return {
        "confidence_score": 0.85,
        "risk_level": "low",
        "recommendations": [
            "Consider adding more assertions",
            "Test data could be more diverse"
        ],
        "patterns_detected": [
            "Standard login flow",
            "Form validation present"
        ]
    }
```

### Factory Pattern for Test Data
```python
# tests/factories/test_case_factory.py
from factory import Factory, Faker, SubFactory, LazyAttribute
from models.test_case import TestCase

class TestCaseFactory(Factory):
    class Meta:
        model = TestCase
    
    id = Faker('uuid4')
    name = Faker('sentence', nb_words=4)
    description = Faker('paragraph')
    steps = LazyAttribute(lambda obj: [
        {
            "action": "navigate",
            "target": Faker('url').generate()
        },
        {
            "action": "click",
            "target": f"#{Faker('word').generate()}"
        }
    ])
    expected_results = LazyAttribute(lambda obj: [
        Faker('sentence').generate()
    ])
    tags = LazyAttribute(lambda obj: [
        Faker('word').generate() for _ in range(3)
    ])

# Usage
test_case = TestCaseFactory.create()
test_cases = TestCaseFactory.create_batch(10)
```

## Continuous Testing

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit -v
        language: system
        pass_filenames: false
        always_run: true
      
      - id: vitest-check
        name: vitest-check
        entry: npm run test:unit
        language: system
        pass_filenames: false
        always_run: true
```

### CI/CD Pipeline Testing
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: pytest tests/unit -v --cov=src --cov-report=xml
      
      - name: Run integration tests
        run: pytest tests/integration -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit
      
      - name: Run component tests
        run: npm run test:component
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
