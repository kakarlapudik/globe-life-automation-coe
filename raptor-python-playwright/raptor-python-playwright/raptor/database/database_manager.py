"""
Database Manager for RAPTOR Python Playwright framework.

This module provides database operations for SQL Server including:
- Connection management with pooling
- Query execution (SELECT, INSERT, UPDATE, DELETE)
- DDFE element definition management
- DDDB test data import/export
- Parameterized query support
"""

import pyodbc
import logging
from typing import Optional, Dict, Any, List, Union
from contextlib import contextmanager

from .connection_pool import ConnectionPool
from ..core.exceptions import DatabaseException


logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database operations for RAPTOR framework.
    
    Provides methods for connecting to SQL Server databases, executing queries,
    and managing test data through DDFE and DDDB systems.
    """
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        server: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        driver: str = "{ODBC Driver 17 for SQL Server}",
        use_pooling: bool = True,
        pool_min_size: int = 2,
        pool_max_size: int = 10
    ):
        """
        Initialize the Database Manager.
        
        Args:
            connection_string: Complete connection string (if provided, other params ignored)
            server: Database server address
            database: Database name
            user: Database username
            password: Database password
            driver: ODBC driver name
            use_pooling: Whether to use connection pooling
            pool_min_size: Minimum pool size
            pool_max_size: Maximum pool size
            
        Example:
            # Using connection string
            db = DatabaseManager(connection_string="DRIVER={...};SERVER=...;DATABASE=...")
            
            # Using individual parameters
            db = DatabaseManager(
                server="localhost",
                database="DDFE",
                user="testuser",
                password="password"
            )
        """
        self._connection_string = connection_string
        self._server = server
        self._database = database
        self._user = user
        self._password = password
        self._driver = driver
        self._use_pooling = use_pooling
        self._pool: Optional[ConnectionPool] = None
        self._direct_connection: Optional[pyodbc.Connection] = None
        self._connected = False
        
        # Build connection string if not provided
        if not self._connection_string:
            self._connection_string = self._build_connection_string()
        
        # Initialize connection pool if using pooling
        if self._use_pooling:
            try:
                self._pool = ConnectionPool(
                    connection_string=self._connection_string,
                    min_size=pool_min_size,
                    max_size=pool_max_size
                )
                self._connected = True
                logger.info(f"Database connection pool initialized for database: {database}")
            except Exception as e:
                logger.error(f"Failed to initialize connection pool: {e}")
                raise DatabaseException(
                    operation="initialize_pool",
                    database_error=e
                )
    
    def _build_connection_string(self) -> str:
        """
        Build a connection string from individual parameters.
        
        Returns:
            str: Complete connection string
            
        Raises:
            DatabaseException: If required parameters are missing
        """
        if not all([self._server, self._database]):
            raise DatabaseException(
                operation="build_connection_string",
                sql_query="Missing required connection parameters (server, database)"
            )
        
        conn_parts = [
            f"DRIVER={self._driver}",
            f"SERVER={self._server}",
            f"DATABASE={self._database}"
        ]
        
        if self._user and self._password:
            conn_parts.extend([
                f"UID={self._user}",
                f"PWD={self._password}"
            ])
        else:
            # Use Windows Authentication
            conn_parts.append("Trusted_Connection=yes")
        
        return ";".join(conn_parts)
    
    def connect(self):
        """
        Establish database connection.
        
        If pooling is disabled, creates a direct connection.
        If pooling is enabled, connection pool is already initialized.
        
        Raises:
            DatabaseException: If connection fails
        """
        if self._connected:
            logger.debug("Already connected to database")
            return
        
        if not self._use_pooling:
            try:
                self._direct_connection = pyodbc.connect(self._connection_string)
                self._connected = True
                logger.info(f"Direct database connection established to: {self._database}")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise DatabaseException(
                    operation="connect",
                    database_error=e
                )
        else:
            # Pool already initialized in __init__
            self._connected = True
    
    def disconnect(self):
        """
        Close database connection(s).
        
        Closes connection pool if using pooling, or direct connection otherwise.
        """
        if not self._connected:
            return
        
        try:
            if self._use_pooling and self._pool:
                self._pool.close_all()
                logger.info("Connection pool closed")
            elif self._direct_connection:
                self._direct_connection.close()
                logger.info("Direct database connection closed")
            
            self._connected = False
        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")
            raise DatabaseException(
                operation="disconnect",
                database_error=e
            )
    
    @contextmanager
    def _get_connection(self):
        """
        Get a database connection (internal use).
        
        Yields:
            pyodbc.Connection: Database connection
        """
        if not self._connected:
            self.connect()
        
        if self._use_pooling and self._pool:
            with self._pool.get_connection() as conn:
                yield conn
        else:
            yield self._direct_connection
    
    def execute_query(
        self,
        sql: str,
        params: Optional[Union[tuple, Dict[str, Any]]] = None,
        fetch_all: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            sql: SQL SELECT statement
            params: Query parameters (tuple or dict for named parameters)
            fetch_all: If True, fetch all rows; if False, fetch one row
            
        Returns:
            List of dictionaries representing rows (or single dict if fetch_all=False)
            
        Raises:
            DatabaseException: If query execution fails
            
        Example:
            # Simple query
            results = db.execute_query("SELECT * FROM Users WHERE active = 1")
            
            # Parameterized query
            results = db.execute_query(
                "SELECT * FROM Users WHERE user_id = ?",
                params=(123,)
            )
            
            # Named parameters
            results = db.execute_query(
                "SELECT * FROM Users WHERE name = :name AND age > :age",
                params={'name': 'John', 'age': 25}
            )
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Execute query with or without parameters
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                # Fetch results
                if fetch_all:
                    rows = cursor.fetchall()
                else:
                    rows = [cursor.fetchone()] if cursor.fetchone() else []
                
                # Convert to list of dictionaries
                if rows and rows[0]:
                    columns = [column[0] for column in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]
                else:
                    results = []
                
                cursor.close()
                logger.debug(f"Query executed successfully. Rows returned: {len(results)}")
                return results
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseException(
                operation="execute_query",
                sql_query=sql,
                database_error=e
            )
    
    def execute_update(
        self,
        sql: str,
        params: Optional[Union[tuple, Dict[str, Any]]] = None,
        commit: bool = True
    ) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE statement.
        
        Args:
            sql: SQL statement (INSERT, UPDATE, DELETE)
            params: Query parameters (tuple or dict for named parameters)
            commit: Whether to commit the transaction immediately
            
        Returns:
            int: Number of rows affected
            
        Raises:
            DatabaseException: If execution fails
            
        Example:
            # Insert
            rows = db.execute_update(
                "INSERT INTO Users (name, email) VALUES (?, ?)",
                params=('John Doe', 'john@example.com')
            )
            
            # Update
            rows = db.execute_update(
                "UPDATE Users SET active = 1 WHERE user_id = ?",
                params=(123,)
            )
            
            # Delete
            rows = db.execute_update(
                "DELETE FROM Users WHERE user_id = ?",
                params=(123,)
            )
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Execute statement with or without parameters
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                
                rows_affected = cursor.rowcount
                
                if commit:
                    conn.commit()
                
                cursor.close()
                logger.debug(f"Update executed successfully. Rows affected: {rows_affected}")
                return rows_affected
                
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            raise DatabaseException(
                operation="execute_update",
                sql_query=sql,
                database_error=e
            )
    
    def import_data(
        self,
        table: str,
        test_id: int,
        iteration: int = 1,
        instance: int = 1,
        additional_filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Import test data from DDDB table.
        
        Retrieves a row from the specified DDDB table based on test_id,
        iteration, and instance parameters.
        
        Args:
            table: DDDB table name
            test_id: Test identifier
            iteration: Test iteration number
            instance: Test instance number
            additional_filters: Additional WHERE clause filters
            
        Returns:
            Dictionary containing the row data
            
        Raises:
            DatabaseException: If import fails or no data found
            
        Example:
            data = db.import_data(
                table="TestData_Login",
                test_id=101,
                iteration=1,
                instance=1
            )
            username = data['username']
            password = data['password']
        """
        try:
            # Build WHERE clause
            where_parts = [
                f"test_id = {test_id}",
                f"iteration = {iteration}",
                f"instance = {instance}"
            ]
            
            if additional_filters:
                for key, value in additional_filters.items():
                    if isinstance(value, str):
                        where_parts.append(f"{key} = '{value}'")
                    else:
                        where_parts.append(f"{key} = {value}")
            
            where_clause = " AND ".join(where_parts)
            sql = f"SELECT * FROM {table} WHERE {where_clause}"
            
            results = self.execute_query(sql, fetch_all=False)
            
            if not results:
                raise DatabaseException(
                    operation="import_data",
                    sql_query=sql,
                    database_error=Exception(
                        f"No data found for test_id={test_id}, iteration={iteration}, instance={instance}"
                    )
                )
            
            logger.info(f"Data imported from {table} for test_id={test_id}")
            return results[0]
            
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Data import failed: {e}")
            raise DatabaseException(
                operation="import_data",
                database_error=e
            )
    
    def export_data(
        self,
        table: str,
        pk_id: int,
        field: str,
        value: Any
    ) -> int:
        """
        Export/update a field value in DDDB table.
        
        Updates a specific field in a DDDB table row identified by primary key.
        
        Args:
            table: DDDB table name
            pk_id: Primary key ID of the row to update
            field: Field name to update
            value: New value for the field
            
        Returns:
            int: Number of rows affected (should be 1)
            
        Raises:
            DatabaseException: If export fails
            
        Example:
            # Update test result
            db.export_data(
                table="TestData_Login",
                pk_id=12345,
                field="test_result",
                value="PASS"
            )
            
            # Update error message
            db.export_data(
                table="TestData_Login",
                pk_id=12345,
                field="err_msg",
                value="Login successful"
            )
        """
        try:
            # Build UPDATE statement with parameterized query
            sql = f"UPDATE {table} SET {field} = ? WHERE pk_id = ?"
            params = (value, pk_id)
            
            rows_affected = self.execute_update(sql, params)
            
            if rows_affected == 0:
                logger.warning(f"No rows updated for pk_id={pk_id} in table {table}")
            else:
                logger.info(f"Data exported to {table}, pk_id={pk_id}, field={field}")
            
            return rows_affected
            
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            raise DatabaseException(
                operation="export_data",
                database_error=e
            )
    
    def get_field(
        self,
        table: str,
        field: str,
        pk_id: int
    ) -> Any:
        """
        Retrieve a single field value from a DDDB table.
        
        Args:
            table: DDDB table name
            field: Field name to retrieve
            pk_id: Primary key ID of the row
            
        Returns:
            The field value (type depends on database column type)
            
        Raises:
            DatabaseException: If query fails or row not found
            
        Example:
            username = db.get_field(
                table="TestData_Login",
                field="username",
                pk_id=12345
            )
        """
        try:
            sql = f"SELECT {field} FROM {table} WHERE pk_id = ?"
            params = (pk_id,)
            
            results = self.execute_query(sql, params, fetch_all=False)
            
            if not results:
                raise DatabaseException(
                    operation="get_field",
                    sql_query=sql,
                    database_error=Exception(f"No row found with pk_id={pk_id}")
                )
            
            value = results[0][field]
            logger.debug(f"Retrieved field {field} from {table}, pk_id={pk_id}")
            return value
            
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Get field failed: {e}")
            raise DatabaseException(
                operation="get_field",
                database_error=e
            )
    
    def get_row(
        self,
        table: str,
        pk_id: int
    ) -> Dict[str, Any]:
        """
        Retrieve a complete row from a DDDB table.
        
        Args:
            table: DDDB table name
            pk_id: Primary key ID of the row
            
        Returns:
            Dictionary containing all fields from the row
            
        Raises:
            DatabaseException: If query fails or row not found
            
        Example:
            row = db.get_row(
                table="TestData_Login",
                pk_id=12345
            )
            username = row['username']
            password = row['password']
        """
        try:
            sql = f"SELECT * FROM {table} WHERE pk_id = ?"
            params = (pk_id,)
            
            results = self.execute_query(sql, params, fetch_all=False)
            
            if not results:
                raise DatabaseException(
                    operation="get_row",
                    sql_query=sql,
                    database_error=Exception(f"No row found with pk_id={pk_id}")
                )
            
            logger.debug(f"Retrieved row from {table}, pk_id={pk_id}")
            return results[0]
            
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Get row failed: {e}")
            raise DatabaseException(
                operation="get_row",
                database_error=e
            )
    
    def get_element_definition(
        self,
        pv_name: str,
        application_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve element definition from DDFE.
        
        Args:
            pv_name: Primary identifier for the element
            application_name: Optional application context filter
            
        Returns:
            Dictionary containing element definition (locators, type, etc.)
            
        Raises:
            DatabaseException: If element not found
            
        Example:
            element = db.get_element_definition(
                pv_name="login_button",
                application_name="V3"
            )
            primary_locator = element['locator_primary']
            fallback = element['locator_fallback1']
        """
        try:
            sql = "SELECT * FROM DDFE_Elements WHERE pv_name = ?"
            params = [pv_name]
            
            if application_name:
                sql += " AND application_name = ?"
                params.append(application_name)
            
            results = self.execute_query(sql, tuple(params), fetch_all=False)
            
            if not results:
                raise DatabaseException(
                    operation="get_element_definition",
                    sql_query=sql,
                    database_error=Exception(
                        f"Element definition not found: {pv_name}"
                    )
                )
            
            logger.debug(f"Retrieved element definition for: {pv_name}")
            return results[0]
            
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Get element definition failed: {e}")
            raise DatabaseException(
                operation="get_element_definition",
                database_error=e
            )
    
    def get_pool_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get connection pool statistics.
        
        Returns:
            Dictionary with pool stats if pooling is enabled, None otherwise
        """
        if self._use_pooling and self._pool:
            return self._pool.get_stats()
        return None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __del__(self):
        """Destructor to ensure connection cleanup."""
        try:
            self.disconnect()
        except Exception:
            pass

