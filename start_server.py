#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialização do servidor API com configuração UTF-8.
Resolve problemas de codificação Unicode no Windows.
"""

import os
import sys
import locale
import subprocess

def setup_encoding():
    """Configurar codificação UTF-8 para evitar erros Unicode."""
    
    # Configurar variáveis de ambiente para UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSFSENCODING'] = '0'
    
    # Configurar locale se possível
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            print("Warning: Could not set UTF-8 locale")
    
    # Configurar stdout/stderr para UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

def main():
    """Função principal para iniciar o servidor."""
    
    print("=== Agentic Real Estate API Server ===")
    print("Configuring UTF-8 encoding...")
    
    # Configurar codificação
    setup_encoding()
    
    print("Starting server...")
    
    try:
        # Importar e executar o servidor
        import uvicorn
        from api_server import app
        
        # Configuração do servidor
        config = {
            "app": "api_server:app",
            "host": "127.0.0.1",
            "port": 8000,
            "reload": True,
            "log_level": "info",
            "access_log": True
        }
        
        print(f"Server starting at http://{config['host']}:{config['port']}")
        print("Press Ctrl+C to stop the server")
        
        # Iniciar servidor
        uvicorn.run(**config)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 