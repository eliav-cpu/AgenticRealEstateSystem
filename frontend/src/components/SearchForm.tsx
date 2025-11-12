import { useState, useEffect } from 'react';
import { Search, Filter, MapPin, Home, DollarSign, Bed, Bath, Square } from 'lucide-react';
import { SearchFilters, SearchFormProps } from '@/types/property';

const PROPERTY_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'Apartment', label: 'Apartment' },
  { value: 'House', label: 'House' },
  { value: 'Condo', label: 'Condo' },
  { value: 'Townhouse', label: 'Townhouse' },
];

const BEDROOM_OPTIONS = [
  { value: '', label: 'Any' },
  { value: '1', label: '1+ bedroom' },
  { value: '2', label: '2+ bedrooms' },
  { value: '3', label: '3+ bedrooms' },
  { value: '4', label: '4+ bedrooms' },
];

const BATHROOM_OPTIONS = [
  { value: '', label: 'Any' },
  { value: '1', label: '1+ bathroom' },
  { value: '2', label: '2+ bathrooms' },
  { value: '3', label: '3+ bathrooms' },
];

export default function SearchForm({ onSearch, loading, initialFilters }: SearchFormProps) {
  const [filters, setFilters] = useState<SearchFilters>(initialFilters || {});
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    if (initialFilters) {
      setFilters(initialFilters);
    }
  }, [initialFilters]);

  const handleInputChange = (field: keyof SearchFilters, value: string | number) => {
    setFilters(prev => ({
      ...prev,
      [field]: value === '' ? undefined : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log(`🔍 [SEARCH FORM] Form submitted with filters:`, filters);
    console.log(`🔍 [SEARCH FORM] Calling onSearch callback`);
    onSearch(filters);
  };

  const clearFilters = () => {
    setFilters({});
    onSearch({});
  };

  const hasActiveFilters = Object.values(filters).some(value => value !== undefined && value !== '');

  return (
    <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Main Search */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MapPin className="h-5 w-5 text-secondary-400" />
          </div>
          <input
            type="text"
            placeholder="Enter city, neighborhood or address..."
            value={filters.city || ''}
            onChange={(e) => handleInputChange('city', e.target.value)}
            className="block w-full pl-10 pr-3 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-secondary-900 placeholder-secondary-500 transition-colors"
          />
        </div>

        {/* Basic Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Property Type */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              <Home className="inline h-4 w-4 mr-1" />
              Property Type
            </label>
            <select
              value={filters.propertyType || ''}
              onChange={(e) => handleInputChange('propertyType', e.target.value)}
              className="block w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-secondary-900"
            >
              {PROPERTY_TYPES.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Bedrooms */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              <Bed className="inline h-4 w-4 mr-1" />
              Bedrooms
            </label>
            <select
              value={filters.minBedrooms || ''}
              onChange={(e) => handleInputChange('minBedrooms', e.target.value ? parseInt(e.target.value) : '')}
              className="block w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-secondary-900"
            >
              {BEDROOM_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Bathrooms */}
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              <Bath className="inline h-4 w-4 mr-1" />
              Bathrooms
            </label>
            <select
              value={filters.minBathrooms || ''}
              onChange={(e) => handleInputChange('minBathrooms', e.target.value ? parseInt(e.target.value) : '')}
              className="block w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-secondary-900"
            >
              {BATHROOM_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Price Range */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            <DollarSign className="inline h-4 w-4 mr-1" />
            Price Range
          </label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <input
                type="number"
                placeholder="Minimum price"
                value={filters.minPrice || ''}
                onChange={(e) => handleInputChange('minPrice', e.target.value ? parseInt(e.target.value) : '')}
                className="block w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-secondary-900 placeholder-secondary-500"
              />
            </div>
            <div>
              <input
                type="number"
                placeholder="Maximum price"
                value={filters.maxPrice || ''}
                onChange={(e) => handleInputChange('maxPrice', e.target.value ? parseInt(e.target.value) : '')}
                className="block w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-secondary-900 placeholder-secondary-500"
              />
            </div>
          </div>
        </div>

        {/* Advanced Filters */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-primary-600 hover:text-primary-700 font-medium transition-colors"
          >
            <Filter className="h-4 w-4 mr-2" />
            {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
          </button>

          {showAdvanced && (
            <div className="mt-4 space-y-4 p-4 bg-secondary-50 rounded-lg">
              {/* Area */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  <Square className="inline h-4 w-4 mr-1" />
                  Area (sq ft)
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <input
                    type="number"
                    placeholder="Minimum area"
                    value={filters.minSquareFootage || ''}
                    onChange={(e) => handleInputChange('minSquareFootage', e.target.value ? parseInt(e.target.value) : '')}
                    className="block w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-secondary-900 placeholder-secondary-500"
                  />
                  <input
                    type="number"
                    placeholder="Maximum area"
                    value={filters.maxSquareFootage || ''}
                    onChange={(e) => handleInputChange('maxSquareFootage', e.target.value ? parseInt(e.target.value) : '')}
                    className="block w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-secondary-900 placeholder-secondary-500"
                  />
                </div>
              </div>

              {/* State */}
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  State
                </label>
                <input
                  type="text"
                  placeholder="Ex: FL, CA, NY..."
                  value={filters.state || ''}
                  onChange={(e) => handleInputChange('state', e.target.value)}
                  className="block w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-secondary-900 placeholder-secondary-500"
                />
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 flex items-center justify-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Searching...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Search Properties
              </>
            )}
          </button>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={clearFilters}
              className="px-6 py-3 border border-secondary-300 text-secondary-700 font-medium rounded-lg hover:bg-secondary-50 focus:ring-2 focus:ring-secondary-500 focus:ring-offset-2 transition-colors"
            >
              Clear Filters
            </button>
          )}
        </div>

        {/* Active Filters Indicator */}
        {hasActiveFilters && (
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-secondary-600">Active filters:</span>
            {Object.entries(filters).map(([key, value]) => {
              if (value === undefined || value === '') return null;
              return (
                <span
                  key={key}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                >
                  {key}: {value}
                </span>
              );
            })}
          </div>
        )}
      </form>
    </div>
  );
} 