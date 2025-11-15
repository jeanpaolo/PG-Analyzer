# Installation Guide

This guide provides detailed instructions for installing and setting up the PostgreSQL Performance Analyzer.

## System Requirements

### Minimum Requirements

- **Operating System**: Linux, macOS, or Windows with WSL
- **Python**: 3.11 or higher
- **PostgreSQL**: Any version (for the database to analyze)
- **RAM**: 512 MB minimum
- **Disk Space**: 100 MB for application and dependencies

### Recommended Requirements

- **Python**: 3.11 or 3.12
- **RAM**: 2 GB or more
- **Network**: Internet connection for cloud AI providers

## Installation Methods

### Method 1: Install from Source (Recommended)

This method gives you full control and allows easy customization.

#### Step 1: Download the Application

```bash
# Clone or download the repository
cd /path/to/installation
# Extract if downloaded as archive
```

#### Step 2: Install Python Dependencies

```bash
cd pg-perf-analyzer

# Install dependencies
pip3 install -r requirements.txt

# Or install specific packages
pip3 install psycopg2-binary sqlalchemy openai ollama \
             pyyaml python-dotenv click rich jinja2 \
             markdown weasyprint tabulate
```

#### Step 3: Install the Package

```bash
# Install in development mode (recommended for testing)
pip3 install -e .

# Or install normally
pip3 install .
```

#### Step 4: Verify Installation

```bash
# Check if command is available
pg-perf-analyzer --version

# If not in PATH, use Python module directly
python3 -m pg_perf_analyzer.cli --version
```

### Method 2: Direct Execution (No Installation)

You can run the application directly without installing it.

```bash
cd pg-perf-analyzer

# Set Python path
export PYTHONPATH=/path/to/pg-perf-analyzer/src:$PYTHONPATH

# Run the application
python3 -m pg_perf_analyzer.cli --help
```

## AI Provider Setup

The application supports both local and cloud AI providers.

### Option 1: Local AI with Ollama

Ollama allows you to run AI models locally without requiring internet access or API keys.

#### Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from [https://ollama.ai](https://ollama.ai)

#### Start Ollama Service

```bash
# Start Ollama (runs in background)
ollama serve
```

#### Pull AI Models

```bash
# Pull recommended model (llama2)
ollama pull llama2

# Or pull other models
ollama pull mistral
ollama pull codellama
ollama pull llama3
```

#### Verify Ollama Setup

```bash
pg-perf-analyzer check-ai --ai-provider local
```

### Option 2: Cloud AI Providers

Cloud AI providers offer more powerful models but require API keys and internet access.

#### OpenAI Setup

1. **Get API Key**
   - Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key (starts with `sk-`)

2. **Set Environment Variable**
   ```bash
   export OPENAI_API_KEY='sk-your-api-key-here'
   
   # Make it permanent (add to ~/.bashrc or ~/.zshrc)
   echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Verify Setup**
   ```bash
   pg-perf-analyzer check-ai --ai-provider cloud
   ```

#### Other Cloud Providers

The application uses OpenAI-compatible API format. For other providers:

- **Google Gemini**: Uses OpenAI format via environment variables
- **Anthropic Claude**: Configure via base URL and API key
- **Custom endpoints**: Set via configuration file

## Database Setup

### PostgreSQL Connection Requirements

The application requires:
- Read-only access to the database
- Connection permissions
- Access to system catalogs (pg_catalog)

### Recommended Database User Setup

Create a dedicated read-only user for analysis:

```sql
-- Create read-only user
CREATE USER analyzer WITH PASSWORD 'secure_password';

-- Grant connection to database
GRANT CONNECT ON DATABASE your_database TO analyzer;

-- Grant usage on schemas
GRANT USAGE ON SCHEMA public TO analyzer;
GRANT USAGE ON SCHEMA your_schema TO analyzer;

-- Grant select on all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyzer;
GRANT SELECT ON ALL TABLES IN SCHEMA your_schema TO analyzer;

-- Grant select on system catalogs (already available by default)
-- No additional grants needed for pg_catalog
```

### Test Database Connection

```bash
# Test connection with psql
psql -h localhost -U analyzer -d your_database -c "SELECT version();"
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Database connection
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=mydb
export PGUSER=analyzer
export PGPASSWORD=secure_password

# AI provider
export OPENAI_API_KEY=sk-your-key-here
```

### Configuration File (Optional)

Create `config.yaml`:

```yaml
database:
  host: localhost
  port: 5432
  database: mydb
  user: analyzer
  password: secure_password
  sslmode: prefer

ai:
  provider: cloud
  cloud:
    provider: openai
    model: gpt-4.1-mini
    temperature: 0.7
    max_tokens: 2000

output:
  format: markdown
  path: report.md
```

## Testing the Installation

### Run Basic Test

```bash
# Test without AI
pg-perf-analyzer analyze \
  --host localhost \
  --database postgres \
  --user postgres \
  --skip-ai \
  --output test_report.md
```

### Run Full Test with AI

```bash
# Test with cloud AI
pg-perf-analyzer analyze \
  --host localhost \
  --database postgres \
  --user postgres \
  --ai-provider cloud \
  --output test_report.md

# Test with local AI
pg-perf-analyzer analyze \
  --host localhost \
  --database postgres \
  --user postgres \
  --ai-provider local \
  --ai-model llama2 \
  --output test_report.md
```

## Troubleshooting

### Common Issues

#### 1. Module Not Found Errors

```bash
# Solution: Install missing dependencies
pip3 install psycopg2-binary rich click openai

# Or reinstall all dependencies
pip3 install -r requirements.txt
```

#### 2. Database Connection Failed

```bash
# Check PostgreSQL is running
sudo service postgresql status

# Test connection manually
psql -h localhost -U your_user -d your_database

# Check firewall and pg_hba.conf settings
```

#### 3. Ollama Not Available

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama service
ollama serve

# Pull a model if none available
ollama pull llama2
```

#### 4. Permission Denied Errors

```bash
# For PostgreSQL access
# Grant necessary permissions (see Database Setup section)

# For file system
# Ensure output directory is writable
chmod 755 /path/to/output/directory
```

#### 5. SSL Connection Issues

```bash
# Try different SSL modes
--sslmode disable    # No SSL
--sslmode prefer     # Try SSL, fallback to no SSL
--sslmode require    # Require SSL
```

## Uninstallation

### Remove the Application

```bash
# If installed with pip
pip3 uninstall pg-perf-analyzer

# Remove source directory
rm -rf /path/to/pg-perf-analyzer
```

### Remove Dependencies (Optional)

```bash
pip3 uninstall psycopg2-binary sqlalchemy openai ollama \
               pyyaml python-dotenv click rich jinja2 \
               markdown weasyprint tabulate
```

### Remove Ollama (Optional)

```bash
# Linux
sudo rm -rf /usr/local/bin/ollama
sudo rm -rf ~/.ollama

# macOS
brew uninstall ollama
```

## Next Steps

After installation:

1. Read the [User Guide](USER_GUIDE.md) for usage instructions
2. Review the [Architecture Documentation](ARCHITECTURE.md)
3. Run your first analysis on a test database
4. Explore different AI providers and models
5. Customize output formats and reports

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review the documentation in the `docs/` directory
- Open an issue on the project repository
