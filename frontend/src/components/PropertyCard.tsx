import { 
  MapPin, 
  Bed, 
  Bath, 
  Square, 
  Calendar, 
  Phone, 
  Mail, 
  Globe,
  Clock,
  DollarSign,
  Eye,
  CalendarPlus
} from 'lucide-react';
import { PropertyCardProps } from '@/types/property';
import { 
  safeFormatPrice, 
  safeFormatDate, 
  safeFormatArea,
  getPropertyTypeLabel,
  getStatusColor,
  getStatusLabel,
  safeGet
} from '@/utils/propertyHelpers';

export default function PropertyCard({ property, onSelect, onSchedule, className = '' }: PropertyCardProps) {
  // Early return if property is invalid
  if (!property) {
    return (
      <div className="bg-white rounded-xl shadow-soft border border-error-200 p-4">
        <p className="text-error-600">Invalid property data</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-soft border border-secondary-200 overflow-hidden hover:shadow-medium transition-all duration-300 group ${className}`}>
      {/* Header with Status and Type */}
      <div className="p-4 border-b border-secondary-100">
        <div className="flex items-center justify-between mb-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(property.status)}`}>
            {getStatusLabel(property.status)}
          </span>
          <span className="text-xs text-secondary-500 font-medium">
            {getPropertyTypeLabel(property.propertyType)}
          </span>
        </div>
        
        {/* Address */}
        <div className="flex items-start">
          <MapPin className="h-4 w-4 text-secondary-400 mt-0.5 mr-2 flex-shrink-0" />
          <div>
            <p className="font-semibold text-secondary-900 text-sm">
              {safeGet(property, 'formattedAddress', 'Address not available')}
            </p>
            <p className="text-xs text-secondary-600">
              {safeGet(property, 'county', 'Unknown')}, {safeGet(property, 'state', 'Unknown')} - {safeGet(property, 'zipCode', 'Unknown')}
            </p>
          </div>
        </div>
      </div>

      {/* Main Information */}
      <div className="p-4">
        {/* Price */}
        <div className="mb-4">
          <div className="flex items-center">
            <DollarSign className="h-5 w-5 text-primary-600 mr-1" />
            <span className="text-2xl font-bold text-primary-600">
              {safeFormatPrice(property.price)}
            </span>
            <span className="text-sm text-secondary-500 ml-1">/month</span>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="flex items-center text-secondary-600">
            <Bed className="h-4 w-4 mr-1" />
            <span className="text-sm font-medium">{safeGet(property, 'bedrooms', 0)}</span>
          </div>
          <div className="flex items-center text-secondary-600">
            <Bath className="h-4 w-4 mr-1" />
            <span className="text-sm font-medium">{safeGet(property, 'bathrooms', 0)}</span>
          </div>
          <div className="flex items-center text-secondary-600">
            <Square className="h-4 w-4 mr-1" />
            <span className="text-sm font-medium">{safeFormatArea(property.squareFootage)}</span>
          </div>
        </div>

        {/* Additional Information */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-xs text-secondary-500">
            <Calendar className="h-3 w-3 mr-1" />
            <span>Built in {safeGet(property, 'yearBuilt', 'Unknown')}</span>
          </div>
          <div className="flex items-center text-xs text-secondary-500">
            <Clock className="h-3 w-3 mr-1" />
            <span>{safeGet(property, 'daysOnMarket', 0)} days on market</span>
          </div>
          <div className="flex items-center text-xs text-secondary-500">
            <span className="font-medium">MLS:</span>
            <span className="ml-1">{safeGet(property, 'mlsNumber', 'N/A')}</span>
          </div>
        </div>

        {/* Agent */}
        <div className="border-t border-secondary-100 pt-3 mb-4">
          <p className="text-xs font-medium text-secondary-700 mb-1">Listing Agent</p>
          <div className="space-y-1">
            <p className="text-sm font-semibold text-secondary-900">{safeGet(property, 'listingAgent.name', 'Unknown Agent')}</p>
            <div className="flex items-center space-x-3 text-xs text-secondary-600">
              <div className="flex items-center">
                <Phone className="h-3 w-3 mr-1" />
                <span>{safeGet(property, 'listingAgent.phone', 'N/A')}</span>
              </div>
              <div className="flex items-center">
                <Mail className="h-3 w-3 mr-1" />
                <span>{safeGet(property, 'listingAgent.email', 'N/A')}</span>
              </div>
            </div>
            {safeGet(property, 'listingAgent.website') && (
              <div className="flex items-center text-xs text-primary-600">
                <Globe className="h-3 w-3 mr-1" />
                <a 
                  href={`https://${safeGet(property, 'listingAgent.website', '')}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:underline"
                >
                  {safeGet(property, 'listingAgent.website', '')}
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Office */}
        <div className="border-t border-secondary-100 pt-3 mb-4">
          <p className="text-xs font-medium text-secondary-700 mb-1">Listing Office</p>
          <div className="space-y-1">
            <p className="text-sm font-semibold text-secondary-900">{safeGet(property, 'listingOffice.name', 'Unknown Office')}</p>
            <div className="flex items-center space-x-3 text-xs text-secondary-600">
              <div className="flex items-center">
                <Phone className="h-3 w-3 mr-1" />
                <span>{safeGet(property, 'listingOffice.phone', 'N/A')}</span>
              </div>
              <div className="flex items-center">
                <Mail className="h-3 w-3 mr-1" />
                <span>{safeGet(property, 'listingOffice.email', 'N/A')}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Important Dates */}
        <div className="border-t border-secondary-100 pt-3 mb-4">
          <div className="grid grid-cols-2 gap-2 text-xs text-secondary-600">
            <div>
              <span className="font-medium">Listed on:</span>
              <br />
              <span>{safeFormatDate(property.listedDate)}</span>
            </div>
            <div>
              <span className="font-medium">Last seen:</span>
              <br />
              <span>{safeFormatDate(property.lastSeenDate)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-4 border-t border-secondary-100 bg-secondary-50">
        <div className="flex space-x-2">
          {onSelect && (
            <button
              onClick={() => {
                console.log('🔵 PropertyCard: View Details button clicked!');
                console.log('📦 Property data:', property);
                console.log('🎯 Calling onSelect with property:', property.formattedAddress);
                onSelect(property);
              }}
              className="flex-1 flex items-center justify-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
            >
              <Eye className="h-4 w-4 mr-2" />
              View Details
            </button>
          )}
          
          {onSchedule && (
            <button
              onClick={() => {
                console.log('📅 PropertyCard: Schedule Visit button clicked!');
                console.log('📦 Property data:', property);
                console.log('🎯 Calling onSchedule with property:', property.formattedAddress);
                onSchedule(property);
              }}
              className="flex-1 flex items-center justify-center px-4 py-2 border border-primary-600 text-primary-600 text-sm font-medium rounded-lg hover:bg-primary-50 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
            >
              <CalendarPlus className="h-4 w-4 mr-2" />
              Schedule Visit
            </button>
          )}
        </div>
      </div>
    </div>
  );
} 