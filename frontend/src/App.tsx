import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from '@/context/AppContext';
import Header from '@/components/Header';
import HomePage from '@/pages/HomePage';
import './App.css';

function App() {
  return (
    <AppProvider>
      <Router>
        <div className="min-h-screen bg-secondary-50">
          <Header />
          
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/search" element={<HomePage />} />
              {/* Futuras rotas podem ser adicionadas aqui */}
              <Route path="/appointments" element={<div className="p-8 text-center">Página de Agendamentos - Em desenvolvimento</div>} />
              <Route path="/properties/:id" element={<div className="p-8 text-center">Detalhes da Propriedade - Em desenvolvimento</div>} />
              <Route path="*" element={<div className="p-8 text-center">Página não encontrada</div>} />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="bg-white border-t border-secondary-200 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <div className="flex items-center justify-between">
                <div className="text-sm text-secondary-600">
                  © 2024 Agentic Real Estate. Sistema Inteligente de Imóveis.
                </div>
                <div className="flex items-center space-x-4 text-sm text-secondary-500">
                  <span>Powered by PydanticAI + LangGraph</span>
                  <span>•</span>
                  <span>API RentCast Integration</span>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </AppProvider>
  );
}

export default App; 