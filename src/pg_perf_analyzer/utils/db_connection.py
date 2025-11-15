"""Database connection management with read-only enforcement."""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, List
from contextlib import contextmanager


class DatabaseConnection:
    """Manages PostgreSQL database connections with read-only enforcement."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database connection.
        
        Args:
            config: Database configuration dictionary with keys:
                - host: Database host
                - port: Database port
                - database: Database name
                - user: Database user
                - password: Database password
                - sslmode: SSL mode (optional)
        """
        self.config = config
        self.connection: Optional[psycopg2.extensions.connection] = None
        
    def connect(self) -> None:
        """Establish database connection with read-only mode."""
        try:
            self.connection = psycopg2.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                database=self.config['database'],
                user=self.config['user'],
                password=self.config.get('password', ''),
                sslmode=self.config.get('sslmode', 'prefer'),
                connect_timeout=10
            )
            # Set connection to read-only mode
            self.connection.set_session(readonly=True, autocommit=True)
        except psycopg2.Error as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    @contextmanager
    def cursor(self):
        """
        Context manager for database cursor with dictionary results.
        
        Yields:
            psycopg2.extras.RealDictCursor: Database cursor
        """
        if not self.connection:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a read-only query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries containing query results
        """
        with self.cursor() as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
    
    def execute_scalar(self, query: str, params: Optional[tuple] = None) -> Any:
        """
        Execute a query and return a single scalar value.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Single value from query result
        """
        with self.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return list(result.values())[0] if result else None
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            version = self.execute_scalar("SELECT version()")
            return version is not None
        except Exception:
            return False
    
    def get_server_version(self) -> str:
        """
        Get PostgreSQL server version.
        
        Returns:
            PostgreSQL version string
        """
        return self.execute_scalar("SELECT version()")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
