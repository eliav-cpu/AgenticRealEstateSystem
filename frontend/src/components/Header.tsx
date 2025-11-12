import { 
  Home, 
  Menu, 
  Settings, 
  User, 
  Database, 
  Cloud,
  Activity,
  Moon,
  Sun,
  Bell
} from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { apiService } from '@/services/api';

export default function Header() {
  const { state, toggleSidebar, setApiMode, setTheme } = useApp();

  const handleModeChange = (mode: 'mock' | 'real') => {
    setApiMode(mode);
    apiService.setMode(mode);
  };

  const getModeIcon = (mode: 'mock' | 'real') => {
    return mode === 'mock' ? Database : Cloud;
  };

  const getModeLabel = (mode: 'mock' | 'real') => {
    return mode === 'mock' ? 'Mock Data' : 'Real API';
  };

  const getModeDescription = (mode: 'mock' | 'real') => {
    return mode === 'mock' 
      ? 'Demo data (free)' 
      : 'Real RentCast API data';
  };

  return (
    <header className="bg-white border-b border-secondary-200 shadow-soft">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left Section */}
          <div className="flex items-center">
            {/* Menu Toggle */}
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-lg text-secondary-600 hover:bg-secondary-100 focus:ring-2 focus:ring-primary-500 transition-colors lg:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>

            {/* Logo */}
            <div className="flex items-center ml-2 lg:ml-0">
              <div className="flex items-center justify-center w-8 h-8 bg-primary-600 rounded-lg mr-3">
                <Home className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-secondary-900">
                  Agentic Real Estate
                </h1>
                <p className="text-xs text-secondary-500 hidden sm:block">
                  Intelligent Real Estate System
                </p>
              </div>
            </div>
          </div>

          {/* Center Section - API Mode Selector */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center bg-secondary-100 rounded-lg p-1">
              {(['mock', 'real'] as const).map((mode) => {
                const Icon = getModeIcon(mode);
                const isActive = state.apiMode === mode;
                
                return (
                  <button
                    key={mode}
                    onClick={() => handleModeChange(mode)}
                    className={`relative flex items-center px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-white text-primary-600 shadow-sm'
                        : 'text-secondary-600 hover:text-secondary-900'
                    }`}
                    title={getModeDescription(mode)}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    <span className="hidden sm:inline">{getModeLabel(mode)}</span>
                    
                    {/* Status Indicator */}
                    <div className={`absolute -top-1 -right-1 w-2 h-2 rounded-full ${
                      isActive 
                        ? mode === 'mock' 
                          ? 'bg-warning-400' 
                          : 'bg-success-400'
                        : 'bg-secondary-300'
                    }`} />
                  </button>
                );
              })}
            </div>

            {/* Mode Info */}
            <div className="hidden md:flex items-center text-xs text-secondary-500">
              <Activity className="h-3 w-3 mr-1" />
              <span>
                {state.apiMode === 'mock' ? 'Demo' : 'Production'}
              </span>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-2">
            {/* Theme Toggle */}
            <button
              onClick={() => setTheme(state.theme === 'light' ? 'dark' : 'light')}
              className="p-2 rounded-lg text-secondary-600 hover:bg-secondary-100 focus:ring-2 focus:ring-primary-500 transition-colors"
              title="Toggle theme"
            >
              {state.theme === 'light' ? (
                <Moon className="h-5 w-5" />
              ) : (
                <Sun className="h-5 w-5" />
              )}
            </button>

            {/* Notifications */}
            <button
              className="relative p-2 rounded-lg text-secondary-600 hover:bg-secondary-100 focus:ring-2 focus:ring-primary-500 transition-colors"
              title="Notifications"
            >
              <Bell className="h-5 w-5" />
              {state.appointments.length > 0 && (
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-primary-600 text-white text-xs rounded-full flex items-center justify-center">
                  {state.appointments.length}
                </span>
              )}
            </button>

            {/* User Menu */}
            <div className="flex items-center">
              {state.user ? (
                <div className="flex items-center space-x-3">
                  <div className="hidden sm:block text-right">
                    <p className="text-sm font-medium text-secondary-900">
                      {state.user.name}
                    </p>
                    <p className="text-xs text-secondary-500">
                      {state.user.email}
                    </p>
                  </div>
                  <div className="flex items-center justify-center w-8 h-8 bg-primary-600 rounded-full">
                    <span className="text-sm font-medium text-white">
                      {state.user.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                </div>
              ) : (
                <button className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-secondary-700 hover:text-secondary-900 transition-colors">
                  <User className="h-4 w-4" />
                  <span className="hidden sm:inline">Sign In</span>
                </button>
              )}
            </div>

            {/* Settings */}
            <button
              className="p-2 rounded-lg text-secondary-600 hover:bg-secondary-100 focus:ring-2 focus:ring-primary-500 transition-colors"
              title="Settings"
            >
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* API Mode Status Bar */}
      <div className={`px-4 sm:px-6 lg:px-8 py-2 text-xs ${
        state.apiMode === 'mock' 
          ? 'bg-warning-50 text-warning-700 border-t border-warning-200'
          : 'bg-success-50 text-success-700 border-t border-success-200'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`w-2 h-2 rounded-full mr-2 ${
              state.apiMode === 'mock' ? 'bg-warning-400' : 'bg-success-400'
            }`} />
            <span className="font-medium">
              {state.apiMode === 'mock' 
                ? '🧪 Demo Mode Active - Mock Data Identical to Real API'
                : '🚀 Production Mode Active - Consuming Real RentCast API'
              }
            </span>
          </div>
          
          {state.loading && (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-current mr-2"></div>
              <span>Loading...</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
} 