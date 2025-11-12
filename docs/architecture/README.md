# System Architecture Documentation

## Overview

This directory contains comprehensive architecture documentation for the Real Estate Reviews System refactor, designed to support 10,000+ house entries with intelligent LLM integration and complete observability.

## Document Index

### 1. [System Architecture Design](./SYSTEM_ARCHITECTURE_DESIGN.md)
**Primary document** - Complete system architecture overview

**Key Topics:**
- Layer-by-layer architecture breakdown
- Component interaction diagrams
- Technology stack decisions
- Directory structure and module organization
- Performance targets and scalability
- Security considerations
- Migration path from mock to production

**Critical Decisions:**
- **ADR-001**: DuckDB for mock data storage
- **ADR-002**: Groq as primary LLM provider
- **ADR-003**: Repository Pattern for data access
- **ADR-004**: Multi-layer caching strategy
- **ADR-005**: Comprehensive observability stack

### 2. [Mock Data Design](./MOCK_DATA_DESIGN.md)
**Data architecture** - 10,000+ property and review generation

**Key Topics:**
- DuckDB schema design (properties, reviews, amenities)
- Data generation algorithms
- Realistic distribution strategies (geographic, pricing, sentiment)
- Quality assurance and validation
- Query optimization patterns
- Backup and versioning

**Data Specifications:**
- 10,000 properties across 7 major cities
- Realistic property type distribution
- 50,000+ reviews with sentiment analysis
- Geographic clustering by neighborhood
- Market-realistic pricing patterns

### 3. [LLM Integration Design](./LLM_INTEGRATION_DESIGN.md)
**LLM architecture** - Groq provider with fallback chain

**Key Topics:**
- Groq provider implementation
- Fallback chain (Groq → OpenRouter → Ollama)
- Model selection strategy
- Response caching (Redis)
- Token usage tracking and cost management
- Error handling and retry logic
- Request batching for efficiency
- Agent-specific configuration

**Performance Targets:**
- <1s response time with Groq
- 80%+ cache hit rate
- <$50/day LLM costs
- Automatic failover <5s

### 4. [Context Engineering Design](./CONTEXT_ENGINEERING_DESIGN.md)
**Context pipeline** - RAG, memory, and prompt engineering

**Key Topics:**
- Prompt template system
- Retrieval-Augmented Generation (RAG) with vector store (FAISS)
- Memory management (short-term session + long-term persistent)
- Context injection pipeline
- Chain-of-thought prompting
- Few-shot learning examples

**Pipeline Stages:**
1. Query analysis & intent detection
2. Context retrieval via semantic search
3. Memory integration (session + user preferences)
4. Dynamic prompt construction
5. LLM execution with enriched context

### 5. [Observability Design](./OBSERVABILITY_DESIGN.md)
**Monitoring stack** - Langfuse, Logfire, Grafana

**Key Topics:**
- Langfuse for LLM call tracking and cost analysis
- Logfire for distributed tracing
- Prometheus metrics collection
- Grafana dashboards and alerts
- Structured logging with structlog
- Custom analytics for business metrics

**Monitored Metrics:**
- LLM request rate, latency, costs
- Agent execution success rate
- Token usage by provider/model
- Cache hit rates
- Database query performance
- Active user sessions

## Quick Reference

### Key Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data Storage** | DuckDB | Mock data (10K+ properties) |
| | SQLite | Metadata and configuration |
| | Redis | Caching and sessions |
| **LLM Provider** | Groq | Primary (Llama 3, Mixtral) |
| | OpenRouter | Fallback provider |
| | Ollama | Local development |
| **Vector Store** | FAISS | Semantic search embeddings |
| **Orchestration** | LangGraph-Swarm | Agent coordination |
| **Agent Framework** | PydanticAI | Type-safe agents |
| **API** | FastAPI | REST endpoints |
| **Observability** | Langfuse | LLM monitoring |
| | Logfire | Distributed tracing |
| | Grafana | Metrics dashboards |
| | Prometheus | Metrics collection |

### Directory Structure Reference

```
AgenticRealEstateSystem/
├── app/
│   ├── agents/              # Agent implementations
│   ├── api/                 # REST API endpoints
│   ├── context/             # NEW: Context engineering
│   │   ├── prompts/         # Prompt templates
│   │   ├── retrieval/       # RAG pipeline
│   │   └── memory/          # Memory management
│   ├── data/                # NEW: Data layer
│   │   ├── interfaces/      # Repository interfaces
│   │   ├── sources/         # Mock/API implementations
│   │   └── generators/      # Mock data generation
│   ├── database/            # Database connections
│   │   ├── duckdb/          # NEW: DuckDB for mock data
│   │   ├── sqlite/          # Metadata
│   │   └── redis/           # Cache
│   ├── integrations/        # External integrations
│   │   └── llm/             # NEW: LLM providers
│   ├── observability/       # NEW: Observability stack
│   └── orchestration/       # Swarm orchestration
├── config/                  # Configuration
├── data/                    # NEW: Data storage
│   ├── properties.duckdb    # Mock properties
│   └── backups/             # Database backups
├── docs/
│   └── architecture/        # THIS DIRECTORY
├── scripts/                 # Utility scripts
│   ├── generate_mock_data.py
│   └── migrate_to_duckdb.py
└── tests/                   # Test suites
```

## Implementation Phases

### Phase 1: Data Layer (Week 1)
**Focus**: Mock data generation and storage
- [ ] Implement DuckDB schema
- [ ] Create property generator (10K entries)
- [ ] Create review generator (50K+ reviews)
- [ ] Implement repository interfaces
- [ ] Seed database with realistic data

**Deliverables**: Working DuckDB with 10K properties

### Phase 2: LLM Integration (Week 2)
**Focus**: Groq provider with fallback
- [ ] Implement Groq provider
- [ ] Set up fallback chain
- [ ] Implement response caching
- [ ] Add token tracking
- [ ] Configure model selection

**Deliverables**: Working LLM pipeline with <1s responses

### Phase 3: Context Engineering (Week 3)
**Focus**: RAG and memory systems
- [ ] Implement vector store (FAISS)
- [ ] Create prompt templates
- [ ] Build RAG pipeline
- [ ] Implement memory management
- [ ] Add context injection

**Deliverables**: Intelligent context-aware responses

### Phase 4: Observability (Week 4)
**Focus**: Monitoring and analytics
- [ ] Configure Langfuse
- [ ] Set up Logfire tracing
- [ ] Create Grafana dashboards
- [ ] Implement metrics collection
- [ ] Add alert rules

**Deliverables**: Complete observability stack

### Phase 5: Testing & Optimization (Week 5)
**Focus**: Performance tuning
- [ ] Unit tests for all components
- [ ] Integration tests
- [ ] Load testing (100+ concurrent users)
- [ ] Performance optimization
- [ ] Cost optimization

**Deliverables**: Production-ready system

## Design Principles

### 1. Separation of Concerns
- Clear boundaries between layers
- Interface-driven architecture
- Easy to swap implementations

### 2. Modularity
- Self-contained modules
- Minimal dependencies
- High cohesion

### 3. Testability
- Interface mocking
- Dependency injection
- Isolated test data

### 4. Observability
- Comprehensive logging
- Distributed tracing
- Metrics at all levels

### 5. Scalability
- Stateless design
- Multi-layer caching
- Async operations

### 6. Future-Proof
- API abstraction
- Provider agnostic
- Feature flags

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Property Search | <500ms (p95) | Including LLM analysis |
| Review Analysis | <1000ms (p95) | With Groq |
| LLM Response | <1500ms (p95) | End-to-end |
| Concurrent Users | 100+ | Simultaneous users |
| Database Queries | <100ms (p95) | DuckDB queries |
| Cache Hit Rate | >80% | Redis cache |
| Uptime | 99.9% | System availability |
| Error Rate | <0.1% | Failed requests |

## Cost Projections

### Development Phase (Mock Data)
- **LLM Costs**: ~$5-10/day (testing)
- **Infrastructure**: Free (local development)

### Production Phase
- **LLM Costs**: ~$20-50/day (with caching)
- **Infrastructure**: ~$50/month (Redis, monitoring)
- **Total**: ~$650-1,550/month

**Cost Optimization Strategies:**
- Response caching (80% hit rate)
- Groq free tier for development
- Efficient prompt engineering
- Token usage monitoring

## Migration Path: Mock → Production

### Current State (Mock)
```python
# Uses DuckDB with 10K generated properties
data_mode = "mock"
repository = MockPropertyRepository(duckdb_conn)
```

### Hybrid Mode
```python
# Some features use real API
data_mode = "hybrid"
if feature_flag("use_real_reviews"):
    repository = APIReviewRepository()
else:
    repository = MockReviewRepository()
```

### Production Mode
```python
# All features use real APIs
data_mode = "production"
repository = APIPropertyRepository(api_client)
```

**Migration Steps:**
1. Verify mock implementation matches API contract
2. Enable feature flags for specific functionality
3. Gradually migrate features to real APIs
4. Monitor performance and costs
5. Complete migration to production

## Support and Resources

### Team Coordination (Hive Mind)
- **Architect**: System design and decisions
- **Researcher**: Technology evaluation and best practices
- **Coder**: Implementation and integration
- **Tester**: Quality assurance and testing
- **DevOps**: Infrastructure and deployment

### Shared Memory Keys
- `hive/architecture/summary`: Architecture overview
- `hive/architecture/complete-designs`: All design documents
- `hive/research/findings`: Technology research
- `hive/implementation/progress`: Implementation status

### External Documentation
- [DuckDB Documentation](https://duckdb.org/docs/)
- [Groq API Documentation](https://console.groq.com/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Langfuse Documentation](https://langfuse.com/docs)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)

---

**Architecture Version**: 1.0.0
**Status**: ✅ **APPROVED FOR IMPLEMENTATION**
**Last Updated**: 2025-11-11
**Architect**: Architecture Agent (Hive Mind)
**Review Status**: Complete - Ready for Development Phase
