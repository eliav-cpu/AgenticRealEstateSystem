"""
Ferramentas nativas do LangGraph para busca de propriedades.

Implementação sem dependências do LangChain, usando apenas LangGraph tools.
"""

from typing import List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
from langgraph.prebuilt import InjectedState

from ..models.property import Property, SearchCriteria, SearchResult, PropertyType, PropertyStatus
from ..utils.logging import get_logger
from config.settings import get_settings


class PropertySearchTool(BaseModel):
    """Ferramenta para busca de propriedades via APIs externas."""
    
    name: str = "property_search"
    description: str = "Buscar propriedades em APIs externas baseado em critérios"


def search_properties_api(
    criteria: SearchCriteria,
    state: Annotated[Dict[str, Any], InjectedState]
) -> SearchResult:
    """
    Ferramenta nativa para buscar propriedades em APIs externas.
    
    Args:
        criteria: Critérios de busca
        state: Estado injetado do LangGraph
    
    Returns:
        Resultado da busca com propriedades encontradas
    """
    logger = get_logger("property_tools")
    settings = get_settings()
    
    logger.info(f"Searching properties with criteria: {criteria}")
    
    # TODO: Implementar integração real com APIs
    # Por enquanto, retornar dados mock baseados nos critérios
    
    mock_properties = []
    
    # Simular propriedades baseadas nos critérios
    if "copacabana" in [n.lower() for n in criteria.neighborhoods]:
        mock_properties.append(
            Property(
                id=1,
                title="Apartamento Vista Mar - Copacabana",
                description="Lindo apartamento com vista para o mar, totalmente reformado",
                property_type=PropertyType.APARTMENT,
                status=PropertyStatus.FOR_RENT,
                address={
                    "street": "Rua Barata Ribeiro",
                    "number": "100",
                    "neighborhood": "Copacabana",
                    "city": "Rio de Janeiro",
                    "state": "RJ",
                    "latitude": -22.9711,
                    "longitude": -43.1822
                },
                features={
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "garage_spaces": 1,
                    "area_built": 85.0,
                    "has_balcony": True,
                    "has_security": True,
                    "allows_pets": True
                },
                rent_price=4500.00,
                condo_fee=800.00,
                images=[
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ],
                agent_name="João Silva",
                agent_phone="(21) 99999-9999",
                agent_email="joao@imobiliaria.com"
            )
        )
    
    if "ipanema" in [n.lower() for n in criteria.neighborhoods]:
        mock_properties.append(
            Property(
                id=2,
                title="Cobertura Duplex - Ipanema",
                description="Cobertura duplex com terraço e churrasqueira",
                property_type=PropertyType.APARTMENT,
                status=PropertyStatus.FOR_RENT,
                address={
                    "street": "Rua Visconde de Pirajá",
                    "number": "500",
                    "neighborhood": "Ipanema",
                    "city": "Rio de Janeiro", 
                    "state": "RJ",
                    "latitude": -22.9838,
                    "longitude": -43.2096
                },
                features={
                    "bedrooms": 3,
                    "bathrooms": 3,
                    "garage_spaces": 2,
                    "area_built": 150.0,
                    "has_pool": True,
                    "has_gym": True,
                    "has_balcony": True,
                    "has_security": True
                },
                rent_price=8500.00,
                condo_fee=1200.00,
                agent_name="Maria Santos",
                agent_phone="(21) 88888-8888",
                agent_email="maria@premium.com"
            )
        )
    
    # Filtrar por preço se especificado
    if criteria.max_price:
        mock_properties = [
            p for p in mock_properties 
            if p.main_price and p.main_price <= criteria.max_price
        ]
    
    # Filtrar por quartos se especificado
    if criteria.min_bedrooms:
        mock_properties = [
            p for p in mock_properties
            if p.features.bedrooms and p.features.bedrooms >= criteria.min_bedrooms
        ]
    
    result = SearchResult(
        properties=mock_properties,
        total_count=len(mock_properties),
        search_criteria=criteria,
        execution_time=0.5,
        has_next=False,
        has_previous=False,
        page_number=1,
        total_pages=1
    )
    
    logger.info(f"Found {len(mock_properties)} properties")
    return result


def get_property_details(
    property_id: int,
    state: Annotated[Dict[str, Any], InjectedState]
) -> Optional[Property]:
    """
    Ferramenta para obter detalhes de uma propriedade específica.
    
    Args:
        property_id: ID da propriedade
        state: Estado injetado
    
    Returns:
        Propriedade com detalhes completos ou None se não encontrada
    """
    logger = get_logger("property_tools")
    
    # TODO: Implementar busca real por ID
    # Por enquanto, retornar propriedade mock
    
    if property_id == 1:
        return Property(
            id=1,
            title="Apartamento Vista Mar - Copacabana",
            description="""
            Apartamento completamente reformado com vista deslumbrante para o mar de Copacabana.
            
            Características:
            - 2 quartos sendo 1 suíte
            - Sala ampla com varanda
            - Cozinha americana equipada
            - Área de serviço
            - 1 vaga de garagem
            
            Condomínio oferece:
            - Portaria 24h
            - Piscina
            - Salão de festas
            - Academia
            
            Localização privilegiada a 2 quadras da praia, próximo ao metrô e comércio.
            """,
            property_type=PropertyType.APARTMENT,
            status=PropertyStatus.FOR_RENT,
            address={
                "street": "Rua Barata Ribeiro",
                "number": "100",
                "complement": "Apto 801",
                "neighborhood": "Copacabana",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "postal_code": "22040-000",
                "latitude": -22.9711,
                "longitude": -43.1822
            },
            features={
                "bedrooms": 2,
                "bathrooms": 2,
                "garage_spaces": 1,
                "area_total": 85.0,
                "area_built": 75.0,
                "floor": 8,
                "total_floors": 15,
                "has_balcony": True,
                "has_security": True,
                "allows_pets": True,
                "is_furnished": False,
                "amenities": [
                    "Piscina", "Academia", "Salão de festas", 
                    "Portaria 24h", "Elevador", "Interfone"
                ]
            },
            rent_price=4500.00,
            condo_fee=800.00,
            iptu=150.00,
            images=[
                "https://example.com/sala.jpg",
                "https://example.com/quarto.jpg", 
                "https://example.com/cozinha.jpg",
                "https://example.com/varanda.jpg"
            ],
            virtual_tour_url="https://example.com/tour360",
            agent_name="João Silva",
            agent_phone="(21) 99999-9999",
            agent_email="joao@imobiliaria.com",
            agency_name="Imobiliária Copacabana"
        )
    
    logger.warning(f"Property {property_id} not found")
    return None


def calculate_property_score(
    property: Property,
    user_preferences: Dict[str, Any],
    state: Annotated[Dict[str, Any], InjectedState]
) -> float:
    """
    Ferramenta para calcular score de relevância de uma propriedade.
    
    Args:
        property: Propriedade a ser avaliada
        user_preferences: Preferências do usuário
        state: Estado injetado
    
    Returns:
        Score de 0.0 a 1.0 indicando relevância
    """
    logger = get_logger("property_tools")
    
    score = 0.0
    max_score = 0.0
    
    # Score por localização (peso 30%)
    preferred_neighborhoods = user_preferences.get("neighborhoods", [])
    if preferred_neighborhoods:
        max_score += 0.3
        if property.address.neighborhood.lower() in [n.lower() for n in preferred_neighborhoods]:
            score += 0.3
    
    # Score por preço (peso 25%)
    max_price = user_preferences.get("max_price")
    if max_price and property.main_price:
        max_score += 0.25
        price_ratio = property.main_price / max_price
        if price_ratio <= 1.0:
            score += 0.25 * (1.0 - price_ratio * 0.5)  # Melhor score para preços menores
    
    # Score por quartos (peso 20%)
    preferred_bedrooms = user_preferences.get("min_bedrooms")
    if preferred_bedrooms and property.features.bedrooms:
        max_score += 0.2
        if property.features.bedrooms >= preferred_bedrooms:
            score += 0.2
    
    # Score por amenidades (peso 15%)
    preferred_amenities = user_preferences.get("amenities", [])
    if preferred_amenities:
        max_score += 0.15
        property_amenities = property.features.amenities or []
        matches = sum(1 for amenity in preferred_amenities 
                     if any(amenity.lower() in pa.lower() for pa in property_amenities))
        if matches > 0:
            score += 0.15 * (matches / len(preferred_amenities))
    
    # Score por características especiais (peso 10%)
    max_score += 0.1
    special_features = 0
    if property.features.has_balcony:
        special_features += 1
    if property.features.has_security:
        special_features += 1
    if property.features.allows_pets:
        special_features += 1
    if property.virtual_tour_url:
        special_features += 1
    
    score += 0.1 * min(special_features / 4, 1.0)
    
    # Normalizar score
    final_score = score / max_score if max_score > 0 else 0.0
    
    logger.debug(f"Property {property.id} scored {final_score:.2f}")
    return final_score


# Lista de ferramentas disponíveis
PROPERTY_TOOLS = [
    search_properties_api,
    get_property_details,
    calculate_property_score
] 