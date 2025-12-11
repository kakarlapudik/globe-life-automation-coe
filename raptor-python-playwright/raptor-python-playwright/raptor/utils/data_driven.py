"""
Data-Driven Test Support for RAPTOR Framework

This module provides utilities for data-driven testing with DDDB:
- Loading test data from database
- pytest parametrization helpers
- Iteration-based test execution
- Instance-based test execution

Requirements: 4.2, 12.1
"""

import pytest
import logging
from typing import List, Dict, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from functools import wraps

from ..database.database_manager import DatabaseManager
from ..core.exceptions import DatabaseException


logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TestDataRow:
    """
    Represents a single row of test data from DDDB.
    
    Attributes:
        pk_id: Primary key identifier
        test_id: Test identifier
        iteration: Iteration number
        instance: Instance number
        fk_id: Foreign key (optional)
        action: Action to perform (optional)
        err_msg: Expected error message (optional)
        data: Dictionary of all field values
    """
    pk_id: int
    test_id: int
    iteration: int
    instance: int
    fk_id: Optional[int] = None
    action: Optional[str] = None
    err_msg: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to data fields."""
        if key in self.__dict__:
            return self.__dict__[key]
        return self.data.get(key)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a field value with default fallback."""
        if key in self.__dict__:
            return self.__dict__[key]
        return self.data.get(key, default)
    
    def __repr__(self) -> str:
        """String representation for test IDs."""
        return f"TestData(test_id={self.test_id}, iter={self.iteration}, inst={self.instance})"


@dataclass
class TestDataSet:
    """
    Represents a complete set of test data for a test case.
    
    Attributes:
        test_id: Test identifier
        table_name: Source DDDB table
        rows: List of test data rows
        total_iterations: Total number of iterations
        total_instances: Total number of instances per iteration
    """
    test_id: int
    table_name: str
    rows: List[TestDataRow] = field(default_factory=list)
    total_iterations: int = 0
    total_instances: int = 0
    
    def get_by_iteration(self, iteration: int) -> List[TestDataRow]:
        """Get all rows for a specific iteration."""
        return [row for row in self.rows if row.iteration == iteration]
    
    def get_by_instance(self, iteration: int, instance: int) -> Optional[TestDataRow]:
        """Get a specific row by iteration and instance."""
        for row in self.rows:
            if row.iteration == iteration and row.instance == instance:
                return row
        return None
    
    def get_iterations(self) -> List[int]:
        """Get list of all iteration numbers."""
        return sorted(set(row.iteration for row in self.rows))
    
    def get_instances(self, iteration: int) -> List[int]:
        """Get list of all instance numbers for a specific iteration."""
        return sorted(set(row.instance for row in self.rows if row.iteration == iteration))


# ============================================================================
# Data Loader Class
# ============================================================================

class DataDrivenTestLoader:
    """
    Loads test data from DDDB for data-driven testing.
    
    Provides methods to load test data by test_id, iteration, or instance,
    and prepare data for pytest parametrization.
    """
    
    def __init__(self, database: DatabaseManager):
        """
        Initialize the data loader.
        
        Args:
            database: DatabaseManager instance for data access
        """
        self.database = database
    
    def load_test_data(
        self,
        table: str,
        test_id: int,
        iterations: Optional[List[int]] = None,
        instances: Optional[List[int]] = None
    ) -> TestDataSet:
        """
        Load test data from DDDB table.
        
        Args:
            table: DDDB table name
            test_id: Test identifier
            iterations: Optional list of specific iterations to load
            instances: Optional list of specific instances to load
            
        Returns:
            TestDataSet containing all loaded test data
            
        Raises:
            DatabaseException: If data loading fails
            
        Example:
            loader = DataDrivenTestLoader(database)
            data_set = loader.load_test_data("TestData_Login", test_id=101)
            
            # Load specific iterations
            data_set = loader.load_test_data(
                "TestData_Login",
                test_id=101,
                iterations=[1, 2, 3]
            )
        """
        try:
            # Build query to get all matching rows
            where_parts = [f"test_id = {test_id}"]
            
            if iterations:
                iter_list = ",".join(str(i) for i in iterations)
                where_parts.append(f"iteration IN ({iter_list})")
            
            if instances:
                inst_list = ",".join(str(i) for i in instances)
                where_parts.append(f"instance IN ({inst_list})")
            
            where_clause = " AND ".join(where_parts)
            sql = f"SELECT * FROM {table} WHERE {where_clause} ORDER BY iteration, instance"
            
            results = self.database.execute_query(sql)
            
            if not results:
                logger.warning(
                    f"No test data found for test_id={test_id} in table {table}"
                )
                return TestDataSet(test_id=test_id, table_name=table)
            
            # Convert results to TestDataRow objects
            rows = []
            for result in results:
                # Extract standard fields
                row_data = TestDataRow(
                    pk_id=result.get('pk_id', 0),
                    test_id=result.get('test_id', test_id),
                    iteration=result.get('iteration', 1),
                    instance=result.get('instance', 1),
                    fk_id=result.get('fk_id'),
                    action=result.get('action'),
                    err_msg=result.get('err_msg')
                )
                
                # Store all fields in data dictionary
                row_data.data = result
                rows.append(row_data)
            
            # Calculate totals
            total_iterations = len(set(row.iteration for row in rows))
            total_instances = max(len(set(row.instance for row in rows if row.iteration == i))
                                for i in set(row.iteration for row in rows))
            
            data_set = TestDataSet(
                test_id=test_id,
                table_name=table,
                rows=rows,
                total_iterations=total_iterations,
                total_instances=total_instances
            )
            
            logger.info(
                f"Loaded {len(rows)} rows from {table} for test_id={test_id} "
                f"({total_iterations} iterations, {total_instances} instances)"
            )
            
            return data_set
            
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Failed to load test data: {e}")
            raise DatabaseException(
                operation="load_test_data",
                database_error=e
            )
    
    def load_by_iteration(
        self,
        table: str,
        test_id: int,
        iteration: int
    ) -> List[TestDataRow]:
        """
        Load all test data for a specific iteration.
        
        Args:
            table: DDDB table name
            test_id: Test identifier
            iteration: Iteration number
            
        Returns:
            List of TestDataRow objects for the iteration
            
        Example:
            loader = DataDrivenTestLoader(database)
            iteration_data = loader.load_by_iteration("TestData_Login", 101, 1)
            for row in iteration_data:
                print(f"Instance {row.instance}: {row['username']}")
        """
        data_set = self.load_test_data(table, test_id, iterations=[iteration])
        return data_set.rows
    
    def load_by_instance(
        self,
        table: str,
        test_id: int,
        iteration: int,
        instance: int
    ) -> Optional[TestDataRow]:
        """
        Load test data for a specific iteration and instance.
        
        Args:
            table: DDDB table name
            test_id: Test identifier
            iteration: Iteration number
            instance: Instance number
            
        Returns:
            TestDataRow object or None if not found
            
        Example:
            loader = DataDrivenTestLoader(database)
            row = loader.load_by_instance("TestData_Login", 101, 1, 1)
            if row:
                username = row['username']
                password = row['password']
        """
        try:
            result = self.database.import_data(table, test_id, iteration, instance)
            
            if not result:
                return None
            
            row_data = TestDataRow(
                pk_id=result.get('pk_id', 0),
                test_id=result.get('test_id', test_id),
                iteration=result.get('iteration', iteration),
                instance=result.get('instance', instance),
                fk_id=result.get('fk_id'),
                action=result.get('action'),
                err_msg=result.get('err_msg')
            )
            row_data.data = result
            
            return row_data
            
        except DatabaseException:
            return None


# ============================================================================
# pytest Parametrization Helpers
# ============================================================================

def parametrize_from_dddb(
    table: str,
    test_id: int,
    database: DatabaseManager,
    iterations: Optional[List[int]] = None,
    instances: Optional[List[int]] = None,
    id_func: Optional[Callable[[TestDataRow], str]] = None
) -> Callable:
    """
    Decorator to parametrize a test function with data from DDDB.
    
    This decorator loads test data from DDDB and parametrizes the test
    function to run once for each row of data.
    
    Args:
        table: DDDB table name
        test_id: Test identifier
        database: DatabaseManager instance
        iterations: Optional list of specific iterations to run
        instances: Optional list of specific instances to run
        id_func: Optional function to generate test IDs
        
    Returns:
        Decorator function
        
    Example:
        @parametrize_from_dddb("TestData_Login", test_id=101, database=db)
        def test_login(test_data):
            username = test_data['username']
            password = test_data['password']
            # ... test code ...
    """
    def decorator(func):
        # Load test data
        loader = DataDrivenTestLoader(database)
        data_set = loader.load_test_data(table, test_id, iterations, instances)
        
        if not data_set.rows:
            # If no data, skip the test
            return pytest.mark.skip(reason=f"No test data found for test_id={test_id}")(func)
        
        # Generate test IDs
        if id_func:
            ids = [id_func(row) for row in data_set.rows]
        else:
            ids = [f"iter{row.iteration}_inst{row.instance}" for row in data_set.rows]
        
        # Apply pytest.mark.parametrize
        return pytest.mark.parametrize(
            "test_data",
            data_set.rows,
            ids=ids
        )(func)
    
    return decorator


def parametrize_iterations(
    table: str,
    test_id: int,
    database: DatabaseManager,
    iterations: Optional[List[int]] = None
) -> Callable:
    """
    Decorator to parametrize a test function by iterations.
    
    Each test run receives all instances for a specific iteration.
    
    Args:
        table: DDDB table name
        test_id: Test identifier
        database: DatabaseManager instance
        iterations: Optional list of specific iterations to run
        
    Returns:
        Decorator function
        
    Example:
        @parametrize_iterations("TestData_Login", test_id=101, database=db)
        def test_login_iteration(iteration_data):
            for instance in iteration_data:
                username = instance['username']
                # ... test code ...
    """
    def decorator(func):
        # Load test data
        loader = DataDrivenTestLoader(database)
        data_set = loader.load_test_data(table, test_id, iterations=iterations)
        
        if not data_set.rows:
            return pytest.mark.skip(reason=f"No test data found for test_id={test_id}")(func)
        
        # Group by iteration
        iteration_groups = []
        for iteration_num in data_set.get_iterations():
            iteration_rows = data_set.get_by_iteration(iteration_num)
            iteration_groups.append(iteration_rows)
        
        # Generate test IDs
        ids = [f"iteration{rows[0].iteration}" for rows in iteration_groups]
        
        # Apply pytest.mark.parametrize
        return pytest.mark.parametrize(
            "iteration_data",
            iteration_groups,
            ids=ids
        )(func)
    
    return decorator


def parametrize_instances(
    table: str,
    test_id: int,
    database: DatabaseManager,
    iteration: int = 1,
    instances: Optional[List[int]] = None
) -> Callable:
    """
    Decorator to parametrize a test function by instances within an iteration.
    
    Args:
        table: DDDB table name
        test_id: Test identifier
        database: DatabaseManager instance
        iteration: Iteration number to load instances from
        instances: Optional list of specific instances to run
        
    Returns:
        Decorator function
        
    Example:
        @parametrize_instances("TestData_Login", test_id=101, iteration=1, database=db)
        def test_login_instance(instance_data):
            username = instance_data['username']
            # ... test code ...
    """
    def decorator(func):
        # Load test data for specific iteration
        loader = DataDrivenTestLoader(database)
        data_set = loader.load_test_data(
            table,
            test_id,
            iterations=[iteration],
            instances=instances
        )
        
        if not data_set.rows:
            return pytest.mark.skip(
                reason=f"No test data found for test_id={test_id}, iteration={iteration}"
            )(func)
        
        # Generate test IDs
        ids = [f"instance{row.instance}" for row in data_set.rows]
        
        # Apply pytest.mark.parametrize
        return pytest.mark.parametrize(
            "instance_data",
            data_set.rows,
            ids=ids
        )(func)
    
    return decorator


# ============================================================================
# Helper Functions
# ============================================================================

def load_test_data_for_fixture(
    database: DatabaseManager,
    table: str,
    test_id: int,
    iterations: Optional[List[int]] = None,
    instances: Optional[List[int]] = None
) -> TestDataSet:
    """
    Helper function to load test data for use in pytest fixtures.
    
    Args:
        database: DatabaseManager instance
        table: DDDB table name
        test_id: Test identifier
        iterations: Optional list of specific iterations to load
        instances: Optional list of specific instances to load
        
    Returns:
        TestDataSet containing all loaded test data
        
    Example:
        @pytest.fixture
        def login_test_data(database):
            return load_test_data_for_fixture(
                database,
                "TestData_Login",
                test_id=101
            )
        
        def test_login(login_test_data):
            for row in login_test_data.rows:
                # ... test code ...
    """
    loader = DataDrivenTestLoader(database)
    return loader.load_test_data(table, test_id, iterations, instances)


def get_test_data_params(
    database: DatabaseManager,
    table: str,
    test_id: int,
    iterations: Optional[List[int]] = None,
    instances: Optional[List[int]] = None
) -> Tuple[List[TestDataRow], List[str]]:
    """
    Get test data and IDs for manual pytest.mark.parametrize usage.
    
    Args:
        database: DatabaseManager instance
        table: DDDB table name
        test_id: Test identifier
        iterations: Optional list of specific iterations to load
        instances: Optional list of specific instances to load
        
    Returns:
        Tuple of (test_data_rows, test_ids)
        
    Example:
        test_data, test_ids = get_test_data_params(
            database,
            "TestData_Login",
            test_id=101
        )
        
        @pytest.mark.parametrize("data", test_data, ids=test_ids)
        def test_login(data):
            # ... test code ...
    """
    loader = DataDrivenTestLoader(database)
    data_set = loader.load_test_data(table, test_id, iterations, instances)
    
    test_ids = [f"iter{row.iteration}_inst{row.instance}" for row in data_set.rows]
    
    return data_set.rows, test_ids


def export_test_result(
    database: DatabaseManager,
    test_data: TestDataRow,
    result: str,
    error_message: Optional[str] = None
) -> None:
    """
    Export test result back to DDDB.
    
    Args:
        database: DatabaseManager instance
        test_data: TestDataRow containing pk_id
        result: Test result (PASS, FAIL, SKIP, etc.)
        error_message: Optional error message for failures
        
    Example:
        try:
            # ... test code ...
            export_test_result(database, test_data, "PASS")
        except Exception as e:
            export_test_result(database, test_data, "FAIL", str(e))
    """
    try:
        # Update test result field
        database.export_data(
            table=test_data.data.get('_table_name', 'TestData'),
            pk_id=test_data.pk_id,
            field='test_result',
            value=result
        )
        
        # Update error message if provided
        if error_message:
            database.export_data(
                table=test_data.data.get('_table_name', 'TestData'),
                pk_id=test_data.pk_id,
                field='err_msg',
                value=error_message
            )
        
        logger.info(f"Exported test result for pk_id={test_data.pk_id}: {result}")
        
    except Exception as e:
        logger.error(f"Failed to export test result: {e}")


# ============================================================================
# Utility Functions
# ============================================================================

def filter_test_data(
    data_set: TestDataSet,
    filter_func: Callable[[TestDataRow], bool]
) -> TestDataSet:
    """
    Filter test data based on a custom function.
    
    Args:
        data_set: TestDataSet to filter
        filter_func: Function that returns True for rows to keep
        
    Returns:
        New TestDataSet with filtered rows
        
    Example:
        # Filter for active users only
        active_users = filter_test_data(
            data_set,
            lambda row: row.get('active') == True
        )
    """
    filtered_rows = [row for row in data_set.rows if filter_func(row)]
    
    return TestDataSet(
        test_id=data_set.test_id,
        table_name=data_set.table_name,
        rows=filtered_rows,
        total_iterations=len(set(row.iteration for row in filtered_rows)),
        total_instances=max(
            len(set(row.instance for row in filtered_rows if row.iteration == i))
            for i in set(row.iteration for row in filtered_rows)
        ) if filtered_rows else 0
    )


def merge_test_data(
    *data_sets: TestDataSet
) -> TestDataSet:
    """
    Merge multiple TestDataSet objects into one.
    
    Args:
        *data_sets: Variable number of TestDataSet objects to merge
        
    Returns:
        Merged TestDataSet
        
    Example:
        data1 = loader.load_test_data("TestData_Login", 101)
        data2 = loader.load_test_data("TestData_Login", 102)
        merged = merge_test_data(data1, data2)
    """
    if not data_sets:
        raise ValueError("At least one TestDataSet required")
    
    all_rows = []
    for data_set in data_sets:
        all_rows.extend(data_set.rows)
    
    return TestDataSet(
        test_id=data_sets[0].test_id,
        table_name=data_sets[0].table_name,
        rows=all_rows,
        total_iterations=len(set(row.iteration for row in all_rows)),
        total_instances=max(
            len(set(row.instance for row in all_rows if row.iteration == i))
            for i in set(row.iteration for row in all_rows)
        ) if all_rows else 0
    )
