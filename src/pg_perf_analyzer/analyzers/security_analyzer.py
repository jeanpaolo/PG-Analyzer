"""Database security analyzer for roles, permissions, and security settings."""

from typing import Dict, Any, List
from .base_analyzer import BaseAnalyzer


class SecurityAnalyzer(BaseAnalyzer):
    """Analyzes database security including roles, permissions, and configurations."""
    
    def get_analysis_name(self) -> str:
        return "Database Security Analysis"
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive security analysis.
        
        Returns:
            Dictionary containing security analysis results
        """
        return {
            "roles": self._get_roles(),
            "user_privileges": self._get_user_privileges(),
            "table_privileges": self._get_table_privileges(),
            "schema_privileges": self._get_schema_privileges(),
            "database_privileges": self._get_database_privileges(),
            "row_level_security": self._get_row_level_security(),
            "ssl_configuration": self._get_ssl_configuration(),
            "authentication_methods": self._get_authentication_methods(),
            "password_settings": self._get_password_settings(),
            "security_settings": self._get_security_settings(),
        }
    
    def _get_roles(self) -> List[Dict[str, Any]]:
        """Get all database roles and their attributes."""
        query = """
        SELECT 
            rolname as role_name,
            rolsuper as is_superuser,
            rolinherit as can_inherit,
            rolcreaterole as can_create_role,
            rolcreatedb as can_create_db,
            rolcanlogin as can_login,
            rolreplication as is_replication,
            rolconnlimit as connection_limit,
            rolvaliduntil as valid_until,
            ARRAY(
                SELECT b.rolname
                FROM pg_catalog.pg_auth_members m
                JOIN pg_catalog.pg_roles b ON (m.roleid = b.oid)
                WHERE m.member = r.oid
            ) as member_of
        FROM pg_catalog.pg_roles r
        WHERE rolname NOT LIKE 'pg_%'
        ORDER BY rolname
        """
        return self._safe_execute(query)
    
    def _get_user_privileges(self) -> List[Dict[str, Any]]:
        """Get user-level privileges."""
        query = """
        SELECT 
            grantee,
            privilege_type,
            is_grantable
        FROM information_schema.role_table_grants
        WHERE grantee NOT IN ('postgres', 'pg_database_owner')
        GROUP BY grantee, privilege_type, is_grantable
        ORDER BY grantee, privilege_type
        """
        return self._safe_execute(query)
    
    def _get_table_privileges(self) -> List[Dict[str, Any]]:
        """Get table-level privileges."""
        query = """
        SELECT 
            table_schema,
            table_name,
            grantee,
            privilege_type,
            is_grantable
        FROM information_schema.table_privileges
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name, grantee
        """
        return self._safe_execute(query)
    
    def _get_schema_privileges(self) -> List[Dict[str, Any]]:
        """Get schema-level privileges."""
        query = """
        SELECT 
            nspname as schema_name,
            nspowner::regrole as owner,
            nspacl as access_privileges
        FROM pg_namespace
        WHERE nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY nspname
        """
        return self._safe_execute(query)
    
    def _get_database_privileges(self) -> List[Dict[str, Any]]:
        """Get database-level privileges."""
        query = """
        SELECT 
            datname as database_name,
            datacl as access_privileges,
            datconnlimit as connection_limit
        FROM pg_database
        WHERE datname = current_database()
        """
        return self._safe_execute(query)
    
    def _get_row_level_security(self) -> List[Dict[str, Any]]:
        """Get row-level security policies."""
        query = """
        SELECT 
            schemaname as schema_name,
            tablename as table_name,
            policyname as policy_name,
            permissive,
            roles,
            cmd as command,
            qual as using_expression,
            with_check as with_check_expression
        FROM pg_policies
        ORDER BY schemaname, tablename, policyname
        """
        return self._safe_execute(query)
    
    def _get_ssl_configuration(self) -> Dict[str, Any]:
        """Get SSL/TLS configuration."""
        ssl_query = "SHOW ssl"
        ssl_enabled = self._safe_execute_scalar(ssl_query, default='off')
        
        result = {
            "ssl_enabled": ssl_enabled == 'on',
            "ssl_setting": ssl_enabled
        }
        
        if ssl_enabled == 'on':
            # Try to get additional SSL settings
            ssl_settings = [
                'ssl_cert_file',
                'ssl_key_file',
                'ssl_ca_file',
                'ssl_ciphers',
                'ssl_min_protocol_version',
                'ssl_max_protocol_version'
            ]
            
            for setting in ssl_settings:
                try:
                    value = self._safe_execute_scalar(f"SHOW {setting}")
                    result[setting] = value
                except:
                    result[setting] = None
        
        return result
    
    def _get_authentication_methods(self) -> Dict[str, Any]:
        """Get authentication method information."""
        # Note: pg_hba_file_rules requires superuser, so we'll try but handle gracefully
        query = """
        SELECT 
            line_number,
            type,
            database,
            user_name,
            address,
            auth_method
        FROM pg_hba_file_rules
        ORDER BY line_number
        """
        
        hba_rules = self._safe_execute(query, default=None)
        
        return {
            "hba_rules": hba_rules,
            "hba_accessible": hba_rules is not None,
            "note": "Requires superuser privileges to view pg_hba.conf rules" if hba_rules is None else None
        }
    
    def _get_password_settings(self) -> Dict[str, Any]:
        """Get password-related settings."""
        settings = {}
        
        password_settings = [
            'password_encryption',
            'ssl_passphrase_command_supports_reload'
        ]
        
        for setting in password_settings:
            value = self._safe_execute_scalar(f"SHOW {setting}")
            settings[setting] = value
        
        return settings
    
    def _get_security_settings(self) -> Dict[str, Any]:
        """Get general security-related configuration settings."""
        settings = {}
        
        security_params = [
            'log_connections',
            'log_disconnections',
            'log_duration',
            'log_statement',
            'log_hostname',
            'log_line_prefix',
            'row_security',
            'ssl',
            'password_encryption'
        ]
        
        for param in security_params:
            value = self._safe_execute_scalar(f"SHOW {param}")
            settings[param] = value
        
        return settings
