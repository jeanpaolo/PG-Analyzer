"""Base analyzer class for all database analyzers."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..utils.db_connection import DatabaseConnection


class BaseAnalyzer(ABC):
    """Abstract base class for database analyzers."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize analyzer with database connection.
        
        Args:
            db_connection: DatabaseConnection instance
        """
        self.db = db_connection
    
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Perform analysis and return results.
        
        Returns:
            Dictionary containing analysis results
        """
        pass
    
    @abstractmethod
    def get_analysis_name(self) -> str:
        """
        Get the name of this analysis.
        
        Returns:
            Analysis name string
        """
        pass
    
    def _safe_execute(self, query: str, params: tuple = None, default=None):
        """
        Safely execute a query with error handling.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            default: Default value to return on error
            
        Returns:
            Query results or default value on error
        """
        try:
            return self.db.execute_query(query, params)
        except Exception as e:
            return default if default is not None else []
    
    def _safe_execute_scalar(self, query: str, params: tuple = None, default=None):
        """
        Safely execute a scalar query with error handling.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            default: Default value to return on error
            
        Returns:
            Scalar result or default value on error
        """
        try:
            return self.db.execute_scalar(query, params)
        except Exception as e:
            return default
