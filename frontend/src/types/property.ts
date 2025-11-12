// Tipos baseados na estrutura exata da API RentCast
export interface ListingAgent {
  name: string;
  phone: string;
  email: string;
  website: string;
}

export interface ListingOffice {
  name: string;
  phone: string;
  email: string;
}

export interface PropertyHistory {
  [date: string]: {
    event: string;
    price: number;
    listingType: string;
    listedDate: string;
    removedDate: string | null;
    daysOnMarket: number;
  };
}

export interface Property {
  id: string;
  formattedAddress: string;
  addressLine1: string;
  addressLine2: string;
  city: string;
  state: string;
  zipCode: string;
  county: string;
  latitude: number;
  longitude: number;
  propertyType: string;
  bedrooms: number;
  bathrooms: number;
  squareFootage: number;
  lotSize: number;
  yearBuilt: number;
  status: string;
  price: number;
  listingType: string;
  listedDate: string;
  removedDate: string | null;
  createdDate: string;
  lastSeenDate: string;
  daysOnMarket: number;
  mlsName: string;
  mlsNumber: string;
  listingAgent: ListingAgent;
  listingOffice: ListingOffice;
  history: PropertyHistory;
}

export interface SearchFilters {
  city?: string;
  state?: string;
  minPrice?: number;
  maxPrice?: number;
  minBedrooms?: number;
  maxBedrooms?: number;
  minBathrooms?: number;
  maxBathrooms?: number;
  propertyType?: string;
  minSquareFootage?: number;
  maxSquareFootage?: number;
}

export interface SearchResponse {
  properties: Property[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export type ApiMode = 'mock' | 'real';

export interface PropertyCardProps {
  property: Property;
  onSelect?: (property: Property) => void;
  onSchedule?: (property: Property) => void;
  className?: string;
}

export interface SearchFormProps {
  onSearch: (filters: SearchFilters) => void;
  loading?: boolean;
  initialFilters?: SearchFilters;
} 