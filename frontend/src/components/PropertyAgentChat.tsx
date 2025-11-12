import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Home, Loader2, Bot, X } from 'lucide-react';
import { agentService } from '@/services/agentService';
import { useApp } from '@/context/AppContext';
import {
  ChatMessage,
  AgentResponse,
  AgentSession,
  PropertyChatContext,
} from '@/types/agent';

interface PropertyAgentChatProps {
  property?: any;
  initialMode?: 'details' | 'schedule';
}

const PropertyAgentChat: React.FC<PropertyAgentChatProps> = ({
  property: propProperty,
  initialMode = 'details',
}) => {
  const { state, appMode, openChat, closeChat } = useApp();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [session, setSession] = useState<AgentSession | null>(null);
  const [lastPropertyId, setLastPropertyId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use global state for chat control
  const isOpen = state.chatOpen;
  const property = state.chatProperty || propProperty;
  const mode = state.chatMode || initialMode;

  console.log('🔍 PropertyAgentChat render:', { isOpen, hasProperty: !!property, mode });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Detectar mudança de propriedade e resetar chat
  useEffect(() => {
    const currentPropertyId = property?.id?.toString() || property?.formattedAddress || null;
    
    if (isOpen && currentPropertyId && currentPropertyId !== lastPropertyId) {
      console.log('🔄 Property changed! Resetting chat...');
      console.log('   Previous property:', lastPropertyId);
      console.log('   New property:', currentPropertyId);
      
      // Limpar estado anterior
      setMessages([]);
      setSession(null);
      setIsLoading(false);
      setInputValue('');
      
      // Encerrar sessão anterior se existir
      if (session?.session_id) {
        agentService.endSession(session.session_id).catch(err => {
          console.warn('⚠️ Failed to end previous session:', err);
        });
      }
      
      // Atualizar propriedade atual
      setLastPropertyId(currentPropertyId);
      
      // 🔥 SINCRONIZAR agentService com AppContext
      console.log(`🔄 Synchronizing agentService mode with AppContext: ${appMode}`);
      agentService.setMode(appMode);
      
      // Inicializar nova sessão
      initializeChat();
    } else if (isOpen && !session && !isLoading) {
      console.log('🔄 Chat opened without property change, initializing...');
      
      // 🔥 SINCRONIZAR agentService com AppContext
      console.log(`🔄 Synchronizing agentService mode with AppContext: ${appMode}`);
      agentService.setMode(appMode);
      
      initializeChat();
    }
  }, [isOpen, property, appMode]);

  const initializeChat = async () => {
    try {
      console.log(`🚀 Initializing chat in ${appMode} mode`);
      console.log('📍 Property:', property?.formattedAddress || 'No property');
      console.log('🎯 Mode:', mode);
      
      agentService.setMode(appMode);
      setIsLoading(true);
      
      // Create context for both mock and real modes
      const context = {
        property: property,
        mode: mode,
        user_preferences: {
          language: 'en' as const,
          communication_style: 'professional' as const,
        },
      } satisfies PropertyChatContext;

      console.log('🔧 Creating session with context:', context);
      
      // Start session (handles both mock and real modes)
      const newSession = await agentService.startSession(context);
      setSession(newSession);
      
      console.log('✅ Session created:', newSession);
      
      // Get session history (empty for mock, might have data for real)
      if (newSession.session_id) {
        const history = await agentService.getSessionHistory(newSession.session_id);
        if (history.length > 0) {
          setMessages(history);
          console.log(`📋 Loaded ${history.length} messages from history`);
        } else {
          // Se não há histórico, criar mensagem de boas-vindas
          console.log('📝 No history found, creating welcome message');
          const welcomeMessage: ChatMessage = {
            id: `welcome-${Date.now()}`,
            content: `👋 Hello! Welcome to Real Estate Assistant\n\n🏠 I'm here to help you with information about this property${property ? ` at ${property.formattedAddress}` : ''}.\n\nHow can I assist you today?`,
            sender: 'agent',
            timestamp: new Date(),
            agent_name: mode === 'schedule' ? 'Mike - Scheduling Specialist' : 'Emma - Property Expert',
          };
          setMessages([welcomeMessage]);
        }
      }
      
    } catch (error) {
      console.error('❌ Error initializing chat:', error);
      
      // Fallback: create basic welcome message
      const fallbackMessage: ChatMessage = {
        id: `fallback-${Date.now()}`,
        content: `👋 Hello! Welcome to Real Estate Assistant\n\nI'm here to help you with property information. How can I assist you today?`,
        sender: 'agent',
        timestamp: new Date(),
        agent_name: 'AI Assistant',
      };
      setMessages([fallbackMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response: AgentResponse = await agentService.sendMessage(
        inputValue,
        session?.session_id
      );

      const agentMessage: ChatMessage = {
        id: `agent-${Date.now()}`,
        content: response.message,
        sender: 'agent',
        timestamp: new Date(),
        agent_name: response.agent_name,
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      console.error('❌ Error sending message:', error);
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        content: `I apologize, but I encountered an error. Please try again.`,
        sender: 'agent',
        timestamp: new Date(),
        agent_name: 'System',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Show floating button if chat is not open
  if (!isOpen) {
    return (
      <button
        onClick={() => {
          console.log('🎯 Floating button clicked, opening chat');
          if (property) {
            openChat(property, initialMode);
          } else {
            // Create minimal mock property
            const mockProperty: any = {
              id: 'general-chat',
              formattedAddress: 'General Real Estate Inquiry'
            };
            openChat(mockProperty, 'details');
          }
        }}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all duration-200 z-50"
        title="Open Real Estate Assistant"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    );
  }

  // Show chat interface if open
  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50">
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Home className="w-4 h-4" />
            <div>
              <h3 className="font-semibold text-sm">Real Estate Assistant</h3>
              <p className="text-blue-100 text-xs">
                {appMode === 'real' ? '🌐 Live Agent' : '🧪 Demo Mode'} • {session?.status || 'Connecting...'}
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              console.log('❌ Close button clicked');
              // Encerrar sessão ao fechar
              if (session?.session_id) {
                agentService.endSession(session.session_id).catch(err => {
                  console.warn('⚠️ Failed to end session on close:', err);
                });
              }
              closeChat();
            }}
            className="text-blue-100 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white ml-4'
                  : 'bg-gray-100 text-gray-800 mr-4'
              }`}
            >
              {message.sender === 'agent' && (
                <div className="flex items-center space-x-2 mb-2 text-xs text-gray-600">
                  <Bot className="w-3 h-3" />
                  <span className="font-medium">{message.agent_name || 'AI Assistant'}</span>
                </div>
              )}
              
              <div className="text-sm whitespace-pre-wrap">
                {message.content}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 p-3 rounded-lg mr-4">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Agent is typing...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about property details, schedule a visit..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white p-2 rounded-lg transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        
        <div className="mt-2 text-xs text-gray-500 text-center">
          {appMode === 'real' ? '🌐 Live agent powered by AI' : '🧪 Demo responses - No real API calls'}
        </div>
      </div>
    </div>
  );
};

export default PropertyAgentChat; 