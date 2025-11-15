"""Base AI provider interface for analysis and recommendations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI provider.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config or {}
    
    @abstractmethod
    def analyze(self, analysis_data: Dict[str, Any], analysis_type: str) -> str:
        """
        Analyze database data and generate recommendations.
        
        Args:
            analysis_data: Dictionary containing analysis results
            analysis_type: Type of analysis (structure, security, performance)
            
        Returns:
            Analysis report as string
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the AI provider.
        
        Returns:
            Provider name string
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and properly configured.
        
        Returns:
            True if available, False otherwise
        """
        pass
    
    def _build_prompt(self, analysis_data: Dict[str, Any], analysis_type: str) -> str:
        """
        Build a prompt for the AI model based on analysis data.
        
        Args:
            analysis_data: Dictionary containing analysis results
            analysis_type: Type of analysis
            
        Returns:
            Formatted prompt string
        """
        if analysis_type == "structure":
            return self._build_structure_prompt(analysis_data)
        elif analysis_type == "security":
            return self._build_security_prompt(analysis_data)
        elif analysis_type == "performance":
            return self._build_performance_prompt(analysis_data)
        else:
            return self._build_general_prompt(analysis_data, analysis_type)
    
    def _build_structure_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for structure analysis."""
        prompt = """You are a PostgreSQL database expert. Analyze the following database structure information and provide recommendations following industry best practices.

Database Structure Analysis:
"""
        
        if 'database_info' in data:
            prompt += f"\n## Database Information\n{self._format_dict(data['database_info'])}\n"
        
        if 'tables' in data and data['tables']:
            prompt += f"\n## Tables ({len(data['tables'])} total)\n"
            for table in data['tables'][:10]:  # Limit to first 10 tables
                prompt += f"- {table.get('schema_name')}.{table.get('table_name')}: "
                prompt += f"{table.get('total_size_pretty')}, {table.get('row_count_estimate')} rows\n"
                # Add column information for naming analysis
                if 'columns' in table and table['columns']:
                    prompt += f"  Columns: {', '.join([col.get('column_name', '') for col in table['columns'][:5]])}\n"
        
        if 'indexes' in data and data['indexes']:
            prompt += f"\n## Indexes ({len(data['indexes'])} total)\n"
            unused_count = sum(1 for idx in data['indexes'] if idx.get('index_scans', 0) == 0)
            prompt += f"- Total indexes: {len(data['indexes'])}\n"
            prompt += f"- Unused indexes: {unused_count}\n"
            # Include sample index names for naming analysis
            if len(data['indexes']) > 0:
                prompt += "\n  Sample index names:\n"
                for idx in data['indexes'][:5]:
                    prompt += f"  - {idx.get('index_name', '')} on {idx.get('schema_name', '')}.{idx.get('table_name', '')}\n"
        
        prompt += """

Please provide:
1. Overall assessment of the database structure

2. Naming Standards Analysis:
   - Evaluate table naming conventions (snake_case, PascalCase, camelCase)
   - Assess column naming consistency and clarity
   - Review index naming patterns (e.g., idx_tablename_columnname)
   - Check for reserved words or problematic names
   - Identify naming inconsistencies across schemas
   - Verify plural vs singular table names
   - Check for abbreviations and acronyms clarity
   - Assess foreign key naming conventions
   
3. Data Structure Issues:
   - Inappropriate data types for columns
   - Missing primary keys or unique constraints
   - Missing foreign key relationships
   - Lack of NOT NULL constraints where appropriate
   - Missing indexes on frequently queried columns
   
4. Recommendations for improvement following PostgreSQL best practices:
   - Specific naming standard violations to fix
   - Suggested renaming for non-compliant objects
   - Data type optimizations
   - Missing constraints to add
   - Index optimization suggestions
   
5. Specific action items with priority levels:
   - High: Critical naming issues, missing primary keys, data integrity risks
   - Medium: Naming inconsistencies, suboptimal data types, missing indexes
   - Low: Minor naming improvements, documentation needs

Format your response in clear sections with actionable recommendations. For naming standards, provide specific examples of violations and suggested corrections."""
        
        return prompt
    
    def _build_security_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for security analysis."""
        prompt = """You are a PostgreSQL security expert. Analyze the following database security configuration and provide recommendations following industry best practices and security standards (OWASP, CIS PostgreSQL Benchmark).

Database Security Analysis:
"""
        
        if 'roles' in data and data['roles']:
            prompt += f"\n## Roles ({len(data['roles'])} total)\n"
            superusers = [r for r in data['roles'] if r.get('is_superuser')]
            prompt += f"- Superuser accounts: {len(superusers)}\n"
            for su in superusers:
                prompt += f"  - {su.get('role_name')}\n"
        
        if 'ssl_configuration' in data:
            ssl_config = data['ssl_configuration']
            prompt += f"\n## SSL Configuration\n"
            prompt += f"- SSL Enabled: {ssl_config.get('ssl_enabled')}\n"
        
        if 'row_level_security' in data and data['row_level_security']:
            prompt += f"\n## Row-Level Security\n"
            prompt += f"- RLS Policies: {len(data['row_level_security'])}\n"
        
        if 'security_settings' in data:
            prompt += f"\n## Security Settings\n{self._format_dict(data['security_settings'])}\n"
        
        prompt += """

Please provide:
1. Security risk assessment (Critical/High/Medium/Low risks)
2. Analysis of authentication and authorization configurations
3. SSL/TLS configuration review
4. Privilege escalation risks
5. Compliance with security best practices (OWASP, CIS)
6. Specific remediation steps with priority levels

Format your response in clear sections with actionable security recommendations."""
        
        return prompt
    
    def _build_performance_prompt(self, data: Dict[str, Any]) -> str:
        """Build prompt for performance analysis."""
        prompt = """You are a PostgreSQL performance tuning expert. Analyze the following database performance metrics and provide optimization recommendations following industry best practices.

Database Performance Analysis:
"""
        
        if 'cache_hit_ratios' in data:
            cache = data['cache_hit_ratios']
            prompt += f"\n## Cache Hit Ratios\n"
            prompt += f"- Heap Hit Ratio: {cache.get('heap_hit_ratio')}%\n"
            prompt += f"- Index Hit Ratio: {cache.get('index_hit_ratio')}%\n"
        
        if 'unused_indexes' in data and data['unused_indexes']:
            prompt += f"\n## Unused Indexes\n"
            prompt += f"- Count: {len(data['unused_indexes'])}\n"
            total_size = sum(idx.get('index_size_bytes', 0) for idx in data['unused_indexes'])
            prompt += f"- Total wasted space: ~{total_size / (1024*1024):.2f} MB\n"
        
        if 'missing_indexes' in data and data['missing_indexes']:
            prompt += f"\n## Tables with High Sequential Scans\n"
            for table in data['missing_indexes'][:5]:
                prompt += f"- {table.get('schema_name')}.{table.get('table_name')}: "
                prompt += f"{table.get('sequential_scans')} seq scans\n"
        
        if 'table_bloat' in data and data['table_bloat']:
            prompt += f"\n## Table Bloat\n"
            for table in data['table_bloat'][:5]:
                prompt += f"- {table.get('schema_name')}.{table.get('table_name')}: "
                prompt += f"{table.get('bloat_ratio')}% dead tuples\n"
        
        if 'configuration_settings' in data:
            prompt += f"\n## Key Configuration Settings\n"
            settings = data['configuration_settings']
            for key in ['shared_buffers', 'work_mem', 'effective_cache_size', 'max_connections']:
                if key in settings:
                    prompt += f"- {key}: {settings[key]}\n"
        
        prompt += """

Please provide:
1. Overall performance assessment
2. Analysis of cache hit ratios and memory usage
3. Index optimization recommendations (unused indexes to drop, missing indexes to create)
4. Query performance issues and solutions
5. Configuration tuning recommendations
6. Vacuum and maintenance recommendations
7. Specific action items with expected performance impact (High/Medium/Low)

Format your response in clear sections with actionable performance recommendations."""
        
        return prompt
    
    def _build_general_prompt(self, data: Dict[str, Any], analysis_type: str) -> str:
        """Build a general prompt for unknown analysis types."""
        prompt = f"""You are a PostgreSQL database expert. Analyze the following {analysis_type} data and provide recommendations.

Analysis Data:
{self._format_dict(data)}

Please provide detailed analysis and actionable recommendations."""
        
        return prompt
    
    def _format_dict(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary for inclusion in prompt."""
        lines = []
        prefix = "  " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_dict(value, indent + 1))
            elif isinstance(value, list):
                if value and len(value) < 10:
                    lines.append(f"{prefix}{key}: {value}")
                else:
                    lines.append(f"{prefix}{key}: [{len(value)} items]")
            else:
                lines.append(f"{prefix}{key}: {value}")
        
        return "\n".join(lines)
