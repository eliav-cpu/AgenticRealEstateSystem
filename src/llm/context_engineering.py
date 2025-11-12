"""
Context Engineering for LLM Optimization
Implements prompt optimization, context retrieval, and token management
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class ContextConfig:
    """Context engineering configuration"""
    max_context_tokens: int = 4000
    overlap_tokens: int = 200
    compression_ratio: float = 0.3
    retrieval_top_k: int = 5


class PromptOptimizer:
    """Optimize prompts for better LLM performance"""

    @staticmethod
    def create_real_estate_prompt(
        query: str,
        property_data: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Create optimized prompt for real estate queries"""

        # Base system context
        system_context = """You are an expert real estate assistant with deep knowledge of:
- Property valuation and market analysis
- Neighborhood characteristics and trends
- Home buying and selling processes
- Investment strategies
- Legal and financial considerations

Provide accurate, helpful, and actionable advice."""

        # Add property context if available
        property_context = ""
        if property_data:
            property_context = f"""

Current Property Context:
- Address: {property_data.get('address', 'N/A')}
- Price: ${property_data.get('price', 0):,}
- Bedrooms: {property_data.get('bedrooms', 'N/A')}
- Bathrooms: {property_data.get('bathrooms', 'N/A')}
- Square Feet: {property_data.get('square_feet', 'N/A'):,}
- Neighborhood: {property_data.get('neighborhood', 'N/A')}
- Features: {', '.join(property_data.get('amenities', [])[:5])}"""

        # Add conversation history if available
        history_context = ""
        if conversation_history:
            recent_history = conversation_history[-3:]  # Last 3 exchanges
            history_context = "\n\nRecent Conversation:\n"
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                history_context += f"{role.capitalize()}: {content}\n"

        # Combine all contexts
        full_prompt = f"""{system_context}{property_context}{history_context}

User Query: {query}

Please provide a comprehensive, helpful response."""

        return full_prompt

    @staticmethod
    def create_search_prompt(
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create optimized prompt for property search"""

        filter_context = ""
        if filters:
            filter_parts = []
            if "min_price" in filters or "max_price" in filters:
                min_p = filters.get("min_price", 0)
                max_p = filters.get("max_price", float('inf'))
                filter_parts.append(f"Price range: ${min_p:,} - ${max_p:,}")

            if "bedrooms" in filters:
                filter_parts.append(f"Bedrooms: {filters['bedrooms']}+")

            if "bathrooms" in filters:
                filter_parts.append(f"Bathrooms: {filters['bathrooms']}+")

            if "property_type" in filters:
                filter_parts.append(f"Type: {filters['property_type']}")

            if "city" in filters:
                filter_parts.append(f"City: {filters['city']}")

            if filter_parts:
                filter_context = "\n\nSearch Criteria:\n- " + "\n- ".join(filter_parts)

        prompt = f"""Analyze this property search request and provide relevant recommendations.

User Search Query: {query}{filter_context}

Based on the query and filters, suggest:
1. Properties that match the criteria
2. Alternative options if criteria is too restrictive
3. Important factors to consider
4. Questions to ask for better refinement"""

        return prompt

    @staticmethod
    def create_comparison_prompt(
        properties: List[Dict[str, Any]],
        comparison_factors: Optional[List[str]] = None
    ) -> str:
        """Create prompt for property comparison"""

        if not properties:
            return "No properties to compare."

        factors = comparison_factors or [
            "price", "location", "size", "amenities", "investment_potential"
        ]

        # Format properties for comparison
        property_summaries = []
        for i, prop in enumerate(properties, 1):
            summary = f"""Property {i}:
- Address: {prop.get('address', 'N/A')}, {prop.get('city', 'N/A')}
- Price: ${prop.get('price', 0):,}
- Size: {prop.get('square_feet', 0):,} sq ft
- Beds/Baths: {prop.get('bedrooms', 0)}/{prop.get('bathrooms', 0)}
- Year Built: {prop.get('year_built', 'N/A')}
- Key Features: {', '.join(prop.get('amenities', [])[:3])}"""
            property_summaries.append(summary)

        prompt = f"""Compare these properties and provide a detailed analysis:

{chr(10).join(property_summaries)}

Comparison Factors: {', '.join(factors)}

Provide:
1. Side-by-side comparison on each factor
2. Pros and cons of each property
3. Best use case for each property
4. Value assessment and investment potential
5. Final recommendation based on typical buyer priorities"""

        return prompt


class ContextRetriever:
    """Retrieve and manage relevant context for queries"""

    def __init__(self, config: Optional[ContextConfig] = None):
        """Initialize context retriever"""
        self.config = config or ContextConfig()

    def retrieve_relevant_properties(
        self,
        query: str,
        properties: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve most relevant properties for query"""
        k = top_k or self.config.retrieval_top_k

        # Simple keyword-based relevance scoring
        query_lower = query.lower()
        query_terms = set(re.findall(r'\w+', query_lower))

        scored_properties = []
        for prop in properties:
            score = 0

            # Score based on description match
            description = prop.get('description', '').lower()
            desc_terms = set(re.findall(r'\w+', description))
            score += len(query_terms & desc_terms) * 2

            # Score based on amenities match
            amenities = [a.lower() for a in prop.get('amenities', [])]
            for amenity in amenities:
                if any(term in amenity for term in query_terms):
                    score += 3

            # Score based on location match
            city = prop.get('city', '').lower()
            neighborhood = prop.get('neighborhood', '').lower()
            if any(term in city or term in neighborhood for term in query_terms):
                score += 5

            # Score based on property type match
            prop_type = prop.get('property_type', '').lower()
            if any(term in prop_type for term in query_terms):
                score += 2

            scored_properties.append((score, prop))

        # Sort by score and return top k
        scored_properties.sort(key=lambda x: x[0], reverse=True)
        return [prop for score, prop in scored_properties[:k]]

    def compress_context(
        self,
        context: str,
        max_length: Optional[int] = None
    ) -> str:
        """Compress context to fit token limits"""
        if not max_length:
            max_length = int(self.config.max_context_tokens * self.config.compression_ratio)

        # Simple compression: keep first and last parts
        if len(context) <= max_length:
            return context

        keep_start = max_length // 2
        keep_end = max_length // 2

        start = context[:keep_start]
        end = context[-keep_end:]

        return f"{start}\n\n[...content compressed...]\n\n{end}"

    def sliding_window_context(
        self,
        messages: List[Dict[str, str]],
        current_message: str
    ) -> List[Dict[str, str]]:
        """Manage context with sliding window"""
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4

        current_tokens = estimate_tokens(current_message)
        max_tokens = self.config.max_context_tokens - current_tokens

        # Keep adding messages from end until we hit limit
        selected_messages = []
        total_tokens = 0

        for msg in reversed(messages):
            msg_tokens = estimate_tokens(msg.get("content", ""))
            if total_tokens + msg_tokens > max_tokens:
                break
            selected_messages.insert(0, msg)
            total_tokens += msg_tokens

        return selected_messages


class TokenManager:
    """Manage token usage and optimization"""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimate: 1 token ≈ 4 characters for English
        return len(text) // 4

    @staticmethod
    def truncate_to_tokens(text: str, max_tokens: int) -> str:
        """Truncate text to approximate token limit"""
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "..."

    @staticmethod
    def optimize_property_data(
        property_data: Dict[str, Any],
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """Optimize property data to reduce tokens"""
        optimized = {
            "id": property_data.get("id"),
            "address": property_data.get("address"),
            "city": property_data.get("city"),
            "state": property_data.get("state"),
            "price": property_data.get("price"),
            "bedrooms": property_data.get("bedrooms"),
            "bathrooms": property_data.get("bathrooms"),
            "square_feet": property_data.get("square_feet"),
            "property_type": property_data.get("property_type"),
        }

        # Add top amenities only
        amenities = property_data.get("amenities", [])
        optimized["amenities"] = amenities[:3]

        # Truncate description
        description = property_data.get("description", "")
        optimized["description"] = description[:200]

        return optimized


# Example usage
if __name__ == "__main__":
    # Prompt optimization
    optimizer = PromptOptimizer()

    query = "I'm looking for a family home with a pool"
    property_data = {
        "address": "123 Main St",
        "price": 450000,
        "bedrooms": 4,
        "bathrooms": 2.5,
        "square_feet": 2500,
        "neighborhood": "Sunset Hills",
        "amenities": ["Pool", "Garage", "Fireplace", "Patio"]
    }

    prompt = optimizer.create_real_estate_prompt(query, property_data)
    print("=== Optimized Prompt ===")
    print(prompt[:500], "...\n")

    # Context retrieval
    retriever = ContextRetriever()

    sample_properties = [
        {"description": "Beautiful family home with pool", "city": "Austin", "amenities": ["Pool"]},
        {"description": "Downtown condo", "city": "Austin", "amenities": ["Gym"]},
        {"description": "Spacious house with large backyard", "city": "Houston", "amenities": ["Garden"]}
    ]

    relevant = retriever.retrieve_relevant_properties("family home pool Austin", sample_properties, top_k=2)
    print(f"=== Retrieved {len(relevant)} relevant properties ===")

    # Token management
    token_mgr = TokenManager()
    estimated = token_mgr.estimate_tokens(prompt)
    print(f"\n=== Token estimate: {estimated} tokens ===")
