"""Naming standards analyzer for database objects."""

import re
from typing import Dict, Any, List
from .base_analyzer import BaseAnalyzer


class NamingAnalyzer(BaseAnalyzer):
    """Analyzes database naming conventions and standards compliance."""
    
    # PostgreSQL reserved words (sample - add more as needed)
    RESERVED_WORDS = {
        'user', 'order', 'group', 'table', 'index', 'select', 'insert', 
        'update', 'delete', 'from', 'where', 'join', 'left', 'right',
        'inner', 'outer', 'on', 'as', 'and', 'or', 'not', 'null',
        'default', 'primary', 'foreign', 'key', 'constraint', 'check'
    }
    
    def get_analysis_name(self) -> str:
        return "Naming Standards Analysis"
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive naming standards analysis.
        
        Returns:
            Dictionary containing naming analysis results
        """
        return {
            "table_naming": self._analyze_table_naming(),
            "column_naming": self._analyze_column_naming(),
            "index_naming": self._analyze_index_naming(),
            "constraint_naming": self._analyze_constraint_naming(),
            "schema_naming": self._analyze_schema_naming(),
            "naming_summary": self._generate_naming_summary(),
        }
    
    def _analyze_table_naming(self) -> Dict[str, Any]:
        """Analyze table naming conventions."""
        query = """
        SELECT 
            schemaname as schema_name,
            tablename as table_name
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schemaname, tablename
        """
        tables = self._safe_execute(query)
        
        analysis = {
            "total_tables": len(tables),
            "naming_patterns": {},
            "issues": [],
            "reserved_words": [],
            "case_inconsistencies": [],
            "plural_singular_mix": []
        }
        
        snake_case = 0
        camel_case = 0
        pascal_case = 0
        mixed_case = 0
        
        for table in tables:
            table_name = table['table_name']
            
            # Check naming pattern
            if self._is_snake_case(table_name):
                snake_case += 1
            elif self._is_camel_case(table_name):
                camel_case += 1
            elif self._is_pascal_case(table_name):
                pascal_case += 1
            else:
                mixed_case += 1
                analysis['case_inconsistencies'].append({
                    'schema': table['schema_name'],
                    'table': table_name,
                    'issue': 'Mixed or inconsistent case'
                })
            
            # Check for reserved words
            if table_name.lower() in self.RESERVED_WORDS:
                analysis['reserved_words'].append({
                    'schema': table['schema_name'],
                    'table': table_name,
                    'issue': f"'{table_name}' is a PostgreSQL reserved word"
                })
            
            # Check for problematic patterns
            if len(table_name) < 3:
                analysis['issues'].append({
                    'schema': table['schema_name'],
                    'table': table_name,
                    'issue': 'Table name too short (< 3 characters)'
                })
            
            if len(table_name) > 63:
                analysis['issues'].append({
                    'schema': table['schema_name'],
                    'table': table_name,
                    'issue': 'Table name exceeds PostgreSQL limit (63 characters)'
                })
            
            # Check for numbers at start
            if table_name[0].isdigit():
                analysis['issues'].append({
                    'schema': table['schema_name'],
                    'table': table_name,
                    'issue': 'Table name starts with a number'
                })
        
        analysis['naming_patterns'] = {
            'snake_case': snake_case,
            'camelCase': camel_case,
            'PascalCase': pascal_case,
            'mixed_case': mixed_case
        }
        
        # Determine dominant pattern
        patterns = analysis['naming_patterns']
        dominant = max(patterns, key=patterns.get)
        analysis['dominant_pattern'] = dominant
        analysis['consistency_score'] = round(100 * patterns[dominant] / max(len(tables), 1), 2)
        
        return analysis
    
    def _analyze_column_naming(self) -> Dict[str, Any]:
        """Analyze column naming conventions."""
        query = """
        SELECT 
            table_schema as schema_name,
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name, ordinal_position
        """
        columns = self._safe_execute(query)
        
        analysis = {
            "total_columns": len(columns),
            "naming_patterns": {},
            "issues": [],
            "reserved_words": [],
            "common_prefixes": {},
            "common_suffixes": {}
        }
        
        snake_case = 0
        camel_case = 0
        pascal_case = 0
        mixed_case = 0
        
        for col in columns:
            col_name = col['column_name']
            
            # Check naming pattern
            if self._is_snake_case(col_name):
                snake_case += 1
            elif self._is_camel_case(col_name):
                camel_case += 1
            elif self._is_pascal_case(col_name):
                pascal_case += 1
            else:
                mixed_case += 1
            
            # Check for reserved words
            if col_name.lower() in self.RESERVED_WORDS:
                analysis['reserved_words'].append({
                    'table': f"{col['schema_name']}.{col['table_name']}",
                    'column': col_name,
                    'issue': f"'{col_name}' is a PostgreSQL reserved word"
                })
            
            # Track common prefixes/suffixes
            if '_' in col_name:
                parts = col_name.split('_')
                if len(parts) > 1:
                    prefix = parts[0]
                    suffix = parts[-1]
                    analysis['common_prefixes'][prefix] = analysis['common_prefixes'].get(prefix, 0) + 1
                    analysis['common_suffixes'][suffix] = analysis['common_suffixes'].get(suffix, 0) + 1
            
            # Check for problematic patterns
            if len(col_name) > 63:
                analysis['issues'].append({
                    'table': f"{col['schema_name']}.{col['table_name']}",
                    'column': col_name,
                    'issue': 'Column name exceeds PostgreSQL limit (63 characters)'
                })
        
        analysis['naming_patterns'] = {
            'snake_case': snake_case,
            'camelCase': camel_case,
            'PascalCase': pascal_case,
            'mixed_case': mixed_case
        }
        
        # Get top prefixes and suffixes
        analysis['top_prefixes'] = sorted(
            analysis['common_prefixes'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        analysis['top_suffixes'] = sorted(
            analysis['common_suffixes'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return analysis
    
    def _analyze_index_naming(self) -> Dict[str, Any]:
        """Analyze index naming conventions."""
        query = """
        SELECT 
            schemaname as schema_name,
            tablename as table_name,
            indexname as index_name
        FROM pg_indexes
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schemaname, tablename, indexname
        """
        indexes = self._safe_execute(query)
        
        analysis = {
            "total_indexes": len(indexes),
            "naming_patterns": {},
            "issues": [],
            "conventions": {}
        }
        
        has_prefix = 0
        no_prefix = 0
        pkey_pattern = 0
        idx_pattern = 0
        other_pattern = 0
        
        for idx in indexes:
            idx_name = idx['index_name']
            
            # Check for common prefixes
            if idx_name.startswith('idx_'):
                idx_pattern += 1
                has_prefix += 1
            elif idx_name.endswith('_pkey'):
                pkey_pattern += 1
                has_prefix += 1
            elif idx_name.startswith('pk_') or idx_name.startswith('fk_') or idx_name.startswith('uk_'):
                has_prefix += 1
                other_pattern += 1
            else:
                no_prefix += 1
                analysis['issues'].append({
                    'schema': idx['schema_name'],
                    'table': idx['table_name'],
                    'index': idx_name,
                    'issue': 'Index name lacks standard prefix (idx_, pk_, fk_, uk_)'
                })
            
            # Check if index name includes table name
            table_name = idx['table_name']
            if table_name not in idx_name and not idx_name.endswith('_pkey'):
                analysis['issues'].append({
                    'schema': idx['schema_name'],
                    'table': table_name,
                    'index': idx_name,
                    'issue': f"Index name doesn't include table name '{table_name}'"
                })
        
        analysis['naming_patterns'] = {
            'with_prefix': has_prefix,
            'no_prefix': no_prefix
        }
        
        analysis['conventions'] = {
            'idx_prefix': idx_pattern,
            'pkey_suffix': pkey_pattern,
            'other_prefix': other_pattern
        }
        
        return analysis
    
    def _analyze_constraint_naming(self) -> Dict[str, Any]:
        """Analyze constraint naming conventions."""
        query = """
        SELECT 
            tc.table_schema as schema_name,
            tc.table_name,
            tc.constraint_name,
            tc.constraint_type
        FROM information_schema.table_constraints tc
        WHERE tc.table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY tc.table_schema, tc.table_name, tc.constraint_name
        """
        constraints = self._safe_execute(query)
        
        analysis = {
            "total_constraints": len(constraints),
            "by_type": {},
            "naming_patterns": {},
            "issues": []
        }
        
        for constraint in constraints:
            constraint_type = constraint['constraint_type']
            constraint_name = constraint['constraint_name']
            
            # Count by type
            analysis['by_type'][constraint_type] = analysis['by_type'].get(constraint_type, 0) + 1
            
            # Check naming conventions
            expected_prefix = {
                'PRIMARY KEY': 'pk_',
                'FOREIGN KEY': 'fk_',
                'UNIQUE': 'uk_',
                'CHECK': 'ck_'
            }
            
            if constraint_type in expected_prefix:
                prefix = expected_prefix[constraint_type]
                if not constraint_name.startswith(prefix) and not constraint_name.endswith('_pkey'):
                    analysis['issues'].append({
                        'schema': constraint['schema_name'],
                        'table': constraint['table_name'],
                        'constraint': constraint_name,
                        'type': constraint_type,
                        'issue': f"Constraint doesn't follow naming convention (expected prefix: {prefix})"
                    })
        
        return analysis
    
    def _analyze_schema_naming(self) -> Dict[str, Any]:
        """Analyze schema naming conventions."""
        query = """
        SELECT 
            schema_name,
            schema_owner
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schema_name
        """
        schemas = self._safe_execute(query)
        
        analysis = {
            "total_schemas": len(schemas),
            "schemas": [],
            "issues": []
        }
        
        for schema in schemas:
            schema_name = schema['schema_name']
            analysis['schemas'].append(schema_name)
            
            # Check for problematic patterns
            if not self._is_snake_case(schema_name) and not schema_name.islower():
                analysis['issues'].append({
                    'schema': schema_name,
                    'issue': 'Schema name not in lowercase or snake_case'
                })
        
        return analysis
    
    def _generate_naming_summary(self) -> Dict[str, Any]:
        """Generate overall naming standards summary."""
        table_analysis = self._analyze_table_naming()
        column_analysis = self._analyze_column_naming()
        index_analysis = self._analyze_index_naming()
        
        total_issues = (
            len(table_analysis.get('issues', [])) +
            len(table_analysis.get('reserved_words', [])) +
            len(column_analysis.get('issues', [])) +
            len(column_analysis.get('reserved_words', [])) +
            len(index_analysis.get('issues', []))
        )
        
        return {
            "total_naming_issues": total_issues,
            "table_consistency": table_analysis.get('consistency_score', 0),
            "dominant_table_pattern": table_analysis.get('dominant_pattern', 'unknown'),
            "reserved_word_violations": (
                len(table_analysis.get('reserved_words', [])) +
                len(column_analysis.get('reserved_words', []))
            ),
            "recommendation": self._get_naming_recommendation(table_analysis, column_analysis)
        }
    
    def _get_naming_recommendation(self, table_analysis: Dict, column_analysis: Dict) -> str:
        """Generate naming recommendation based on analysis."""
        table_pattern = table_analysis.get('dominant_pattern', 'unknown')
        consistency = table_analysis.get('consistency_score', 0)
        
        if consistency >= 80:
            return f"Good: {consistency}% of tables follow {table_pattern} convention. Maintain this standard."
        elif consistency >= 50:
            return f"Fair: {consistency}% of tables follow {table_pattern}. Consider standardizing remaining tables."
        else:
            return f"Poor: Only {consistency}% consistency. Recommend establishing and enforcing a naming standard (preferably snake_case)."
    
    # Helper methods for pattern detection
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention."""
        return bool(re.match(r'^[a-z][a-z0-9_]*$', name))
    
    def _is_camel_case(self, name: str) -> bool:
        """Check if name follows camelCase convention."""
        return bool(re.match(r'^[a-z][a-zA-Z0-9]*$', name)) and any(c.isupper() for c in name)
    
    def _is_pascal_case(self, name: str) -> bool:
        """Check if name follows PascalCase convention."""
        return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))
