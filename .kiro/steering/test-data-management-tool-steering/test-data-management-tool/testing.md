---
inclusion: manual
---

# Testing Guidelines

## Testing Philosophy

Follow the test pyramid: 70% unit tests, 20% integration tests, 10% E2E tests.

## Python Backend Testing

### Unit Tests with pytest

```python
# tests/unit/services/test_data_generation.py
import pytest
from services.data_generation import DataGenerationService
from models.schema import Schema

@pytest.fixture
def service():
    return DataGenerationService()

@pytest.fixture
def sample_schema():
    return Schema(
        id="test-schema",
        name="Test Schema",
        fields=[
            {"name": "email", "type": "email"},
            {"name": "age", "type": "integer", "min": 18, "max": 100}
        ]
    )

@pytest.mark.asyncio
async def test_generate_dataset(service, sample_schema):
    """Test dataset generation."""
    result = await service.generate_dataset(
        schema=sample_schema,
        count=10
    )
    
    assert len(result.records) == 10
    assert all('@' in record['email'] for record in result.records)
    assert all(18 <= record['age'] <= 100 for record in result.records)
```

### Property-Based Testing

```python
# tests/property/test_masking.py
from hypothesis import given, strategies as st
from services.data_masking import DataMaskingService

@given(
    email=st.emails(),
    masking_char=st.sampled_from(['*', 'X', '#'])
)
def test_email_masking_preserves_format(email, masking_char):
    """Property: Masked emails should preserve @ symbol."""
    service = DataMaskingService()
    masked = service.mask_email(email, masking_char)
    
    assert '@' in masked
    assert len(masked) == len(email)
```

## React Frontend Testing

```javascript
// tests/components/DatasetList.test.tsx
import { render, screen } from '@testing-library/react'
import { DatasetList } from '@/components/DatasetList'

describe('DatasetList', () => {
  it('renders dataset list', () => {
    const datasets = [
      { id: '1', name: 'Test Dataset', recordCount: 100 }
    ]
    
    render(<DatasetList datasets={datasets} />)
    
    expect(screen.getByText('Test Dataset')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
  })
})
```
