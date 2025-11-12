import { createContext, useContext, useReducer, ReactNode } from 'react';
import { Property, ApiMode } from '@/types/property';
import { Appointment } from '@/types/appointment';
import { AgentSession } from '@/types/agent';

// Estado da aplicação
interface AppState {
  // API Mode
  apiMode: ApiMode;
  
  // Properties
  properties: Property[];
  selectedProperty: Property | null;
  loading: boolean;
  error: string | null;
  
  // Search
  searchFilters: Record<string, any>;
  searchHistory: string[];
  
  // Appointments
  appointments: Appointment[];
  
  // UI State
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  
  // User State
  user: {
    name: string;
    email: string;
    phone: string;
  } | null;
  
  // Chat State
  chatOpen: boolean;
  chatMode: 'details' | 'schedule' | 'general';
  chatProperty: Property | null;
  agentSession: AgentSession | null;
}

// Ações
type AppAction =
  | { type: 'SET_API_MODE'; payload: ApiMode }
  | { type: 'SET_PROPERTIES'; payload: Property[] }
  | { type: 'SET_SELECTED_PROPERTY'; payload: Property | null }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_SEARCH_FILTERS'; payload: Record<string, any> }
  | { type: 'ADD_SEARCH_HISTORY'; payload: string }
  | { type: 'SET_APPOINTMENTS'; payload: Appointment[] }
  | { type: 'ADD_APPOINTMENT'; payload: Appointment }
  | { type: 'REMOVE_APPOINTMENT'; payload: string }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_THEME'; payload: 'light' | 'dark' }
  | { type: 'SET_USER'; payload: AppState['user'] }
  | { type: 'OPEN_CHAT'; payload: { property: Property; mode: 'details' | 'schedule' | 'general' } }
  | { type: 'CLOSE_CHAT' }
  | { type: 'SET_AGENT_SESSION'; payload: AgentSession | null }
  | { type: 'RESET_STATE' };

// Estado inicial
const initialState: AppState = {
  apiMode: 'real',
  properties: [],
  selectedProperty: null,
  loading: false,
  error: null,
  searchFilters: {},
  searchHistory: [],
  appointments: [],
  sidebarOpen: true,
  theme: 'light',
  user: null,
  chatOpen: false,
  chatMode: 'details',
  chatProperty: null,
  agentSession: null,
};

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_API_MODE':
      return { ...state, apiMode: action.payload };
      
    case 'SET_PROPERTIES':
      console.log(`📋 [REDUCER] SET_PROPERTIES action with ${action.payload.length} properties`);
      return { ...state, properties: action.payload, loading: false, error: null };
      
    case 'SET_SELECTED_PROPERTY':
      return { ...state, selectedProperty: action.payload };
      
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
      
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
      
    case 'SET_SEARCH_FILTERS':
      return { ...state, searchFilters: action.payload };
      
    case 'ADD_SEARCH_HISTORY':
      const newHistory = [action.payload, ...state.searchHistory.filter(item => item !== action.payload)].slice(0, 10);
      return { ...state, searchHistory: newHistory };
      
    case 'SET_APPOINTMENTS':
      return { ...state, appointments: action.payload };
      
    case 'ADD_APPOINTMENT':
      return { ...state, appointments: [...state.appointments, action.payload] };
      
    case 'REMOVE_APPOINTMENT':
      return { 
        ...state, 
        appointments: state.appointments.filter(apt => apt.id !== action.payload) 
      };
      
    case 'TOGGLE_SIDEBAR':
      return { ...state, sidebarOpen: !state.sidebarOpen };
      
    case 'SET_THEME':
      return { ...state, theme: action.payload };
      
    case 'SET_USER':
      return { ...state, user: action.payload };
      
    case 'OPEN_CHAT':
      console.log('📡 REDUCER: OPEN_CHAT action received', action.payload);
      return { 
        ...state, 
        chatOpen: true, 
        chatProperty: action.payload.property,
        chatMode: action.payload.mode 
      };
      
    case 'CLOSE_CHAT':
      return { 
        ...state, 
        chatOpen: false, 
        chatProperty: null,
        agentSession: null 
      };
      
    case 'SET_AGENT_SESSION':
      return { ...state, agentSession: action.payload };
      
    case 'RESET_STATE':
      return { 
        ...initialState, 
        apiMode: state.apiMode, 
        theme: state.theme,
        chatOpen: false,
        chatMode: 'details',
        chatProperty: null,
        agentSession: null,
      };
      
    default:
      return state;
  }
}

// Context
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  appMode: ApiMode; // Alias for state.apiMode
  
  // Helper functions
  setApiMode: (mode: ApiMode) => void;
  setProperties: (properties: Property[]) => void;
  setSelectedProperty: (property: Property | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSearchFilters: (filters: Record<string, any>) => void;
  addSearchHistory: (query: string) => void;
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setUser: (user: AppState['user']) => void;
  openChat: (property: Property, mode: 'details' | 'schedule' | 'general') => void;
  closeChat: () => void;
  setAgentSession: (session: AgentSession | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider
interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Helper functions
  const setApiMode = (mode: ApiMode) => {
    dispatch({ type: 'SET_API_MODE', payload: mode });
  };

  const setProperties = (properties: Property[]) => {
    console.log(`🏪 [CONTEXT] Setting ${properties.length} properties in global state`);
    dispatch({ type: 'SET_PROPERTIES', payload: properties });
  };

  const setSelectedProperty = (property: Property | null) => {
    dispatch({ type: 'SET_SELECTED_PROPERTY', payload: property });
  };

  const setLoading = (loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const setSearchFilters = (filters: Record<string, any>) => {
    dispatch({ type: 'SET_SEARCH_FILTERS', payload: filters });
  };

  const addSearchHistory = (query: string) => {
    if (query.trim()) {
      dispatch({ type: 'ADD_SEARCH_HISTORY', payload: query.trim() });
    }
  };

  const toggleSidebar = () => {
    dispatch({ type: 'TOGGLE_SIDEBAR' });
  };

  const setTheme = (theme: 'light' | 'dark') => {
    dispatch({ type: 'SET_THEME', payload: theme });
  };

  const setUser = (user: AppState['user']) => {
    dispatch({ type: 'SET_USER', payload: user });
  };

  const openChat = (property: Property, mode: 'details' | 'schedule' | 'general') => {
    console.log('🔥 openChat called with:', { property: property.formattedAddress, mode });
    dispatch({ type: 'OPEN_CHAT', payload: { property, mode } });
    console.log('📡 OPEN_CHAT action dispatched');
  };

  const closeChat = () => {
    console.log('❌ closeChat called');
    dispatch({ type: 'CLOSE_CHAT' });
  };

  const setAgentSession = (session: AgentSession | null) => {
    dispatch({ type: 'SET_AGENT_SESSION', payload: session });
  };

  const value: AppContextType = {
    state,
    dispatch,
    appMode: state.apiMode,
    setApiMode,
    setProperties,
    setSelectedProperty,
    setLoading,
    setError,
    setSearchFilters,
    addSearchHistory,
    toggleSidebar,
    setTheme,
    setUser,
    openChat,
    closeChat,
    setAgentSession,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// Hook
export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

export default AppContext; 