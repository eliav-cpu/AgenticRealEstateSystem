# UV Quick Start Guide

## 30-Second Setup

```bash
# Clone and setup in one go
git clone <repo-url> && cd AgenticRealEstateSystem
./scripts/setup.sh

# Done! Ready to use
uv run python main.py
```

## 5-Minute Development Workflow

### 1. Setup Environment (First Time Only)

```bash
# Install UV (skip if already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### 2. Daily Commands

```bash
# Run application
uv run python api_server.py

# Run tests
uv run pytest

# Add package
uv add package-name

# Update all packages
uv sync --upgrade
```

### 3. Common Tasks

```bash
# Development server with auto-reload
uv run uvicorn api_server:app --reload

# Run specific test file
uv run pytest tests/test_agents.py

# Check code quality
uv run ruff check . && uv run black .

# Interactive Python with all packages
uv run python
```

## Key Differences from pip

| Task | pip | UV |
|------|-----|-----|
| Install packages | `pip install -r requirements.txt` | `uv sync` |
| Add package | `pip install package` | `uv add package` |
| Run script | `python script.py` | `uv run python script.py` |
| Create venv | `python -m venv .venv` | `uv sync` (automatic) |
| Update packages | `pip install --upgrade package` | `uv sync --upgrade` |

## Why UV is Better

- **10-100x faster** than pip
- **Automatic** virtual environment management
- **Better** dependency resolution (no conflicts)
- **Reproducible** builds with uv.lock
- **Compatible** with all pip packages

## Troubleshooting

### Problem: "uv: command not found"

**Solution**:
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make permanent
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Problem: Import errors after installation

**Solution**:
```bash
# Reinstall dependencies
uv sync --reinstall

# Verify imports
uv run python -c "import pydantic_ai; print('OK')"
```

### Problem: Dependency conflicts

**Solution**:
```bash
# Regenerate lock file
rm uv.lock
uv lock
uv sync
```

## Essential Commands Reference

```bash
# SETUP
uv sync                         # Install all dependencies
uv sync --all-extras           # Include optional dependencies
uv sync --no-dev               # Production only

# ADD/REMOVE
uv add package                 # Add runtime dependency
uv add --dev pytest            # Add dev dependency
uv remove package              # Remove dependency

# RUN
uv run python script.py        # Run Python script
uv run pytest                  # Run tests
uv run --python 3.11 ...       # Use specific Python version

# UPDATE
uv sync --upgrade              # Update all packages
uv lock --upgrade              # Update lock file only
uv add --upgrade package       # Update specific package

# INFO
uv pip list                    # List installed packages
uv pip tree                    # Show dependency tree
uv pip list --outdated         # Check for updates
```

## Next Steps

1. **Read full guide**: [docs/UV_GUIDE.md](UV_GUIDE.md)
2. **Check examples**: Look at existing project code
3. **Join community**: https://github.com/astral-sh/uv/discussions

## Quick Tips

✅ **DO**:
- Use `uv run` for all Python commands
- Commit `uv.lock` to version control
- Run `uv sync` after pulling changes
- Use `uv add` to add dependencies

❌ **DON'T**:
- Don't use `pip install` (use `uv add` instead)
- Don't edit `uv.lock` manually
- Don't commit `.venv` directory
- Don't mix pip and uv in the same project

## Support

- **Documentation**: [UV_GUIDE.md](UV_GUIDE.md)
- **Official docs**: https://docs.astral.sh/uv/
- **Issues**: https://github.com/astral-sh/uv/issues

---

**Last Updated**: 2025-11-11
