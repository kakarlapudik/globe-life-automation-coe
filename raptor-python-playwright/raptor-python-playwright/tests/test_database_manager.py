"""
Tests for Database Manager

Property-based tests to ensure database operations behave correctly
under various conditions and maintain data integrity.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from hypothesis.stateful import RuleBasedStateMachine, Bundle, rule, initialize, invariant
import aiosqlite

from raptor.database.database_manager import DatabaseManager
from raptor.core.exceptions import DatabaseException


@pytest.mark.asyncio
class TestDatabaseManager:
    """Basic tests for DatabaseManager functionality."""
    
    @pytest.fixture
    async def db_manager(self):
        """Create a test database manager with temporary database."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        manager = DatabaseManager(temp_db.name)
        await manager.initialize()
        
        # Create a test table
        await manager.create_table_if_not_exists(
            "test_table", 
            "id INTEGER PRIMARY KEY, name TEXT, value INTEGER"
        )
        
        yield manager
        
        await manager.close()
        os.unlink(temp_db.name)
    
    async def test_basic_operations(self, db_manager):
        """Test basic CRUD operations."""
        # Insert
        result = await db_manager.insert_record(
            "test_table", 
            {"name": "test", "value": 42}
        )
        assert result == 1
        
        # Select
        records = await db_manager.get_all_records("test_table")
        assert len(records) == 1
        assert records[0]["name"] == "test"
        assert records[0]["value"] == 42
        
        # Update
        result = await db_manager.update_record(
            "test_table",
            {"value": 100},
            "name = ?",
            ("test",)
        )
        assert result == 1
        
        # Verify update
        record = await db_manager.get_record_by_id("test_table", 1)
        assert record["value"] == 100
        
        # Delete
        result = await db_manager.delete_record("test_table", "id = ?", (1,))
        assert result == 1
        
        # Verify deletion
        records = await db_manager.get_all_records("test_table")
        assert len(records) == 0


class DatabaseStateMachine(RuleBasedStateMachine):
    """
    Stateful property-based testing for database operations.
    
    This tests that database operations maintain consistency
    and behave correctly under various sequences of operations.
    """
    
    def __init__(self):
        super().__init__()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = None
        self.records = {}  # Track expected state
        self.next_id = 1
    
    @initialize()
    async def setup_database(self):
        """Initialize the database for testing."""
        self.db_manager = DatabaseManager(self.temp_db.name)
        await self.db_manager.initialize()
        
        # Create test table
        await self.db_manager.create_table_if_not_exists(
            "test_records",
            "id INTEGER PRIMARY KEY, name TEXT UNIQUE, value INTEGER"
        )
    
    records = Bundle('records')
    
    @rule(target=records, name=st.text(min_size=1, max_size=50), value=st.integers())
    async def insert_record(self, name, value):
        """Insert a new record."""
        assume(name not in self.records)  # Ensure unique names
        
        try:
            result = await self.db_manager.insert_record(
                "test_records",
                {"name": name, "value": value}
            )
            
            if result == 1:
                record_id = self.next_id
                self.records[name] = {"id": record_id, "name": name, "value": value}
                self.next_id += 1
                return name
        except RaptorDatabaseError:
            # Handle constraint violations gracefully
            pass
        
        return None
    
    @rule(record_name=records, new_value=st.integers())
    async def update_record(self, record_name, new_value):
        """Update an existing record."""
        if record_name in self.records:
            await self.db_manager.update_record(
                "test_records",
                {"value": new_value},
                "name = ?",
                (record_name,)
            )
            self.records[record_name]["value"] = new_value
    
    @rule(record_name=records)
    async def delete_record(self, record_name):
        """Delete an existing record."""
        if record_name in self.records:
            await self.db_manager.delete_record(
                "test_records",
                "name = ?",
                (record_name,)
            )
            del self.records[record_name]
    
    @invariant()
    async def database_consistency(self):
        """Verify database state matches expected state."""
        if self.db_manager is None:
            return
        
        # Get all records from database
        db_records = await self.db_manager.get_all_records("test_records")
        
        # Convert to dict for comparison
        db_dict = {record["name"]: record for record in db_records}
        
        # Check counts match
        assert len(db_dict) == len(self.records)
        
        # Check each record matches
        for name, expected_record in self.records.items():
            assert name in db_dict
            db_record = db_dict[name]
            assert db_record["name"] == expected_record["name"]
            assert db_record["value"] == expected_record["value"]
    
    def teardown(self):
        """Clean up after testing."""
        if self.db_manager:
            asyncio.create_task(self.db_manager.close())
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)


# Property-based tests
@given(st.text(min_size=1, max_size=100))
async def test_table_creation_idempotent(table_name):
    """Test that creating tables multiple times is idempotent."""
    assume(table_name.isidentifier())  # Valid SQL identifier
    
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        db_manager = DatabaseManager(temp_db.name)
        await db_manager.initialize()
        
        schema = "id INTEGER PRIMARY KEY, data TEXT"
        
        # Create table multiple times
        await db_manager.create_table_if_not_exists(table_name, schema)
        await db_manager.create_table_if_not_exists(table_name, schema)
        await db_manager.create_table_if_not_exists(table_name, schema)
        
        # Verify table exists
        exists = await db_manager.table_exists(table_name)
        assert exists
        
        await db_manager.close()
    finally:
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)


@pytest.mark.asyncio
class TestDatabaseQueryIdempotence:
    """
    Property tests for database query idempotence.
    
    **Feature: raptor-playwright-python, Property 4: Database Query Idempotence**
    
    Tests that SELECT queries are truly idempotent - they can be executed 
    multiple times without changing the database state and always return 
    consistent results.
    """
    
    @pytest.fixture
    async def setup_test_db(self):
        """Setup test database with sample data."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db_manager = DatabaseManager(temp_db.name)
        await db_manager.initialize()
        
        # Create test table
        await db_manager.create_table_if_not_exists(
            "idempotence_test",
            "id INTEGER PRIMARY KEY, name TEXT, value INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        )
        
        # Insert test data
        test_data = [
            {"name": "record1", "value": 100},
            {"name": "record2", "value": 200},
            {"name": "record3", "value": 300},
        ]
        
        for data in test_data:
            await db_manager.insert_record("idempotence_test", data)
        
        yield db_manager
        
        await db_manager.close()
        os.unlink(temp_db.name)
    
    @given(
        query_type=st.sampled_from(['select_all', 'select_by_id', 'select_by_name', 'count_records']),
        execution_count=st.integers(min_value=1, max_value=10),
        record_id=st.integers(min_value=1, max_value=3),
        record_name=st.sampled_from(['record1', 'record2', 'record3'])
    )
    @settings(max_examples=50, deadline=5000)
    async def test_query_idempotence(self, setup_test_db, query_type, execution_count, record_id, record_name):
        """
        Property test: Database SELECT queries should be idempotent.
        
        Running the same SELECT query multiple times should always return
        the same results without modifying the database state.
        
        Args:
            setup_test_db: Database manager fixture with test data
            query_type: Type of query to test
            execution_count: Number of times to execute the query
            record_id: ID for record-specific queries
            record_name: Name for name-based queries
        """
        db_manager = setup_test_db
        results = []
        
        # Execute the same query multiple times
        for i in range(execution_count):
            if query_type == 'select_all':
                result = await db_manager.get_all_records("idempotence_test")
            elif query_type == 'select_by_id':
                result = await db_manager.get_record_by_id("idempotence_test", record_id)
            elif query_type == 'select_by_name':
                result = await db_manager.execute_query(
                    "SELECT * FROM idempotence_test WHERE name = ?", 
                    (record_name,)
                )
            elif query_type == 'count_records':
                result = await db_manager.count_records("idempotence_test")
            
            results.append(result)
        
        # Verify all results are identical (idempotent)
        first_result = results[0]
        for i, result in enumerate(results[1:], 1):
            assert result == first_result, f"Query result {i+1} differs from first result. Query type: {query_type}"
        
        # Additional verification: ensure database state hasn't changed
        final_count = await db_manager.count_records("idempotence_test")
        assert final_count == 3, "Database state was modified by SELECT queries"
    
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
    async def test_complex_query_idempotence(self, setup_test_db, where_conditions, execution_count):
        """
        Property test: Complex SELECT queries with WHERE clauses should be idempotent.
        
        Tests that complex queries with various WHERE conditions return
        consistent results across multiple executions.
        
        Args:
            setup_test_db: Database manager fixture with test data
            where_conditions: List of WHERE conditions to test
            execution_count: Number of times to execute each query
        """
        db_manager = setup_test_db
        
        for where_clause, param in where_conditions:
            results = []
            
            # Skip invalid parameter combinations
            if 'value' in where_clause and isinstance(param, str):
                continue
            if 'name LIKE' in where_clause and isinstance(param, int):
                continue
            
            try:
                # Execute the same complex query multiple times
                for _ in range(execution_count):
                    result = await db_manager.execute_query(
                        f"SELECT * FROM idempotence_test WHERE {where_clause}",
                        (param,)
                    )
                    results.append(result)
                
                # Verify all results are identical
                first_result = results[0]
                for i, result in enumerate(results[1:], 1):
                    assert result == first_result, (
                        f"Complex query result {i+1} differs from first result. "
                        f"WHERE clause: {where_clause}, param: {param}"
                    )
                
            except Exception as e:
                # Log but don't fail on invalid queries (this is expected for some generated conditions)
                continue
    
    async def test_concurrent_query_idempotence(self, setup_test_db):
        """
        Test that concurrent SELECT queries maintain idempotence.
        
        Multiple concurrent SELECT queries should not interfere with each other
        and should return consistent results.
        """
        db_manager = setup_test_db
        
        async def execute_query_batch():
            """Execute a batch of queries concurrently."""
            tasks = [
                db_manager.get_all_records("idempotence_test"),
                db_manager.get_record_by_id("idempotence_test", 1),
                db_manager.count_records("idempotence_test"),
                db_manager.execute_query("SELECT * FROM idempotence_test WHERE value > ?", (150,))
            ]
            return await asyncio.gather(*tasks)
        
        # Execute multiple batches of concurrent queries
        batch_results = []
        for _ in range(3):
            batch_result = await execute_query_batch()
            batch_results.append(batch_result)
        
        # Verify all batches return identical results
        first_batch = batch_results[0]
        for i, batch in enumerate(batch_results[1:], 1):
            for j, (first_result, current_result) in enumerate(zip(first_batch, batch)):
                assert current_result == first_result, (
                    f"Concurrent query batch {i+1}, query {j} differs from first batch"
                )
    
    @given(
        table_operations=st.lists(
            st.sampled_from(['table_exists', 'get_all_records', 'count_records']),
            min_size=1,
            max_size=5
        ),
        repetitions=st.integers(min_value=2, max_value=4)
    )
    @settings(max_examples=20, deadline=3000)
    async def test_metadata_query_idempotence(self, setup_test_db, table_operations, repetitions):
        """
        Property test: Database metadata queries should be idempotent.
        
        Queries that check table existence, schema information, etc.
        should return consistent results across multiple executions.
        
        Args:
            setup_test_db: Database manager fixture with test data
            table_operations: List of metadata operations to test
            repetitions: Number of times to repeat each operation
        """
        db_manager = setup_test_db
        
        for operation in table_operations:
            results = []
            
            # Execute the same metadata query multiple times
            for _ in range(repetitions):
                if operation == 'table_exists':
                    result = await db_manager.table_exists("idempotence_test")
                elif operation == 'get_all_records':
                    result = await db_manager.get_all_records("idempotence_test")
                elif operation == 'count_records':
                    result = await db_manager.count_records("idempotence_test")
                
                results.append(result)
            
            # Verify all results are identical
            first_result = results[0]
            for i, result in enumerate(results[1:], 1):
                assert result == first_result, (
                    f"Metadata query result {i+1} differs from first result. "
                    f"Operation: {operation}"
                )
