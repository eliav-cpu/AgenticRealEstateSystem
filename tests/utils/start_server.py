#!/usr/bin/env python3
"""
Script para iniciar o servidor Agentic Real Estate
"""

import os
import sys
import subprocess
from pathlib import Path

def check_frontend_build():
    """Verificar se o frontend foi compilado"""
    dist_path = Path("frontend/dist")
    if not dist_path.exists():
        print("❌ Frontend não compilado!")
        print("🔧 Execute: cd frontend && npm run build")
        return False
    
    index_path = dist_path / "index.html"
    if not index_path.exists():
        print("❌ Build do frontend incompleto!")
        print("🔧 Execute: cd frontend && npm run build")
        return False
    
    print("✅ Frontend compilado encontrado")
    return True

def start_server():
    """Iniciar o servidor FastAPI"""
    if not check_frontend_build():
        sys.exit(1)
    
    print("🚀 Iniciando Agentic Real Estate Server...")
    print("=" * 60)
    print("📱 Frontend: http://localhost:8000")
    print("🔧 API Docs: http://localhost:8000/api/docs")
    print("📊 API Redoc: http://localhost:8000/api/redoc")
    print("=" * 60)
    print("🧪 Mock Mode: Dados brasileiros de demonstração")
    print("🌐 Real Mode: API RentCast real (EUA)")
    print("🎛️  Seletor no header da interface")
    print("=" * 60)
    print("Pressione Ctrl+C para parar o servidor")
    print()
    
    try:
        # Executar o servidor usando uvicorn diretamente
        subprocess.run([
            "uv", "run", "uvicorn", "api_server:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 