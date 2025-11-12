# UV Package Manager Guide

## Overview

This project uses **UV** - an extremely fast Python package installer and resolver written in Rust. UV is 10-100x faster than pip and provides better dependency resolution.

## Why UV?

- **🚀 Speed**: 10-100x faster than pip
- **🔒 Reliable**: Better dependency resolution
- **💾 Efficient**: Smart caching and minimal disk usage
- **🔄 Compatible**: Works with existing pip/pyproject.toml
- **🛠️ Modern**: Built-in virtual environment management

## Installation

### Quick Install (Recommended)

Use our setup script:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Installation

#### Linux/macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

#### Using pip
```bash
pip install uv
```

## Basic Usage

### First-Time Setup

```bash
# Clone repository
git clone <repo-url>
cd AgenticRealEstateSystem

# Install dependencies
uv sync

# Or use the setup script
./scripts/setup.sh
```

### Daily Workflow

```bash
# Install/update all dependencies
uv sync

# Run Python scripts
uv run python main.py
uv run python api_server.py

# Run tests
uv run pytest tests/

# Run with specific Python version
uv run --python 3.11 python main.py
```

## Dependency Management

### Adding Packages

```bash
# Add production dependency
uv add package-name

# Add with version constraint
uv add "package-name>=1.0.0,<2.0.0"

# Add development dependency
uv add --dev pytest

# Add with extras
uv add "pydantic-ai[logfire,openrouter]"
```

### Removing Packages

```bash
# Remove package
uv remove package-name

# Remove dev dependency
uv remove --dev package-name
```

### Updating Packages

```bash
# Update all packages
uv sync --upgrade

# Update specific package
uv add --upgrade package-name

# Update to latest compatible versions
uv lock --upgrade
```

### Viewing Dependencies

```bash
# Show installed packages
uv pip list

# Show dependency tree
uv pip tree

# Check for outdated packages
uv pip list --outdated
```

## Virtual Environment Management

### UV handles virtual environments automatically:

```bash
# Create and sync (automatic)
uv sync

# Activate manually if needed
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# Run without activating
uv run python script.py

# Recreate virtual environment
rm -rf .venv
uv sync
```

## Project Structure

### pyproject.toml

Our project uses standard pyproject.toml format compatible with UV:

```toml
[project]
name = "agentic-real-estate"
version = "1.0.0"
requires-python = ">=3.11"

dependencies = [
    "langgraph>=0.2.0",
    "langgraph-swarm>=0.0.11",
    "pydantic-ai[logfire,openrouter]>=0.0.14",
    # ... more dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    # ... more dev dependencies
]

production = [
    "uvicorn[standard]>=0.30.0",
    # ... more production dependencies
]
```

### uv.lock

The `uv.lock` file contains exact versions of all dependencies and their transitive dependencies. This ensures reproducible builds.

**Important**:
- Commit `uv.lock` to version control
- Regenerate when dependencies change: `uv lock`
- Never edit manually

## Common Commands

### Development

```bash
# Install all dependencies including dev
uv sync --all-extras

# Install only production dependencies
uv sync --no-dev

# Run with environment variables
ENV_VAR=value uv run python main.py

# Run interactive Python
uv run python

# Run IPython if installed
uv run ipython
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app tests/

# Run specific test file
uv run pytest tests/test_agents.py

# Run with markers
uv run pytest -m unit
```

### Code Quality

```bash
# Run linter
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run black .

# Type checking
uv run mypy app/

# Run all quality checks
uv run ruff check . && uv run black --check . && uv run mypy app/
```

## Advanced Usage

### Multiple Python Versions

```bash
# Use specific Python version
uv sync --python 3.11
uv sync --python 3.12

# Run with specific version
uv run --python 3.11 python script.py
```

### Custom Virtual Environment Location

```bash
# Set custom venv path
export UV_PROJECT_ENVIRONMENT=/path/to/venv
uv sync
```

### Offline Installation

```bash
# Download packages for offline use
uv pip download -r requirements.txt -d packages/

# Install from local cache
uv pip install --no-index --find-links packages/ -r requirements.txt
```

### Performance Optimization

```bash
# Use parallel downloads (default)
uv sync --parallel

# Disable cache (not recommended)
uv sync --no-cache

# Clear UV cache
uv cache clean
```

## Troubleshooting

### Common Issues

#### 1. UV not found after installation

**Solution**: Add UV to PATH
```bash
# Linux/Mac
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Windows: Add to System Environment Variables
# C:\Users\YourName\.local\bin
```

#### 2. Permission denied on scripts/setup.sh

**Solution**: Make script executable
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

#### 3. Dependency resolution conflicts

**Solution**: Clear lock and resync
```bash
rm uv.lock
uv lock
uv sync
```

#### 4. Import errors after installation

**Solution**: Verify installation
```bash
uv sync --reinstall
uv run python -c "import pydantic_ai; import langgraph_swarm"
```

#### 5. Slow dependency resolution

**Solution**: Update UV
```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install --upgrade uv
```

### Debug Commands

```bash
# Verbose output
uv sync -v

# Check configuration
uv config list

# Verify lock file
uv lock --check

# Show resolved dependencies
uv tree
```

## Migration from pip/poetry

### From pip

```bash
# If you have requirements.txt
uv pip compile requirements.txt -o requirements.lock
uv pip sync requirements.lock

# Or import directly to pyproject.toml
# (manually add dependencies to pyproject.toml)
uv sync
```

### From Poetry

```bash
# Export poetry dependencies
poetry export -f requirements.txt -o requirements.txt

# Add to pyproject.toml and sync
uv sync
```

## Best Practices

### 1. Always Use uv.lock

- **Do**: Commit `uv.lock` to version control
- **Don't**: Edit `uv.lock` manually
- **Update**: Run `uv lock` after changing dependencies

### 2. Dependency Groups

Organize dependencies logically:
- `dependencies`: Core runtime dependencies
- `dev`: Development and testing tools
- `production`: Production-specific packages
- Custom groups for specific features

### 3. Version Constraints

Use appropriate version constraints:
```bash
# Exact version (use sparingly)
uv add "package==1.0.0"

# Compatible release
uv add "package~=1.0.0"  # >=1.0.0, <1.1.0

# Minimum version
uv add "package>=1.0.0"

# Range
uv add "package>=1.0.0,<2.0.0"
```

### 4. Regular Updates

```bash
# Weekly: check for updates
uv pip list --outdated

# Monthly: update dependencies
uv lock --upgrade
uv sync

# Test after updates
uv run pytest
```

### 5. CI/CD Integration

```yaml
# GitHub Actions example
- name: Install UV
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: uv sync --frozen

- name: Run tests
  run: uv run pytest
```

## Performance Comparison

| Operation | pip | Poetry | UV |
|-----------|-----|--------|-----|
| Fresh install | 45s | 60s | 3s |
| Cached install | 20s | 25s | 0.5s |
| Lock generation | N/A | 40s | 2s |
| Resolution | Slow | Slow | Fast |

## Environment Variables

```bash
# Cache location
export UV_CACHE_DIR=/path/to/cache

# Disable cache
export UV_NO_CACHE=1

# Custom venv location
export UV_PROJECT_ENVIRONMENT=/path/to/venv

# Python version
export UV_PYTHON=3.11

# Parallel downloads
export UV_CONCURRENT_DOWNLOADS=10
```

## Resources

- **UV Documentation**: https://docs.astral.sh/uv/
- **GitHub Repository**: https://github.com/astral-sh/uv
- **Release Notes**: https://github.com/astral-sh/uv/releases
- **Discussion Forum**: https://github.com/astral-sh/uv/discussions

## Quick Reference Card

```bash
# Setup
uv sync                    # Install dependencies
uv sync --all-extras      # Install with all optional deps

# Add/Remove
uv add package            # Add dependency
uv add --dev package      # Add dev dependency
uv remove package         # Remove dependency

# Run
uv run python script.py   # Run Python script
uv run pytest             # Run tests
uv run --python 3.11 ...  # Use specific Python

# Update
uv lock --upgrade         # Update lock file
uv sync --upgrade         # Update and install

# Info
uv pip list               # List packages
uv pip tree               # Dependency tree
uv pip list --outdated    # Check updates

# Maintenance
uv cache clean            # Clear cache
rm -rf .venv && uv sync   # Fresh install
```

## Support

For issues or questions:
1. Check this guide first
2. Review UV documentation: https://docs.astral.sh/uv/
3. Check project issues: https://github.com/astral-sh/uv/issues
4. Contact project maintainers

---

**Last Updated**: 2025-11-11
**UV Version**: 0.5.x+
**Python Version**: 3.11+
