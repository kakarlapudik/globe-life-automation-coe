"""
Tests for Data-Driven Test Support

This module tests the data-driven testing utilities including:
- Loading test data from DDDB
- pytest parametrization helpers
- Iteration-based test execution
- Instance-based test execution

Requirements: 4.2, 12.1
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Dict, Any

from raptor.utils.data_driven import (
    TestDataRow,
    TestDataSet,
    DataDrivenTestLoader,
    parametrize_from_dddb,
    parametrize_iterations,
    parametrize_instances,
    load_test_data_for_fixture,
    get_test_data_params,
    export_test_result,
    filter_test_data,
    merge_test_data
)
from raptor.database.database_manager import DatabaseManager
from raptor.core.exceptions import DatabaseException


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def mock_database():
    """Create a mock DatabaseManager for testing."""
    db = Mock(spec=DatabaseManager)
    return db


@pytest.fixture
def sample_db_results():
    """Sample database query results."""
    return [
        {
            'pk_id': 1,
            'test_id': 101,
            'iteration': 1,
            'instance': 1,
            'fk_id': None,
            'action': 'login',
            'err_msg': None,
            'username': 'user1',
            'password': 'pass1',
            'expected_result': 'success'
        },
        {
            'pk_id': 2,
            'test_id': 101,
            'iteration': 1,
            'instance': 2,
            'fk_id': None,
            'action': 'login',
            'err_msg': None,
            'username': 'user2',
            'password': 'pass2',
            'expected_result': 'success'
        },
        {
            'pk_id': 3,
            'test_id': 101,
            'iteration': 2,
            'instance': 1,
            'fk_id': None,
            'action': 'login',
            'err_msg': 'Invalid credentials',
            'username': 'invalid',
            'password': 'wrong',
            'expected_result': 'failure'
        }
    ]


@pytest.fixture
def sample_test_data_set(sample_db_results):
    """Create a sample TestDataSet."""
    rows = []
    for result in sample_db_results:
        row = TestDataRow(
            pk_id=result['pk_id'],
            test_id=result['test_id'],
            iteration=result['iteration'],
            instance=result['instance'],
            fk_id=result.get('fk_id'),
            action=result.get('action'),
            err_msg=result.get('err_msg')
        )
        row.data = result
        rows.append(row)
    
    return TestDataSet(
        test_id=101,
        table_name='TestData_Login',
        rows=rows,
        total_iterations=2,
        total_instances=2
    )


# ============================================================================
# TestDataRow Tests
# ============================================================================

def test_test_data_row_creation():
    """Test creating a TestDataRow."""
    row = TestDataRow(
        pk_id=1,
        test_id=101,
        iteration=1,
        instance=1,
        action='login'
    )
    
    assert row.pk_id == 1
    assert row.test_id == 101
    assert row.iteration == 1
    assert row.instance == 1
    assert row.action == 'login'


def test_test_data_row_dict_access():
    """Test dictionary-style access to TestDataRow."""
    row = TestDataRow(
        pk_id=1,
        test_id=101,
        iteration=1,
        instance=1
    )
    row.data = {'username': 'testuser', 'password': 'testpass'}
    
    # Access standard fields
    assert row['pk_id'] == 1
    assert row['test_id'] == 101
    
    # Access data fields
    assert row['username'] == 'testuser'
    assert row['password'] == 'testpass'


def test_test_data_row_get_method():
    """Test get method with default values."""
    row = TestDataRow(
        pk_id=1,
        test_id=101,
        iteration=1,
        instance=1
    )
    row.data = {'username': 'testuser'}
    
    # Existing field
    assert row.get('username') == 'testuser'
    
    # Non-existing field with default
    assert row.get('email', 'default@example.com') == 'default@example.com'
    
    # Non-existing field without default
    assert row.get('phone') is None


def test_test_data_row_repr():
    """Test string representation of TestDataRow."""
    row = TestDataRow(
        pk_id=1,
        test_id=101,
        iteration=2,
        instance=3
    )
    
    repr_str = repr(row)
    assert 'test_id=101' in repr_str
    assert 'iter=2' in repr_str
    assert 'inst=3' in repr_str


# ============================================================================
# TestDataSet Tests
# ============================================================================

def test_test_data_set_creation(sample_test_data_set):
    """Test creating a TestDataSet."""
    assert sample_test_data_set.test_id == 101
    assert sample_test_data_set.table_name == 'TestData_Login'
    assert len(sample_test_data_set.rows) == 3
    assert sample_test_data_set.total_iterations == 2
    assert sample_test_data_set.total_instances == 2


def test_test_data_set_get_by_iteration(sample_test_data_set):
    """Test getting rows by iteration."""
    # Get iteration 1
    iter1_rows = sample_test_data_set.get_by_iteration(1)
    assert len(iter1_rows) == 2
    assert all(row.iteration == 1 for row in iter1_rows)
    
    # Get iteration 2
    iter2_rows = sample_test_data_set.get_by_iteration(2)
    assert len(iter2_rows) == 1
    assert iter2_rows[0].iteration == 2


def test_test_data_set_get_by_instance(sample_test_data_set):
    """Test getting a specific row by iteration and instance."""
    # Get existing row
    row = sample_test_data_set.get_by_instance(1, 1)
    assert row is not None
    assert row.iteration == 1
    assert row.instance == 1
    assert row['username'] == 'user1'
    
    # Get non-existing row
    row = sample_test_data_set.get_by_instance(99, 99)
    assert row is None


def test_test_data_set_get_iterations(sample_test_data_set):
    """Test getting list of iterations."""
    iterations = sample_test_data_set.get_iterations()
    assert iterations == [1, 2]


def test_test_data_set_get_instances(sample_test_data_set):
    """Test getting list of instances for an iteration."""
    # Iteration 1 has 2 instances
    instances = sample_test_data_set.get_instances(1)
    assert instances == [1, 2]
    
    # Iteration 2 has 1 instance
    instances = sample_test_data_set.get_instances(2)
    assert instances == [1]


# ============================================================================
# DataDrivenTestLoader Tests
# ============================================================================

def test_loader_initialization(mock_database):
    """Test DataDrivenTestLoader initialization."""
    loader = DataDrivenTestLoader(mock_database)
    assert loader.database == mock_database


def test_load_test_data_success(mock_database, sample_db_results):
    """Test loading test data successfully."""
    mock_database.execute_query.return_value = sample_db_results
    
    loader = DataDrivenTestLoader(mock_database)
    data_set = loader.load_test_data('TestData_Login', test_id=101)
    
    assert data_set.test_id == 101
    assert data_set.table_name == 'TestData_Login'
    assert len(data_set.rows) == 3
    assert data_set.total_iterations == 2
    assert data_set.total_instances == 2
    
    # Verify query was called
    mock_database.execute_query.assert_called_once()
    call_args = mock_database.execute_query.call_args[0][0]
    assert 'test_id = 101' in call_args


def test_load_test_data_with_iterations(mock_database, sample_db_results):
    """Test loading test data with specific iterations."""
    # Filter results to only iteration 1
    filtered_results = [r for r in sample_db_results if r['iteration'] == 1]
    mock_database.execute_query.return_value = filtered_results
    
    loader = DataDrivenTestLoader(mock_database)
    data_set = loader.load_test_data('TestData_Login', test_id=101, iterations=[1])
    
    assert len(data_set.rows) == 2
    assert all(row.iteration == 1 for row in data_set.rows)
    
    # Verify query includes iteration filter
    call_args = mock_database.execute_query.call_args[0][0]
    assert 'iteration IN (1)' in call_args


def test_load_test_data_with_instances(mock_database, sample_db_results):
    """Test loading test data with specific instances."""
    # Filter results to only instance 1
    filtered_results = [r for r in sample_db_results if r['instance'] == 1]
    mock_database.execute_query.return_value = filtered_results
    
    loader = DataDrivenTestLoader(mock_database)
    data_set = loader.load_test_data('TestData_Login', test_id=101, instances=[1])
    
    assert len(data_set.rows) == 2
    assert all(row.instance == 1 for row in data_set.rows)
    
    # Verify query includes instance filter
    call_args = mock_database.execute_query.call_args[0][0]
    assert 'instance IN (1)' in call_args


def test_load_test_data_no_results(mock_database):
    """Test loading test data when no results found."""
    mock_database.execute_query.return_value = []
    
    loader = DataDrivenTestLoader(mock_database)
    data_set = loader.load_test_data('TestData_Login', test_id=999)
    
    assert data_set.test_id == 999
    assert len(data_set.rows) == 0
    assert data_set.total_iterations == 0


def test_load_by_iteration(mock_database, sample_db_results):
    """Test loading data by specific iteration."""
    filtered_results = [r for r in sample_db_results if r['iteration'] == 1]
    mock_database.execute_query.return_value = filtered_results
    
    loader = DataDrivenTestLoader(mock_database)
    rows = loader.load_by_iteration('TestData_Login', test_id=101, iteration=1)
    
    assert len(rows) == 2
    assert all(row.iteration == 1 for row in rows)


def test_load_by_instance(mock_database):
    """Test loading data by specific instance."""
    mock_database.import_data.return_value = {
        'pk_id': 1,
        'test_id': 101,
        'iteration': 1,
        'instance': 1,
        'username': 'testuser',
        'password': 'testpass'
    }
    
    loader = DataDrivenTestLoader(mock_database)
    row = loader.load_by_instance('TestData_Login', test_id=101, iteration=1, instance=1)
    
    assert row is not None
    assert row.pk_id == 1
    assert row.test_id == 101
    assert row.iteration == 1
    assert row.instance == 1
    assert row['username'] == 'testuser'


def test_load_by_instance_not_found(mock_database):
    """Test loading data by instance when not found."""
    mock_database.import_data.side_effect = DatabaseException(
        operation="import_data",
        database_error=Exception("No data found")
    )
    
    loader = DataDrivenTestLoader(mock_database)
    row = loader.load_by_instance('TestData_Login', test_id=999, iteration=1, instance=1)
    
    assert row is None


# ============================================================================
# Helper Function Tests
# ============================================================================

def test_load_test_data_for_fixture(mock_database, sample_db_results):
    """Test load_test_data_for_fixture helper."""
    mock_database.execute_query.return_value = sample_db_results
    
    data_set = load_test_data_for_fixture(
        mock_database,
        'TestData_Login',
        test_id=101
    )
    
    assert isinstance(data_set, TestDataSet)
    assert len(data_set.rows) == 3


def test_get_test_data_params(mock_database, sample_db_results):
    """Test get_test_data_params helper."""
    mock_database.execute_query.return_value = sample_db_results
    
    rows, test_ids = get_test_data_params(
        mock_database,
        'TestData_Login',
        test_id=101
    )
    
    assert len(rows) == 3
    assert len(test_ids) == 3
    assert test_ids[0] == 'iter1_inst1'
    assert test_ids[1] == 'iter1_inst2'
    assert test_ids[2] == 'iter2_inst1'


def test_export_test_result(mock_database):
    """Test exporting test result."""
    test_data = TestDataRow(
        pk_id=1,
        test_id=101,
        iteration=1,
        instance=1
    )
    test_data.data = {'_table_name': 'TestData_Login'}
    
    export_test_result(mock_database, test_data, 'PASS')
    
    # Verify export_data was called
    assert mock_database.export_data.call_count == 1
    call_args = mock_database.export_data.call_args
    assert call_args[1]['pk_id'] == 1
    assert call_args[1]['field'] == 'test_result'
    assert call_args[1]['value'] == 'PASS'


def test_export_test_result_with_error(mock_database):
    """Test exporting test result with error message."""
    test_data = TestDataRow(
        pk_id=1,
        test_id=101,
        iteration=1,
        instance=1
    )
    test_data.data = {'_table_name': 'TestData_Login'}
    
    export_test_result(mock_database, test_data, 'FAIL', 'Login failed')
    
    # Verify export_data was called twice (result + error message)
    assert mock_database.export_data.call_count == 2


def test_filter_test_data(sample_test_data_set):
    """Test filtering test data."""
    # Filter for iteration 1 only
    filtered = filter_test_data(
        sample_test_data_set,
        lambda row: row.iteration == 1
    )
    
    assert len(filtered.rows) == 2
    assert all(row.iteration == 1 for row in filtered.rows)
    assert filtered.total_iterations == 1


def test_merge_test_data(sample_db_results):
    """Test merging test data sets."""
    # Create two data sets
    rows1 = [TestDataRow(
        pk_id=r['pk_id'],
        test_id=r['test_id'],
        iteration=r['iteration'],
        instance=r['instance']
    ) for r in sample_db_results[:2]]
    
    rows2 = [TestDataRow(
        pk_id=r['pk_id'],
        test_id=r['test_id'],
        iteration=r['iteration'],
        instance=r['instance']
    ) for r in sample_db_results[2:]]
    
    data_set1 = TestDataSet(test_id=101, table_name='TestData_Login', rows=rows1)
    data_set2 = TestDataSet(test_id=101, table_name='TestData_Login', rows=rows2)
    
    merged = merge_test_data(data_set1, data_set2)
    
    assert len(merged.rows) == 3
    assert merged.test_id == 101


def test_merge_test_data_empty():
    """Test merging with no data sets raises error."""
    with pytest.raises(ValueError, match="At least one TestDataSet required"):
        merge_test_data()


# ============================================================================
# Integration Tests (require actual database)
# ============================================================================

@pytest.mark.database
def test_integration_load_test_data(database):
    """Integration test for loading test data from actual database."""
    if database is None:
        pytest.skip("Database not configured")
    
    # This test would require actual test data in the database
    # Skipping for now as it requires database setup
    pytest.skip("Requires actual database with test data")


@pytest.mark.database
def test_integration_parametrize_from_dddb(database):
    """Integration test for parametrize_from_dddb decorator."""
    if database is None:
        pytest.skip("Database not configured")
    
    # This test would require actual test data in the database
    pytest.skip("Requires actual database with test data")


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_empty_test_data_set():
    """Test handling empty test data set."""
    data_set = TestDataSet(
        test_id=101,
        table_name='TestData_Empty',
        rows=[],
        total_iterations=0,
        total_instances=0
    )
    
    assert len(data_set.rows) == 0
    assert data_set.get_iterations() == []
    assert data_set.get_by_iteration(1) == []
    assert data_set.get_by_instance(1, 1) is None


def test_test_data_row_with_none_values():
    """Test TestDataRow with None values."""
    row = TestDataRow(
        pk_id=1,
        test_id=101,
        iteration=1,
        instance=1,
        fk_id=None,
        action=None,
        err_msg=None
    )
    
    assert row.fk_id is None
    assert row.action is None
    assert row.err_msg is None


def test_load_test_data_database_error(mock_database):
    """Test handling database errors during load."""
    mock_database.execute_query.side_effect = Exception("Database connection failed")
    
    loader = DataDrivenTestLoader(mock_database)
    
    with pytest.raises(DatabaseException):
        loader.load_test_data('TestData_Login', test_id=101)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
