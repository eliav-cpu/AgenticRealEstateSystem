# Context Engineering Pipeline Design

## Overview

This document outlines the context engineering architecture for intelligent prompt management, retrieval-augmented generation (RAG), and memory systems to enhance LLM performance in the real estate reviews system.

## Architecture Overview

```
User Query
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│              Context Engineering Pipeline                   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 1. Query Analysis & Intent Detection                │ │
│  │    - Extract entities (location, price, features)   │ │
│  │    - Detect intent (search, analyze, schedule)      │ │
│  │    - Identify context needs                         │ │
│  └────────────────────┬─────────────────────────────────┘ │
│                       │                                    │
│  ┌────────────────────▼─────────────────────────────────┐ │
│  │ 2. Context Retrieval (RAG)                          │ │
│  │    - Semantic search in vector store                │ │
│  │    - Retrieve relevant properties/reviews           │ │
│  │    - Rank and filter results                        │ │
│  └────────────────────┬─────────────────────────────────┘ │
│                       │                                    │
│  ┌────────────────────▼─────────────────────────────────┐ │
│  │ 3. Memory Integration                               │ │
│  │    - Short-term: Session context                    │ │
│  │    - Long-term: User preferences                    │ │
│  │    - Conversation history                           │ │
│  └────────────────────┬─────────────────────────────────┘ │
│                       │                                    │
│  ┌────────────────────▼─────────────────────────────────┐ │
│  │ 4. Prompt Construction                              │ │
│  │    - Template selection                             │ │
│  │    - Dynamic context injection                      │ │
│  │    - Few-shot examples                              │ │
│  │    - Chain-of-thought prompting                     │ │
│  └────────────────────┬─────────────────────────────────┘ │
│                       │                                    │
└───────────────────────┼────────────────────────────────────┘
                        │
                        ▼
                    LLM (Groq)
                        │
                        ▼
                  Response
```

## 1. Prompt Template System

### Template Structure

```python
# app/context/prompts/templates.py
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class PromptTemplate(BaseModel):
    """Base prompt template."""

    name: str = Field(..., description="Template identifier")
    system_prompt: str = Field(..., description="System instructions")
    user_prompt_template: str = Field(..., description="User message template with placeholders")
    few_shot_examples: List[Dict[str, str]] = Field(default_factory=list)
    variables: List[str] = Field(default_factory=list, description="Required template variables")
    max_context_length: int = Field(default=4000, description="Max context tokens")

    def render(self, variables: Dict[str, Any]) -> str:
        """Render template with variables."""
        return self.user_prompt_template.format(**variables)

    def build_messages(
        self,
        user_input: str,
        variables: Dict[str, Any] = None,
        include_examples: bool = True
    ) -> List[Dict[str, str]]:
        """Build complete message list for LLM."""

        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add few-shot examples
        if include_examples and self.few_shot_examples:
            for example in self.few_shot_examples:
                messages.append({"role": "user", "content": example["input"]})
                messages.append({"role": "assistant", "content": example["output"]})

        # Add user message with context
        if variables:
            user_content = self.render(variables)
        else:
            user_content = user_input

        messages.append({"role": "user", "content": user_content})

        return messages
```

### Agent-Specific Templates

```python
# app/context/prompts/property_templates.py
PROPERTY_ANALYSIS_TEMPLATE = PromptTemplate(
    name="property_analysis",
    system_prompt="""You are an expert real estate analyst with deep knowledge of property markets,
pricing trends, and neighborhood characteristics. Your role is to provide detailed, accurate, and
helpful property analysis to users.

Key Responsibilities:
- Analyze property features and their value
- Compare properties and provide recommendations
- Explain pricing in context of market and location
- Identify pros and cons objectively
- Provide actionable insights

Always be:
- Specific and data-driven
- Honest about property limitations
- Clear about assumptions
- Helpful without being pushy""",

    user_prompt_template="""Analyze this property in detail:

Property Information:
{property_details}

Recent Reviews:
{recent_reviews}

Neighborhood Context:
{neighborhood_info}

User Question: {user_question}

Provide a comprehensive analysis addressing the user's question while considering:
1. Property features and value proposition
2. Location advantages and considerations
3. Review sentiment and common themes
4. Price competitiveness
5. Recommendations based on the analysis""",

    few_shot_examples=[
        {
            "input": "Is this apartment worth $3,500/month for a 2-bedroom in Brickell?",
            "output": """Based on the analysis:

**Value Assessment**: At $3,500/month for 2BR/2BA with 1,200 sq ft, this property is competitively priced for Brickell. The neighborhood average for similar units is $3,200-$3,800.

**Key Value Drivers**:
- Prime location near Financial District (walkable to work)
- Modern amenities (pool, gym, 24/7 security)
- Recent renovation (2023) with high-end finishes
- Positive reviews (4.3/5 stars) citing safety and maintenance

**Considerations**:
- Reviews mention occasional noise from nearby construction
- Parking included but limited guest spots
- HOA fee of $450/month is above neighborhood average

**Recommendation**: Fair market value given location and amenities. The $350 premium over average is justified by recent renovation and building amenities. Consider if walking distance to work justifies the cost."""
        }
    ],

    variables=["property_details", "recent_reviews", "neighborhood_info", "user_question"],
    max_context_length=6000
)

# Review analysis template
REVIEW_ANALYSIS_TEMPLATE = PromptTemplate(
    name="review_analysis",
    system_prompt="""You are a review analysis expert specializing in real estate. Your role is to
analyze property reviews, identify patterns, extract sentiment, and provide actionable insights.

Analysis Framework:
1. Sentiment: Positive, neutral, negative aspects
2. Common themes: What reviewers consistently mention
3. Red flags: Issues that appear repeatedly
4. Context: Consider reviewer type and stay duration
5. Reliability: Assess review credibility

Always provide:
- Balanced perspective (pros and cons)
- Specific examples from reviews
- Pattern recognition across multiple reviews
- Actionable recommendations""",

    user_prompt_template="""Analyze these reviews for the property:

Property: {property_title}
Location: {property_location}

Reviews ({review_count} total):
{reviews_text}

Analysis Request: {analysis_question}

Provide a comprehensive review analysis including:
1. Overall sentiment breakdown
2. Most common positive themes
3. Most common negative themes
4. Reliability indicators
5. Key takeaways for potential tenants""",

    few_shot_examples=[
        {
            "input": "What are tenants saying about maintenance in this building?",
            "output": """**Maintenance Analysis** (Based on 23 reviews mentioning maintenance):

**Overall Sentiment**: Mostly positive (70% positive, 20% neutral, 10% negative)

**Positive Patterns**:
- Quick response time: "Maintenance requests resolved within 24-48 hours" (mentioned 8 times)
- Professional staff: "Friendly and competent maintenance team" (5 reviews)
- Proactive: "Regular building inspections prevent issues" (3 reviews)

**Areas of Concern**:
- AC issues in summer: 2 reviewers mentioned AC repairs taking longer than expected
- Weekend coverage: Limited maintenance staff on weekends

**Recommendation**: Maintenance appears reliable with quick response times. However, for urgent AC issues in summer, may want to confirm warranty coverage. Overall, maintenance quality is above average for the area."""
        }
    ],

    variables=["property_title", "property_location", "reviews_text", "review_count", "analysis_question"],
    max_context_length=8000
)
```

## 2. Retrieval-Augmented Generation (RAG)

### Vector Store Implementation

```python
# app/context/retrieval/vector_store.py
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class VectorStore:
    """Vector store for semantic search of properties and reviews."""

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        dimension: int = 384
    ):
        self.model = SentenceTransformer(embedding_model)
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents: List[Dict[str, Any]] = []

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to vector store."""

        # Extract text for embedding
        texts = [doc["text"] for doc in documents]

        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))

        # Store document metadata
        self.documents.extend(documents)

    def search(
        self,
        query: str,
        k: int = 5,
        filter_fn: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""

        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Search FAISS index
        distances, indices = self.index.search(
            query_embedding.astype('float32'),
            k * 2  # Get more results for filtering
        )

        # Retrieve documents
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc["similarity_score"] = float(1 / (1 + dist))  # Convert distance to similarity
                results.append(doc)

        # Apply filter if provided
        if filter_fn:
            results = [doc for doc in results if filter_fn(doc)]

        # Return top k results
        return results[:k]

    async def hybrid_search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Combine semantic search with metadata filtering."""

        # Semantic search
        semantic_results = self.search(query, k=k*3)

        # Apply metadata filters
        if filters:
            filtered_results = []
            for doc in semantic_results:
                if self._matches_filters(doc, filters):
                    filtered_results.append(doc)
        else:
            filtered_results = semantic_results

        # Re-rank and return top k
        return self._rerank(query, filtered_results)[:k]

    def _matches_filters(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if document matches metadata filters."""
        for key, value in filters.items():
            if key not in doc.get("metadata", {}):
                return False
            if doc["metadata"][key] != value:
                return False
        return True

    def _rerank(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-rank documents using additional criteria."""
        # Can implement more sophisticated re-ranking here
        # For now, just sort by similarity score
        return sorted(documents, key=lambda x: x["similarity_score"], reverse=True)
```

### RAG Pipeline

```python
# app/context/retrieval/rag_pipeline.py
from typing import List, Dict, Any
from app.context.retrieval.vector_store import VectorStore
from app.models.property import Property
from app.models.review import Review

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline."""

    def __init__(
        self,
        property_store: VectorStore,
        review_store: VectorStore,
        max_context_length: int = 6000
    ):
        self.property_store = property_store
        self.review_store = review_store
        self.max_context_length = max_context_length

    async def retrieve_context(
        self,
        query: str,
        context_type: str = "property_analysis",
        filters: Dict[str, Any] = None,
        k_properties: int = 3,
        k_reviews: int = 5
    ) -> Dict[str, Any]:
        """Retrieve relevant context for query."""

        context = {}

        # Retrieve relevant properties
        if context_type in ["property_analysis", "property_search"]:
            properties = await self.property_store.hybrid_search(
                query=query,
                filters=filters,
                k=k_properties
            )
            context["properties"] = self._format_properties(properties)

        # Retrieve relevant reviews
        if context_type in ["property_analysis", "review_analysis"]:
            reviews = await self.review_store.hybrid_search(
                query=query,
                filters=filters,
                k=k_reviews
            )
            context["reviews"] = self._format_reviews(reviews)

        # Ensure context fits within token limit
        context = self._truncate_context(context)

        return context

    def _format_properties(self, properties: List[Dict[str, Any]]) -> str:
        """Format properties for context injection."""
        formatted = []

        for prop in properties:
            formatted.append(f"""
Property: {prop['metadata']['title']}
Location: {prop['metadata']['neighborhood']}, {prop['metadata']['city']}
Type: {prop['metadata']['property_type']}
Price: ${prop['metadata']['price']}/month
Features: {prop['metadata']['bedrooms']}BR, {prop['metadata']['bathrooms']}BA
Amenities: {', '.join(prop['metadata']['amenities'][:5])}
Description: {prop['text'][:200]}...
            """.strip())

        return "\n\n".join(formatted)

    def _format_reviews(self, reviews: List[Dict[str, Any]]) -> str:
        """Format reviews for context injection."""
        formatted = []

        for review in reviews:
            formatted.append(f"""
Rating: {review['metadata']['rating']}/5 stars
Reviewer: {review['metadata']['reviewer_type']} ({review['metadata']['stay_duration_months']} months)
Review: {review['text']}
Sentiment: {review['metadata']['sentiment']}
            """.strip())

        return "\n\n".join(formatted)

    def _truncate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Truncate context to fit within token limit."""
        # Approximate: 1 token ≈ 4 characters
        max_chars = self.max_context_length * 4

        total_chars = sum(len(str(v)) for v in context.values())

        if total_chars > max_chars:
            # Proportionally reduce each section
            reduction_factor = max_chars / total_chars
            for key in context:
                if isinstance(context[key], str):
                    target_length = int(len(context[key]) * reduction_factor)
                    context[key] = context[key][:target_length]

        return context
```

## 3. Memory Management

### Short-Term Memory (Session)

```python
# app/context/memory/short_term.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque

class SessionMemory:
    """Short-term memory for conversation context."""

    def __init__(self, max_messages: int = 10, ttl_minutes: int = 30):
        self.max_messages = max_messages
        self.ttl = timedelta(minutes=ttl_minutes)
        self.messages: deque = deque(maxlen=max_messages)
        self.context: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now()
        })
        self.last_activity = datetime.now()

    def get_conversation_history(
        self,
        max_messages: Optional[int] = None,
        include_metadata: bool = False
    ) -> List[Dict[str, str]]:
        """Get recent conversation history."""
        messages = list(self.messages)

        if max_messages:
            messages = messages[-max_messages:]

        if not include_metadata:
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]

        return messages

    def update_context(self, key: str, value: Any):
        """Update session context."""
        self.context[key] = value
        self.last_activity = datetime.now()

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get session context value."""
        return self.context.get(key, default)

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return (datetime.now() - self.last_activity) > self.ttl

    def get_summary(self) -> Dict[str, Any]:
        """Get session summary."""
        return {
            "message_count": len(self.messages),
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "context_keys": list(self.context.keys()),
            "is_expired": self.is_expired()
        }
```

### Long-Term Memory (Persistent)

```python
# app/context/memory/long_term.py
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import sqlite3

class LongTermMemory:
    """Persistent memory across sessions."""

    def __init__(self, db_path: str = "data/memory.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interaction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                session_id TEXT,
                interaction_type TEXT,
                data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                pattern_type TEXT,
                pattern_data JSON,
                confidence REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Save user preferences."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (user_id, preferences, updated_at)
            VALUES (?, ?, ?)
        """, (user_id, json.dumps(preferences), datetime.now()))

        conn.commit()
        conn.close()

    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user preferences."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT preferences FROM user_preferences WHERE user_id = ?
        """, (user_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return json.loads(result[0])
        return None

    def record_interaction(
        self,
        user_id: str,
        session_id: str,
        interaction_type: str,
        data: Dict[str, Any]
    ):
        """Record user interaction for learning."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO interaction_history (user_id, session_id, interaction_type, data)
            VALUES (?, ?, ?, ?)
        """, (user_id, session_id, interaction_type, json.dumps(data)))

        conn.commit()
        conn.close()

    def learn_pattern(
        self,
        user_id: str,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        confidence: float
    ):
        """Store learned pattern."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO learned_patterns (user_id, pattern_type, pattern_data, confidence)
            VALUES (?, ?, ?, ?)
        """, (user_id, pattern_type, json.dumps(pattern_data), confidence))

        conn.commit()
        conn.close()

    def get_learned_patterns(
        self,
        user_id: str,
        pattern_type: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Retrieve learned patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT pattern_type, pattern_data, confidence
            FROM learned_patterns
            WHERE user_id = ? AND confidence >= ?
        """
        params = [user_id, min_confidence]

        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return [
            {
                "pattern_type": row[0],
                "pattern_data": json.loads(row[1]),
                "confidence": row[2]
            }
            for row in results
        ]
```

### Memory Manager

```python
# app/context/memory/manager.py
from typing import Dict, Any, Optional
from app.context.memory.short_term import SessionMemory
from app.context.memory.long_term import LongTermMemory

class MemoryManager:
    """Coordinate short-term and long-term memory."""

    def __init__(self):
        self.sessions: Dict[str, SessionMemory] = {}
        self.long_term = LongTermMemory()

    def get_session(self, session_id: str) -> SessionMemory:
        """Get or create session memory."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory()
        return self.sessions[session_id]

    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]
        for sid in expired:
            del self.sessions[sid]

    async def get_full_context(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get complete context from both memory systems."""

        context = {}

        # Short-term: Conversation history
        session = self.get_session(session_id)
        context["conversation_history"] = session.get_conversation_history()
        context["session_context"] = session.context

        # Long-term: User preferences and patterns
        if user_id:
            preferences = self.long_term.get_user_preferences(user_id)
            if preferences:
                context["user_preferences"] = preferences

            patterns = self.long_term.get_learned_patterns(user_id)
            if patterns:
                context["learned_patterns"] = patterns

        return context
```

## 4. Context Injection Pipeline

### Complete Pipeline Implementation

```python
# app/context/injection.py
from typing import Dict, Any, Optional, List
from app.context.prompts.templates import PromptTemplate
from app.context.retrieval.rag_pipeline import RAGPipeline
from app.context.memory.manager import MemoryManager

class ContextInjectionPipeline:
    """Complete context engineering pipeline."""

    def __init__(
        self,
        rag_pipeline: RAGPipeline,
        memory_manager: MemoryManager
    ):
        self.rag = rag_pipeline
        self.memory = memory_manager

    async def prepare_context(
        self,
        user_query: str,
        template: PromptTemplate,
        session_id: str,
        user_id: Optional[str] = None,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, str]]:
        """Prepare complete context for LLM."""

        # 1. Retrieve relevant context via RAG
        retrieved_context = await self.rag.retrieve_context(
            query=user_query,
            context_type=template.name,
            filters=filters
        )

        # 2. Get memory context
        memory_context = await self.memory.get_full_context(
            session_id=session_id,
            user_id=user_id
        )

        # 3. Combine contexts
        full_context = {
            **retrieved_context,
            "conversation_history": self._format_conversation_history(
                memory_context.get("conversation_history", [])
            ),
            "user_preferences": memory_context.get("user_preferences", {}),
            "user_query": user_query
        }

        # 4. Build messages using template
        messages = template.build_messages(
            user_input=user_query,
            variables=full_context
        )

        return messages

    def _format_conversation_history(
        self,
        history: List[Dict[str, str]],
        max_messages: int = 5
    ) -> str:
        """Format conversation history for context."""
        recent = history[-max_messages:]

        formatted = []
        for msg in recent:
            role = msg["role"].capitalize()
            content = msg["content"][:200]  # Truncate long messages
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)
```

## 5. Advanced Prompting Techniques

### Chain-of-Thought Prompting

```python
# app/context/prompts/chains.py
CHAIN_OF_THOUGHT_TEMPLATE = PromptTemplate(
    name="property_comparison_cot",
    system_prompt="""You are a real estate analyst. When comparing properties, use systematic
reasoning. Break down your analysis step-by-step before reaching conclusions.""",

    user_prompt_template="""Compare these two properties:

Property A:
{property_a}

Property B:
{property_b}

Question: {comparison_question}

Please analyze step-by-step:
1. First, identify key comparison dimensions
2. Then, evaluate each property on those dimensions
3. Next, consider trade-offs and user priorities
4. Finally, provide a clear recommendation with reasoning

Let's think through this carefully:""",

    few_shot_examples=[
        {
            "input": "Which property offers better value?",
            "output": """Let me analyze this step-by-step:

**Step 1: Identify comparison dimensions**
- Price per square foot
- Location quality
- Amenities included
- Condition/age
- Monthly costs (including HOA/utilities)

**Step 2: Evaluate each property**

Property A:
- $2,800/mo for 1,000 sqft = $2.80/sqft
- Prime location in downtown
- Modern amenities (gym, pool)
- Newly renovated (2023)
- $350/mo HOA

Property B:
- $2,400/mo for 1,100 sqft = $2.18/sqft
- Residential neighborhood, 15 min from downtown
- Basic amenities (gym only)
- Built 2015, good condition
- $250/mo HOA

**Step 3: Consider trade-offs**
- Property A costs $400 more but saves commute time/costs
- Property B offers more space and lower monthly costs
- Property A has newer finishes and more amenities

**Step 4: Recommendation**
Property B offers better value IF you don't mind the commute. You get 10% more space and save $500/month ($400 rent + $100 HOA). However, if walking to work is important, Property A's location premium may be worth it.

Bottom line: B for value, A for convenience."""
        }
    ],

    variables=["property_a", "property_b", "comparison_question"]
)
```

---

**Document Version**: 1.0.0
**Author**: Architecture Agent (Hive Mind)
**Date**: 2025-11-11
**Status**: READY FOR IMPLEMENTATION
