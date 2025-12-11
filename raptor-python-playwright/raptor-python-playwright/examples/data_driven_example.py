"""
Data-Driven Testing Examples for RAPTOR Framework

This module demonstrates various ways to use data-driven testing with DDDB:
- Loading test data from database
- Using pytest parametrization decorators
- Iteration-based test execution
- Instance-based test execution
- Exporting test results

Requirements: 4.2, 12.1
"""

import pytest
from raptor.database.database_manager import DatabaseManager
from raptor.utils.data_driven import (
    DataDrivenTestLoader,
    parametrize_from_dddb,
    parametrize_iterations,
    parametrize_instances,
    load_test_data_for_fixture,
    get_test_data_params,
    export_test_result,
    filter_test_data
)


# ============================================================================
# Example 1: Basic Data Loading
# ============================================================================

def example_basic_data_loading():
    """
    Example: Load test data from DDDB table.
    
    This example shows how to manually load test data and iterate through it.
    """
    # Initialize database connection
    db = DatabaseManager(
        server="localhost",
        database="DDDB",
        user="testuser",
        password="testpass"
    )
    
    # Create data loader
    loader = DataDrivenTestLoader(db)
    
    # Load all test data for test_id 101
    data_set = loader.load_test_data(
        table="TestData_Login",
        test_id=101
    )
    
    print(f"Loaded {len(data_set.rows)} rows")
    print(f"Iterations: {data_set.total_iterations}")
    print(f"Instances per iteration: {data_set.total_instances}")
    
    # Iterate through all rows
    for row in data_set.rows:
        print(f"Iteration {row.iteration}, Instance {row.instance}")
        print(f"  Username: {row['username']}")
        print(f"  Password: {row['password']}")
        print(f"  Expected: {row['expected_result']}")
    
    db.disconnect()


# ============================================================================
# Example 2: Pytest Parametrization with Decorator
# ============================================================================

# Setup database fixture (would typically be in conftest.py)
@pytest.fixture(scope="session")
def database():
    """Database fixture for examples."""
    db = DatabaseManager(
        server="localhost",
        database="DDDB",
        user="testuser",
        password="testpass"
    )
    yield db
    db.disconnect()


@parametrize_from_dddb(
    table="TestData_Login",
    test_id=101,
    database=None  # Would be injected by fixture in real usage
)
def test_login_with_decorator(test_data):
    """
    Example: Test parametrized with DDDB data using decorator.
    
    This test will run once for each row in the DDDB table.
    Each run receives a TestDataRow object with all the data.
    """
    username = test_data['username']
    password = test_data['password']
    expected = test_data['expected_result']
    
    print(f"Testing login with {username}")
    
    # Perform login test
    # ... test code here ...
    
    # Export result back to DDDB
    # export_test_result(database, test_data, "PASS")


# ============================================================================
# Example 3: Iteration-Based Testing
# ============================================================================

@parametrize_iterations(
    table="TestData_Login",
    test_id=101,
    database=None  # Would be injected by fixture
)
def test_login_by_iteration(iteration_data):
    """
    Example: Test parametrized by iterations.
    
    This test runs once per iteration, receiving all instances
    for that iteration. Useful for testing workflows that involve
    multiple steps or data sets.
    """
    print(f"Testing iteration with {len(iteration_data)} instances")
    
    for instance in iteration_data:
        username = instance['username']
        password = instance['password']
        
        print(f"  Instance {instance.instance}: {username}")
        
        # Perform test for this instance
        # ... test code here ...


# ============================================================================
# Example 4: Instance-Based Testing
# ============================================================================

@parametrize_instances(
    table="TestData_Login",
    test_id=101,
    iteration=1,  # Test only iteration 1
    database=None  # Would be injected by fixture
)
def test_login_by_instance(instance_data):
    """
    Example: Test parametrized by instances within an iteration.
    
    This test runs once per instance in the specified iteration.
    Useful when you want to test a specific iteration with multiple
    data variations.
    """
    username = instance_data['username']
    password = instance_data['password']
    
    print(f"Testing instance {instance_data.instance}: {username}")
    
    # Perform test
    # ... test code here ...


# ============================================================================
# Example 5: Manual Parametrization
# ============================================================================

def test_login_manual_parametrization(database):
    """
    Example: Manually load data and use pytest.mark.parametrize.
    
    This approach gives you more control over how data is loaded
    and parametrized.
    """
    # Load test data
    test_data, test_ids = get_test_data_params(
        database,
        table="TestData_Login",
        test_id=101,
        iterations=[1, 2]  # Only test iterations 1 and 2
    )
    
    # Use with pytest.mark.parametrize
    @pytest.mark.parametrize("data", test_data, ids=test_ids)
    def inner_test(data):
        username = data['username']
        password = data['password']
        
        # Perform test
        assert username is not None
        assert password is not None
    
    # Run the parametrized test
    for data in test_data:
        inner_test(data)


# ============================================================================
# Example 6: Using Fixtures
# ============================================================================

@pytest.fixture
def login_test_data(database):
    """
    Example: Create a fixture that loads test data.
    
    This fixture can be reused across multiple tests.
    """
    return load_test_data_for_fixture(
        database,
        table="TestData_Login",
        test_id=101
    )


def test_with_fixture(login_test_data):
    """
    Example: Use test data fixture in a test.
    
    The fixture loads the data once and provides it to the test.
    """
    print(f"Testing with {len(login_test_data.rows)} data rows")
    
    for row in login_test_data.rows:
        username = row['username']
        password = row['password']
        
        # Perform test
        print(f"Testing {username}")
        # ... test code here ...


# ============================================================================
# Example 7: Filtering Test Data
# ============================================================================

def test_with_filtered_data(database):
    """
    Example: Filter test data before running tests.
    
    This is useful when you want to run tests only for specific
    data conditions.
    """
    # Load all test data
    loader = DataDrivenTestLoader(database)
    data_set = loader.load_test_data("TestData_Login", test_id=101)
    
    # Filter for only successful login scenarios
    success_data = filter_test_data(
        data_set,
        lambda row: row.get('expected_result') == 'success'
    )
    
    print(f"Testing {len(success_data.rows)} successful login scenarios")
    
    for row in success_data.rows:
        username = row['username']
        password = row['password']
        
        # Perform test
        print(f"Testing successful login: {username}")
        # ... test code here ...


# ============================================================================
# Example 8: Exporting Test Results
# ============================================================================

def test_with_result_export(database):
    """
    Example: Export test results back to DDDB.
    
    This allows you to track test execution results in the database.
    """
    # Load test data
    loader = DataDrivenTestLoader(database)
    data_set = loader.load_test_data("TestData_Login", test_id=101)
    
    for row in data_set.rows:
        username = row['username']
        password = row['password']
        
        try:
            # Perform test
            print(f"Testing {username}")
            # ... test code here ...
            
            # Simulate successful test
            result = "PASS"
            error_msg = None
            
            # Export result
            export_test_result(database, row, result, error_msg)
            
        except Exception as e:
            # Export failure
            export_test_result(database, row, "FAIL", str(e))


# ============================================================================
# Example 9: Loading Specific Iterations and Instances
# ============================================================================

def test_specific_iterations_and_instances(database):
    """
    Example: Load only specific iterations and instances.
    
    This is useful for debugging or testing specific scenarios.
    """
    # Load only iterations 1 and 2, instances 1 and 3
    loader = DataDrivenTestLoader(database)
    data_set = loader.load_test_data(
        table="TestData_Login",
        test_id=101,
        iterations=[1, 2],
        instances=[1, 3]
    )
    
    print(f"Loaded {len(data_set.rows)} specific rows")
    
    for row in data_set.rows:
        print(f"Iteration {row.iteration}, Instance {row.instance}")
        # ... test code here ...


# ============================================================================
# Example 10: Working with Test Data Hierarchy
# ============================================================================

def test_data_hierarchy(database):
    """
    Example: Work with hierarchical test data using iterations and instances.
    
    This demonstrates how to organize tests with multiple levels:
    - Iteration: Major test scenario (e.g., different user types)
    - Instance: Variations within scenario (e.g., different inputs)
    """
    loader = DataDrivenTestLoader(database)
    data_set = loader.load_test_data("TestData_Login", test_id=101)
    
    # Process by iteration
    for iteration_num in data_set.get_iterations():
        print(f"\n=== Testing Iteration {iteration_num} ===")
        
        iteration_rows = data_set.get_by_iteration(iteration_num)
        
        # Process each instance in the iteration
        for row in iteration_rows:
            print(f"  Instance {row.instance}:")
            print(f"    Username: {row['username']}")
            print(f"    Expected: {row['expected_result']}")
            
            # Perform test
            # ... test code here ...


# ============================================================================
# Example 11: Custom Test ID Generation
# ============================================================================

def custom_test_id_func(row):
    """Custom function to generate test IDs."""
    username = row.get('username', 'unknown')
    return f"{username}_iter{row.iteration}_inst{row.instance}"


@parametrize_from_dddb(
    table="TestData_Login",
    test_id=101,
    database=None,
    id_func=custom_test_id_func
)
def test_with_custom_ids(test_data):
    """
    Example: Use custom test ID generation.
    
    This makes test output more readable by using meaningful names
    instead of generic iteration/instance numbers.
    """
    username = test_data['username']
    print(f"Testing {username}")
    # ... test code here ...


# ============================================================================
# Example 12: Accessing Test Data Fields
# ============================================================================

def test_data_field_access(database):
    """
    Example: Different ways to access test data fields.
    
    TestDataRow supports multiple access patterns for convenience.
    """
    loader = DataDrivenTestLoader(database)
    row = loader.load_by_instance("TestData_Login", test_id=101, iteration=1, instance=1)
    
    if row:
        # Dictionary-style access
        username1 = row['username']
        
        # Get method with default
        email = row.get('email', 'default@example.com')
        
        # Direct attribute access for standard fields
        pk_id = row.pk_id
        test_id = row.test_id
        iteration = row.iteration
        instance = row.instance
        
        print(f"PK: {pk_id}, Test: {test_id}")
        print(f"Iteration: {iteration}, Instance: {instance}")
        print(f"Username: {username1}")
        print(f"Email: {email}")


# ============================================================================
# Running Examples
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("RAPTOR Data-Driven Testing Examples")
    print("=" * 70)
    
    print("\nExample 1: Basic Data Loading")
    print("-" * 70)
    # example_basic_data_loading()  # Uncomment to run with actual database
    print("(Requires database connection)")
    
    print("\nFor pytest examples, run:")
    print("  pytest examples/data_driven_example.py -v")
    print("\nNote: Examples require a configured database connection.")
