import axios, { AxiosInstance } from 'axios';
import {
  ChatMessage,
  AgentResponse,
  AgentSession,
  PropertyChatContext,
  AgentMode,
  AgentConfig,
} from '@/types/agent';
import { Property } from '@/types/property';

// Mock responses in ENGLISH for demo system
const MOCK_RESPONSES = {
  welcome: {
    property_agent: (property: Property) => 
      `Hello! 👋 I'm Emma, your property specialist. I'm here to help you with all the details about this property at ${property.formattedAddress}. 

🏠 **Property Summary:**
• 📍 Location: ${property.formattedAddress}
• 💰 Price: $${property.price?.toLocaleString('en-US')}
• 🛏️ Bedrooms: ${property.bedrooms}
• 🚿 Bathrooms: ${property.bathrooms}
• 📐 Area: ${property.squareFootage} sq ft

How can I help you? I can discuss location, pricing, property features, or schedule a viewing! 😊`,

    scheduling_agent: (property: Property) =>
      `Hi! 👋 I'm Mike, your scheduling specialist. I'll help you arrange a visit to the property at ${property.formattedAddress}.

📅 **Available Time Slots:**
• **Today** - 2:00 PM, 4:30 PM
• **Tomorrow** - 9:00 AM, 11:30 AM, 3:00 PM  
• **Friday** - 10:00 AM, 2:00 PM, 5:00 PM
• **Saturday** - 9:30 AM, 1:00 PM, 4:00 PM

What time works best for you? 🗓️`,

    search_agent: () =>
      `Hello! 👋 I'm Alex, your property search specialist. I can help you find the perfect property based on your needs.

🔍 **How I can help:**
• Search properties by location
• Filter by price and features  
• Compare available options
• Recommend the best properties

What are you looking for? 🏠`
  },

  responses: {
    price: (property: Property) => 
      `💰 **Price Analysis - ${property.formattedAddress}**

**Value:** $${property.price?.toLocaleString('en-US')}/month
**Cost per sq ft:** $${((property.price || 0) / (property.squareFootage || 1)).toFixed(2)}/sq ft

**📊 Market Comparison:**
This property is competitively priced for the area. Similar properties range from $${((property.price || 0) - 200).toLocaleString('en-US')} to $${((property.price || 0) + 300).toLocaleString('en-US')}.

**💡 Value Highlights:**
• ${property.squareFootage} sq ft provides great space for the price
• Built in ${property.yearBuilt}, featuring ${property.yearBuilt > 2000 ? 'modern amenities' : 'classic charm'}
• ${property.bedrooms} bedrooms offer ${property.bedrooms > 1 ? 'flexibility for home office' : 'cozy living space'}

Would you like to schedule a viewing? 📅`,

    location: (property: Property) =>
      `📍 **Premium Location - ${property.formattedAddress}**

**🌆 Neighborhood Highlights:**
• Prime location in ${property.city} with easy downtown access
• Established residential area with tree-lined streets  
• Family-friendly community with low crime rates
• Walkability score 85+ with many conveniences nearby

**🚗 Transportation:**
• Major highways within 5 minutes
• Public transit options available
• Average commute to downtown: 15-20 minutes
• Ample parking available

**🛒 Daily Conveniences:**
• Grocery stores within 1 mile (Whole Foods, Target, local markets)
• Restaurants and cafes within walking distance
• Banks, pharmacies, and essential services nearby
• Shopping centers and entertainment options

**🏃 Recreation:**
• Parks and green spaces for outdoor activities
• Fitness centers and recreational facilities
• Community centers with events and programs

This area offers the perfect balance of convenience and quality of life! 🌟`,

    details: (property: Property) =>
      `🏠 **Complete Details - ${property.formattedAddress}**

**🔍 Features:**
• **Type:** ${property.propertyType}
• **Area:** ${property.squareFootage} sq ft
• **Bedrooms:** ${property.bedrooms}
• **Bathrooms:** ${property.bathrooms}
• **Year Built:** ${property.yearBuilt}
• **Monthly Rent:** $${property.price?.toLocaleString('en-US')}

**✨ Key Features:**
• Spacious layout with ${property.yearBuilt > 2000 ? 'modern' : 'classic'} design
• ${property.yearBuilt > 2010 ? 'Updated kitchen and bathrooms' : 'Charming original details'}
• ${property.yearBuilt > 1990 ? 'Central air conditioning' : 'Window AC units available'}
• ${property.propertyType === 'Apartment' ? 'In-unit laundry' : 'Laundry facilities nearby'}

**🏢 Building/Community:**
• Professional management company
• ${property.propertyType === 'Apartment' ? 'Elevator access' : 'Ground level access'}
• On-site maintenance and support
• ${(property.price || 0) > 2000 ? 'Amenities like pool, gym, clubhouse' : 'Basic amenities included'}

**📋 Important Information:**
• Available for immediate move-in
• Pet policy: Pet-friendly with deposit
• Lease terms: 12-month preferred, 6-month available
• Utilities: ${(property.price || 0) > 2500 ? 'Some included' : 'Tenant responsible'}

What specific aspect would you like to know more about? 🤔`,

    schedule: (property: Property) =>
      `📅 **Schedule Visit - ${property.formattedAddress}**

**Available Time Slots:**
• **Wednesday** - 2:00 PM, 4:30 PM
• **Thursday** - 10:30 AM, 1:00 PM, 5:00 PM  
• **Friday** - 9:00 AM, 3:00 PM, 6:00 PM
• **Saturday** - 11:00 AM, 1:30 PM, 4:00 PM

**⏰ Duration:** Typically 30-45 minutes
**👥 Group Size:** Up to 4 people welcome

**📋 What to Bring:**
• Valid photo ID
• Proof of income (if ready to apply)
• List of questions about the property
• Checkbook (to secure the property if interested)

**🚗 Parking:**
• On-site parking available
• Street parking as backup option
• Public transit accessible

Which time slot works best for you? I can confirm immediately! ✅`,

    general: () =>
      `Hello! How can I help you today? 😊

I can assist with:
• 🔍 Details about this property
• 📍 Location information
• 💰 Price analysis
• 📅 Scheduling visits
• 🏠 Features and amenities

What interests you?`
  }
};

class AgentService {
  private api: AxiosInstance;
  private config: AgentConfig;
  private currentSession: AgentSession | null = null;
  private dataMode: 'mock' | 'real' = 'real';

  constructor() {
    this.config = {
      mode: 'real',
      api_base_url: '/api/agent', // Use relative URL to go through Vite proxy
      enable_streaming: false,
      agent_personality: 'professional',
      language: 'en', // 🇺🇸 English by default
    };

    this.api = axios.create({
      baseURL: this.config.api_base_url,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    console.log('🚀 AgentService initialized with REAL mode by default');
  }

  private setupInterceptors(): void {
    this.api.interceptors.request.use(
      (config) => {
        if (config.params) {
          config.params.mode = this.dataMode;
        } else {
          config.params = { mode: this.dataMode };
        }

        console.log(`🤖 Agent API Request [${this.dataMode.toUpperCase()}]:`, {
          method: config.method?.toUpperCase(),
          url: config.url,
          params: config.params,
        });

        return config;
      },
      (error) => {
        console.error('❌ Agent Request Error:', error);
        return Promise.reject(error);
      }
    );

    this.api.interceptors.response.use(
      (response) => {
        console.log(`✅ Agent API Response [${this.dataMode.toUpperCase()}]:`, {
          status: response.status,
          agent: response.data?.data?.agent_name || response.data?.agent_name,
          session: response.data?.data?.session_id || response.data?.session_id,
        });
        return response;
      },
      (error) => {
        console.error(`❌ Agent API Error [${this.dataMode.toUpperCase()}]:`, {
          status: error.response?.status,
          message: error.response?.data?.message || error.message,
          url: error.config?.url,
        });
        return Promise.reject(error);
      }
    );
  }

  setMode(mode: AgentMode): void {
    this.dataMode = mode === 'mock' ? 'mock' : 'real';
    console.log(`🔄 Agent mode changed to: ${this.dataMode.toUpperCase()}`);
  }

  getMode(): AgentMode {
    return this.dataMode;
  }

  // Generate local mock response (fallback only)
  private generateMockResponse(message: string, property: Property, agentType: string): AgentResponse {
    const lowerMessage = message.toLowerCase();
    
    let responseContent: string;

    // Determine response type based on message
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
      responseContent = MOCK_RESPONSES.welcome[agentType as keyof typeof MOCK_RESPONSES.welcome]?.(property) 
        || MOCK_RESPONSES.responses.general();
    } else if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('rent') || lowerMessage.includes('monthly')) {
      responseContent = MOCK_RESPONSES.responses.price(property);
    } else if (lowerMessage.includes('location') || lowerMessage.includes('neighborhood') || lowerMessage.includes('area') || lowerMessage.includes('nearby')) {
      responseContent = MOCK_RESPONSES.responses.location(property);
    } else if (lowerMessage.includes('schedule') || lowerMessage.includes('visit') || lowerMessage.includes('appointment') || lowerMessage.includes('viewing')) {
      responseContent = MOCK_RESPONSES.responses.schedule(property);
    } else if (lowerMessage.includes('details') || lowerMessage.includes('features') || lowerMessage.includes('about')) {
      responseContent = MOCK_RESPONSES.responses.details(property);
    } else {
      responseContent = MOCK_RESPONSES.responses.general();
    }

    // Map agent names
    const agentNames = {
      'property_agent': 'Emma - Property Expert',
      'scheduling_agent': 'Mike - Scheduling Specialist', 
      'search_agent': 'Alex - Search Specialist'
    };

    return {
      success: true,
      message: responseContent,
      agent_name: agentNames[agentType as keyof typeof agentNames] || 'AI Assistant',
      session_id: this.currentSession?.session_id || `fallback-${Date.now()}`,
      current_agent: agentType,
      data: { property_context: property },
      suggested_actions: ['Schedule Visit', 'View Details', 'Price Analysis'],
      confidence: 0.95,
      timestamp: new Date()
    };
  }

  async startSession(context: PropertyChatContext): Promise<AgentSession> {
    try {
      console.log(`🚀 Starting session in ${this.dataMode.toUpperCase()} mode`);
      console.log('📍 Property context:', {
        id: context.property?.id,
        address: context.property?.formattedAddress,
        mode: context.mode
      });

      // 🌐 ALWAYS use server API (both mock and real modes use backend)
      console.log('🌐 Calling server API for session start');
      const response = await this.api.post(`/session/start`, {
        property_id: context.property?.id,
        agent_mode: context.mode === 'schedule' ? 'schedule' : 'details',
        user_preferences: context.user_preferences,
        language: this.config.language,
      });

      if (response.data.success) {
        this.currentSession = response.data.data.session;
        
        // Store property context for reference
        if (this.currentSession) {
          (this.currentSession as any).property_context = context.property;
        }
        
        console.log('✅ Session created successfully:', {
          session_id: this.currentSession?.session_id,
          property_id: this.currentSession?.property_id,
          current_agent: this.currentSession?.current_agent
        });
        
        return this.currentSession!;
      }
      throw new Error(response.data.message || 'Failed to start session');
    } catch (error: any) {
      console.error('❌ Error starting session:', error);
      throw new Error(`Session start failed: ${error.message}`);
    }
  }

  async sendMessage(message: string, session_id?: string): Promise<AgentResponse> {
    try {
      const sessionId = session_id || this.currentSession?.session_id;
      if (!sessionId) {
        throw new Error('No active session');
      }

      console.log(`💬 Sending message in ${this.dataMode.toUpperCase()} mode: "${message}"`);

      // 🌐 BOTH MODES: Use server API (mock mode will use OpenRouter too)
      console.log('🌐 Sending to server API');
      const response = await this.api.post(`/chat`, {
        message,
        session_id: sessionId,
        property_context: (this.currentSession as any)?.property_context || null,
      });

      if (response.data.success) {
        return response.data.data;
      }
      throw new Error(response.data.message || 'Failed to send message');
    } catch (error) {
      console.error('❌ Error sending message:', error);
      
      // Fallback to mock response only if API completely fails
      if (this.dataMode === 'mock' && this.currentSession) {
        console.log('🔄 API failed, using fallback mock response');
        const property = (this.currentSession as any).property_context || {
          id: this.currentSession.property_id,
          formattedAddress: 'Demo Property',
          price: 2500,
          bedrooms: 2,
          bathrooms: 1,
          squareFootage: 800,
          yearBuilt: 2015,
          propertyType: 'Apartment',
          city: 'Miami',
          state: 'FL'
        };
        
        return this.generateMockResponse(message, property, this.currentSession.current_agent);
      }
      
      throw new Error(`Message send failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async endSession(session_id?: string): Promise<void> {
    try {
      const sessionId = session_id || this.currentSession?.session_id;
      if (!sessionId) return;

      if (this.dataMode === 'mock') {
        // 🧪 MOCK MODE: Only clear local session
        console.log('🧪 [MOCK] Ending local session');
        this.currentSession = null;
      } else {
        // 🌐 REAL MODE: Call server API
        console.log('🌐 [REAL] Ending session via API');
        await this.api.post('/session/end', { session_id: sessionId });
        this.currentSession = null;
      }
    } catch (error) {
      console.error('❌ Error ending session:', error);
      this.currentSession = null;
    }
  }

  async getSessionHistory(session_id: string): Promise<ChatMessage[]> {
    try {
      if (this.dataMode === 'mock') {
        // 🧪 MOCK MODE: Return empty history
        console.log('🧪 [MOCK] Returning empty history');
        return [];
      } else {
        // 🌐 REAL MODE: Use server API
        const response = await this.api.get(`/session/${session_id}/history`);
        if (response.data.success) {
          return response.data.data.messages;
        }
        return [];
      }
    } catch (error) {
      console.error('❌ Error getting session history:', error);
      return [];
    }
  }

  getCurrentSession(): AgentSession | null {
    return this.currentSession;
  }

  updateConfig(newConfig: Partial<AgentConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('🔧 Agent config updated:', this.config);
  }
}

export const agentService = new AgentService(); 