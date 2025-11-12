import { useState, useEffect } from 'react';
import { AlertCircle, RefreshCw, Filter, Grid, List } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { apiService } from '@/services/api';
import SearchForm from '@/components/SearchForm';
import PropertyCard from '@/components/PropertyCard';
import PropertyAgentChat from '@/components/PropertyAgentChat';
import { Property, SearchFilters } from '@/types/property';
import { validateProperties } from '@/utils/propertyHelpers';

export default function HomePage() {
  const { 
    state, 
    setProperties, 
    setLoading, 
    setError, 
    setSelectedProperty, 
    setSearchFilters,
    openChat
  } = useApp();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(true);

  // Carregar propriedades iniciais
  useEffect(() => {
    loadInitialProperties();
  }, [state.apiMode]);

  const loadInitialProperties = async () => {
    try {
      console.log(`🏠 [HOMEPAGE] Loading initial properties in ${state.apiMode} mode`);
      setLoading(true);
      setError(null);
      
      // Search properties without filters to show initial data
      const rawProperties = await apiService.searchProperties({});
      console.log(`📦 [HOMEPAGE] Received ${rawProperties.length} raw properties from API`);
      
      const validProperties = validateProperties(rawProperties);
      console.log(`✅ [HOMEPAGE] ${validProperties.length} properties passed validation`);
      
      setProperties(validProperties);
      console.log(`🎯 [HOMEPAGE] Set ${validProperties.length} properties in state`);
      
      if (rawProperties.length !== validProperties.length) {
        console.warn(`⚠️ [HOMEPAGE] Filtered out ${rawProperties.length - validProperties.length} invalid properties`);
      }
      
    } catch (error) {
      console.error('❌ [HOMEPAGE] Error loading properties:', error);
      setError(error instanceof Error ? error.message : 'Error loading properties');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (filters: SearchFilters) => {
    try {
      console.log(`🔍 [HOMEPAGE] Starting search with filters:`, filters);
      setLoading(true);
      setError(null);
      
      // Atualizar filtros no contexto
      setSearchFilters(filters);
      console.log(`💾 [HOMEPAGE] Updated search filters in context`);
      
      const rawProperties = await apiService.searchProperties(filters);
      console.log(`📦 [HOMEPAGE] Received ${rawProperties.length} raw properties from search`);
      
      const validProperties = validateProperties(rawProperties);
      console.log(`✅ [HOMEPAGE] ${validProperties.length} properties passed validation after search`);
      
      setProperties(validProperties);
      console.log(`🎯 [HOMEPAGE] Set ${validProperties.length} properties in state after search`);
      
      if (rawProperties.length !== validProperties.length) {
        console.warn(`⚠️ [HOMEPAGE] Filtered out ${rawProperties.length - validProperties.length} invalid properties`);
      }
      
      // Adicionar à busca histórica se houver cidade
      if (filters.city) {
        console.log(`📝 [HOMEPAGE] Would add "${filters.city}" to search history`);
      }
      
    } catch (error) {
      console.error('❌ [HOMEPAGE] Search error:', error);
      setError(error instanceof Error ? error.message : 'Error searching properties');
    } finally {
      setLoading(false);
    }
  };

  const handlePropertySelect = (property: Property) => {
    console.log('🏠 View Details clicked for property:', property.formattedAddress);
    console.log('🔍 State before openChat:', { chatOpen: state.chatOpen, chatProperty: state.chatProperty });
    setSelectedProperty(property);
    // Open AI chat for property details
    openChat(property, 'details');
    console.log('✅ openChat called with mode: details');
  };

  const handleScheduleAppointment = (property: Property) => {
    console.log('📅 Schedule Visit clicked for property:', property.formattedAddress);
    console.log('🔍 State before openChat:', { chatOpen: state.chatOpen, chatProperty: state.chatProperty });
    setSelectedProperty(property);
    // Open AI chat for scheduling
    openChat(property, 'schedule');
    console.log('✅ openChat called with mode: schedule');
  };

  const handleRefresh = () => {
    loadInitialProperties();
  };

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900">
                Search Properties
              </h1>
              <p className="mt-2 text-secondary-600">
                Find the perfect property with our intelligent system
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              {/* Toggle Filters */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  showFilters
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-white text-secondary-700 hover:bg-secondary-50'
                }`}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </button>

              {/* View Mode Toggle */}
              <div className="flex items-center bg-white rounded-lg p-1 border border-secondary-200">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'grid'
                      ? 'bg-primary-600 text-white'
                      : 'text-secondary-600 hover:text-secondary-900'
                  }`}
                  title="Grid view"
                >
                  <Grid className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'list'
                      ? 'bg-primary-600 text-white'
                      : 'text-secondary-600 hover:text-secondary-900'
                  }`}
                  title="List view"
                >
                  <List className="h-4 w-4" />
                </button>
              </div>

              {/* Refresh Button */}
              <button
                onClick={handleRefresh}
                disabled={state.loading}
                className="flex items-center px-3 py-2 bg-white border border-secondary-200 text-secondary-700 rounded-lg hover:bg-secondary-50 focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Refresh data"
              >
                <RefreshCw className={`h-4 w-4 ${state.loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Search Form */}
        {showFilters && (
          <div className="mb-8 animate-slide-down">
            <SearchForm
              onSearch={handleSearch}
              loading={state.loading}
              initialFilters={state.searchFilters}
            />
          </div>
        )}

        {/* Statistics */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div className="text-sm text-secondary-600">
              {state.loading ? (
                <span>Loading properties...</span>
              ) : (
                <span>
                  {state.properties.length} {state.properties.length === 1 ? 'property found' : 'properties found'}
                </span>
              )}
            </div>
            
            {state.apiMode === 'mock' && (
              <div className="flex items-center text-xs text-warning-600 bg-warning-50 px-2 py-1 rounded-md">
                <AlertCircle className="h-3 w-3 mr-1" />
                Demo data
              </div>
            )}
          </div>
        </div>

        {/* Error State */}
        {state.error && (
          <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-error-600 mr-3" />
              <div>
                <h3 className="text-sm font-medium text-error-800">
                  Error loading properties
                </h3>
                <p className="text-sm text-error-600 mt-1">
                  {state.error}
                </p>
              </div>
            </div>
            <div className="mt-3">
              <button
                onClick={handleRefresh}
                className="text-sm font-medium text-error-600 hover:text-error-500"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {state.loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-secondary-600">Loading properties...</p>
            </div>
          </div>
        )}

        {/* Properties Grid/List */}
        {!state.loading && !state.error && (
          <div className="animate-fade-in">
            {state.properties.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-secondary-400 mb-4">
                  <Filter className="h-16 w-16 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-secondary-900 mb-2">
                  No properties found
                </h3>
                <p className="text-secondary-600 mb-4">
                  Try adjusting the search filters or removing some criteria.
                </p>
                <button
                  onClick={() => handleSearch({})}
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  View all properties
                </button>
              </div>
            ) : (
              <div className={
                viewMode === 'grid'
                  ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
                  : 'space-y-4'
              }>
                {state.properties.map((property) => (
                  <PropertyCard
                    key={property.id}
                    property={property}
                    onSelect={handlePropertySelect}
                    onSchedule={handleScheduleAppointment}
                    className={viewMode === 'list' ? 'max-w-none' : ''}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Load More Button (if needed) */}
        {!state.loading && state.properties.length > 0 && (
          <div className="mt-8 text-center">
            <button
              className="inline-flex items-center px-6 py-3 border border-secondary-300 text-secondary-700 rounded-lg hover:bg-secondary-50 focus:ring-2 focus:ring-primary-500 transition-colors"
              onClick={() => {
                // Implement pagination if needed
                console.log('Load more properties');
              }}
            >
              Load more properties
            </button>
          </div>
        )}

        {/* AI Agent Chat */}
        <PropertyAgentChat
          property={state.chatProperty}
          initialMode={state.chatMode === 'general' ? 'details' : state.chatMode}
        />

      </div>
    </div>
  );
} 