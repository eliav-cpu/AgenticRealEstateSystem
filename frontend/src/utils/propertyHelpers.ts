import { Property } from '../types/property';

// Safe property validation function
export const isValidProperty = (property: any): property is Property => {
  return property && 
         typeof property === 'object' &&
         property.id &&
         property.formattedAddress &&
         property.propertyType;
};

// Safe property getter with fallback
export const safeGet = (obj: any, path: string, fallback: any = 'N/A'): any => {
  try {
    const keys = path.split('.');
    let result = obj;
    for (const key of keys) {
      if (result && typeof result === 'object' && key in result) {
        result = result[key];
      } else {
        return fallback;
      }
    }
    return result !== null && result !== undefined ? result : fallback;
  } catch {
    return fallback;
  }
};

// Safe price formatting
export const safeFormatPrice = (price: any): string => {
  try {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    if (isNaN(numPrice) || numPrice <= 0) {
      return 'Price on request';
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(numPrice);
  } catch {
    return 'Price on request';
  }
};

// Safe date formatting
export const safeFormatDate = (date: any): string => {
  try {
    if (!date) return 'Date not available';
    const dateObj = new Date(date);
    if (isNaN(dateObj.getTime())) {
      return 'Date not available';
    }
    return dateObj.toLocaleDateString('en-US');
  } catch {
    return 'Date not available';
  }
};

// Safe area formatting
export const safeFormatArea = (area: any): string => {
  try {
    const numArea = typeof area === 'string' ? parseFloat(area) : area;
    if (isNaN(numArea) || numArea <= 0) {
      return 'Area not specified';
    }
    return `${numArea.toLocaleString('en-US')} sq ft`;
  } catch {
    return 'Area not specified';
  }
};

// Get property type label
export const getPropertyTypeLabel = (type: any): string => {
  if (!type) return 'Unknown';
  
  const typeMap: Record<string, string> = {
    'Apartment': 'Apartment',
    'House': 'House', 
    'Condo': 'Condo',
    'Townhouse': 'Townhouse',
    'SingleFamily': 'Single Family',
    'MultiFamily': 'Multi Family'
  };
  
  return typeMap[type] || type;
};

// Get status color classes
export const getStatusColor = (status: any): string => {
  if (!status) return 'bg-secondary-100 text-secondary-800';
  
  const statusColors: Record<string, string> = {
    'ForRent': 'bg-success-100 text-success-800',
    'ForSale': 'bg-primary-100 text-primary-800',
    'Rented': 'bg-warning-100 text-warning-800',
    'Sold': 'bg-error-100 text-error-800',
    'OffMarket': 'bg-secondary-100 text-secondary-800'
  };
  
  return statusColors[status] || 'bg-secondary-100 text-secondary-800';
};

// Get status label
export const getStatusLabel = (status: any): string => {
  if (!status) return 'Unknown';
  
  const statusLabels: Record<string, string> = {
    'ForRent': 'For Rent',
    'ForSale': 'For Sale', 
    'Rented': 'Rented',
    'Sold': 'Sold',
    'OffMarket': 'Off Market'
  };
  
  return statusLabels[status] || status;
};

// Validate and filter properties array
export const validateProperties = (properties: any[]): Property[] => {
  console.log(`🔍 [VALIDATION] Starting validation of properties:`, {
    type: typeof properties,
    isArray: Array.isArray(properties),
    length: Array.isArray(properties) ? properties.length : 'N/A',
    firstItem: Array.isArray(properties) && properties.length > 0 ? properties[0] : 'No items'
  });

  if (!Array.isArray(properties)) {
    console.warn('⚠️ [VALIDATION] Properties is not an array:', properties);
    return [];
  }
  
  const validProperties = properties.filter((prop, index) => {
    const isValid = isValidProperty(prop);
    if (!isValid) {
      console.warn(`❌ [VALIDATION] Property ${index} failed validation:`, {
        id: prop?.id,
        address: prop?.address,
        propertyType: prop?.propertyType,
        fullProperty: prop
      });
    }
    return isValid;
  });
  
  const invalidCount = properties.length - validProperties.length;
  
  console.log(`✅ [VALIDATION] Validation complete:`, {
    total: properties.length,
    valid: validProperties.length,
    invalid: invalidCount
  });
  
  if (invalidCount > 0) {
    console.warn(`⚠️ [VALIDATION] Filtered out ${invalidCount} invalid properties`);
  }
  
  return validProperties;
}; 