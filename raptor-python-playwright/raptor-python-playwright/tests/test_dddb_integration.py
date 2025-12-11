"""
Tests for DDDB Integration Methods

This module tests the DDDB integration methods:
- import_data()
- export_data()
- get_field()
- get_row()
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from raptor.database.database_manager import DatabaseManager
from raptor.core.exceptions import DatabaseException


class TestDDDBIntegration:
    """Test DDDB integration methods."""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Create a mock database manager for testing."""
        with patch('raptor.database.database_manager.pyodbc'):
            db = DatabaseManager(
                server="localhost",
                database="DDFE",
                user="testuser",
                password="password",
                use_pooling=False
            )
            
            # Mock the connection
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            
            db._direct_connection = mock_conn
            db._connected = True
            
            yield db, mock_cursor
    
    def test_import_data_basic(self, mock_db_manager):
        """Test basic import_data functionality."""
        db, mock_cursor = mock_db_manager
        
        # Mock the query result
        mock_cursor.fetchall.return_value = [
            (1, 101, 1, 1, 'testuser', 'password123', 'PASS', None)
        ]
        mock_cursor.description = [
            ('pk_id',), ('test_id',), ('iteration',), ('instance',),
            ('username',), ('password',), ('test_result',), ('err_msg',)
        ]
        
        # Import data
        result = db.import_data(
            table="TestData_Login",
            test_id=101,
            iteration=1,
            instance=1
        )
        
        # Verify result
        assert result['pk_id'] == 1
        assert result['test_id'] == 101
        assert result['username'] == 'testuser'
        assert result['password'] == 'password123'
        
        # Verify SQL was executed
        mock_cursor.execute.assert_called_once()
        sql = mock_cursor.execute.call_args[0][0]
        assert 'SELECT * FROM TestData_Login' in sql
        assert 'test_id = 101' in sql
        assert 'iteration = 1' in sql
        assert 'instance = 1' in sql
    
    def test_import_data_with_additional_filters(self, mock_db_manager):
        """Test import_data with additional filters."""
        db, mock_cursor = mock_db_manager
        
        # Mock the query result
        mock_cursor.fetchall.return_value = [
            (1, 101, 1, 1, 'testuser', 'password123', 'PASS', None, 'staging')
        ]
        mock_cursor.description = [
            ('pk_id',), ('test_id',), ('iteration',), ('instance',),
            ('username',), ('password',), ('test_result',), ('err_msg',), ('environment',)
        ]
        
        # Import data with additional filters
        result = db.import_data(
            table="TestData_Login",
            test_id=101,
            iteration=1,
            instance=1,
            additional_filters={'environment': 'staging'}
        )
        
        # Verify result
        assert result['environment'] == 'staging'
        
        # Verify SQL includes additional filter
        sql = mock_cursor.execute.call_args[0][0]
        assert "environment = 'staging'" in sql
    
    def test_import_data_not_found(self, mock_db_manager):
        """Test import_data when no data is found."""
        db, mock_cursor = mock_db_manager
        
        # Mock empty result
        mock_cursor.fetchall.return_value = []
        
        # Should raise DatabaseException
        with pytest.raises(DatabaseException) as exc_info:
            db.import_data(
                table="TestData_Login",
                test_id=999,
                iteration=1,
                instance=1
            )
        
        assert "No data found" in str(exc_info.value)
    
    def test_export_data_basic(self, mock_db_manager):
        """Test basic export_data functionality."""
        db, mock_cursor = mock_db_manager
        
        # Mock successful update
        mock_cursor.rowcount = 1
        
        # Export data
        rows_affected = db.export_data(
            table="TestData_Login",
            pk_id=12345,
            field="test_result",
            value="PASS"
        )
        
        # Verify result
        assert rows_affected == 1
        
        # Verify SQL was executed with parameters
        mock_cursor.execute.assert_called_once()
        sql, params = mock_cursor.execute.call_args[0]
        assert 'UPDATE TestData_Login' in sql
        assert 'SET test_result = ?' in sql
        assert 'WHERE pk_id = ?' in sql
        assert params == ("PASS", 12345)
    
    def test_export_data_no_rows_affected(self, mock_db_manager):
        """Test export_data when no rows are affected."""
        db, mock_cursor = mock_db_manager
        
        # Mock no rows affected
        mock_cursor.rowcount = 0
        
        # Export data
        rows_affected = db.export_data(
            table="TestData_Login",
            pk_id=99999,
            field="test_result",
            value="PASS"
        )
        
        # Should return 0 but not raise exception
        assert rows_affected == 0
    
    def test_get_field_basic(self, mock_db_manager):
        """Test basic get_field functionality."""
        db, mock_cursor = mock_db_manager
        
        # Mock the query result
        mock_cursor.fetchall.return_value = [('testuser',)]
        mock_cursor.description = [('username',)]
        
        # Get field value
        value = db.get_field(
            table="TestData_Login",
            field="username",
            pk_id=12345
        )
        
        # Verify result
        assert value == 'testuser'
        
        # Verify SQL was executed
        sql, params = mock_cursor.execute.call_args[0]
        assert 'SELECT username FROM TestData_Login' in sql
        assert 'WHERE pk_id = ?' in sql
        assert params == (12345,)
    
    def test_get_field_not_found(self, mock_db_manager):
        """Test get_field when row is not found."""
        db, mock_cursor = mock_db_manager
        
        # Mock empty result
        mock_cursor.fetchall.return_value = []
        
        # Should raise DatabaseException
        with pytest.raises(DatabaseException) as exc_info:
            db.get_field(
                table="TestData_Login",
                field="username",
                pk_id=99999
            )
        
        assert "No row found" in str(exc_info.value)
    
    def test_get_row_basic(self, mock_db_manager):
        """Test basic get_row functionality."""
        db, mock_cursor = mock_db_manager
        
        # Mock the query result
        mock_cursor.fetchall.return_value = [
            (12345, 101, 1, 1, 'testuser', 'password123', 'PASS', None)
        ]
        mock_cursor.description = [
            ('pk_id',), ('test_id',), ('iteration',), ('instance',),
            ('username',), ('password',), ('test_result',), ('err_msg',)
        ]
        
        # Get row
        row = db.get_row(
            table="TestData_Login",
            pk_id=12345
        )
        
        # Verify result
        assert row['pk_id'] == 12345
        assert row['test_id'] == 101
        assert row['username'] == 'testuser'
        assert row['password'] == 'password123'
        assert row['test_result'] == 'PASS'
        
        # Verify SQL was executed
        sql, params = mock_cursor.execute.call_args[0]
        assert 'SELECT * FROM TestData_Login' in sql
        assert 'WHERE pk_id = ?' in sql
        assert params == (12345,)
    
    def test_get_row_not_found(self, mock_db_manager):
        """Test get_row when row is not found."""
        db, mock_cursor = mock_db_manager
        
        # Mock empty result
        mock_cursor.fetchall.return_value = []
        
        # Should raise DatabaseException
        with pytest.raises(DatabaseException) as exc_info:
            db.get_row(
                table="TestData_Login",
                pk_id=99999
            )
        
        assert "No row found" in str(exc_info.value)
    
    def test_complete_workflow(self, mock_db_manager):
        """Test complete DDDB workflow: import -> export -> get_field."""
        db, mock_cursor = mock_db_manager
        
        # Step 1: Import data
        mock_cursor.fetchall.return_value = [
            (12345, 101, 1, 1, 'testuser', 'password123', None, None)
        ]
        mock_cursor.description = [
            ('pk_id',), ('test_id',), ('iteration',), ('instance',),
            ('username',), ('password',), ('test_result',), ('err_msg',)
        ]
        
        data = db.import_data(
            table="TestData_Login",
            test_id=101,
            iteration=1,
            instance=1
        )
        
        assert data['pk_id'] == 12345
        assert data['username'] == 'testuser'
        
        # Step 2: Export result
        mock_cursor.rowcount = 1
        rows = db.export_data(
            table="TestData_Login",
            pk_id=data['pk_id'],
            field="test_result",
            value="PASS"
        )
        
        assert rows == 1
        
        # Step 3: Verify export
        mock_cursor.fetchall.return_value = [('PASS',)]
        mock_cursor.description = [('test_result',)]
        
        result = db.get_field(
            table="TestData_Login",
            field="test_result",
            pk_id=data['pk_id']
        )
        
        assert result == 'PASS'
    
    def test_multiple_iterations(self, mock_db_manager):
        """Test importing data for multiple iterations."""
        db, mock_cursor = mock_db_manager
        
        # Test 3 iterations
        for iteration in range(1, 4):
            # Mock different data for each iteration
            mock_cursor.fetchall.return_value = [
                (iteration, 101, iteration, 1, f'user{iteration}', f'pass{iteration}', None, None)
            ]
            mock_cursor.description = [
                ('pk_id',), ('test_id',), ('iteration',), ('instance',),
                ('username',), ('password',), ('test_result',), ('err_msg',)
            ]
            
            data = db.import_data(
                table="TestData_Login",
                test_id=101,
                iteration=iteration,
                instance=1
            )
            
            assert data['iteration'] == iteration
            assert data['username'] == f'user{iteration}'
            assert data['password'] == f'pass{iteration}'
    
    def test_multiple_instances(self, mock_db_manager):
        """Test importing data for multiple instances."""
        db, mock_cursor = mock_db_manager
        
        # Test 3 instances
        for instance in range(1, 4):
            # Mock different data for each instance
            mock_cursor.fetchall.return_value = [
                (instance, 101, 1, instance, f'user{instance}', f'pass{instance}', None, None)
            ]
            mock_cursor.description = [
                ('pk_id',), ('test_id',), ('iteration',), ('instance',),
                ('username',), ('password',), ('test_result',), ('err_msg',)
            ]
            
            data = db.import_data(
                table="TestData_Login",
                test_id=101,
                iteration=1,
                instance=instance
            )
            
            assert data['instance'] == instance
            assert data['username'] == f'user{instance}'
            assert data['password'] == f'pass{instance}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
