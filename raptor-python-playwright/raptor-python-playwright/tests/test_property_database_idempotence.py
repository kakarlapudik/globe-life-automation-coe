"""
Property-Based Test: Database Query Idempotence

**Feature: raptor-playwright-python, Property 4: Database Query Idempotence**
**Validates: Requirements 4.1**

This test verifies that database SELECT queries are truly idempotent - they can be 
executed multiple times without changing the database state and always return 
consistent results.

Property Statement:
    For any database query with the same parameters, executing it multiple times 
    should return the same results (assuming no data changes between executions).
"""

import pytest
import tempfile
import os
import sqlite3
from hypothesis import given, strategies as st, settings
from typing import List, Dict, Any


class TestDatabaseQueryIdempotence:
    """
    Property-based tests for database query idempotence.
    
    These tests verify that SELECT queries maintain idempotence - running the same
    query multiple times produces identical results without modifying database state.
    """
    
    @pytest.fixture(scope="class")
    def test_db_connection(self):
        """
        Create a test database connection with SQLite.
        
        Note: Using SQLite for testing as it doesn't require external database setup.
        The idempotence property should hold for any SQL database including SQL Server.
        """
        # Create temporary database file
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db_path = temp_db.name
        temp_db.close()
        
        # Create SQLite connection
        conn = sqlite3.connect(temp_db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # Create test table with sample data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT,
                age INTEGER,
                active INTEGER DEFAULT 1
            )
        """)
        
        # Insert test data
        test_users = [
            (1, 'alice', 'alice@example.com', 25, 1),
            (2, 'bob', 'bob@example.com', 30, 1),
            (3, 'charlie', 'charlie@example.com', 35, 0),
            (4, 'diana', 'diana@example.com', 28, 1),
            (5, 'eve', 'eve@example.com', 32, 1),
        ]
        
        for user in test_users:
            cursor.execute(
                "INSERT INTO test_users (user_id, username, email, age, active) VALUES (?, ?, ?, ?, ?)",
                user
            )
        
        conn.commit()
        cursor.close()
        
        yield conn
        
        # Cleanup
        conn.close()
        if os.path.exists(temp_db_path):
            try:
                os.unlink(temp_db_path)
            except:
                pass
    
    @given(
        execution_count=st.integers(min_value=2, max_value=10)
    )
    @settings(max_examples=20, deadline=5000)
    def test_simple_select_idempotence(self, test_db_connection, execution_count):
        """
        Property: Simple SELECT queries should be idempotent.
        
        Running the same SELECT query multiple times should always return
        the same results without modifying the database.
        
        Args:
            test_db_connection: Database connection fixture with test data
            execution_count: Number of times to execute the query
        """
        conn = test_db_connection
        results_list = []
        
        # Execute the same query multiple times
        for i in range(execution_count):
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_users ORDER BY user_id")
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            results_list.append(results)
        
        # Verify all results are identical
        first_result = results_list[0]
        for i, result in enumerate(results_list[1:], start=1):
            assert len(result) == len(first_result), (
                f"Execution {i+1} returned different number of rows: "
                f"{len(result)} vs {len(first_result)}"
            )
            
            for j, (first_row, current_row) in enumerate(zip(first_result, result)):
                assert first_row == current_row, (
                    f"Execution {i+1}, row {j} differs from first execution"
                )
    
    @given(
        user_id=st.integers(min_value=1, max_value=5),
        execution_count=st.integers(min_value=2, max_value=8)
    )
    @settings(max_examples=30, deadline=5000)
    def test_parameterized_query_idempotence(self, test_db_connection, user_id, execution_count):
        """
        Property: Parameterized SELECT queries should be idempotent.
        
        Running the same parameterized query with the same parameters multiple
        times should always return identical results.
        
        Args:
            test_db_connection: Database connection fixture with test data
            user_id: User ID parameter for the query
            execution_count: Number of times to execute the query
        """
        conn = test_db_connection
        results_list = []
        
        # Execute the same parameterized query multiple times
        for i in range(execution_count):
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_users WHERE user_id = ?", (user_id,))
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            results_list.append(results)
        
        # Verify all results are identical
        first_result = results_list[0]
        for i, result in enumerate(results_list[1:], start=1):
            assert result == first_result, (
                f"Execution {i+1} returned different results for user_id={user_id}"
            )
    
    @given(
        min_age=st.integers(min_value=20, max_value=35),
        active_status=st.integers(min_value=0, max_value=1),
        execution_count=st.integers(min_value=2, max_value=6)
    )
    @settings(max_examples=25, deadline=5000)
    def test_complex_where_clause_idempotence(self, test_db_connection, min_age, active_status, execution_count):
        """
        Property: Complex WHERE clause queries should be idempotent.
        
        Queries with multiple conditions should return consistent results
        across multiple executions.
        
        Args:
            test_db_connection: Database connection fixture with test data
            min_age: Minimum age filter
            active_status: Active status filter (0 or 1)
            execution_count: Number of times to execute the query
        """
        conn = test_db_connection
        results_list = []
        
        # Execute complex query multiple times
        for i in range(execution_count):
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM test_users WHERE age >= ? AND active = ? ORDER BY username",
                (min_age, active_status)
            )
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            results_list.append(results)
        
        # Verify all results are identical
        first_result = results_list[0]
        for i, result in enumerate(results_list[1:], start=1):
            assert result == first_result, (
                f"Execution {i+1} returned different results for "
                f"age>={min_age}, active={active_status}"
            )
    
    @given(
        execution_count=st.integers(min_value=2, max_value=8)
    )
    @settings(max_examples=15, deadline=5000)
    def test_aggregate_query_idempotence(self, test_db_connection, execution_count):
        """
        Property: Aggregate queries (COUNT, SUM, AVG) should be idempotent.
        
        Aggregate functions should return consistent results across
        multiple executions.
        
        Args:
            test_db_connection: Database connection fixture with test data
            execution_count: Number of times to execute the query
        """
        conn = test_db_connection
        results_list = []
        
        # Execute aggregate query multiple times
        for i in range(execution_count):
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as total_users, AVG(age) as avg_age, SUM(active) as active_count FROM test_users"
            )
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            results_list.append(results)
        
        # Verify all results are identical
        first_result = results_list[0]
        for i, result in enumerate(results_list[1:], start=1):
            assert result == first_result, (
                f"Execution {i+1} returned different aggregate results"
            )
            
            # Verify specific aggregate values
            assert result[0]['total_users'] == first_result[0]['total_users']
            assert result[0]['avg_age'] == first_result[0]['avg_age']
            assert result[0]['active_count'] == first_result[0]['active_count']
    
    def test_query_does_not_modify_database(self, test_db_connection):
        """
        Property: SELECT queries should not modify database state.
        
        After executing multiple SELECT queries, the database should
        contain the same data as before.
        """
        conn = test_db_connection
        
        # Get initial row count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM test_users")
        initial_count = cursor.fetchone()['count']
        cursor.close()
        
        # Execute various SELECT queries
        queries = [
            "SELECT * FROM test_users",
            "SELECT * FROM test_users WHERE active = 1",
            "SELECT username, email FROM test_users",
            "SELECT AVG(age) FROM test_users",
            "SELECT * FROM test_users WHERE age > 25 ORDER BY username"
        ]
        
        for query in queries:
            cursor = conn.cursor()
            cursor.execute(query)
            cursor.fetchall()
            cursor.close()
        
        # Verify row count hasn't changed
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM test_users")
        final_count = cursor.fetchone()['count']
        cursor.close()
        
        assert final_count == initial_count, (
            f"Database was modified by SELECT queries: "
            f"initial count={initial_count}, final count={final_count}"
        )
    
    @given(
        query_sequence=st.lists(
            st.sampled_from([
                "SELECT * FROM test_users",
                "SELECT * FROM test_users WHERE active = 1",
                "SELECT username, email FROM test_users",
                "SELECT COUNT(*) as count FROM test_users",
                "SELECT * FROM test_users ORDER BY age DESC"
            ]),
            min_size=3,
            max_size=10
        )
    )
    @settings(max_examples=20, deadline=5000)
    def test_query_sequence_idempotence(self, test_db_connection, query_sequence):
        """
        Property: A sequence of SELECT queries should be idempotent.
        
        Executing the same sequence of queries multiple times should
        produce identical results for each query in the sequence.
        
        Args:
            test_db_connection: Database connection fixture with test data
            query_sequence: List of queries to execute in sequence
        """
        conn = test_db_connection
        
        # Execute the query sequence twice
        first_run_results = []
        for query in query_sequence:
            cursor = conn.cursor()
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            first_run_results.append(results)
        
        second_run_results = []
        for query in query_sequence:
            cursor = conn.cursor()
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            second_run_results.append(results)
        
        # Verify both runs produced identical results
        assert len(first_run_results) == len(second_run_results)
        
        for i, (first_result, second_result) in enumerate(zip(first_run_results, second_run_results)):
            assert first_result == second_result, (
                f"Query {i} in sequence produced different results on second execution: "
                f"Query: {query_sequence[i]}"
            )


def test_property_coverage():
    """
    Verify that this test file covers Property 4: Database Query Idempotence.
    
    This is a meta-test to ensure the property is properly documented and tested.
    """
    # Verify property is documented in module docstring
    assert "Property 4: Database Query Idempotence" in __doc__
    assert "Validates: Requirements 4.1" in __doc__
    
    # Verify test class exists
    assert TestDatabaseQueryIdempotence is not None
    
    # Verify key test methods exist
    test_methods = [
        'test_simple_select_idempotence',
        'test_parameterized_query_idempotence',
        'test_complex_where_clause_idempotence',
        'test_aggregate_query_idempotence',
        'test_query_does_not_modify_database',
        'test_query_sequence_idempotence'
    ]
    
    for method_name in test_methods:
        assert hasattr(TestDatabaseQueryIdempotence, method_name), (
            f"Test method {method_name} not found"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
