#!/usr/bin/env python3
"""
Sistema de Fallback Inteligente usando Ollama.

Quando OpenRouter falha, usa Ollama local com modelo gemma3n:e2b 
para manter as características agênticas do sistema.
"""

import asyncio
import httpx
import json
from typing import Dict, Any, Optional
from .logging import get_logger, log_api_call, log_error

class OllamaFallback:
    """Sistema de fallback usando Ollama local."""
    
    def __init__(self, model_name: str = "gemma3n:e2b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.logger = get_logger("ollama_fallback")
        self._is_available = None
    
    async def is_available(self) -> bool:
        """Verificar se Ollama está disponível e o modelo está instalado."""
        if self._is_available is not None:
            return self._is_available
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Verificar se Ollama está rodando
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code != 200:
                    self._is_available = False
                    return False
                
                # Verificar se o modelo está disponível
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                
                if self.model_name in model_names:
                    self._is_available = True
                    self.logger.info(f"Ollama model {self.model_name} is available")
                    return True
                else:
                    self.logger.warning(f"Ollama model {self.model_name} not found. Available: {model_names}")
                    # Tentar instalar o modelo automaticamente
                    await self._pull_model()
                    self._is_available = True
                    return True
                    
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
            self._is_available = False
            return False
    
    async def _pull_model(self) -> bool:
        """Tentar fazer pull do modelo automaticamente."""
        try:
            self.logger.info(f"Trying to pull model {self.model_name}...")
            
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout for model pull
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": self.model_name},
                    timeout=300.0
                )
                
                if response.status_code == 200:
                    self.logger.info(f"Successfully pulled model {self.model_name}")
                    return True
                else:
                    self.logger.error(f"Failed to pull model: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error pulling model: {e}")
            return False
    
    async def generate_response(
        self, 
        agent_name: str, 
        user_message: str, 
        property_context: Dict[str, Any] = None,
        data_mode: str = "mock"
    ) -> str:
        """
        Gerar resposta agêntica usando Ollama.
        
        Mantém as mesmas características do sistema principal.
        """
        if not await self.is_available():
            self.logger.warning("Ollama not available, using static fallback")
            return self._static_fallback(agent_name, user_message, property_context, data_mode)
        
        try:
            # Criar prompt específico para cada agente
            prompt = self._create_agent_prompt(agent_name, user_message, property_context, data_mode)
            
            # Fazer chamada para Ollama
            start_time = asyncio.get_event_loop().time()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.9,
                            "max_tokens": 1000,
                            "stop": ["Human:", "User:", "\n\n---"]
                        }
                    },
                    timeout=60.0
                )
                
                duration = asyncio.get_event_loop().time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("response", "").strip()
                    
                    # Log da chamada bem-sucedida
                    log_api_call(
                        api_name="Ollama",
                        endpoint="/api/generate",
                        method="POST",
                        status_code=200,
                        duration=duration
                    )
                    
                    # Validar resposta
                    if len(content) < 20:
                        self.logger.warning(f"Ollama response too short: {content}")
                        return self._static_fallback(agent_name, user_message, property_context, data_mode)
                    
                    self.logger.info(f"Ollama fallback successful: {len(content)} chars")
                    return content
                    
                else:
                    self.logger.error(f"Ollama API error: {response.status_code}")
                    return self._static_fallback(agent_name, user_message, property_context, data_mode)
                    
        except Exception as e:
            self.logger.error(f"Ollama fallback error: {e}")
            log_error(e, context={"agent": agent_name, "operation": "ollama_fallback"})
            return self._static_fallback(agent_name, user_message, property_context, data_mode)
    
    def _create_agent_prompt(
        self, 
        agent_name: str, 
        user_message: str, 
        property_context: Dict[str, Any] = None,
        data_mode: str = "mock"
    ) -> str:
        """Criar prompt específico para cada agente."""
        
        # Contexto da propriedade se disponível
        property_info = ""
        if property_context:
            property_info = f"""
PROPERTY CONTEXT:
Address: {property_context.get('formattedAddress', 'N/A')}
Price: ${property_context.get('price', 'N/A')}/month
Bedrooms: {property_context.get('bedrooms', 'N/A')}
Bathrooms: {property_context.get('bathrooms', 'N/A')}
Size: {property_context.get('squareFootage', 'N/A')} sq ft
Type: {property_context.get('propertyType', 'N/A')}
Year Built: {property_context.get('yearBuilt', 'N/A')}
City: {property_context.get('city', 'N/A')}, {property_context.get('state', 'N/A')}
"""
        
        if agent_name == "search_agent":
            return f"""You are Alex, a professional real estate search specialist. You help clients find properties that match their needs and provide market insights.

User's Message: "{user_message}"
Data Mode: {data_mode.upper()}
{property_info}

INSTRUCTIONS:
1. Be helpful and professional in finding properties for the user
2. Ask clarifying questions about their preferences (location, budget, size, etc.)
3. Provide market insights and suggestions
4. Keep responses concise but informative (3-5 sentences)
5. Use appropriate emojis to make responses engaging
6. Always end with a helpful question or suggestion
7. Be conversational and friendly

Respond as Alex, the search specialist:"""

        elif agent_name == "property_agent":
            return f"""You are Emma, a professional real estate property expert. You provide detailed, objective, and helpful information about properties.

User's Message: "{user_message}"
Data Mode: {data_mode.upper()}
{property_info}

INSTRUCTIONS:
1. Provide detailed information about the property above
2. Answer specific questions about price, features, location, etc.
3. Be objective and informative but maintain a friendly tone
4. Use the property details provided above
5. Keep responses comprehensive but not overwhelming (3-6 sentences)
6. Use appropriate emojis to make responses engaging
7. Always reference the specific property address when answering
8. End with a question or suggestion to continue the conversation

Respond as Emma, the property expert:"""

        elif agent_name == "scheduling_agent":
            return f"""You are Mike, a professional scheduling assistant for real estate property viewings. You help clients schedule visits efficiently.

User's Message: "{user_message}"
Data Mode: {data_mode.upper()}
{property_info}

INSTRUCTIONS:
1. Help schedule property viewings and appointments
2. Provide specific available time slots (suggest 2-3 options)
3. Mention what to bring (ID, proof of income if applicable)
4. Specify viewing duration (typically 30-45 minutes)
5. Keep responses concise but complete (2-4 sentences)
6. Use appropriate emojis to make responses engaging
7. Always end with a clear next step or confirmation request
8. Be professional but friendly and accommodating

Respond as Mike, the scheduling assistant:"""

        else:
            return f"""You are a helpful real estate assistant. Respond to the user's message: "{user_message}"

Be professional, helpful, and concise. Use appropriate emojis and maintain a friendly tone."""
    
    def _static_fallback(
        self, 
        agent_name: str, 
        user_message: str, 
        property_context: Dict[str, Any] = None,
        data_mode: str = "mock"
    ) -> str:
        """Fallback estático como última opção."""
        
        if agent_name == "search_agent":
            return f"""Hello! I'm Alex, your search specialist. I'm here to help you find the perfect property.

I can help you search for properties based on:
• Location (city, neighborhood, zip code)  
• Price range and budget
• Number of bedrooms and bathrooms
• Property type (apartment, house, condo)
• Amenities and features you want

What type of property are you looking for today? Just tell me your preferences and I'll find the best matches!

*Ready to search {data_mode} listings*"""

        elif agent_name == "property_agent":
            if property_context:
                address = property_context.get('formattedAddress', 'Property')
                price = property_context.get('price', 0)
                bedrooms = property_context.get('bedrooms', 'N/A')
                bathrooms = property_context.get('bathrooms', 'N/A')
                
                return f"""Hi! I'm Emma, your property expert. Here are the details for this property:

🏠 **{address}**
💰 **Monthly Rent:** ${price}
🛏️ **Bedrooms:** {bedrooms}
🛁 **Bathrooms:** {bathrooms}

This property offers great value in the current market. What specific aspect would you like to know more about?

*Analysis from {data_mode} data*"""
            else:
                return f"""Hello! I'm Emma, your property expert. I provide detailed analysis and insights about any property you're interested in.

I can help you with property details, market analysis, neighborhood information, and more. Do you have a specific property you'd like me to analyze?

*Expert analysis using {data_mode} data*"""

        elif agent_name == "scheduling_agent":
            return f"""Hi! I'm Mike, your scheduling specialist. I can help you arrange property visits quickly and easily.

Just let me know which property interests you and your preferred times. I'll handle all the coordination and send you confirmation details.

Ready to schedule a visit? Which property would you like to see?

*Professional scheduling via {data_mode} platform*"""

        else:
            return f"Hello! I'm here to help you with your real estate needs. How can I assist you today? (Using {data_mode} data)"


# Instância global do fallback Ollama
_ollama_fallback = None

def get_ollama_fallback() -> OllamaFallback:
    """Obter instância singleton do OllamaFallback."""
    global _ollama_fallback
    if _ollama_fallback is None:
        _ollama_fallback = OllamaFallback()
    return _ollama_fallback

async def generate_intelligent_fallback(
    agent_name: str, 
    user_message: str, 
    property_context: Dict[str, Any] = None,
    data_mode: str = "mock"
) -> str:
    """
    Função principal para fallback inteligente.
    
    Tenta Ollama primeiro, depois fallback estático.
    """
    ollama = get_ollama_fallback()
    return await ollama.generate_response(agent_name, user_message, property_context, data_mode) 