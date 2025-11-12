export interface ChatMessage {
  id: string;
  role?: 'user' | 'assistant' | 'system';
  sender?: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  property_id?: string;
  agent_name?: string;
  confidence?: number;
  suggested_actions?: string[];
}

export interface AgentSession {
  session_id: string;
  user_id?: string;
  property_id?: string;
  current_agent: 'search_agent' | 'property_agent' | 'scheduling_agent';
  status: 'active' | 'completed' | 'error';
  created_at: Date;
  updated_at: Date;
}

export interface AgentResponse {
  success: boolean;
  message: string;
  agent_name: string;
  session_id: string;
  current_agent: string;
  data?: any;
  suggested_actions?: string[];
  confidence?: number;
  timestamp: Date;
}

export interface AgentStreamChunk {
  chunk_id: string;
  session_id: string;
  agent: string;
  content: string;
  is_final: boolean;
  timestamp: Date;
}

export interface PropertyChatContext {
  property: any; // Property type from property.ts
  mode: 'details' | 'schedule' | 'general';
  user_preferences?: {
    name?: string;
    email?: string;
    phone?: string;
    budget?: number;
    preferences?: string[];
    language?: 'en' | 'pt' | 'es';
    communication_style?: 'professional' | 'friendly' | 'expert';
  };
}

export type AgentMode = 'mock' | 'real' | 'api';

export interface AgentCapabilities {
  can_search_properties: boolean;
  can_analyze_properties: boolean;
  can_schedule_visits: boolean;
  can_answer_questions: boolean;
  can_compare_properties: boolean;
  can_provide_market_insights: boolean;
}

export interface AgentConfig {
  mode: AgentMode;
  api_base_url: string;
  websocket_url?: string;
  enable_streaming: boolean;
  agent_personality: 'professional' | 'friendly' | 'expert';
  language: 'en' | 'pt' | 'es';
} 