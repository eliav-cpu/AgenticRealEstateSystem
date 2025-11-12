# System Architecture Design - Reviews System Refactor

## Executive Summary

This document presents the comprehensive system architecture for the Real Estate Reviews System refactor, designed to support 10,000+ house entries with intelligent LLM integration via Groq, comprehensive observability, and clean modular structure for seamless future API integration.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│  (React Frontend / REST API / CLI)                                  │
└────────────────────┬────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                                 │
│  - Request Validation                                                │
│  - Rate Limiting                                                     │
│  - Authentication/Authorization                                      │
│  - Request/Response Logging                                          │
└────────────────────┬────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  LangGraph-Swarm Orchestrator                               │   │
│  │  - Agent Coordination                                        │   │
│  │  - Context Management                                        │   │
│  │  - Memory Management (Short-term + Long-term)               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────────┐
│                    AGENT LAYER                                       │
│  ┌───────────┐  ┌────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Search   │  │  Property  │  │  Scheduling  │  │   Review    │ │
│  │  Agent    │  │  Agent     │  │  Agent       │  │   Agent     │ │
│  └─────┬─────┘  └──────┬─────┘  └──────┬───────┘  └──────┬──────┘ │
└────────┼────────────────┼────────────────┼──────────────────┼────────┘
         │                │                │                  │
┌────────▼────────────────▼────────────────▼──────────────────▼────────┐
│                  CONTEXT ENGINEERING LAYER                            │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Prompt Engineering Pipeline                                   │  │
│  │  - Template Management                                         │  │
│  │  - Dynamic Context Injection                                   │  │
│  │  - Few-Shot Learning Examples                                  │  │
│  │  - Chain-of-Thought Prompting                                  │  │
│  └────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Retrieval System (RAG)                                        │  │
│  │  - Vector Store (FAISS/Chroma)                                 │  │
│  │  - Semantic Search                                             │  │
│  │  - Context Ranking                                             │  │
│  │  - Relevance Filtering                                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Memory Management                                             │  │
│  │  - Short-term (Session Memory)                                 │  │
│  │  - Long-term (Cross-session Memory)                            │  │
│  │  - User Preference Memory                                      │  │
│  │  - Context Window Management                                   │  │
│  └────────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│                       LLM INTEGRATION LAYER                            │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Groq LLM Provider (Primary)                                   │   │
│  │  - Model: llama3-8b-8192 / mixtral-8x7b-32768                 │   │
│  │  - Ultra-fast inference (<1s)                                  │   │
│  │  - Cost-effective                                              │   │
│  └────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Fallback Providers                                            │   │
│  │  - OpenRouter (Mistral/Gemma)                                  │   │
│  │  - Ollama (Local fallback)                                     │   │
│  └────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  LLM Middleware                                                │   │
│  │  - Request/Response Caching                                    │   │
│  │  - Token Management                                            │   │
│  │  - Error Handling & Retry Logic                               │   │
│  │  - Rate Limiting                                               │   │
│  └────────────────────────────────────────────────────────────────┘   │
└───────────────────────────┬───────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│                      DATA ACCESS LAYER                                 │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Repository Pattern                                            │   │
│  │  - PropertyRepository                                          │   │
│  │  - ReviewRepository                                            │   │
│  │  - UserRepository                                              │   │
│  │  - AppointmentRepository                                       │   │
│  └────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Data Source Abstraction                                       │   │
│  │  - Interface: IDataSource                                      │   │
│  │  - MockDataSource (Development)                                │   │
│  │  - APIDataSource (Production)                                  │   │
│  └────────────────────────────────────────────────────────────────┘   │
└───────────────────────────┬───────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│                      DATA STORAGE LAYER                                │
│  ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐     │
│  │  DuckDB          │  │  SQLite         │  │  Redis Cache     │     │
│  │  (Mock Data)     │  │  (Metadata)     │  │  (Session Data)  │     │
│  │  - 10K houses    │  │  - User prefs   │  │  - Rate limits   │     │
│  │  - Reviews       │  │  - Sessions     │  │  - LLM cache     │     │
│  │  - Analytics     │  │  - Audit logs   │  │  - Temp data     │     │
│  └──────────────────┘  └─────────────────┘  └──────────────────┘     │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY LAYER (Cross-cutting)                  │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌────────────────┐   │
│  │  Langfuse  │  │  Logfire   │  │  Grafana │  │  Structlog     │   │
│  │  (LLM)     │  │  (Tracing) │  │  (Metrics│  │  (Logs)        │   │
│  └────────────┘  └────────────┘  └──────────┘  └────────────────┘   │
└───────────────────────────────────────────────────────────────────────┘
```

## Core Design Principles

### 1. Separation of Concerns
- **Clear Layer Boundaries**: Each layer has a single responsibility
- **Interface-Driven**: All layers communicate through well-defined interfaces
- **Dependency Injection**: Easy to swap implementations (mock ↔ real)

### 2. Modularity
- **Self-Contained Modules**: Each module can be developed/tested independently
- **Loose Coupling**: Minimal dependencies between modules
- **High Cohesion**: Related functionality grouped together

### 3. Testability
- **Interface Mocking**: Easy to mock any layer for testing
- **Dependency Injection**: Facilitates unit testing
- **Test Data Separation**: Clear separation between test and production data

### 4. Observability
- **Comprehensive Logging**: Structured logs at all levels
- **Distributed Tracing**: End-to-end request tracing
- **Metrics Collection**: Performance and business metrics
- **LLM Monitoring**: Special focus on LLM call tracking

### 5. Scalability
- **Horizontal Scaling**: Stateless design enables easy scaling
- **Caching Strategy**: Multi-layer caching (Redis, LLM, DB)
- **Async Processing**: Non-blocking operations where possible

### 6. Future-Proof Design
- **API Abstraction**: Easy to replace mock data with real APIs
- **Provider Agnostic**: LLM provider can be changed without system changes
- **Feature Flags**: Easy to enable/disable features

## Directory Structure

```
AgenticRealEstateSystem/
├── app/
│   ├── agents/                      # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py                  # Base agent interface
│   │   ├── search.py                # Search agent
│   │   ├── property.py              # Property agent
│   │   ├── scheduling.py            # Scheduling agent
│   │   └── review.py                # NEW: Review agent
│   │
│   ├── api/                         # REST API
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── properties.py
│   │   │   ├── reviews.py           # NEW: Review endpoints
│   │   │   ├── chat.py
│   │   │   └── health.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── logging.py
│   │   │   └── rate_limit.py
│   │   └── dashboard.py
│   │
│   ├── context/                     # NEW: Context Engineering
│   │   ├── __init__.py
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   ├── templates.py         # Prompt templates
│   │   │   ├── examples.py          # Few-shot examples
│   │   │   └── chains.py            # Chain-of-thought prompts
│   │   ├── retrieval/
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py      # Vector DB integration
│   │   │   ├── embeddings.py        # Embedding generation
│   │   │   └── ranker.py            # Context ranking
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── short_term.py        # Session memory
│   │   │   ├── long_term.py         # Persistent memory
│   │   │   └── manager.py           # Memory coordinator
│   │   └── injection.py             # Context injection logic
│   │
│   ├── data/                        # Data layer
│   │   ├── __init__.py
│   │   ├── interfaces/              # NEW: Data abstractions
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # IDataSource interface
│   │   │   ├── property_repo.py
│   │   │   └── review_repo.py       # NEW: Review repository
│   │   ├── sources/                 # NEW: Data source implementations
│   │   │   ├── __init__.py
│   │   │   ├── mock/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── property_mock.py
│   │   │   │   └── review_mock.py   # NEW: Mock reviews
│   │   │   └── api/
│   │   │       ├── __init__.py
│   │   │       ├── property_api.py
│   │   │       └── review_api.py    # NEW: Real review API
│   │   ├── generators/              # NEW: Mock data generation
│   │   │   ├── __init__.py
│   │   │   ├── property_generator.py
│   │   │   ├── review_generator.py  # NEW: Generate reviews
│   │   │   └── fixtures.py
│   │   └── migrations/              # NEW: Data migrations
│   │       ├── __init__.py
│   │       └── migrate_to_duckdb.py
│   │
│   ├── database/                    # Database layer
│   │   ├── __init__.py
│   │   ├── duckdb/                  # NEW: DuckDB for mock data
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   ├── schema.py
│   │   │   └── queries.py
│   │   ├── sqlite/                  # SQLite for metadata
│   │   │   ├── __init__.py
│   │   │   └── connection.py
│   │   └── redis/                   # Redis for caching
│   │       ├── __init__.py
│   │       └── client.py
│   │
│   ├── integrations/                # External integrations
│   │   ├── __init__.py
│   │   ├── llm/                     # NEW: LLM integration
│   │   │   ├── __init__.py
│   │   │   ├── groq_provider.py     # NEW: Groq integration
│   │   │   ├── openrouter_provider.py
│   │   │   ├── ollama_provider.py
│   │   │   ├── base.py              # Provider interface
│   │   │   └── middleware.py        # Caching, retry, etc.
│   │   └── mcp.py
│   │
│   ├── models/                      # Domain models
│   │   ├── __init__.py
│   │   ├── property.py
│   │   ├── review.py                # NEW: Review model
│   │   ├── appointment.py
│   │   ├── user.py
│   │   └── response.py
│   │
│   ├── observability/               # NEW: Observability layer
│   │   ├── __init__.py
│   │   ├── langfuse_config.py       # NEW: Langfuse setup
│   │   ├── logfire_config.py
│   │   ├── grafana/                 # NEW: Grafana integration
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py
│   │   │   └── dashboards/
│   │   └── logger.py
│   │
│   ├── orchestration/               # Swarm orchestration
│   │   ├── __init__.py
│   │   ├── swarm.py
│   │   ├── swarm_fixed.py
│   │   └── swarm_hybrid.py
│   │
│   ├── prompts/                     # Agent prompts
│   │   ├── __init__.py
│   │   ├── property.py
│   │   ├── scheduling.py
│   │   ├── search.py
│   │   └── review.py                # NEW: Review prompts
│   │
│   ├── tools/                       # Agent tools
│   │   ├── __init__.py
│   │   ├── calendar.py
│   │   ├── property.py
│   │   └── review.py                # NEW: Review tools
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── api_monitor.py
│       ├── container.py             # NEW: Dependency injection
│       ├── datetime_context.py
│       ├── langsmith_config.py
│       ├── logfire_config.py
│       ├── logging.py
│       └── ollama_fallback.py
│
├── config/                          # Configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── api_config.py
│   └── observability.yaml           # NEW: Observability config
│
├── data/                            # Data storage
│   ├── properties.duckdb            # NEW: DuckDB database
│   ├── reviews.duckdb               # NEW: Reviews database
│   ├── backups/                     # NEW: Backup directory
│   └── fixtures/                    # JSON fixtures
│       ├── properties.json
│       └── reviews.json             # NEW: Review fixtures
│
├── docs/                            # Documentation
│   ├── architecture/                # NEW: Architecture docs
│   │   ├── SYSTEM_ARCHITECTURE_DESIGN.md
│   │   ├── MOCK_DATA_DESIGN.md
│   │   ├── LLM_INTEGRATION_DESIGN.md
│   │   ├── CONTEXT_ENGINEERING_DESIGN.md
│   │   └── OBSERVABILITY_DESIGN.md
│   └── api/
│       └── openapi.yaml
│
├── scripts/                         # Utility scripts
│   ├── setup.sh
│   ├── generate_mock_data.py        # NEW: Generate mock data
│   ├── migrate_to_duckdb.py         # NEW: Migration script
│   └── seed_database.py             # NEW: Seed script
│
├── tests/                           # Tests
│   ├── unit/
│   │   ├── agents/
│   │   ├── context/                 # NEW: Context tests
│   │   └── data/                    # NEW: Data layer tests
│   ├── integration/
│   │   ├── api/
│   │   └── llm/                     # NEW: LLM integration tests
│   └── fixtures/
│       └── test_data.json
│
├── .env.example                     # Environment template
├── pyproject.toml                   # Project configuration
└── README.md                        # Project documentation
```

## Key Architectural Decisions

### ADR-001: DuckDB for Mock Data Storage
**Decision**: Use DuckDB as the primary storage for 10,000+ mock house entries and reviews

**Rationale**:
- Columnar storage optimized for analytics queries
- 10-100x faster than SQLite for large datasets
- Native support for complex analytical queries
- Easy migration path to production data warehouse
- Zero-dependency embedded database
- Excellent Python integration

**Alternatives Considered**:
- SQLite: Too slow for 10K+ entries with complex queries
- PostgreSQL: Overkill for development, requires external service
- JSON files: Not performant for queries, no indexing

### ADR-002: Groq as Primary LLM Provider
**Decision**: Use Groq as the primary LLM provider with OpenRouter fallback

**Rationale**:
- Ultra-fast inference (<1 second response time)
- Cost-effective compared to OpenAI
- Support for Llama 3 8B and Mixtral models
- Free tier available for development
- Production-grade reliability

**Alternatives Considered**:
- OpenAI: More expensive, slower
- OpenRouter: Good fallback, used as secondary
- Local Ollama: Good for offline, but slower

### ADR-003: Repository Pattern for Data Access
**Decision**: Implement Repository Pattern with interface abstraction

**Rationale**:
- Clean separation between business logic and data access
- Easy to swap mock data with real API calls
- Testability through interface mocking
- Consistent data access patterns across the application

**Implementation**:
```python
# Interface
class IPropertyRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: int) -> Optional[Property]: ...

    @abstractmethod
    async def search(self, criteria: SearchCriteria) -> SearchResult: ...

# Mock implementation
class MockPropertyRepository(IPropertyRepository):
    def __init__(self, duckdb_connection):
        self.db = duckdb_connection

    async def find_by_id(self, id: int) -> Optional[Property]:
        # Query DuckDB
        ...

# Real API implementation
class APIPropertyRepository(IPropertyRepository):
    def __init__(self, api_client):
        self.api = api_client

    async def find_by_id(self, id: int) -> Optional[Property]:
        # Call external API
        ...
```

### ADR-004: Multi-Layer Caching Strategy
**Decision**: Implement caching at multiple layers

**Layers**:
1. **Redis Cache**: Session data, rate limits (TTL: minutes-hours)
2. **LLM Response Cache**: Identical prompts, embeddings (TTL: hours-days)
3. **Database Query Cache**: Frequent queries (TTL: minutes)
4. **In-Memory Cache**: Hot data (TTL: seconds)

**Rationale**:
- Reduce LLM API costs (cached responses)
- Improve response times
- Reduce database load
- Better user experience

### ADR-005: Comprehensive Observability Stack
**Decision**: Integrate Langfuse, Logfire, and Grafana

**Components**:
- **Langfuse**: LLM call tracking, token usage, cost analysis
- **Logfire**: Distributed tracing, PydanticAI integration
- **Grafana**: System metrics, custom dashboards
- **Structlog**: Structured logging with JSON output

**Rationale**:
- Langfuse specializes in LLM observability
- Logfire provides native PydanticAI integration
- Grafana for infrastructure metrics
- Comprehensive visibility into system behavior

## Technology Stack

### Core Framework
- **Python 3.11+**: Modern Python with type hints
- **PydanticAI**: Type-safe agent framework
- **LangGraph-Swarm**: Agent orchestration
- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server

### Data Layer
- **DuckDB**: Mock data storage (10K+ entries)
- **SQLite**: Metadata and configuration
- **Redis**: Caching and session management
- **Pydantic**: Data validation and serialization

### LLM Integration
- **Groq**: Primary LLM provider (Llama 3, Mixtral)
- **OpenRouter**: Fallback provider
- **Ollama**: Local development fallback
- **FAISS/Chroma**: Vector storage for embeddings

### Observability
- **Langfuse**: LLM monitoring and analytics
- **Logfire**: Distributed tracing
- **Grafana**: Metrics and dashboards
- **Structlog**: Structured logging
- **Prometheus**: Metrics collection

### Development Tools
- **UV**: Ultra-fast package manager
- **Ruff**: Linting and formatting
- **MyPy**: Type checking
- **Pytest**: Testing framework
- **Pre-commit**: Git hooks

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│              Load Balancer (Nginx)              │
└──────────────┬──────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌───────▼──────┐
│  API       │    │  API         │
│  Instance  │    │  Instance    │
│  1         │    │  2           │
└───┬────────┘    └───────┬──────┘
    │                     │
    └──────────┬──────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌───────▼──────┐
│  Redis     │    │  DuckDB      │
│  Cache     │    │  (Read-only) │
└────────────┘    └──────────────┘
    │
┌───▼─────────────────────────────┐
│  Observability Stack            │
│  - Langfuse                     │
│  - Grafana + Prometheus         │
│  - Log Aggregation              │
└─────────────────────────────────┘
```

## Performance Targets

### Response Times
- **Property Search**: <500ms (p95)
- **Property Details**: <200ms (p95)
- **Review Analysis**: <1000ms (p95) with Groq
- **LLM Response**: <1500ms (p95)

### Scalability
- **Concurrent Users**: 100+ simultaneous users
- **Database**: 10,000+ properties with instant queries
- **Cache Hit Rate**: >80% for frequently accessed data
- **API Throughput**: 1000+ requests/minute

### Reliability
- **Uptime**: 99.9% availability
- **Error Rate**: <0.1% of requests
- **LLM Fallback**: <5s to activate fallback provider

## Security Considerations

### API Security
- Rate limiting per IP/user
- JWT-based authentication
- Request validation with Pydantic
- CORS configuration
- API key rotation

### Data Security
- Sensitive data encryption at rest
- Secure credential storage
- Environment variable isolation
- Audit logging for all data access

### LLM Security
- Prompt injection prevention
- Input sanitization
- Output validation
- Token usage monitoring
- Cost control mechanisms

## Migration Path: Mock → Production

### Phase 1: Interface Compliance
Current mock implementation already uses repository interfaces

### Phase 2: Feature Flags
```python
# config/settings.py
class Settings:
    data_mode: Literal["mock", "hybrid", "production"] = "mock"
```

### Phase 3: Hybrid Mode
```python
# Run mock for development, real API for specific features
if settings.data_mode == "hybrid":
    if feature_flag("use_real_api_for_reviews"):
        return APIReviewRepository()
    else:
        return MockReviewRepository()
```

### Phase 4: Full Production
Simply change `data_mode = "production"` in configuration

## Next Steps

1. **Mock Data Generation** (RESEARCHER → CODER)
   - Generate 10,000 diverse house entries
   - Create realistic review dataset
   - Implement DuckDB schema and seeding

2. **Context Engineering Pipeline** (ARCHITECT → CODER)
   - Implement prompt templates
   - Set up vector store for RAG
   - Create memory management system

3. **Groq Integration** (CODER)
   - Implement Groq provider
   - Set up fallback chain
   - Add caching layer

4. **Observability Setup** (DEVOPS)
   - Configure Langfuse
   - Set up Grafana dashboards
   - Implement structured logging

5. **Testing & Validation** (TESTER)
   - Unit tests for all repositories
   - Integration tests for LLM pipeline
   - Performance benchmarking

---

**Document Version**: 1.0.0
**Author**: Architecture Agent (Hive Mind)
**Date**: 2025-11-11
**Status**: APPROVED FOR IMPLEMENTATION
