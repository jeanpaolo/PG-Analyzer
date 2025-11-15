"""Database structure analyzer for tables, indexes, and schema organization."""

from typing import Dict, Any, List
from .base_analyzer import BaseAnalyzer


class StructureAnalyzer(BaseAnalyzer):
    """Analyzes database structure including tables, indexes, and relationships."""
    
    def get_analysis_name(self) -> str:
        return "Database Structure Analysis"
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive structure analysis.
        
        Returns:
            Dictionary containing structure analysis results
        """
        return {
            "database_info": self._get_database_info(),
            "schemas": self._get_schemas(),
            "tables": self._get_tables(),
            "indexes": self._get_indexes(),
            "foreign_keys": self._get_foreign_keys(),
            "partitions": self._get_partitions(),
            "sequences": self._get_sequences(),
            "views": self._get_views(),
            "materialized_views": self._get_materialized_views(),
        }
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get basic database information."""
        query = """
        SELECT 
            current_database() as database_name,
            pg_database_size(current_database()) as size_bytes,
            pg_size_pretty(pg_database_size(current_database())) as size_pretty,
            (SELECT count(*) FROM pg_stat_user_tables) as table_count,
            (SELECT count(*) FROM pg_stat_user_indexes) as index_count
        """
        result = self._safe_execute(query)
        return result[0] if result else {}
    
    def _get_schemas(self) -> List[Dict[str, Any]]:
        """Get all schemas in the database."""
        query = """
        SELECT 
            schema_name,
            schema_owner,
            (SELECT count(*) FROM information_schema.tables t 
             WHERE t.table_schema = s.schema_name) as table_count
        FROM information_schema.schemata s
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schema_name
        """
        return self._safe_execute(query)
    
    def _get_tables(self) -> List[Dict[str, Any]]:
        """Get detailed table information."""
        query = """
        SELECT 
            schemaname as schema_name,
            tablename as table_name,
            pg_total_relation_size(schemaname||'.'||tablename) as total_size_bytes,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size_pretty,
            pg_relation_size(schemaname||'.'||tablename) as table_size_bytes,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size_pretty,
            n_live_tup as row_count_estimate,
            n_dead_tup as dead_tuples,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """
        tables = self._safe_execute(query)
        
        # Get column information for each table
        for table in tables:
            table['columns'] = self._get_table_columns(
                table['schema_name'], 
                table['table_name']
            )
        
        return tables
    
    def _get_table_columns(self, schema: str, table: str) -> List[Dict[str, Any]]:
        """Get column information for a specific table."""
        query = """
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """
        return self._safe_execute(query, (schema, table))
    
    def _get_indexes(self) -> List[Dict[str, Any]]:
        """Get index information."""
        query = """
        SELECT 
            schemaname as schema_name,
            tablename as table_name,
            indexname as index_name,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
            idx_scan as index_scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched,
            pg_get_indexdef(indexrelid) as index_definition
        FROM pg_stat_user_indexes
        ORDER BY pg_relation_size(indexrelid) DESC
        """
        return self._safe_execute(query)
    
    def _get_foreign_keys(self) -> List[Dict[str, Any]]:
        """Get foreign key relationships."""
        query = """
        SELECT
            tc.table_schema as schema_name,
            tc.table_name,
            kcu.column_name,
            ccu.table_schema AS foreign_schema_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            tc.constraint_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_schema, tc.table_name
        """
        return self._safe_execute(query)
    
    def _get_partitions(self) -> List[Dict[str, Any]]:
        """Get partition information."""
        query = """
        SELECT
            nmsp_parent.nspname AS parent_schema,
            parent.relname AS parent_table,
            nmsp_child.nspname AS partition_schema,
            child.relname AS partition_name,
            pg_get_expr(child.relpartbound, child.oid) AS partition_expression
        FROM pg_inherits
        JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
        JOIN pg_class child ON pg_inherits.inhrelid = child.oid
        JOIN pg_namespace nmsp_parent ON nmsp_parent.oid = parent.relnamespace
        JOIN pg_namespace nmsp_child ON nmsp_child.oid = child.relnamespace
        WHERE parent.relkind = 'p'
        ORDER BY parent_schema, parent_table, partition_name
        """
        return self._safe_execute(query)
    
    def _get_sequences(self) -> List[Dict[str, Any]]:
        """Get sequence information."""
        query = """
        SELECT 
            sequence_schema as schema_name,
            sequence_name,
            data_type,
            start_value,
            minimum_value,
            maximum_value,
            increment
        FROM information_schema.sequences
        WHERE sequence_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY sequence_schema, sequence_name
        """
        return self._safe_execute(query)
    
    def _get_views(self) -> List[Dict[str, Any]]:
        """Get view information."""
        query = """
        SELECT 
            table_schema as schema_name,
            table_name as view_name,
            view_definition
        FROM information_schema.views
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name
        """
        return self._safe_execute(query)
    
    def _get_materialized_views(self) -> List[Dict[str, Any]]:
        """Get materialized view information."""
        query = """
        SELECT 
            schemaname as schema_name,
            matviewname as view_name,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
        FROM pg_matviews
        ORDER BY schemaname, matviewname
        """
        return self._safe_execute(query)
