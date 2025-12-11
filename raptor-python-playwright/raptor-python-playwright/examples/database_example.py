"""
Database Manager Example

This example demonstrates how to use the DatabaseManager for:
- Connecting to SQL Server
- Executing queries
- Managing test data (DDDB)
- Retrieving element definitions (DDFE)
- Using connection pooling
"""

import logging
from raptor.database import DatabaseManager
from raptor.core.exceptions import DatabaseException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_connection():
    """Example 1: Basic database connection."""
    logger.info("=== Example 1: Basic Connection ===")
    
    # Using context manager (recommended)
    with DatabaseManager(
        server="localhost",
        database="DDFE",
        user="testuser",
        password="password"
    ) as db:
        logger.info("Connected to database successfully")
        
        # Connection automatically closed when exiting context


def example_query_operations():
    """Example 2: Query operations."""
    logger.info("=== Example 2: Query Operations ===")
    
    with DatabaseManager(server="localhost", database="DDFE") as db:
        
        # Simple SELECT query
        results = db.execute_query("SELECT TOP 5 * FROM Users WHERE active = 1")
        logger.info(f"Found {len(results)} active users")
        
        for user in results:
            logger.info(f"User: {user['username']}, Email: {user['email']}")
        
        # Parameterized query (prevents SQL injection)
        user_id = 123
        results = db.execute_query(
            "SELECT * FROM Users WHERE user_id = ?",
            params=(user_id,)
        )
        
        if results:
            logger.info(f"Found user: {results[0]['username']}")
        
        # Fetch single row
        result = db.execute_query(
            "SELECT * FROM Users WHERE user_id = ?",
            params=(user_id,),
            fetch_all=False
        )
        
        if result:
            logger.info(f"Single user: {result[0]['username']}")


def example_update_operations():
    """Example 3: INSERT, UPDATE, DELETE operations."""
    logger.info("=== Example 3: Update Operations ===")
    
    with DatabaseManager(server="localhost", database="DDFE") as db:
        
        # Insert new user
        rows = db.execute_update(
            "INSERT INTO Users (username, email, active) VALUES (?, ?, ?)",
            params=('john_doe', 'john@example.com', 1)
        )
        logger.info(f"Inserted {rows} row(s)")
        
        # Update user
        rows = db.execute_update(
            "UPDATE Users SET active = 0 WHERE username = ?",
            params=('john_doe',)
        )
        logger.info(f"Updated {rows} row(s)")
        
        # Delete user
        rows = db.execute_update(
            "DELETE FROM Users WHERE username = ?",
            params=('john_doe',)
        )
        logger.info(f"Deleted {rows} row(s)")


def example_dddb_operations():
    """Example 4: DDDB test data operations."""
    logger.info("=== Example 4: DDDB Operations ===")
    
    with DatabaseManager(server="localhost", database="DDFE") as db:
        
        try:
            # Import test data
            test_data = db.import_data(
                table="TestData_Login",
                test_id=101,
                iteration=1,
                instance=1
            )
            
            logger.info(f"Imported test data: {test_data}")
            
            # Access test data fields
            username = test_data['username']
            password = test_data['password']
            expected_result = test_data.get('expected_result', 'PASS')
            
            logger.info(f"Test credentials - Username: {username}, Password: {password}")
            logger.info(f"Expected result: {expected_result}")
            
            # Simulate test execution
            test_result = "PASS"
            error_message = "Test completed successfully"
            
            # Export test results
            pk_id = test_data['pk_id']
            
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field="test_result",
                value=test_result
            )
            
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field="err_msg",
                value=error_message
            )
            
            logger.info("Test results exported successfully")
            
            # Retrieve specific field
            result = db.get_field(
                table="TestData_Login",
                field="test_result",
                pk_id=pk_id
            )
            logger.info(f"Retrieved test result: {result}")
            
            # Retrieve complete row
            row = db.get_row(
                table="TestData_Login",
                pk_id=pk_id
            )
            logger.info(f"Complete row: {row}")
            
        except DatabaseException as e:
            logger.error(f"DDDB operation failed: {e}")


def example_ddfe_operations():
    """Example 5: DDFE element definition operations."""
    logger.info("=== Example 5: DDFE Operations ===")
    
    with DatabaseManager(server="localhost", database="DDFE") as db:
        
        try:
            # Get element definition
            element = db.get_element_definition(
                pv_name="login_button",
                application_name="V3"
            )
            
            logger.info(f"Element definition: {element}")
            
            # Access element properties
            primary_locator = element['locator_primary']
            fallback1 = element.get('locator_fallback1')
            fallback2 = element.get('locator_fallback2')
            field_type = element['field_type']
            
            logger.info(f"Primary locator: {primary_locator}")
            logger.info(f"Fallback 1: {fallback1}")
            logger.info(f"Fallback 2: {fallback2}")
            logger.info(f"Field type: {field_type}")
            
            # Use locators in test automation
            # element_manager.locate_element(
            #     primary_locator,
            #     fallback_locators=[fallback1, fallback2]
            # )
            
        except DatabaseException as e:
            logger.error(f"DDFE operation failed: {e}")


def example_connection_pooling():
    """Example 6: Connection pooling."""
    logger.info("=== Example 6: Connection Pooling ===")
    
    # Create database manager with connection pooling
    db = DatabaseManager(
        server="localhost",
        database="DDFE",
        use_pooling=True,
        pool_min_size=2,
        pool_max_size=10
    )
    
    try:
        db.connect()
        
        # Get initial pool statistics
        stats = db.get_pool_stats()
        logger.info(f"Initial pool stats: {stats}")
        
        # Perform multiple operations
        for i in range(5):
            results = db.execute_query(f"SELECT TOP 1 * FROM Users")
            logger.info(f"Query {i+1} completed")
        
        # Get updated pool statistics
        stats = db.get_pool_stats()
        logger.info(f"Final pool stats: {stats}")
        logger.info(f"Total connections: {stats['total_connections']}")
        logger.info(f"In use: {stats['in_use']}")
        logger.info(f"Available: {stats['available']}")
        
    finally:
        db.disconnect()


def example_error_handling():
    """Example 7: Error handling."""
    logger.info("=== Example 7: Error Handling ===")
    
    with DatabaseManager(server="localhost", database="DDFE") as db:
        
        # Handle query errors
        try:
            results = db.execute_query("SELECT * FROM NonExistentTable")
        except DatabaseException as e:
            logger.error(f"Query error: {e.message}")
            logger.error(f"Operation: {e.context.get('database_operation')}")
            logger.error(f"SQL: {e.context.get('sql_query')}")
            
            # Get full error details
            error_dict = e.to_dict()
            logger.error(f"Full error details: {error_dict}")
        
        # Handle data import errors
        try:
            data = db.import_data(
                table="TestData_Login",
                test_id=99999,  # Non-existent test ID
                iteration=1,
                instance=1
            )
        except DatabaseException as e:
            logger.error(f"Import error: {e.message}")
            logger.error(f"Context: {e.context}")


def example_complete_test_workflow():
    """Example 8: Complete test workflow with database."""
    logger.info("=== Example 8: Complete Test Workflow ===")
    
    with DatabaseManager(server="localhost", database="DDFE") as db:
        
        try:
            # Step 1: Import test data
            logger.info("Step 1: Importing test data...")
            test_data = db.import_data(
                table="TestData_Login",
                test_id=101,
                iteration=1,
                instance=1
            )
            
            pk_id = test_data['pk_id']
            username = test_data['username']
            password = test_data['password']
            
            logger.info(f"Test data loaded: username={username}")
            
            # Step 2: Get element definitions
            logger.info("Step 2: Getting element definitions...")
            username_field = db.get_element_definition(
                pv_name="username_field",
                application_name="V3"
            )
            password_field = db.get_element_definition(
                pv_name="password_field",
                application_name="V3"
            )
            login_button = db.get_element_definition(
                pv_name="login_button",
                application_name="V3"
            )
            
            logger.info("Element definitions retrieved")
            
            # Step 3: Simulate test execution
            logger.info("Step 3: Executing test...")
            # (Browser automation would happen here)
            # element_manager.fill(username_field['locator_primary'], username)
            # element_manager.fill(password_field['locator_primary'], password)
            # element_manager.click(login_button['locator_primary'])
            
            test_result = "PASS"
            error_message = "Login successful"
            execution_time = 2.5
            
            # Step 4: Export test results
            logger.info("Step 4: Exporting test results...")
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field="test_result",
                value=test_result
            )
            
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field="err_msg",
                value=error_message
            )
            
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field="execution_time",
                value=execution_time
            )
            
            logger.info("Test workflow completed successfully")
            
        except DatabaseException as e:
            logger.error(f"Test workflow failed: {e}")
            
            # Export failure information
            try:
                db.export_data(
                    table="TestData_Login",
                    pk_id=pk_id,
                    field="test_result",
                    value="FAIL"
                )
                db.export_data(
                    table="TestData_Login",
                    pk_id=pk_id,
                    field="err_msg",
                    value=str(e)
                )
            except Exception as export_error:
                logger.error(f"Failed to export error: {export_error}")


def main():
    """Run all examples."""
    examples = [
        example_basic_connection,
        example_query_operations,
        example_update_operations,
        example_dddb_operations,
        example_ddfe_operations,
        example_connection_pooling,
        example_error_handling,
        example_complete_test_workflow
    ]
    
    for example in examples:
        try:
            example()
            print()  # Blank line between examples
        except Exception as e:
            logger.error(f"Example failed: {e}")
            print()


if __name__ == "__main__":
    logger.info("Starting Database Manager Examples")
    logger.info("=" * 60)
    
    # Note: Update connection parameters before running
    logger.warning("Update database connection parameters before running examples!")
    
    # Uncomment to run examples
    # main()
    
    logger.info("=" * 60)
    logger.info("Examples completed")

