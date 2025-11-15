"""Database performance analyzer for queries, indexes, and configuration."""

from typing import Dict, Any, List
from .base_analyzer import BaseAnalyzer


class PerformanceAnalyzer(BaseAnalyzer):
    """Analyzes database performance including queries, indexes, and settings."""
    
    def get_analysis_name(self) -> str:
        return "Database Performance Analysis"
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive performance analysis.
        
        Returns:
            Dictionary containing performance analysis results
        """
        return {
            "database_statistics": self._get_database_statistics(),
            "cache_hit_ratios": self._get_cache_hit_ratios(),
            "table_statistics": self._get_table_statistics(),
            "index_usage": self._get_index_usage(),
            "unused_indexes": self._get_unused_indexes(),
            "missing_indexes": self._get_missing_indexes(),
            "table_bloat": self._get_table_bloat(),
            "slow_queries": self._get_slow_queries(),
            "connection_statistics": self._get_connection_statistics(),
            "lock_statistics": self._get_lock_statistics(),
            "configuration_settings": self._get_configuration_settings(),
            "checkpoint_statistics": self._get_checkpoint_statistics(),
            "vacuum_statistics": self._get_vacuum_statistics(),
        }
    
    def _get_database_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics."""
        query = """
        SELECT 
            numbackends as active_connections,
            xact_commit as transactions_committed,
            xact_rollback as transactions_rolled_back,
            blks_read as blocks_read,
            blks_hit as blocks_hit,
            tup_returned as tuples_returned,
            tup_fetched as tuples_fetched,
            tup_inserted as tuples_inserted,
            tup_updated as tuples_updated,
            tup_deleted as tuples_deleted,
            conflicts,
            temp_files,
            temp_bytes,
            deadlocks,
            blk_read_time,
            blk_write_time,
            stats_reset
        FROM pg_stat_database
        WHERE datname = current_database()
        """
        result = self._safe_execute(query)
        return result[0] if result else {}
    
    def _get_cache_hit_ratios(self) -> Dict[str, Any]:
        """Calculate cache hit ratios."""
        query = """
        SELECT 
            sum(heap_blks_read) as heap_read,
            sum(heap_blks_hit) as heap_hit,
            sum(idx_blks_read) as idx_read,
            sum(idx_blks_hit) as idx_hit,
            CASE 
                WHEN sum(heap_blks_hit) + sum(heap_blks_read) = 0 THEN 0
                ELSE round(100.0 * sum(heap_blks_hit) / 
                    (sum(heap_blks_hit) + sum(heap_blks_read)), 2)
            END as heap_hit_ratio,
            CASE 
                WHEN sum(idx_blks_hit) + sum(idx_blks_read) = 0 THEN 0
                ELSE round(100.0 * sum(idx_blks_hit) / 
                    (sum(idx_blks_hit) + sum(idx_blks_read)), 2)
            END as index_hit_ratio
        FROM pg_statio_user_tables
        """
        result = self._safe_execute(query)
        return result[0] if result else {}
    
    def _get_table_statistics(self) -> List[Dict[str, Any]]:
        """Get per-table performance statistics."""
        query = """
        SELECT 
            schemaname as schema_name,
            relname as table_name,
            seq_scan as sequential_scans,
            seq_tup_read as sequential_tuples_read,
            idx_scan as index_scans,
            idx_tup_fetch as index_tuples_fetched,
            n_tup_ins as tuples_inserted,
            n_tup_upd as tuples_updated,
            n_tup_del as tuples_deleted,
            n_tup_hot_upd as hot_updates,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples,
            CASE 
                WHEN n_live_tup = 0 THEN 0
                ELSE round(100.0 * n_dead_tup / (n_live_tup + n_dead_tup), 2)
            END as dead_tuple_ratio,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze,
            vacuum_count,
            autovacuum_count,
            analyze_count,
            autoanalyze_count
        FROM pg_stat_user_tables
        ORDER BY seq_scan + idx_scan DESC
        LIMIT 50
        """
        return self._safe_execute(query)
    
    def _get_index_usage(self) -> List[Dict[str, Any]]:
        """Get index usage statistics."""
        query = """
        SELECT 
            schemaname as schema_name,
            tablename as table_name,
            indexname as index_name,
            idx_scan as index_scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
            pg_relation_size(indexrelid) as index_size_bytes
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC
        LIMIT 50
        """
        return self._safe_execute(query)
    
    def _get_unused_indexes(self) -> List[Dict[str, Any]]:
        """Identify potentially unused indexes."""
        query = """
        SELECT 
            schemaname as schema_name,
            tablename as table_name,
            indexname as index_name,
            idx_scan as index_scans,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
            pg_relation_size(indexrelid) as index_size_bytes
        FROM pg_stat_user_indexes
        WHERE idx_scan = 0
            AND indexrelname NOT LIKE '%_pkey'
        ORDER BY pg_relation_size(indexrelid) DESC
        """
        return self._safe_execute(query)
    
    def _get_missing_indexes(self) -> List[Dict[str, Any]]:
        """Identify tables with sequential scans that might benefit from indexes."""
        query = """
        SELECT 
            schemaname as schema_name,
            relname as table_name,
            seq_scan as sequential_scans,
            seq_tup_read as tuples_read,
            idx_scan as index_scans,
            n_live_tup as live_tuples,
            pg_size_pretty(pg_relation_size(schemaname||'.'||relname)) as table_size
        FROM pg_stat_user_tables
        WHERE seq_scan > 0
            AND idx_scan < seq_scan
            AND n_live_tup > 10000
        ORDER BY seq_scan DESC
        LIMIT 20
        """
        return self._safe_execute(query)
    
    def _get_table_bloat(self) -> List[Dict[str, Any]]:
        """Estimate table bloat."""
        query = """
        SELECT
            schemaname as schema_name,
            tablename as table_name,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples,
            CASE 
                WHEN n_live_tup + n_dead_tup = 0 THEN 0
                ELSE round(100.0 * n_dead_tup / (n_live_tup + n_dead_tup), 2)
            END as bloat_ratio,
            last_autovacuum,
            last_vacuum
        FROM pg_stat_user_tables
        WHERE n_dead_tup > 1000
        ORDER BY n_dead_tup DESC
        LIMIT 20
        """
        return self._safe_execute(query)
    
    def _get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get slow query statistics (requires pg_stat_statements extension)."""
        # Check if pg_stat_statements is available
        check_query = """
        SELECT EXISTS (
            SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
        ) as has_pg_stat_statements
        """
        has_extension = self._safe_execute_scalar(check_query, default=False)
        
        if not has_extension:
            return [{
                "note": "pg_stat_statements extension not installed",
                "recommendation": "Install pg_stat_statements to track query performance"
            }]
        
        query = """
        SELECT 
            substring(query, 1, 100) as query_preview,
            calls,
            total_exec_time as total_time_ms,
            mean_exec_time as mean_time_ms,
            max_exec_time as max_time_ms,
            stddev_exec_time as stddev_time_ms,
            rows,
            shared_blks_hit,
            shared_blks_read,
            shared_blks_written
        FROM pg_stat_statements
        WHERE query NOT LIKE '%pg_stat_statements%'
        ORDER BY mean_exec_time DESC
        LIMIT 20
        """
        return self._safe_execute(query)
    
    def _get_connection_statistics(self) -> Dict[str, Any]:
        """Get connection statistics."""
        query = """
        SELECT 
            count(*) as total_connections,
            count(*) FILTER (WHERE state = 'active') as active,
            count(*) FILTER (WHERE state = 'idle') as idle,
            count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
            count(*) FILTER (WHERE wait_event_type IS NOT NULL) as waiting,
            max(EXTRACT(EPOCH FROM (now() - backend_start))) as max_connection_age_seconds
        FROM pg_stat_activity
        WHERE pid != pg_backend_pid()
        """
        result = self._safe_execute(query)
        return result[0] if result else {}
    
    def _get_lock_statistics(self) -> Dict[str, Any]:
        """Get lock statistics."""
        query = """
        SELECT 
            mode,
            count(*) as lock_count
        FROM pg_locks
        GROUP BY mode
        ORDER BY count(*) DESC
        """
        locks = self._safe_execute(query)
        
        blocking_query = """
        SELECT count(*) as blocked_queries
        FROM pg_stat_activity
        WHERE wait_event_type = 'Lock'
        """
        blocked = self._safe_execute_scalar(blocking_query, default=0)
        
        return {
            "locks_by_mode": locks,
            "blocked_queries": blocked
        }
    
    def _get_configuration_settings(self) -> Dict[str, Any]:
        """Get performance-related configuration settings."""
        settings = {}
        
        performance_params = [
            'shared_buffers',
            'effective_cache_size',
            'work_mem',
            'maintenance_work_mem',
            'max_connections',
            'max_parallel_workers',
            'max_parallel_workers_per_gather',
            'max_worker_processes',
            'random_page_cost',
            'seq_page_cost',
            'effective_io_concurrency',
            'wal_buffers',
            'checkpoint_completion_target',
            'default_statistics_target',
            'autovacuum',
            'autovacuum_max_workers',
            'autovacuum_naptime'
        ]
        
        for param in performance_params:
            value = self._safe_execute_scalar(f"SHOW {param}")
            settings[param] = value
        
        return settings
    
    def _get_checkpoint_statistics(self) -> Dict[str, Any]:
        """Get checkpoint statistics."""
        query = """
        SELECT 
            checkpoints_timed,
            checkpoints_req as checkpoints_requested,
            checkpoint_write_time,
            checkpoint_sync_time,
            buffers_checkpoint,
            buffers_clean,
            buffers_backend,
            buffers_alloc,
            stats_reset
        FROM pg_stat_bgwriter
        """
        result = self._safe_execute(query)
        return result[0] if result else {}
    
    def _get_vacuum_statistics(self) -> List[Dict[str, Any]]:
        """Get vacuum statistics for tables."""
        query = """
        SELECT 
            schemaname as schema_name,
            relname as table_name,
            last_vacuum,
            last_autovacuum,
            vacuum_count,
            autovacuum_count,
            n_dead_tup as dead_tuples,
            n_live_tup as live_tuples,
            CASE 
                WHEN last_autovacuum IS NULL THEN 'Never'
                ELSE EXTRACT(EPOCH FROM (now() - last_autovacuum))::text || ' seconds ago'
            END as time_since_autovacuum
        FROM pg_stat_user_tables
        ORDER BY n_dead_tup DESC
        LIMIT 20
        """
        return self._safe_execute(query)
