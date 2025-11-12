#!/usr/bin/env python3

"""
Teste para verificar carregamento do arquivo .env
"""

import os
from dotenv import load_dotenv

print("=== TESTE DE CARREGAMENTO DO .ENV ===")

# Verificar se .env existe
print(f"1. Arquivo .env existe: {os.path.exists('.env')}")

# Carregar .env
load_dotenv()

# Verificar chaves carregadas
print(f"2. OPENROUTER_API_KEY carregada: {bool(os.getenv('OPENROUTER_API_KEY'))}")
print(f"3. ENVIRONMENT carregada: {bool(os.getenv('ENVIRONMENT'))}")
print(f"4. DEBUG carregada: {bool(os.getenv('DEBUG'))}")
print(f"5. RENTCAST_API_KEY carregada: {bool(os.getenv('RENTCAST_API_KEY'))}")

# Verificar valores
key = os.getenv('OPENROUTER_API_KEY', '')
if key:
    print(f"6. OpenRouter key starts with: {key[:15]}...")
    print(f"7. OpenRouter key length: {len(key)}")
else:
    print("6. ❌ OpenRouter key não encontrada")

# Teste de configurações
try:
    from config.settings import get_settings
    settings = get_settings()
    print(f"8. Settings OpenRouter key: {bool(settings.apis.openrouter_key)}")
    if settings.apis.openrouter_key:
        print(f"9. Settings key starts with: {settings.apis.openrouter_key[:15]}...")
except Exception as e:
    print(f"8. ❌ Erro ao carregar settings: {e}")

print("\n=== FIM DO TESTE ===") 