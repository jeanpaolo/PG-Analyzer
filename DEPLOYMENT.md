# Deployment Guide

This guide provides instructions for deploying the PostgreSQL Performance Analyzer in various environments.

## Package Contents

The application package includes:

```
pg-perf-analyzer/
├── src/pg_perf_analyzer/          # Main application code
│   ├── analyzers/                 # Database analyzers
│   ├── ai/                        # AI integration
│   ├── reports/                   # Report generation
│   ├── utils/                     # Utilities
│   └── cli.py                     # Command-line interface
├── tests/                         # Test files
│   └── sample_data.sql           # Sample database
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md           # Architecture details
│   ├── INSTALLATION.md           # Installation guide
│   └── USER_GUIDE.md             # User guide
├── config/                        # Configuration examples
│   └── test_config.yaml          # Test configuration
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
├── build.sh                       # Build script
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
└── LICENSE                        # MIT License
```

## Deployment Scenarios

### 1. Local Development Environment

**Use case:** Testing and development

**Setup:**
```bash
# Extract package
tar -xzf pg-perf-analyzer.tar.gz
cd pg-perf-analyzer

# Install dependencies
pip3 install -r requirements.txt

# Run directly
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
python3 -m pg_perf_analyzer.cli analyze --help
```

### 2. Single Server Installation

**Use case:** Database administrator workstation

**Setup:**
```bash
# Extract and install
tar -xzf pg-perf-analyzer.tar.gz
cd pg-perf-analyzer

# Install system-wide (requires sudo)
sudo pip3 install .

# Or install for current user
pip3 install --user .

# Verify
pg-perf-analyzer --version
```

**Configuration:**
```bash
# Set environment variables
cat >> ~/.bashrc << 'EOF'
export PGHOST=localhost
export PGUSER=analyzer
export OPENAI_API_KEY='your-key-here'
EOF

source ~/.bashrc
```

### 3. CI/CD Pipeline Integration

**Use case:** Automated database analysis in CI/CD

**GitHub Actions Example:**
```yaml
name: Database Analysis
on:
  schedule:
    - cron: '0 2 1 * *'  # Monthly on 1st at 2 AM
  workflow_dispatch:

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install analyzer
        run: |
          pip install -r requirements.txt
          pip install .
      
      - name: Run analysis
        env:
          PGHOST: ${{ secrets.DB_HOST }}
          PGDATABASE: ${{ secrets.DB_NAME }}
          PGUSER: ${{ secrets.DB_USER }}
          PGPASSWORD: ${{ secrets.DB_PASSWORD }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pg-perf-analyzer analyze \
            --ai-provider cloud \
            --output report.md
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: analysis-report
          path: report.md
```

**GitLab CI Example:**
```yaml
database-analysis:
  image: python:3.11
  stage: analyze
  script:
    - pip install -r requirements.txt
    - pip install .
    - |
      pg-perf-analyzer analyze \
        --host $DB_HOST \
        --database $DB_NAME \
        --user $DB_USER \
        --password $DB_PASSWORD \
        --ai-provider cloud \
        --output report.md
  artifacts:
    paths:
      - report.md
    expire_in: 30 days
  only:
    - schedules
```

### 4. Docker Container

**Use case:** Containerized deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install PostgreSQL client
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy application
WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir .

# Set entrypoint
ENTRYPOINT ["pg-perf-analyzer"]
CMD ["--help"]
```

**Build and run:**
```bash
# Build image
docker build -t pg-perf-analyzer:latest .

# Run analysis
docker run --rm \
  -e PGHOST=host.docker.internal \
  -e PGDATABASE=mydb \
  -e PGUSER=analyzer \
  -e PGPASSWORD=password \
  -e OPENAI_API_KEY=sk-... \
  -v $(pwd)/reports:/reports \
  pg-perf-analyzer:latest \
  analyze --output /reports/report.md
```

### 5. Kubernetes Deployment

**Use case:** Scheduled analysis in Kubernetes

**CronJob:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-analyzer
spec:
  schedule: "0 2 1 * *"  # Monthly
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: analyzer
            image: pg-perf-analyzer:latest
            env:
            - name: PGHOST
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: host
            - name: PGDATABASE
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: database
            - name: PGUSER
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: user
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: ai-credentials
                  key: api-key
            command:
            - pg-perf-analyzer
            - analyze
            - --ai-provider
            - cloud
            - --output
            - /reports/report.md
            volumeMounts:
            - name: reports
              mountPath: /reports
          volumes:
          - name: reports
            persistentVolumeClaim:
              claimName: reports-pvc
          restartPolicy: OnFailure
```

### 6. AWS Lambda Function

**Use case:** Serverless scheduled analysis

**Lambda deployment package:**
```bash
# Create deployment package
mkdir lambda-package
cd lambda-package

# Install dependencies
pip install -r ../requirements.txt -t .
cp -r ../src/pg_perf_analyzer .

# Create handler
cat > lambda_handler.py << 'EOF'
import os
from pg_perf_analyzer.utils import DatabaseConnection
from pg_perf_analyzer.analyzers import PerformanceAnalyzer
from pg_perf_analyzer.ai import CloudAIProvider
from pg_perf_analyzer.reports import ReportBuilder, ReportFormatter

def lambda_handler(event, context):
    # Get configuration from environment
    db_config = {
        'host': os.environ['DB_HOST'],
        'database': os.environ['DB_NAME'],
        'user': os.environ['DB_USER'],
        'password': os.environ['DB_PASSWORD']
    }
    
    # Run analysis
    with DatabaseConnection(db_config) as db:
        analyzer = PerformanceAnalyzer(db)
        results = analyzer.analyze()
    
    # Generate report
    report_builder = ReportBuilder()
    report_builder.add_performance_analysis(results)
    
    formatter = ReportFormatter(report_builder.get_report_data())
    report = formatter.to_json()
    
    return {
        'statusCode': 200,
        'body': report
    }
EOF

# Create zip
zip -r ../lambda-function.zip .
```

### 7. Ansible Playbook

**Use case:** Automated deployment across multiple servers

**playbook.yml:**
```yaml
---
- name: Deploy PostgreSQL Performance Analyzer
  hosts: database_servers
  become: yes
  
  vars:
    app_dir: /opt/pg-perf-analyzer
    
  tasks:
    - name: Install Python 3.11
      apt:
        name: python3.11
        state: present
        
    - name: Create application directory
      file:
        path: "{{ app_dir }}"
        state: directory
        mode: '0755'
        
    - name: Extract application
      unarchive:
        src: pg-perf-analyzer.tar.gz
        dest: "{{ app_dir }}"
        
    - name: Install dependencies
      pip:
        requirements: "{{ app_dir }}/requirements.txt"
        executable: pip3
        
    - name: Install application
      pip:
        name: "{{ app_dir }}"
        executable: pip3
        
    - name: Create cron job
      cron:
        name: "Monthly database analysis"
        minute: "0"
        hour: "2"
        day: "1"
        job: "pg-perf-analyzer analyze --host localhost --database mydb --user analyzer --output /var/reports/$(date +\\%Y-\\%m).md"
```

## Security Considerations

### 1. Credential Management

**Never hardcode credentials:**
```bash
# Bad
pg-perf-analyzer analyze --password mypassword

# Good - use environment variables
export PGPASSWORD='mypassword'
pg-perf-analyzer analyze

# Better - use secrets management
export PGPASSWORD=$(aws secretsmanager get-secret-value --secret-id db-password --query SecretString --output text)
```

### 2. Network Security

**Use SSL connections:**
```bash
pg-perf-analyzer analyze \
  --sslmode require \
  --host secure-db.example.com
```

**Restrict network access:**
- Use VPN or private networks
- Configure firewall rules
- Use bastion hosts for production databases

### 3. Read-Only Access

**Create dedicated read-only user:**
```sql
CREATE USER analyzer WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO analyzer;
GRANT USAGE ON SCHEMA public TO analyzer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyzer;
```

### 4. API Key Protection

**Secure API keys:**
```bash
# Use environment variables
export OPENAI_API_KEY='sk-...'

# Or use secrets management
export OPENAI_API_KEY=$(vault kv get -field=api_key secret/openai)

# Never commit to version control
echo "*.env" >> .gitignore
echo "config.yaml" >> .gitignore
```

## Monitoring and Maintenance

### 1. Log Management

**Configure logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/pg-analyzer.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Report Archival

**Automated archival:**
```bash
#!/bin/bash
# archive-reports.sh

REPORT_DIR="/var/reports"
ARCHIVE_DIR="/var/reports/archive"
RETENTION_DAYS=90

# Create archive directory
mkdir -p "$ARCHIVE_DIR"

# Move old reports
find "$REPORT_DIR" -name "*.md" -mtime +30 -exec mv {} "$ARCHIVE_DIR/" \;

# Compress old archives
find "$ARCHIVE_DIR" -name "*.md" -mtime +60 -exec gzip {} \;

# Delete very old archives
find "$ARCHIVE_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
```

### 3. Health Checks

**Monitor analyzer health:**
```bash
#!/bin/bash
# health-check.sh

# Test database connection
pg-perf-analyzer analyze \
  --host localhost \
  --database postgres \
  --user postgres \
  --skip-ai \
  --output /tmp/health-check.md

if [ $? -eq 0 ]; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed"
    exit 1
fi
```

## Troubleshooting Deployment

### Common Issues

1. **Permission errors**
   - Use sudo for system-wide installation
   - Check file permissions
   - Verify database user permissions

2. **Missing dependencies**
   - Install all requirements: `pip3 install -r requirements.txt`
   - Check Python version: `python3 --version`

3. **Network connectivity**
   - Test database connection: `psql -h host -U user -d database`
   - Check firewall rules
   - Verify SSL configuration

4. **AI provider issues**
   - Verify API key: `pg-perf-analyzer check-ai`
   - Check internet connectivity
   - Use `--skip-ai` for testing

## Support and Updates

### Getting Updates

```bash
# Download new version
wget https://example.com/pg-perf-analyzer-v2.0.0.tar.gz

# Backup current installation
cp -r /opt/pg-perf-analyzer /opt/pg-perf-analyzer.backup

# Install new version
tar -xzf pg-perf-analyzer-v2.0.0.tar.gz
cd pg-perf-analyzer
sudo pip3 install --upgrade .
```

### Rollback

```bash
# Restore backup
rm -rf /opt/pg-perf-analyzer
mv /opt/pg-perf-analyzer.backup /opt/pg-perf-analyzer

# Reinstall previous version
cd /opt/pg-perf-analyzer
sudo pip3 install --force-reinstall .
```

## Best Practices

1. **Use version control** for configuration files
2. **Test in staging** before production deployment
3. **Schedule regular analysis** (monthly recommended)
4. **Archive reports** for historical comparison
5. **Monitor analyzer performance** and logs
6. **Keep dependencies updated** for security
7. **Use read-only database users** for safety
8. **Secure API keys** with secrets management
9. **Document custom configurations** for your team
10. **Set up alerts** for failed analysis runs
