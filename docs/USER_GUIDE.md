# User Guide

This guide provides comprehensive instructions for using the PostgreSQL Performance Analyzer.

## Overview

The PostgreSQL Performance Analyzer is a command-line tool that analyzes PostgreSQL databases and generates comprehensive reports with AI-powered recommendations. The tool performs three types of analysis:

1. **Structure Analysis** - Tables, indexes, schemas, relationships
2. **Security Analysis** - Roles, permissions, SSL, authentication
3. **Performance Analysis** - Cache hits, query stats, bloat detection

## Basic Usage

### Command Structure

```bash
pg-perf-analyzer [COMMAND] [OPTIONS]
```

### Available Commands

- `analyze` - Analyze a PostgreSQL database and generate a report
- `check-ai` - Check AI provider availability and configuration

## Analyzing a Database

### Basic Analysis

The simplest way to analyze a database:

```bash
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --password mypass \
  --output report.md
```

### Using Environment Variables

Set database credentials as environment variables to avoid exposing them in command history:

```bash
export PGPASSWORD='mypass'
export OPENAI_API_KEY='sk-...'

pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --output report.md
```

### Complete Example with All Options

```bash
pg-perf-analyzer analyze \
  --host localhost \
  --port 5432 \
  --database production_db \
  --user analyzer \
  --password secure_pass \
  --sslmode require \
  --ai-provider cloud \
  --ai-model gpt-4.1-mini \
  --api-key sk-your-key \
  --output reports/prod_analysis.md \
  --format markdown
```

## Command-Line Options

### Database Connection Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `--host` | Database host | localhost | No |
| `--port` | Database port | 5432 | No |
| `--database` | Database name | - | Yes |
| `--user` | Database user | - | Yes |
| `--password` | Database password | $PGPASSWORD | No |
| `--sslmode` | SSL mode (disable/prefer/require) | prefer | No |

### AI Provider Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `--ai-provider` | AI provider (local/cloud) | cloud | No |
| `--ai-model` | Model name | Provider default | No |
| `--api-key` | API key for cloud provider | $OPENAI_API_KEY | No* |
| `--skip-ai` | Skip AI analysis | False | No |

*Required for cloud provider unless set via environment variable

### Output Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `--output` | Output file path | report.md | No |
| `--format` | Output format (markdown/html/json) | markdown | No |

## AI Provider Configuration

### Using Local AI (Ollama)

Local AI runs on your machine without internet access or API keys.

**Basic usage:**
```bash
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --ai-provider local \
  --output report.md
```

**Specify model:**
```bash
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --ai-provider local \
  --ai-model mistral \
  --output report.md
```

**Available local models:**
- `llama2` (default, recommended)
- `mistral`
- `codellama`
- `llama3`
- Any model pulled via `ollama pull`

### Using Cloud AI

Cloud AI provides more powerful models but requires API keys and internet access.

**OpenAI (default):**
```bash
export OPENAI_API_KEY='sk-your-key'

pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --ai-provider cloud \
  --output report.md
```

**Specify model:**
```bash
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --ai-provider cloud \
  --ai-model gpt-4.1-mini \
  --output report.md
```

**Available cloud models:**
- `gpt-4.1-mini` (default, recommended)
- `gpt-4.1-nano`
- `gemini-2.5-flash`

### Skipping AI Analysis

For quick analysis without AI recommendations:

```bash
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --skip-ai \
  --output report.md
```

This generates a report with raw data and statistics only, without AI-generated recommendations.

## Output Formats

### Markdown Format (Default)

Generates a readable Markdown file suitable for viewing in text editors or converting to other formats.

```bash
pg-perf-analyzer analyze \
  --database mydb \
  --user myuser \
  --format markdown \
  --output report.md
```

**Use cases:**
- Human-readable reports
- Version control (Git)
- Converting to PDF or HTML later
- Documentation

### HTML Format

Generates a styled HTML file that can be opened in any web browser.

```bash
pg-perf-analyzer analyze \
  --database mydb \
  --user myuser \
  --format html \
  --output report.html
```

**Use cases:**
- Sharing with stakeholders
- Embedding in websites
- Professional presentations
- Email attachments

### JSON Format

Generates structured JSON data for programmatic access.

```bash
pg-perf-analyzer analyze \
  --database mydb \
  --user myuser \
  --format json \
  --output report.json
```

**Use cases:**
- Integration with other tools
- Automated processing
- Data analysis
- API responses

## Understanding the Report

### Report Structure

Every report contains the following sections:

1. **Report Information**
   - Generation timestamp
   - Database details
   - Server version

2. **Executive Summary**
   - Database size
   - Table and index counts
   - Critical issues identified

3. **Structure Analysis**
   - Database and schema information
   - Table details (size, rows, columns)
   - Index statistics
   - Foreign key relationships
   - Views and materialized views

4. **Security Analysis**
   - User roles and permissions
   - Superuser accounts
   - SSL/TLS configuration
   - Row-level security policies
   - Authentication methods

5. **Performance Analysis**
   - Cache hit ratios
   - Index usage statistics
   - Unused indexes
   - Missing indexes
   - Table bloat
   - Configuration settings
   - Vacuum statistics

6. **AI Recommendations** (if enabled)
   - Structure recommendations
   - Security recommendations
   - Performance recommendations

### Key Metrics Explained

#### Cache Hit Ratios

- **Heap Hit Ratio**: Percentage of table data read from cache vs disk
  - ✅ Good: > 90%
  - ⚠️ Warning: < 90%
  - 🔴 Critical: < 80%

- **Index Hit Ratio**: Percentage of index data read from cache vs disk
  - ✅ Good: > 90%
  - ⚠️ Warning: < 90%

#### Table Bloat

Dead tuples that haven't been cleaned up by VACUUM.

- **Bloat Ratio**: Percentage of dead tuples
  - ✅ Good: < 10%
  - ⚠️ Warning: 10-20%
  - 🔴 Critical: > 20%

#### Index Usage

- **Index Scans**: Number of times an index was used
  - Unused indexes (0 scans) waste space and slow down writes

## Common Use Cases

### 1. Production Database Health Check

```bash
# Monthly health check
pg-perf-analyzer analyze \
  --host prod-db.example.com \
  --database production \
  --user readonly_user \
  --ai-provider cloud \
  --output reports/$(date +%Y-%m-%d)_health_check.md
```

### 2. Pre-Migration Analysis

```bash
# Before major migration
pg-perf-analyzer analyze \
  --host old-server \
  --database legacy_db \
  --user admin \
  --ai-provider cloud \
  --format json \
  --output pre_migration_baseline.json
```

### 3. Security Audit

```bash
# Focus on security issues
pg-perf-analyzer analyze \
  --host localhost \
  --database sensitive_db \
  --user auditor \
  --ai-provider cloud \
  --output security_audit.md

# Review security section in the report
```

### 4. Performance Troubleshooting

```bash
# Identify performance bottlenecks
pg-perf-analyzer analyze \
  --host slow-db \
  --database app_db \
  --user dba \
  --ai-provider cloud \
  --output performance_analysis.md

# Check cache hit ratios, unused indexes, and bloat
```

### 5. Development Environment Setup

```bash
# Analyze development database
pg-perf-analyzer analyze \
  --host localhost \
  --database dev_db \
  --user developer \
  --ai-provider local \
  --ai-model llama2 \
  --skip-ai \
  --output dev_analysis.md
```

## Best Practices

### 1. Use Read-Only Users

Create dedicated read-only users for analysis to minimize security risks:

```sql
CREATE USER analyzer WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO analyzer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyzer;
```

### 2. Schedule Regular Analysis

Set up cron jobs for regular database health checks:

```bash
# Add to crontab (monthly on 1st at 2 AM)
0 2 1 * * /usr/local/bin/pg-perf-analyzer analyze \
  --host localhost --database mydb --user analyzer \
  --output /var/reports/$(date +\%Y-\%m)_report.md
```

### 3. Version Control Reports

Store reports in version control to track changes over time:

```bash
git add reports/
git commit -m "Monthly database analysis - $(date +%Y-%m)"
git push
```

### 4. Compare Reports Over Time

Generate JSON reports and compare metrics:

```bash
# Generate baseline
pg-perf-analyzer analyze --database mydb --user analyzer \
  --format json --output baseline.json

# After optimization
pg-perf-analyzer analyze --database mydb --user analyzer \
  --format json --output after_optimization.json

# Compare (using jq or custom script)
```

### 5. Act on Recommendations

Review AI recommendations and prioritize by:
- **High Priority**: Security vulnerabilities, critical performance issues
- **Medium Priority**: Unused indexes, configuration tuning
- **Low Priority**: Documentation, naming conventions

## Troubleshooting

### Connection Issues

```bash
# Test connection first
psql -h localhost -U myuser -d mydb -c "SELECT 1"

# Check SSL requirements
pg-perf-analyzer analyze --sslmode disable ...
```

### AI Provider Issues

```bash
# Check AI provider status
pg-perf-analyzer check-ai --ai-provider local
pg-perf-analyzer check-ai --ai-provider cloud

# Use --skip-ai if AI is unavailable
pg-perf-analyzer analyze --skip-ai ...
```

### Permission Errors

```bash
# Ensure user has SELECT permissions
# Run as database admin:
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyzer;
```

## Advanced Usage

### Custom Python Scripts

You can use the analyzer programmatically:

```python
from pg_perf_analyzer.utils import DatabaseConnection
from pg_perf_analyzer.analyzers import PerformanceAnalyzer
from pg_perf_analyzer.ai import CloudAIProvider

# Connect to database
db_config = {
    'host': 'localhost',
    'database': 'mydb',
    'user': 'myuser',
    'password': 'mypass'
}

with DatabaseConnection(db_config) as db:
    # Run analysis
    analyzer = PerformanceAnalyzer(db)
    results = analyzer.analyze()
    
    # Use AI for recommendations
    ai = CloudAIProvider({'api_key': 'sk-...'})
    recommendations = ai.analyze(results, 'performance')
    
    print(recommendations)
```

## Next Steps

- Review your first analysis report
- Set up automated monthly reports
- Implement high-priority recommendations
- Explore different AI models and providers
- Integrate with your monitoring tools
