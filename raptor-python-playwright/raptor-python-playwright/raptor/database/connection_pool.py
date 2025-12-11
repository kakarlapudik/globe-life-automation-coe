"""
Connection pool implementation for database connections.

This module provides connection pooling functionality for SQL Server databases
using pyodbc, ensuring efficient resource management and connection reuse.
"""

import pyodbc
import threading
import time
from typing import Optional, Dict, Any, List
from queue import Queue, Empty
from contextlib import contextmanager
import logging

from ..core.exceptions import DatabaseException


logger = logging.getLogger(__name__)


class PooledConnection:
    """Wrapper for a pooled database connection."""
    
    def __init__(self, connection: pyodbc.Connection, pool: 'ConnectionPool'):
        """
        Initialize a pooled connection.
        
        Args:
            connection: The pyodbc connection object
            pool: Reference to the parent connection pool
        """
        self.connection = connection
        self.pool = pool
        self.in_use = False
        self.created_at = time.time()
        self.last_used = time.time()
    
    def is_valid(self) -> bool:
        """
        Check if the connection is still valid.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            # Simple query to test connection
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.warning(f"Connection validation failed: {e}")
            return False
    
    def close(self):
        """Close the underlying connection."""
        try:
            if self.connection:
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")


class ConnectionPool:
    """
    Connection pool for managing database connections.
    
    Provides connection pooling with configurable pool size, connection timeout,
    and automatic connection validation.
    """
    
    def __init__(
        self,
        connection_string: str,
        min_size: int = 2,
        max_size: int = 10,
        max_idle_time: int = 300,
        connection_timeout: int = 30
    ):
        """
        Initialize the connection pool.
        
        Args:
            connection_string: Database connection string for pyodbc
            min_size: Minimum number of connections to maintain
            max_size: Maximum number of connections allowed
            max_idle_time: Maximum idle time in seconds before closing connection
            connection_timeout: Timeout in seconds for getting a connection
        """
        self.connection_string = connection_string
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self.connection_timeout = connection_timeout
        
        self._pool: Queue[PooledConnection] = Queue(maxsize=max_size)
        self._all_connections: List[PooledConnection] = []
        self._lock = threading.Lock()
        self._closed = False
        
        # Initialize minimum connections
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the pool with minimum number of connections."""
        logger.info(f"Initializing connection pool with {self.min_size} connections")
        for _ in range(self.min_size):
            try:
                conn = self._create_connection()
                self._pool.put(conn)
            except Exception as e:
                logger.error(f"Failed to initialize connection: {e}")
                raise DatabaseException(f"Failed to initialize connection pool: {e}")
    
    def _create_connection(self) -> PooledConnection:
        """
        Create a new database connection.
        
        Returns:
            PooledConnection: A new pooled connection
            
        Raises:
            DatabaseException: If connection creation fails
        """
        try:
            connection = pyodbc.connect(self.connection_string)
            pooled_conn = PooledConnection(connection, self)
            
            with self._lock:
                self._all_connections.append(pooled_conn)
            
            logger.debug(f"Created new connection. Total connections: {len(self._all_connections)}")
            return pooled_conn
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise DatabaseException(f"Failed to create database connection: {e}")
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool (context manager).
        
        Yields:
            pyodbc.Connection: A database connection
            
        Raises:
            DatabaseException: If unable to get a connection
            
        Example:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        if self._closed:
            raise DatabaseException("Connection pool is closed")
        
        pooled_conn = None
        try:
            # Try to get an existing connection from the pool
            try:
                pooled_conn = self._pool.get(timeout=self.connection_timeout)
            except Empty:
                # Pool is empty, try to create a new connection if under max_size
                with self._lock:
                    if len(self._all_connections) < self.max_size:
                        pooled_conn = self._create_connection()
                    else:
                        raise DatabaseException(
                            f"Connection pool exhausted. Max size: {self.max_size}"
                        )
            
            # Validate connection before use
            if not pooled_conn.is_valid():
                logger.warning("Invalid connection detected, creating new one")
                pooled_conn.close()
                with self._lock:
                    self._all_connections.remove(pooled_conn)
                pooled_conn = self._create_connection()
            
            pooled_conn.in_use = True
            pooled_conn.last_used = time.time()
            
            yield pooled_conn.connection
            
        finally:
            # Return connection to pool
            if pooled_conn:
                pooled_conn.in_use = False
                pooled_conn.last_used = time.time()
                try:
                    self._pool.put_nowait(pooled_conn)
                except Exception as e:
                    logger.error(f"Failed to return connection to pool: {e}")
    
    def cleanup_idle_connections(self):
        """Remove idle connections that exceed max_idle_time."""
        current_time = time.time()
        connections_to_remove = []
        
        with self._lock:
            for conn in self._all_connections:
                if (not conn.in_use and 
                    current_time - conn.last_used > self.max_idle_time and
                    len(self._all_connections) > self.min_size):
                    connections_to_remove.append(conn)
        
        for conn in connections_to_remove:
            try:
                conn.close()
                with self._lock:
                    self._all_connections.remove(conn)
                logger.debug(f"Closed idle connection. Remaining: {len(self._all_connections)}")
            except Exception as e:
                logger.error(f"Error closing idle connection: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection pool statistics.
        
        Returns:
            Dict containing pool statistics
        """
        with self._lock:
            total = len(self._all_connections)
            in_use = sum(1 for conn in self._all_connections if conn.in_use)
            available = total - in_use
            
            return {
                'total_connections': total,
                'in_use': in_use,
                'available': available,
                'min_size': self.min_size,
                'max_size': self.max_size,
                'pool_queue_size': self._pool.qsize()
            }
    
    def close_all(self):
        """Close all connections in the pool."""
        if self._closed:
            return
        
        logger.info("Closing all connections in pool")
        self._closed = True
        
        # Close all connections
        with self._lock:
            for conn in self._all_connections:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            self._all_connections.clear()
        
        # Clear the queue
        while not self._pool.empty():
            try:
                self._pool.get_nowait()
            except Empty:
                break
        
        logger.info("Connection pool closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_all()
    
    def __del__(self):
        """Destructor to ensure connections are closed."""
        self.close_all()
