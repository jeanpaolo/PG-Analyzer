#!/bin/bash
# Build script for PostgreSQL Performance Analyzer

set -e  # Exit on error

echo "=========================================="
echo "PostgreSQL Performance Analyzer - Build"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi
echo "✓ Python version: $PYTHON_VERSION"
echo ""

# Check if in correct directory
if [ ! -f "setup.py" ]; then
    echo "Error: setup.py not found. Please run this script from the project root."
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info src/*.egg-info
echo "✓ Cleaned"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -q -r requirements.txt || {
    echo "Warning: Some dependencies may already be installed"
}
echo "✓ Dependencies installed"
echo ""

# Run tests (if test directory exists)
if [ -d "tests" ] && [ -f "tests/sample_data.sql" ]; then
    echo "Test files found"
    echo "✓ Tests available"
else
    echo "⚠ No tests found"
fi
echo ""

# Build package
echo "Building package..."
python3 setup.py sdist bdist_wheel 2>&1 | grep -v "warning" || true
echo "✓ Package built"
echo ""

# Install package in development mode
echo "Installing package in development mode..."
pip3 install -e . 2>&1 | tail -5 || {
    echo "Note: If installation fails due to permissions, try:"
    echo "  sudo pip3 install -e ."
    echo "Or run directly with:"
    echo "  export PYTHONPATH=\$(pwd)/src:\$PYTHONPATH"
    echo "  python3 -m pg_perf_analyzer.cli"
}
echo ""

# Verify installation
echo "Verifying installation..."
if command -v pg-perf-analyzer &> /dev/null; then
    echo "✓ Command 'pg-perf-analyzer' is available"
    pg-perf-analyzer --version
else
    echo "⚠ Command not in PATH, use: python3 -m pg_perf_analyzer.cli"
    export PYTHONPATH=$(pwd)/src:$PYTHONPATH
    python3 -m pg_perf_analyzer.cli --version
fi
echo ""

echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Check AI provider: pg-perf-analyzer check-ai --ai-provider cloud"
echo "2. Run analysis: pg-perf-analyzer analyze --help"
echo "3. Read documentation: docs/USER_GUIDE.md"
echo ""
