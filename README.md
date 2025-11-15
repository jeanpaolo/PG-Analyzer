# PostgreSQL Performance Analyzer

[![CI](https://github.com/YOUR_USERNAME/pg-perf-analyzer/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/pg-perf-analyzer/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Any-blue.svg)](https://www.postgresql.org/)

An AI-powered tool for analyzing PostgreSQL database performance, security, structure, and naming standards with industry-standard recommendations.

## Features

- **Comprehensive Database Analysis**
  - Structure analysis (tables, indexes, schemas, relationships)
  - Security analysis (roles, permissions, SSL, authentication)
  - Performance analysis (cache hits, query stats, bloat detection)
  - Naming standards analysis (conventions, consistency, reserved words)

- **AI-Powered Recommendations**
  - Support for local AI models via Ollama
  - Support for cloud AI providers (OpenAI, Gemini, Anthropic)
  - Industry-standard best practices and optimization suggestions

- **Multiple Output Formats**
  - Markdown reports
  - HTML reports with styling
  - JSON for programmatic access

- **Read-Only Operations**
  - All database queries are read-only
  - Safe to run on production databases
  - No data modification or schema changes

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database to analyze
- (Optional) Ollama for local AI analysis
- (Optional) API key for cloud AI providers

### Install from Source

```bash
# Clone or download the repository
cd pg-perf-analyzer

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Analyze database with cloud AI (requires OPENAI_API_KEY)
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --password mypass \
  --ai-provider cloud \
  --output report.md

# Analyze database with local AI (requires Ollama)
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --ai-provider local \
  --ai-model llama2 \
  --output report.md

# Skip AI analysis (raw data only)
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --skip-ai \
  --output report.json \
  --format json
```

### Check AI Provider Status

```bash
# Check local AI (Ollama)
pg-perf-analyzer check-ai --ai-provider local

# Check cloud AI
pg-perf-analyzer check-ai --ai-provider cloud
```

## Configuration

### Environment Variables

```bash
# Database password (alternative to --password)
export PGPASSWORD='your-password'

# OpenAI API key for cloud AI
export OPENAI_API_KEY='your-api-key'
```

### Configuration File

Create a `config.yaml` file:

```yaml
database:
  host: localhost
  port: 5432
  database: mydb
  user: myuser
  password: mypass
  sslmode: prefer

ai:
  provider: cloud
  cloud:
    provider: openai
    model: gpt-4.1-mini
    temperature: 0.7

output:
  format: markdown
  path: report.md
```

## Local AI Setup (Ollama)

### Install Ollama

Visit [https://ollama.ai](https://ollama.ai) and follow installation instructions.

### Pull a Model

```bash
# Pull llama2 model
ollama pull llama2

# Or use other models
ollama pull mistral
ollama pull codellama
```

### Verify Installation

```bash
pg-perf-analyzer check-ai --ai-provider local
```

## Cloud AI Setup

### OpenAI

```bash
export OPENAI_API_KEY='sk-...'
pg-perf-analyzer check-ai --ai-provider cloud
```

### Other Providers

The application uses OpenAI-compatible API format. Configure via environment variables or command-line options.

## Report Contents

The generated report includes:

1. **Executive Summary**
   - Database size and table count
   - Critical issues identified
   - Key recommendations

2. **Structure Analysis**
   - Database and schema information
   - Table sizes and row counts
   - Index statistics
   - Foreign key relationships
   - Views and materialized views

3. **Security Analysis**
   - User roles and permissions
   - Superuser accounts
   - SSL/TLS configuration
   - Row-level security policies
   - Authentication methods

4. **Performance Analysis**
   - Cache hit ratios
   - Index usage statistics
   - Unused indexes
   - Missing indexes (sequential scan analysis)
   - Table bloat detection
   - Configuration settings review
   - Vacuum statistics

5. **AI Recommendations**
   - Detailed analysis for each category
   - Prioritized action items
   - Industry best practices
   - Expected impact assessment

## Testing

A test environment is included with sample data:

```bash
# Set up test database (PostgreSQL must be installed)
sudo service postgresql start
sudo -u postgres psql -c "CREATE DATABASE testdb;"
sudo -u postgres psql -c "CREATE USER testuser WITH PASSWORD 'testpass';"
sudo -u postgres psql -d testdb -f tests/sample_data.sql

# Run analysis on test database
pg-perf-analyzer analyze \
  --host localhost \
  --database testdb \
  --user testuser \
  --password testpass \
  --skip-ai \
  --output test_report.md
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## License

MIT License

## Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Naming Standards Guide](docs/NAMING_STANDARDS.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Support

For issues, questions, or feature requests, please open an issue on the project repository.
