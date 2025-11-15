# Changelog

All notable changes to the PostgreSQL Performance Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-15

### Added
- **Naming Standards Analyzer** - Comprehensive analysis of database naming conventions
  - Table naming pattern detection (snake_case, camelCase, PascalCase)
  - Column naming consistency analysis
  - Index naming convention checking
  - Constraint naming pattern validation
  - Schema naming evaluation
  - Reserved word violation detection
  - Consistency scoring and recommendations
- **Enhanced AI Prompts** - Improved structure analysis prompts with detailed naming standards requests
- **Naming Standards Documentation** - Complete guide in `docs/NAMING_STANDARDS.md`
- **Report Section** - Dedicated naming standards section in all reports
- **Pattern Detection** - Automatic detection of 8+ naming pattern types

### Changed
- Enhanced structure analysis to include column and index name samples
- Updated report formatter to include naming standards section
- Improved AI recommendations to include specific naming violations and corrections

### Fixed
- N/A (initial release with naming standards)

## [1.0.0] - 2025-11-14

### Added
- **Initial Release** - First version of PostgreSQL Performance Analyzer
- **Structure Analyzer** - Database structure analysis
  - Database and schema information
  - Table details (size, rows, columns)
  - Index statistics and usage
  - Foreign key relationships
  - Views and materialized views
- **Security Analyzer** - Security configuration analysis
  - User roles and permissions
  - Superuser account detection
  - SSL/TLS configuration
  - Row-level security policies
  - Authentication methods
- **Performance Analyzer** - Performance metrics analysis
  - Cache hit ratios (heap and index)
  - Index usage statistics
  - Unused index detection
  - Table bloat detection
  - Query performance statistics
  - Configuration parameter analysis
- **AI Integration** - Support for local and cloud AI providers
  - Local AI via Ollama (llama2, mistral, codellama)
  - Cloud AI via OpenAI (gpt-4.1-mini, gpt-4.1-nano)
  - Google Gemini support (gemini-2.5-flash)
- **Report Generation** - Multiple output formats
  - Markdown format (default)
  - HTML format (styled)
  - JSON format (structured data)
- **CLI Interface** - User-friendly command-line interface
  - Rich terminal output with progress indicators
  - Flexible configuration options
  - Environment variable support
- **Documentation** - Comprehensive guides
  - README.md - Main documentation
  - QUICKSTART.md - Quick start guide
  - INSTALLATION.md - Installation instructions
  - USER_GUIDE.md - Complete user guide
  - ARCHITECTURE.md - Technical architecture
  - DEPLOYMENT.md - Deployment guide
- **Test Environment** - PostgreSQL test database with sample data
  - 6 tables with realistic data
  - 15 indexes (used and unused)
  - Sample data for testing all features
- **Build Tools** - Automated build and installation
  - build.sh script for easy setup
  - setup.py for package installation
  - requirements.txt for dependencies

### Security
- Read-only database operations
- No data modification or schema changes
- SSL/TLS connection support
- Secure credential handling via environment variables

## [Unreleased]

### Planned Features
- Historical trend tracking
- Multi-database comparison
- Automated remediation scripts
- Web-based UI
- Real-time monitoring
- Custom rule engine
- Plugin system
- Additional AI providers (Anthropic Claude)
- PDF report generation
- Email report delivery

## Version History

- **1.1.0** - Naming standards analysis enhancement
- **1.0.0** - Initial release with core features

## Migration Guide

### Upgrading from 1.0.0 to 1.1.0

No breaking changes. The naming standards analyzer is automatically included in all analyses.

**Steps:**
1. Extract new version
2. Run `pip install -e .` to update
3. No configuration changes needed
4. Reports will automatically include naming standards section

**New Features Available:**
- Naming standards analysis (automatic)
- Enhanced AI prompts with naming recommendations
- New report section with naming metrics

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check documentation in `docs/` directory
- Review CONTRIBUTING.md for contribution guidelines

## License

This project is licensed under the MIT License - see the LICENSE file for details.
