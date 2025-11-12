#!/bin/bash
# UV Package Manager Setup Script for Agentic Real Estate System
# This script installs UV and sets up the development environment

set -e  # Exit on error

echo "=========================================="
echo "UV Package Manager Setup"
echo "Agentic Real Estate System"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "ℹ $1"
}

# Check if UV is installed
echo "Checking UV installation..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1 | head -n1)
    print_success "UV is already installed: $UV_VERSION"
else
    print_warning "UV is not installed. Installing UV..."

    # Detect OS and install UV accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        # Linux or macOS
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Add UV to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"

        print_success "UV installed successfully"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows (Git Bash, Cygwin, or native)
        print_warning "Windows detected. Please install UV manually:"
        print_info "  PowerShell: irm https://astral.sh/uv/install.ps1 | iex"
        print_info "  Or download from: https://github.com/astral-sh/uv/releases"
        exit 1
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
fi

# Verify UV installation
if ! command -v uv &> /dev/null; then
    print_error "UV installation failed. Please install manually from https://docs.astral.sh/uv/"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setting up project dependencies..."
echo "=========================================="
echo ""

# Remove old virtual environment if exists
if [ -d ".venv" ]; then
    print_warning "Removing old .venv directory..."
    rm -rf .venv
fi

# Sync dependencies with UV
print_info "Running uv sync to install all dependencies..."
uv sync --all-extras

print_success "Dependencies installed successfully"

echo ""
echo "=========================================="
echo "Setting up pre-commit hooks..."
echo "=========================================="
echo ""

# Install pre-commit hooks if .pre-commit-config.yaml exists
if [ -f ".pre-commit-config.yaml" ]; then
    print_info "Installing pre-commit hooks..."
    uv run pre-commit install
    print_success "Pre-commit hooks installed"
else
    print_warning "No .pre-commit-config.yaml found. Skipping pre-commit setup."
fi

echo ""
echo "=========================================="
echo "Verifying installation..."
echo "=========================================="
echo ""

# Test critical imports
print_info "Testing critical package imports..."

uv run python -c "
import sys
import importlib.util

packages = [
    ('pydantic_ai', 'pydantic-ai'),
    ('langgraph_swarm', 'langgraph-swarm'),
    ('langgraph', 'langgraph'),
    ('fastapi', 'fastapi'),
    ('logfire', 'logfire')
]

failed = []
for module_name, package_name in packages:
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        failed.append(package_name)
        print(f'✗ {package_name}: FAILED')
    else:
        print(f'✓ {package_name}: OK')

if failed:
    print(f'\nFailed imports: {', '.join(failed)}')
    sys.exit(1)
else:
    print('\nAll critical packages imported successfully!')
" && print_success "All imports verified" || print_error "Some imports failed"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
print_info "To activate the virtual environment:"
print_info "  source .venv/bin/activate    # Linux/Mac"
print_info "  .venv\\Scripts\\activate      # Windows"
echo ""
print_info "Quick start commands:"
print_info "  uv run python main.py         # Run main application"
print_info "  uv run python api_server.py   # Start API server"
print_info "  uv run pytest tests/          # Run tests"
print_info "  uv add package-name           # Add new package"
print_info "  uv sync                       # Update dependencies"
echo ""
print_success "Environment is ready to use!"
echo ""
