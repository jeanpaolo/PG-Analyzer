"""Report builder for aggregating and formatting analysis results."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class ReportBuilder:
    """Builds comprehensive reports from analysis results."""
    
    def __init__(self):
        """Initialize report builder."""
        self.report_data = {
            'metadata': {},
            'structure_analysis': {},
            'security_analysis': {},
            'performance_analysis': {},
            'naming_analysis': {},
            'ai_recommendations': {},
            'summary': {}
        }
    
    def set_metadata(self, db_config: Dict[str, Any], server_version: str):
        """
        Set report metadata.
        
        Args:
            db_config: Database configuration
            server_version: PostgreSQL server version
        """
        self.report_data['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'database_host': db_config.get('host', 'localhost'),
            'database_name': db_config.get('database'),
            'database_port': db_config.get('port', 5432),
            'server_version': server_version,
            'analyzer_version': '1.0.0'
        }
    
    def add_structure_analysis(self, analysis: Dict[str, Any]):
        """
        Add structure analysis results.
        
        Args:
            analysis: Structure analysis results
        """
        self.report_data['structure_analysis'] = analysis
    
    def add_security_analysis(self, analysis: Dict[str, Any]):
        """
        Add security analysis results.
        
        Args:
            analysis: Security analysis results
        """
        self.report_data['security_analysis'] = analysis
    
    def add_performance_analysis(self, analysis: Dict[str, Any]):
        """
        Add performance analysis results.
        
        Args:
            analysis: Performance analysis results
        """
        self.report_data['performance_analysis'] = analysis
    
    def add_naming_analysis(self, analysis: Dict[str, Any]):
        """
        Add naming standards analysis results.
        
        Args:
            analysis: Naming analysis results
        """
        self.report_data['naming_analysis'] = analysis
    
    def add_ai_recommendation(self, analysis_type: str, recommendation: str, provider: str):
        """
        Add AI-generated recommendation.
        
        Args:
            analysis_type: Type of analysis (structure, security, performance)
            recommendation: AI-generated recommendation text
            provider: AI provider name
        """
        self.report_data['ai_recommendations'][analysis_type] = {
            'recommendation': recommendation,
            'provider': provider,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_summary(self):
        """Generate executive summary from all analyses."""
        summary = {
            'database_size': None,
            'table_count': 0,
            'index_count': 0,
            'security_issues': [],
            'performance_issues': [],
            'key_recommendations': []
        }
        
        # Extract key metrics from structure analysis
        if 'structure_analysis' in self.report_data:
            structure = self.report_data['structure_analysis']
            if 'database_info' in structure:
                db_info = structure['database_info']
                summary['database_size'] = db_info.get('size_pretty')
                summary['table_count'] = db_info.get('table_count', 0)
                summary['index_count'] = db_info.get('index_count', 0)
        
        # Extract security issues
        if 'security_analysis' in self.report_data:
            security = self.report_data['security_analysis']
            
            # Check for superuser accounts
            if 'roles' in security:
                superusers = [r for r in security['roles'] if r.get('is_superuser')]
                if len(superusers) > 2:
                    summary['security_issues'].append(
                        f"Multiple superuser accounts detected ({len(superusers)})"
                    )
            
            # Check SSL configuration
            if 'ssl_configuration' in security:
                if not security['ssl_configuration'].get('ssl_enabled'):
                    summary['security_issues'].append("SSL/TLS is not enabled")
        
        # Extract performance issues
        if 'performance_analysis' in self.report_data:
            perf = self.report_data['performance_analysis']
            
            # Check cache hit ratios
            if 'cache_hit_ratios' in perf:
                cache = perf['cache_hit_ratios']
                heap_ratio = cache.get('heap_hit_ratio', 100)
                if heap_ratio < 90:
                    summary['performance_issues'].append(
                        f"Low heap cache hit ratio ({heap_ratio}%)"
                    )
            
            # Check for unused indexes
            if 'unused_indexes' in perf and perf['unused_indexes']:
                unused_count = len(perf['unused_indexes'])
                summary['performance_issues'].append(
                    f"{unused_count} unused indexes detected"
                )
            
            # Check for table bloat
            if 'table_bloat' in perf and perf['table_bloat']:
                bloated_tables = [t for t in perf['table_bloat'] if t.get('bloat_ratio', 0) > 20]
                if bloated_tables:
                    summary['performance_issues'].append(
                        f"{len(bloated_tables)} tables with significant bloat"
                    )
        
        self.report_data['summary'] = summary
    
    def get_report_data(self) -> Dict[str, Any]:
        """
        Get complete report data.
        
        Returns:
            Dictionary containing all report data
        """
        return self.report_data
    
    def to_json(self, indent: int = 2) -> str:
        """
        Export report as JSON.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string
        """
        return json.dumps(self.report_data, indent=indent, default=str)
    
    def get_structure_summary(self) -> Dict[str, Any]:
        """Get summary of structure analysis."""
        structure = self.report_data.get('structure_analysis', {})
        return {
            'database_info': structure.get('database_info', {}),
            'schema_count': len(structure.get('schemas', [])),
            'table_count': len(structure.get('tables', [])),
            'index_count': len(structure.get('indexes', [])),
            'foreign_key_count': len(structure.get('foreign_keys', [])),
            'view_count': len(structure.get('views', [])),
        }
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get summary of security analysis."""
        security = self.report_data.get('security_analysis', {})
        return {
            'role_count': len(security.get('roles', [])),
            'superuser_count': len([r for r in security.get('roles', []) if r.get('is_superuser')]),
            'ssl_enabled': security.get('ssl_configuration', {}).get('ssl_enabled', False),
            'rls_policy_count': len(security.get('row_level_security', [])),
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance analysis."""
        perf = self.report_data.get('performance_analysis', {})
        cache = perf.get('cache_hit_ratios', {})
        
        return {
            'heap_hit_ratio': cache.get('heap_hit_ratio', 0),
            'index_hit_ratio': cache.get('index_hit_ratio', 0),
            'unused_index_count': len(perf.get('unused_indexes', [])),
            'bloated_table_count': len(perf.get('table_bloat', [])),
            'active_connections': perf.get('connection_statistics', {}).get('active', 0),
        }
