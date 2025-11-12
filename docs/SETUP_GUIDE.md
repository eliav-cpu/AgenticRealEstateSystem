# Setup and Installation Guide

**System:** Agentic Real Estate System
**Version:** 1.2.0
**Last Updated:** 2025-11-11

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Setup (30 Seconds)](#quick-setup-30-seconds)
3. [Detailed Installation](#detailed-installation)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Development Setup](#development-setup)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting Setup](#troubleshooting-setup)

---

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10+, Ubuntu 20.04+, macOS 11+
- **Python**: 3.11 or higher
- **Memory**: 4GB RAM minimum
- **Disk Space**: 2GB free space
- **Internet**: Required for package installation and API access

### Recommended Requirements

- **Operating System**: Latest stable versions
- **Python**: 3.12+ (for best performance)
- **Memory**: 8GB RAM
- **Disk Space**: 5GB free space
- **CPU**: Multi-core processor (4+ cores recommended)

### Software Dependencies

✅ **Required:**
- Python 3.11+
- pip or UV package manager
- Git (for repository cloning)

✅ **Optional:**
- Docker (for containerized deployment)
- Redis (for production caching)
- PostgreSQL (for production data persistence)

---

## Quick Setup (30 Seconds)

### One-Command Installation

```bash
curl -sSL https://raw.githubusercontent.com/your-repo/AgenticRealEstateSystem/main/scripts/quick-setup.sh | bash
```

This script will:
1. Check system requirements
2. Install UV package manager
3. Clone repository
4. Install dependencies
5. Create environment file
6. Verify installation

### Manual Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/AgenticRealEstateSystem.git
cd AgenticRealEstateSystem

# 2. Install UV (ultra-fast package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies (10-100x faster than pip!)
uv sync

# 4. Setup environment
cp .env.example .env
nano .env  # Add your API keys

# 5. Start the system
uv run python api_server.py
```

**Done!** Access the system at `http://localhost:8000`

---

## Detailed Installation

### Step 1: Install Python

#### Windows

```powershell
# Using winget
winget install Python.Python.3.12

# Or download from python.org
# https://www.python.org/downloads/windows/
```

#### macOS

```bash
# Using Homebrew
brew install python@3.12
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

**Verify Installation:**
```bash
python3 --version
# Should show: Python 3.12.x or higher
```

### Step 2: Install UV Package Manager

UV is a blazing-fast Python package installer (10-100x faster than pip).

#### Linux/macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.cargo/bin:$PATH"

# Verify installation
uv --version
```

#### Windows (PowerShell)

```powershell
irm https://astral.sh/uv/install.ps1 | iex

# Verify installation
uv --version
```

### Step 3: Clone Repository

```bash
# Using HTTPS
git clone https://github.com/your-org/AgenticRealEstateSystem.git

# Or using SSH
git clone git@github.com:your-org/AgenticRealEstateSystem.git

# Enter directory
cd AgenticRealEstateSystem
```

### Step 4: Install Dependencies

#### Using UV (Recommended)

```bash
# Install all dependencies
uv sync

# This creates a virtual environment and installs:
# - pydantic-ai[logfire,openrouter]
# - langgraph + langgraph-swarm
# - fastapi + uvicorn
# - All development tools
```

#### Using pip (Alternative)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# Or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Step 5: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```bash
# Core Configuration
ENVIRONMENT=development
DEBUG=true
DATA_MODE=mock  # Use 'real' for production

# API Keys (Required for agents)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# API Keys (Required for real mode)
RENTCAST_API_KEY=your-rentcast-key
GOOGLE_API_KEY=your-google-key

# Observability (Optional)
LOGFIRE_TOKEN=your-logfire-token
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=agentic-real-estate
```

**Get API Keys:**

1. **OpenRouter**: Sign up at [openrouter.ai](https://openrouter.ai)
2. **RentCast**: Sign up at [rentcast.io](https://rentcast.io)
3. **Google Calendar**: Get credentials from [Google Cloud Console](https://console.cloud.google.com)
4. **Logfire**: Sign up at [logfire.pydantic.dev](https://logfire.pydantic.dev)
5. **LangSmith**: Sign up at [smith.langchain.com](https://smith.langchain.com)

### Step 6: Verify Installation

```bash
# Check Python packages
uv run python -c "import pydantic_ai; import langgraph_swarm; print('✓ All packages installed')"

# Check environment variables
uv run python check_env.py

# Run basic tests
uv run pytest tests/ -v

# Start development server
uv run python api_server.py
```

**Expected Output:**
```
✓ All packages installed
✓ Environment variables loaded
✓ Mock data system initialized
✓ Server starting on http://localhost:8000
```

---

## Configuration

### Environment Variables Reference

#### Core Settings

```bash
# Environment mode
ENVIRONMENT=development  # development or production
DEBUG=true              # Enable detailed logging

# Data source
DATA_MODE=mock          # mock (development) or real (production)
```

#### API Configuration

```bash
# OpenRouter (Required)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# RentCast (Real mode only)
RENTCAST_API_KEY=your-rentcast-key
RENTCAST_BASE_URL=https://api.rentcast.io/v1

# Google Calendar (Real mode only)
GOOGLE_API_KEY=your-google-key
GOOGLE_CALENDAR_ID=primary
```

#### Model Configuration

```bash
# LLM Provider
LLM_PROVIDER=openrouter
LLM_DEFAULT_MODEL=mistralai/mistral-7b-instruct:free
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000

# Agent-specific models
LLM_SEARCH_MODEL=mistralai/mistral-7b-instruct:free
LLM_PROPERTY_MODEL=mistralai/mistral-7b-instruct:free
LLM_SCHEDULING_MODEL=mistralai/mistral-7b-instruct:free
```

#### Database Configuration

```bash
# SQLite (Default)
DB_URL=sqlite:///./real_estate.db
DB_ECHO=false

# PostgreSQL (Production)
# DB_URL=postgresql://user:pass@localhost:5432/real_estate
# DB_POOL_SIZE=10
# DB_MAX_OVERFLOW=20

# DuckDB (Mock data)
DUCKDB_DB_PATH=data/properties.duckdb
DUCKDB_AUTO_MIGRATE=true
```

#### Observability

```bash
# Logfire (PydanticAI tracing)
LOGFIRE_TOKEN=your-logfire-token
LOGFIRE_PROJECT=agentic-real-estate

# LangSmith (LangGraph tracing)
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=agentic-real-estate
LANGCHAIN_TRACING_V2=true

# Custom logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/agentic_real_estate.log
```

### Configuration Files

#### pyproject.toml

Main project configuration. Do not modify unless adding new dependencies.

```toml
[project]
name = "agentic-real-estate"
version = "1.2.0"
requires-python = ">=3.11"
```

#### .env.example

Template for environment variables. Copy to `.env` and fill in your values.

---

## Verification

### System Health Check

```bash
# 1. Check API server
curl http://localhost:8000/api/health

# Expected output:
# {
#   "status": "healthy",
#   "version": "1.2.0",
#   "data_mode": "mock"
# }
```

### Component Verification

```bash
# 2. Test property search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "apartments in San Francisco"}'

# 3. Check dashboard
open http://localhost:8000/dashboard/

# 4. Test agent interaction
uv run python -c "
from app.orchestration.unified_swarm import get_unified_swarm_orchestrator
import asyncio

async def test():
    orchestrator = get_unified_swarm_orchestrator()
    result = await orchestrator.process_message({
        'messages': [{'role': 'user', 'content': 'Hello'}],
        'session_id': 'test'
    })
    print(result['messages'][-1]['content'])

asyncio.run(test())
"
```

### Run Test Suite

```bash
# Unit tests
uv run pytest tests/agents/ -v

# Integration tests
uv run pytest tests/integration/ -v

# All tests with coverage
uv run pytest --cov=app tests/

# Expected: 80%+ coverage
```

---

## Development Setup

### Development Tools

```bash
# Install development dependencies
uv add --dev pytest pytest-cov pytest-asyncio
uv add --dev ruff black mypy
uv add --dev pre-commit

# Setup pre-commit hooks
pre-commit install

# Run code quality checks
ruff check .           # Linting
black .                # Formatting
mypy app/              # Type checking
```

### IDE Configuration

#### VSCode

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. Open project
2. Settings → Project → Python Interpreter → Add Local Interpreter
3. Select `.venv` directory
4. Enable pytest in Settings → Tools → Python Integrated Tools

### Hot Reload Development

```bash
# Start server with auto-reload
uv run uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

# Or use the development script
chmod +x scripts/dev.sh
./scripts/dev.sh
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Start with debugger
uv run python -m debugpy --listen 5678 api_server.py

# Or use VSCode launch configuration
# See .vscode/launch.json
```

---

## Production Deployment

### Docker Deployment

#### Build Image

```bash
# Build production image
docker build -t agentic-real-estate:latest .

# Build with specific platform
docker build --platform linux/amd64 -t agentic-real-estate:latest .
```

#### Run Container

```bash
# Run with environment file
docker run -d \
  --name agentic-real-estate \
  -p 8000:8000 \
  --env-file .env.production \
  agentic-real-estate:latest

# Run with volume for data persistence
docker run -d \
  --name agentic-real-estate \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --env-file .env.production \
  agentic-real-estate:latest
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    image: agentic-real-estate:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATA_MODE=real
    env_file:
      - .env.production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=real_estate
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

Start services:
```bash
docker-compose up -d
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentic-real-estate
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentic-real-estate
  template:
    metadata:
      labels:
        app: agentic-real-estate
    spec:
      containers:
      - name: app
        image: agentic-real-estate:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATA_MODE
          value: "real"
        envFrom:
        - secretRef:
            name: api-keys
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

Apply configuration:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Monitoring Setup

```bash
# Health check endpoint for load balancer
curl http://localhost:8000/api/health

# Metrics endpoint (Prometheus format)
curl http://localhost:8000/metrics

# Dashboard for monitoring
open http://localhost:8000/dashboard/
```

---

## Troubleshooting Setup

### Common Installation Issues

#### 1. Python Version Too Old

**Error:** `requires-python = ">=3.11" but you have Python 3.10`

**Solution:**
```bash
# Install Python 3.12
pyenv install 3.12.0
pyenv local 3.12.0

# Or use system package manager
sudo apt install python3.12  # Ubuntu
brew install python@3.12     # macOS
```

#### 2. UV Installation Fails

**Error:** `curl: command not found` or `Permission denied`

**Solution:**
```bash
# Install curl first
sudo apt install curl  # Ubuntu
brew install curl      # macOS

# Install UV with sudo if needed
curl -LsSf https://astral.sh/uv/install.sh | sudo sh

# Or download manually
wget https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz
tar -xzf uv-x86_64-unknown-linux-gnu.tar.gz
sudo mv uv /usr/local/bin/
```

#### 3. Dependency Installation Fails

**Error:** `Package conflicts` or `Could not find compatible versions`

**Solution:**
```bash
# Clear UV cache
uv cache clean

# Reinstall from scratch
rm -rf .venv
uv sync --reinstall

# If still fails, use pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

#### 4. API Key Not Found

**Error:** `ValueError: Valid OpenRouter API key required`

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify API key format (no spaces or quotes)
cat .env | grep OPENROUTER_API_KEY

# Correct format:
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Incorrect formats:
# OPENROUTER_API_KEY="sk-or-v1-your-key-here"  ❌ (quotes)
# OPENROUTER_API_KEY= sk-or-v1-your-key-here   ❌ (space)
```

#### 5. Port Already in Use

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# Or use different port
uv run python api_server.py --port 8001
```

### Platform-Specific Issues

#### Windows

```powershell
# If script execution is disabled
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If path issues
$env:PATH += ";$HOME\.cargo\bin"

# If SSL errors
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .
```

#### macOS

```bash
# If SSL certificate errors
pip install --upgrade certifi

# If command not found after UV install
export PATH="$HOME/.cargo/bin:$PATH"
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
```

#### Linux

```bash
# If permission denied on /usr/local
sudo chown -R $USER:$USER /usr/local

# If missing development headers
sudo apt install python3-dev build-essential

# If SQLite version too old
sudo apt install libsqlite3-dev
```

### Getting Help

1. **Check documentation**: Review setup guide again
2. **Search issues**: Check GitHub issues for similar problems
3. **Enable debug mode**: Run with `DEBUG=true` for detailed logs
4. **Ask for help**: Create GitHub issue with error details

---

## Next Steps

After successful installation:

1. **Explore the dashboard**: `http://localhost:8000/dashboard/`
2. **Try API endpoints**: See [API Reference](API_REFERENCE.md)
3. **Run examples**: Check `examples/` directory
4. **Read architecture docs**: See [System Architecture](reviews/README.md)
5. **Start development**: See [Development Guide](DEVELOPMENT.md)

---

**Setup Guide Maintained By:** Documentation Agent
**Last Updated:** 2025-11-11
**Status:** ✅ Complete
