import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  Property,
  SearchFilters,
  ApiResponse,
  ApiMode,
} from '@/types/property';
import {
  AppointmentRequest,
  Appointment,
  TimeSlot,
} from '@/types/appointment';

class ApiService {
  private api: AxiosInstance;
  private mode: ApiMode = 'mock';

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para requests
    this.api.interceptors.request.use(
      (config) => {
        // Adicionar modo na query string
        if (config.params) {
          config.params.mode = this.mode;
        } else {
          config.params = { mode: this.mode };
        }
        
        console.log(`🚀 API Request [${this.mode.toUpperCase()}]:`, {
          method: config.method?.toUpperCase(),
          url: config.url,
          params: config.params,
        });
        
        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Interceptor para responses
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`✅ API Response [${this.mode.toUpperCase()}]:`, {
          status: response.status,
          data: response.data,
          dataLength: Array.isArray(response.data?.data) ? response.data.data.length : 'Not array',
        });
        return response;
      },
      (error) => {
        console.error(`❌ API Error [${this.mode.toUpperCase()}]:`, {
          status: error.response?.status,
          message: error.response?.data?.message || error.message,
          url: error.config?.url,
        });
        return Promise.reject(error);
      }
    );
  }

  // Configurar modo da API
  setMode(mode: ApiMode): void {
    this.mode = mode;
    console.log(`🔄 API Mode changed to: ${mode.toUpperCase()}`);
  }

  getMode(): ApiMode {
    return this.mode;
  }

  // Buscar propriedades
  async searchProperties(filters: SearchFilters = {}): Promise<Property[]> {
    try {
      console.log(`🔍 [API SERVICE] Starting search with filters:`, filters);
      
      const response = await this.api.get<ApiResponse<Property[]>>('/properties/search', {
        params: filters,
      });

      console.log(`📋 [API SERVICE] Raw response:`, {
        success: response.data.success,
        dataType: typeof response.data.data,
        dataLength: Array.isArray(response.data.data) ? response.data.data.length : 'Not array',
        firstProperty: Array.isArray(response.data.data) && response.data.data.length > 0 ? response.data.data[0] : 'No properties'
      });

      if (!response.data.success) {
        console.error(`❌ [API SERVICE] API returned error:`, response.data.error);
        throw new Error(response.data.error || 'Error searching properties');
      }

      const properties = response.data.data;
      console.log(`✅ [API SERVICE] Returning ${properties.length} properties to component`);
      
      return properties;
    } catch (error) {
      console.error('❌ [API SERVICE] Error searching properties:', error);
      throw error;
    }
  }

  // Obter propriedade por ID
  async getPropertyById(id: string): Promise<Property> {
    try {
      const response = await this.api.get<ApiResponse<Property>>(`/properties/${id}`);

      if (!response.data.success) {
        throw new Error(response.data.error || 'Propriedade não encontrada');
      }

      return response.data.data;
    } catch (error) {
      console.error('Erro ao buscar propriedade:', error);
      throw error;
    }
  }

  // Agendar visita
  async scheduleAppointment(appointment: AppointmentRequest): Promise<Appointment> {
    try {
      const response = await this.api.post<ApiResponse<Appointment>>('/appointments', appointment);

      if (!response.data.success) {
        throw new Error(response.data.error || 'Erro ao agendar visita');
      }

      return response.data.data;
    } catch (error) {
      console.error('Erro ao agendar visita:', error);
      throw error;
    }
  }

  // Obter horários disponíveis
  async getAvailableTimeSlots(propertyId: string, date: string): Promise<TimeSlot[]> {
    try {
      const response = await this.api.get<ApiResponse<TimeSlot[]>>('/appointments/available-slots', {
        params: { propertyId, date },
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'Erro ao buscar horários');
      }

      return response.data.data;
    } catch (error) {
      console.error('Erro ao buscar horários:', error);
      throw error;
    }
  }

  // Obter agendamentos do usuário
  async getUserAppointments(email: string): Promise<Appointment[]> {
    try {
      const response = await this.api.get<ApiResponse<Appointment[]>>('/appointments/user', {
        params: { email },
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'Erro ao buscar agendamentos');
      }

      return response.data.data;
    } catch (error) {
      console.error('Erro ao buscar agendamentos:', error);
      throw error;
    }
  }

  // Cancelar agendamento
  async cancelAppointment(appointmentId: string): Promise<void> {
    try {
      const response = await this.api.delete<ApiResponse<void>>(`/appointments/${appointmentId}`);

      if (!response.data.success) {
        throw new Error(response.data.error || 'Erro ao cancelar agendamento');
      }
    } catch (error) {
      console.error('Erro ao cancelar agendamento:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; mode: ApiMode; timestamp: string }> {
    try {
      const response = await this.api.get<ApiResponse<{ status: string; mode: ApiMode; timestamp: string }>>('/health');
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Health check failed');
      }

      return response.data.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}

// Instância singleton
export const apiService = new ApiService();

// Exports nomeados para facilitar testes
export { ApiService };
export default apiService; 