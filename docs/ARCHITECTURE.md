# PostgreSQL Performance Analyzer - Architecture

## Overview

The PostgreSQL Performance Analyzer is a Python application that connects to PostgreSQL databases, performs comprehensive analysis of database structure, security, and performance settings, and generates AI-powered reports with industry-standard recommendations.

## Architecture Components

### 1. Database Connection Layer (`src/pg_perf_analyzer/utils/db_connection.py`)
- Manages read-only PostgreSQL connections
- Connection pooling and error handling
- Transaction management with read-only mode enforcement

### 2. Analysis Modules (`src/pg_perf_analyzer/analyzers/`)

#### Structure Analyzer (`structure_analyzer.py`)
- Table and index analysis
- Column data types and constraints
- Foreign key relationships
- Partition information
- Schema organization

#### Security Analyzer (`security_analyzer.py`)
- User roles and permissions
- Authentication methods
- SSL/TLS configuration
- Row-level security policies
- Password policies
- Privilege escalation risks

#### Performance Analyzer (`performance_analyzer.py`)
- Query performance statistics
- Index usage and efficiency
- Table bloat detection
- Cache hit ratios
- Connection statistics
- Slow query identification
- Configuration parameter analysis

### 3. AI Integration Layer (`src/pg_perf_analyzer/ai/`)

#### AI Provider Interface (`ai_provider.py`)
- Abstract base class for AI providers
- Standardized prompt formatting
- Response parsing and validation

#### Local Model Provider (`local_provider.py`)
- Integration with local models via Ollama
- Support for llama2, mistral, codellama, etc.
- Offline operation capability

#### Cloud Provider (`cloud_provider.py`)
- OpenAI GPT models
- Anthropic Claude
- Google Gemini
- Configurable API endpoints

### 4. Report Generation (`src/pg_perf_analyzer/reports/`)

#### Report Builder (`report_builder.py`)
- Aggregates analysis results
- Formats data for AI consumption
- Generates structured reports

#### Report Formatter (`report_formatter.py`)
- Markdown output
- HTML output with styling
- JSON output for programmatic use
- PDF export capability

### 5. Configuration Management (`src/pg_perf_analyzer/utils/config.py`)
- YAML/JSON configuration files
- Environment variable support
- Secure credential management
- AI model selection and parameters

## Data Flow

```
1. User Configuration
   ↓
2. Database Connection (Read-Only)
   ↓
3. Parallel Analysis Execution
   ├── Structure Analysis
   ├── Security Analysis
   └── Performance Analysis
   ↓
4. Results Aggregation
   ↓
5. AI Analysis Request
   ├── Local Model (Ollama)
   └── Cloud Provider (OpenAI/Gemini/etc.)
   ↓
6. Report Generation
   ↓
7. Output (Markdown/HTML/JSON/PDF)
```

## Security Considerations

- **Read-Only Access**: All database queries use read-only transactions
- **Credential Storage**: Support for environment variables and secure config files
- **SQL Injection Prevention**: Parameterized queries throughout
- **API Key Management**: Secure handling of cloud provider credentials
- **No Data Exfiltration**: Analysis focuses on metadata and statistics, not actual data

## Industry Standards Referenced

- PostgreSQL official documentation
- OWASP Database Security Guidelines
- CIS PostgreSQL Benchmarks
- PostgreSQL Wiki performance tuning guides
- AWS RDS/Azure Database best practices

## Technology Stack

- **Python 3.11+**
- **psycopg2/psycopg3**: PostgreSQL adapter
- **SQLAlchemy**: Database abstraction (optional)
- **OpenAI Python SDK**: Cloud AI integration
- **Ollama Python SDK**: Local AI integration
- **Jinja2**: Report templating
- **PyYAML**: Configuration management
- **Rich**: CLI interface and formatting
- **WeasyPrint**: PDF generation

## Extensibility

The application is designed with extensibility in mind:
- New analyzers can be added by implementing the base analyzer interface
- Additional AI providers can be integrated via the provider interface
- Custom report formats can be added through the formatter system
- Plugin architecture for custom recommendations
