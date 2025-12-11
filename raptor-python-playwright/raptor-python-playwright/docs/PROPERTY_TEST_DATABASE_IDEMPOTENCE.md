# Property Test: Database Query Idempotence

## Overview

This document describes the property-based test implementation for database query idempotence in the Raptor framework. The test ensures that SELECT queries are truly idempotent - they can be executed multiple times without changing the database state and always return consistent results.

## Property Definition

**Property 4: Database Query Idempotence**

```
For any SELECT query Q and database state S:
  Q(S) = Q(Q(S)) = Q(Q(Q(S))) = ...
  
Where:
- Q is any SELECT query (read operation)
- S is the database state
- Q(S) returns results without modifying S
```

**Validates**: Requirements 4.1 - Database operations must be reliable and consistent

## Test Implementation

### Location
- **File**: `tests/test_database_manager.py`
- **Class**: `TestDatabaseQueryIdempotence`
- **Annotation**: `**Feature: raptor-playwright-python, Property 4: Database Query Idempotence**`

### Test Methods

#### 1. Basic Query Idempotence (`test_query_idempotence`)

Tests that basic SELECT operations return identical results across multiple executions.

**Test Cases**:
- `select_all`: Tests `get_all_records()` method
- `select_by_id`: Tests `get_record_by_id()` method  
- `select_by_name`: Tests parameterized queries with WHERE clauses
- `count_records`: Tests `count_records()` method

**Strategy**:
```python
@given(
    query_type=st.sampled_from(['select_all', 'select_by_id', 'select_by_name', 'count_records']),
    execution_count=st.integers(min_value=1, max_value=10),
    record_id=st.integers(min_value=1, max_value=3),
    record_name=st.sampled_from(['record1', 'record2', 'record3'])
)
@settings(max_examples=50, deadline=5000)
```

**Verification**:
- Executes the same query 1-10 times
- Compares all results for equality
- Ensures database state remains unchanged (record count = 3)

#### 2. Complex Query Idempotence (`test_complex_query_idempotence`)

Tests idempotence of complex SELECT queries with various WHERE conditions.

**Test Cases**:
- Numeric comparisons (`value > ?`, `value < ?`, `value = ?`)
- String pattern matching (`name LIKE ?`)
- Multiple condition combinations
- Various parameter types (integers, strings)

**Strategy**:
```python
@given(
    where_conditions=st.lists(
        st.tuples(
            st.sampled_from(['value > ?', 'value < ?', 'value = ?', 'name LIKE ?']),
            st.one_of(
                st.integers(min_value=50, max_value=350),
                st.text(min_size=1, max_size=10).map(lambda x: f"%{x}%")
            )
        ),
        min_size=1,
        max_size=3
    ),
    execution_count=st.integers(min_value=2, max_value=5)
)
@settings(max_examples=30, deadline=5000)
```

**Verification**:
- Generates random WHERE clauses and parameters
- Executes each query multiple times
- Validates result consistency
- Handles invalid parameter combinations gracefully

#### 3. Concurrent Query Idempotence (`test_concurrent_query_idempotence`)

Ensures that concurrent SELECT queries don't interfere with each other.

**Test Cases**:
- Multiple queries executed concurrently using `asyncio.gather()`
- Different query types in the same batch
- Multiple batches executed sequentially

**Verification**:
- Compares results across concurrent execution batches
- Ensures no race conditions affect query results
- Validates connection pool behavior under concurrent load

#### 4. Metadata Query Idempotence (`test_metadata_query_idempotence`)

Tests idempotence of database metadata queries.

**Test Cases**:
- `table_exists()`: Schema information queries
- `get_all_records()`: Full table scans
- `count_records()`: Aggregate queries

**Strategy**:
```python
@given(
    table_operations=st.lists(
        st.sampled_from(['table_exists', 'get_all_records', 'count_records']),
        min_size=1,
        max_size=5
    ),
    repetitions=st.integers(min_value=2, max_value=4)
)
@settings(max_examples=20, deadline=3000)
```

**Verification**:
- Executes metadata operations multiple times
- Ensures schema queries return consistent results
- Validates that metadata operations don't modify data

## Test Data Setup

The tests use a controlled test database with predictable data:

```python
test_data = [
    {"name": "record1", "value": 100},
    {"name": "record2", "value": 200},
    {"name": "record3", "value": 300},
]
```

**Table Schema**:
```sql
CREATE TABLE idempotence_test (
    id INTEGER PRIMARY KEY,
    name TEXT,
    value INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Running the Tests

### Prerequisites

```bash
pip install pytest pytest-asyncio hypothesis aiosqlite
```

### Execution

```bash
# Run all database property tests
pytest tests/test_database_manager.py::TestDatabaseQueryIdempotence -v

# Run specific idempotence test
pytest tests/test_database_manager.py::TestDatabaseQueryIdempotence::test_query_idempotence -v

# Run with hypothesis statistics
pytest tests/test_database_manager.py::TestDatabaseQueryIdempotence --hypothesis-show-statistics

# Run with verbose output
pytest tests/test_database_manager.py::TestDatabaseQueryIdempotence -vv
```

### Expected Output

```
tests/test_database_manager.py::TestDatabaseQueryIdempotence::test_query_idempotence PASSED
tests/test_database_manager.py::TestDatabaseQueryIdempotence::test_complex_query_idempotence PASSED
tests/test_database_manager.py::TestDatabaseQueryIdempotence::test_concurrent_query_idempotence PASSED
tests/test_database_manager.py::TestDatabaseQueryIdempotence::test_metadata_query_idempotence PASSED
```

## Property Test Configuration

### Hypothesis Settings

```python
@settings(max_examples=50, deadline=5000)
```

- **max_examples**: Runs up to 50 test cases per property
- **deadline**: 5-second timeout per test case
- **Strategies**: Uses controlled input generation for reliable testing

### Input Strategies

- **Query Types**: Predefined set of common query patterns
- **Execution Counts**: 1-10 repetitions to test consistency
- **Parameters**: Realistic data ranges matching test dataset
- **WHERE Conditions**: Common SQL patterns with type-safe parameters

## Assertions and Verification

### Primary Assertions

1. **Result Equality**: All executions of the same query return identical results
2. **State Preservation**: Database state remains unchanged after SELECT queries
3. **Type Consistency**: Result types and structures remain consistent
4. **Concurrent Safety**: Concurrent queries don't interfere with each other

### Error Handling

- **Invalid Queries**: Gracefully handles type mismatches and invalid SQL
- **Connection Issues**: Tests connection pool behavior under stress
- **Timeout Handling**: Ensures tests complete within reasonable time limits

## Benefits

### Comprehensive Coverage
- Tests many more input combinations than manual test cases
- Discovers edge cases that might be missed in traditional testing
- Validates behavior across the entire input space

### Regression Detection
- Automatically catches regressions in query behavior
- Ensures idempotence property is maintained across code changes
- Validates connection pool and transaction handling

### Documentation Value
- Serves as executable specification of idempotence requirements
- Demonstrates expected behavior for different query types
- Provides examples of proper database usage patterns

## Integration with CI/CD

The property tests are designed to run in continuous integration environments:

- **Fast Execution**: Optimized for CI runtime constraints
- **Deterministic**: Uses controlled randomization for reproducible results
- **Resource Efficient**: Uses temporary in-memory databases
- **Clear Reporting**: Provides detailed failure information for debugging

## Troubleshooting

### Common Issues

1. **Test Timeouts**: Increase deadline in `@settings` decorator
2. **Flaky Tests**: Check for proper database cleanup between tests
3. **Memory Issues**: Ensure temporary databases are properly cleaned up
4. **Concurrency Issues**: Verify connection pool configuration

### Debugging Tips

- Use `--hypothesis-show-statistics` to see test case distribution
- Add logging to see which queries are being tested
- Use `@example()` decorator to test specific failing cases
- Check database state before and after test execution

## Dependencies

### Required Packages
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `hypothesis` - Property-based testing
- `aiosqlite` - Async SQLite driver

### Required Implementations
- `DatabaseManager` class (Task 10)
- `ConnectionPool` class (Task 10)
- `RaptorDatabaseError` exception

## Future Enhancements

### Potential Improvements

1. **Transaction Testing**: Add tests for transaction idempotence
2. **Performance Testing**: Measure query performance consistency
3. **Schema Evolution**: Test idempotence across schema changes
4. **Error Recovery**: Test idempotence after connection failures

### Additional Properties

1. **Commutativity**: Test that query order doesn't affect results
2. **Associativity**: Test complex query composition
3. **Monotonicity**: Test that adding data doesn't break existing queries

## References

- **Requirements**: Section 4.1 - Database Support
- **Design**: Property 4 - Database Query Idempotence
- **Implementation**: `tests/test_database_manager.py`
- **Documentation**: `docs/DATABASE_MANAGER_IMPLEMENTATION.md`
