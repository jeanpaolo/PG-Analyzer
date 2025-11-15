# Contributing to PostgreSQL Performance Analyzer

Thank you for your interest in contributing to the PostgreSQL Performance Analyzer! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences
- Accept responsibility and apologize for mistakes

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pg-perf-analyzer.git
   cd pg-perf-analyzer
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/pg-perf-analyzer.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (for testing)
- Git

### Installation

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Set up test database**:
   ```bash
   sudo service postgresql start
   sudo -u postgres psql -c "CREATE DATABASE testdb;"
   sudo -u postgres psql -c "CREATE USER testuser WITH PASSWORD 'testpass';"
   sudo -u postgres psql -d testdb -f tests/sample_data.sql
   ```

4. **Run tests**:
   ```bash
   pg-perf-analyzer analyze \
     --host localhost \
     --database testdb \
     --user testuser \
     --password testpass \
     --skip-ai \
     --output test_report.md
   ```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title** describing the issue
- **Detailed description** of the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, PostgreSQL version)
- **Error messages** or logs if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Clear title** describing the enhancement
- **Detailed description** of the proposed feature
- **Use cases** explaining why this would be useful
- **Possible implementation** approach (if you have ideas)

### Pull Requests

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Test your changes** thoroughly

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub

## Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Write **docstrings** for all public functions and classes
- Keep functions **focused and small** (< 50 lines when possible)
- Use **meaningful variable names**

### Example

```python
def analyze_table_naming(self, schema: str) -> Dict[str, Any]:
    """
    Analyze table naming conventions in a schema.
    
    Args:
        schema: Schema name to analyze
        
    Returns:
        Dictionary containing naming analysis results
        
    Raises:
        DatabaseError: If database connection fails
    """
    # Implementation here
    pass
```

### Code Organization

- **One class per file** (with related helpers)
- **Group related functions** together
- **Use meaningful file names** (snake_case)
- **Keep imports organized**:
  ```python
  # Standard library
  import os
  import sys
  
  # Third-party
  import click
  from rich.console import Console
  
  # Local
  from .utils import DatabaseConnection
  ```

### Documentation

- Update **README.md** if adding new features
- Add entries to **CHANGELOG.md** (if exists)
- Update relevant **docs/** files
- Include **inline comments** for complex logic
- Write **clear commit messages**

## Testing

### Running Tests

```bash
# Test without AI
pg-perf-analyzer analyze \
  --host localhost \
  --database testdb \
  --user testuser \
  --password testpass \
  --skip-ai \
  --output test_report.md

# Test with cloud AI (requires API key)
export OPENAI_API_KEY='your-key'
pg-perf-analyzer analyze \
  --host localhost \
  --database testdb \
  --user testuser \
  --password testpass \
  --ai-provider cloud \
  --output test_report_ai.md
```

### Test Coverage

When adding new features:

- **Add test cases** for new functionality
- **Test edge cases** and error conditions
- **Verify backward compatibility**
- **Test with different PostgreSQL versions** if possible

## Submitting Changes

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows the project's coding standards
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary files are included
- [ ] Changes are focused (one feature/fix per PR)

### Pull Request Description

Include in your PR description:

1. **What** - What does this PR do?
2. **Why** - Why is this change needed?
3. **How** - How does it work?
4. **Testing** - How was it tested?
5. **Screenshots** - If applicable (for UI changes)

### Example PR Description

```markdown
## Add Index Usage Analyzer

### What
Adds a new analyzer to detect unused indexes and recommend removal.

### Why
Unused indexes waste disk space and slow down write operations.

### How
- Queries pg_stat_user_indexes for index usage statistics
- Identifies indexes with zero scans
- Generates recommendations with SQL drop statements

### Testing
- Tested with testdb containing 15 indexes
- Verified detection of unused indexes
- Confirmed report generation includes new section
```

## Areas for Contribution

### High Priority

- Additional database analyzers (e.g., query performance, connection pooling)
- Support for more AI providers (Anthropic Claude, local models)
- Enhanced report formats (PDF, Excel)
- Web-based UI
- Real-time monitoring capabilities

### Medium Priority

- Additional naming pattern detectors
- Custom rule engine for analysis
- Historical trend tracking
- Multi-database comparison
- Automated remediation scripts

### Low Priority

- Additional output formats
- Internationalization (i18n)
- Plugin system
- IDE integrations

## Questions?

If you have questions about contributing:

- Open an issue with the `question` label
- Check existing documentation in `docs/`
- Review closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute!
