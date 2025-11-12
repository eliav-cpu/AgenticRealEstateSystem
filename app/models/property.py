"""
Main models for real estate properties.

Following Pydantic data modeling best practices.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Literal
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, validator

# Importação opcional de geopy
try:
    from geopy.distance import geodesic
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False
    # Fallback function when geopy is not available
    def geodesic(*args, **kwargs):
        class MockGeodistance:
            @property
            def kilometers(self):
                return None
        return MockGeodistance()


class PropertyType(str, Enum):
    """Available property types."""
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    STUDIO = "studio"
    LOFT = "loft"
    COMMERCIAL = "commercial"
    LAND = "land"


class PropertyStatus(str, Enum):
    """Property status."""
    FOR_SALE = "for_sale"
    FOR_RENT = "for_rent"
    SOLD = "sold"
    RENTED = "rented"
    OFF_MARKET = "off_market"


class Address(BaseModel):
    """Address model."""
    street: str = Field(..., description="Street")
    number: Optional[str] = Field(None, description="Number")
    complement: Optional[str] = Field(None, description="Complement")
    neighborhood: str = Field(..., description="Neighborhood")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    country: str = Field(default="USA", description="Country")
    postal_code: Optional[str] = Field(None, description="ZIP Code")
    
    # Geographic coordinates
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    
    @property
    def full_address(self) -> str:
        """Formatted full address."""
        parts = [self.street]
        if self.number:
            parts.append(self.number)
        if self.complement:
            parts.append(self.complement)
        parts.extend([self.neighborhood, self.city, self.state])
        return ", ".join(parts)
    
    def distance_to(self, other: "Address") -> Optional[float]:
        """Calculate distance to another address in km."""
        if not all([self.latitude, self.longitude, other.latitude, other.longitude]):
            return None
        return geodesic(
            (self.latitude, self.longitude),
            (other.latitude, other.longitude)
        ).kilometers


class Features(BaseModel):
    """Property characteristics and amenities."""
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, description="Number of bathrooms")
    garage_spaces: Optional[int] = Field(None, description="Garage spaces")
    area_total: Optional[float] = Field(None, description="Total area in sq ft")
    area_built: Optional[float] = Field(None, description="Built area in sq ft")
    floor: Optional[int] = Field(None, description="Floor (for apartments)")
    total_floors: Optional[int] = Field(None, description="Total floors in building")
    
    # Boolean amenities
    has_pool: bool = Field(default=False, description="Has pool")
    has_gym: bool = Field(default=False, description="Has gym")
    has_garden: bool = Field(default=False, description="Has garden")
    has_balcony: bool = Field(default=False, description="Has balcony")
    has_elevator: bool = Field(default=False, description="Has elevator")
    has_security: bool = Field(default=False, description="Has security")
    allows_pets: bool = Field(default=False, description="Allows pets")
    is_furnished: bool = Field(default=False, description="Is furnished")
    
    # Custom amenities list
    amenities: List[str] = Field(default_factory=list, description="List of amenities")
    
    @validator("bedrooms", "bathrooms", "garage_spaces")
    def validate_positive_int(cls, v):
        if v is not None and v < 0:
            raise ValueError("Values must be positive")
        return v


class Property(BaseModel):
    """Main property model."""
    id: Optional[int] = Field(None, description="Unique property ID")
    external_id: Optional[str] = Field(None, description="External API ID")
    title: str = Field(..., description="Listing title")
    description: Optional[str] = Field(None, description="Detailed description")
    
    property_type: PropertyType = Field(..., description="Property type")
    status: PropertyStatus = Field(..., description="Property status")
    
    address: Address = Field(..., description="Property address")
    features: Features = Field(..., description="Property features")
    
    # Prices
    price: Optional[Decimal] = Field(None, description="Sale price")
    rent_price: Optional[Decimal] = Field(None, description="Rental price")
    price_per_sqm: Optional[Decimal] = Field(None, description="Price per sq ft")
    
    # Additional costs
    condo_fee: Optional[Decimal] = Field(None, description="HOA fee")
    iptu: Optional[Decimal] = Field(None, description="Property tax")
    
    # Media
    images: List[str] = Field(default_factory=list, description="Image URLs")
    virtual_tour_url: Optional[str] = Field(None, description="Virtual tour URL")
    
    # Agent information
    agent_name: Optional[str] = Field(None, description="Agent name")
    agent_phone: Optional[str] = Field(None, description="Agent phone")
    agent_email: Optional[str] = Field(None, description="Agent email")
    agency_name: Optional[str] = Field(None, description="Agency name")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Created date")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated date")
    source: Optional[str] = Field(None, description="Data source (API)")
    relevance_score: Optional[float] = Field(None, description="Relevance score")
    
    @validator("price", "rent_price", pre=True)
    def validate_prices(cls, v):
        if v is not None and v < 0:
            raise ValueError("Preços devem ser positivos")
        return v
    
    @property
    def main_price(self) -> Optional[Decimal]:
        """Retorna o preço principal baseado no status."""
        if self.status == PropertyStatus.FOR_SALE:
            return self.price
        elif self.status == PropertyStatus.FOR_RENT:
            return self.rent_price
        return None
    
    @property
    def price_formatted(self) -> str:
        """Retorna o preço formatado em reais."""
        price = self.main_price
        if price is None:
            return "Preço não informado"
        
        return f"R$ {price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @property
    def summary(self) -> str:
        """Resumo da propriedade."""
        parts = [
            f"{self.property_type.value.title()}",
            f"{self.features.bedrooms or '?'} quartos",
            f"{self.address.neighborhood}",
            self.price_formatted
        ]
        return " • ".join(parts)


class SearchCriteria(BaseModel):
    """Search criteria for properties."""
    
    # Location
    neighborhoods: List[str] = Field(default_factory=list, description="Desired neighborhoods")
    cities: List[str] = Field(default_factory=list, description="Desired cities")
    states: List[str] = Field(default_factory=list, description="Desired states")
    
    # Coordenadas para busca por proximidade
    center_lat: Optional[float] = Field(None, description="Latitude central")
    center_lng: Optional[float] = Field(None, description="Longitude central")
    radius_km: Optional[float] = Field(None, description="Raio de busca em km")
    
    # Tipo e status
    property_types: List[PropertyType] = Field(default_factory=list, description="Tipos de propriedade")
    status: List[PropertyStatus] = Field(default_factory=list, description="Status desejados")
    
    # Preços
    min_price: Optional[Decimal] = Field(None, description="Preço mínimo")
    max_price: Optional[Decimal] = Field(None, description="Preço máximo")
    
    # Características
    min_bedrooms: Optional[int] = Field(None, description="Mínimo de quartos")
    max_bedrooms: Optional[int] = Field(None, description="Máximo de quartos")
    min_bathrooms: Optional[int] = Field(None, description="Mínimo de banheiros")
    min_garage: Optional[int] = Field(None, description="Mínimo de vagas")
    
    # Área
    min_area: Optional[float] = Field(None, description="Área mínima em m²")
    max_area: Optional[float] = Field(None, description="Área máxima em m²")
    
    # Amenidades obrigatórias
    required_amenities: List[str] = Field(default_factory=list, description="Amenidades obrigatórias")
    
    # Configurações de busca
    limit: int = Field(default=20, description="Limite de resultados")
    offset: int = Field(default=0, description="Offset para paginação")
    sort_by: str = Field(default="relevance", description="Campo para ordenação")
    sort_order: Literal["asc", "desc"] = Field(default="desc", description="Ordem de ordenação")
    
    # Flags especiais
    clarification_needed: bool = Field(default=False, description="Indica se precisa de clarificação")
    clarification_message: Optional[str] = Field(None, description="Mensagem de clarificação")


class SearchResult(BaseModel):
    """Resultado de uma busca de propriedades."""
    properties: List[Property] = Field(..., description="Lista de propriedades encontradas")
    total_count: int = Field(..., description="Total de propriedades encontradas")
    search_criteria: SearchCriteria = Field(..., description="Critérios utilizados na busca")
    execution_time: float = Field(..., description="Tempo de execução da busca")
    
    # Estatísticas
    price_range: Optional[Dict[str, Decimal]] = Field(None, description="Faixa de preços")
    location_stats: Optional[Dict[str, int]] = Field(None, description="Estatísticas por localização")
    
    # Paginação
    has_next: bool = Field(False, description="Tem próxima página")
    has_previous: bool = Field(False, description="Tem página anterior")
    page_number: int = Field(1, description="Número da página atual")
    total_pages: int = Field(1, description="Total de páginas")
    
    @property
    def is_empty(self) -> bool:
        """Verifica se o resultado está vazio."""
        return len(self.properties) == 0
    
    @property
    def price_stats(self) -> Dict[str, Any]:
        """Estatísticas de preços."""
        if not self.properties:
            return {}
        
        prices = [p.main_price for p in self.properties if p.main_price]
        if not prices:
            return {}
        
        return {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices),
            "count": len(prices)
        } 