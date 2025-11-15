# Quick Start Guide

Get started with PostgreSQL Performance Analyzer in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database to analyze
- (Optional) OpenAI API key for AI recommendations

## Installation

### 1. Install Dependencies

```bash
cd pg-perf-analyzer
pip3 install -r requirements.txt
```

### 2. Run Build Script

```bash
./build.sh
```

Or install manually:

```bash
pip3 install -e .
```

## Basic Usage

### Without AI (Quick Test)

```bash
pg-perf-analyzer analyze \
  --host localhost \
  --database postgres \
  --user postgres \
  --skip-ai \
  --output report.md
```

### With Cloud AI (Full Analysis)

```bash
# Set API key
export OPENAI_API_KEY='your-api-key-here'

# Run analysis
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --ai-provider cloud \
  --output report.md
```

### With Local AI (Ollama)

```bash
# Install Ollama first
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Run analysis
pg-perf-analyzer analyze \
  --host localhost \
  --database mydb \
  --user myuser \
  --ai-provider local \
  --output report.md
```

## Test Environment

### Set Up Test Database

```bash
# Start PostgreSQL
sudo service postgresql start

# Create test database
sudo -u postgres psql -c "CREATE DATABASE testdb;"
sudo -u postgres psql -c "CREATE USER testuser WITH PASSWORD 'testpass';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;"

# Load sample data
sudo cp tests/sample_data.sql /tmp/
sudo chmod 644 /tmp/sample_data.sql
sudo -u postgres psql -d testdb -f /tmp/sample_data.sql
```

### Run Test Analysis

```bash
pg-perf-analyzer analyze \
  --host localhost \
  --database testdb \
  --user testuser \
  --password testpass \
  --skip-ai \
  --output test_report.md
```

## Check AI Provider

```bash
# Check local AI (Ollama)
pg-perf-analyzer check-ai --ai-provider local

# Check cloud AI (OpenAI)
pg-perf-analyzer check-ai --ai-provider cloud
```

## View Report

```bash
# View Markdown report
cat report.md

# Or open in browser (if HTML format)
xdg-open report.html  # Linux
open report.html      # macOS
```

## Common Commands

```bash
# Help
pg-perf-analyzer --help
pg-perf-analyzer analyze --help

# Version
pg-perf-analyzer --version

# Different output formats
pg-perf-analyzer analyze ... --format markdown
pg-perf-analyzer analyze ... --format html
pg-perf-analyzer analyze ... --format json
```

## Troubleshooting

### Command not found

```bash
# Use Python module directly
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
python3 -m pg_perf_analyzer.cli --help
```

### Database connection failed

```bash
# Test connection manually
psql -h localhost -U myuser -d mydb

# Try without SSL
pg-perf-analyzer analyze ... --sslmode disable
```

### AI provider not available

```bash
# Skip AI analysis
pg-perf-analyzer analyze ... --skip-ai

# Check provider status
pg-perf-analyzer check-ai --ai-provider cloud
```

## Next Steps

1. Read the full [User Guide](docs/USER_GUIDE.md)
2. Review [Installation Guide](docs/INSTALLATION.md)
3. Check [Architecture Documentation](docs/ARCHITECTURE.md)
4. Analyze your production databases
5. Set up automated reports

## Support

For detailed documentation, see the `docs/` directory:
- `INSTALLATION.md` - Complete installation guide
- `USER_GUIDE.md` - Comprehensive user guide
- `ARCHITECTURE.md` - Technical architecture

For issues or questions, please open an issue on the project repository.
