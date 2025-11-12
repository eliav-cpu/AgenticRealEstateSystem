#!/usr/bin/env python3
"""Script para corrigir importações problemáticas"""

def fix_scheduling_imports():
    with open('app/agents/scheduling.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remover importação incorreta
    content = content.replace('from pydantic_ai.models.openrouter import OpenRouterModel', '')
    
    # Adicionar importação de json se não estiver
    if 'import json' not in content:
        content = content.replace('from pydantic_ai.providers.openrouter import OpenRouterProvider', 
                                'from pydantic_ai.providers.openrouter import OpenRouterProvider\nimport json')
    
    # Corrigir o código que falta a declaração da variável openrouter_key
    old_code = '''        try:
            from pydantic_ai.models.openai import OpenAIModel
            from pydantic_ai.providers.openrouter import OpenRouterProvider            
            if openrouter_key and openrouter_key != "your_openrouter_api_key_here":'''
    
    new_code = '''        try:
            from pydantic_ai.models.openai import OpenAIModel
            from pydantic_ai.providers.openrouter import OpenRouterProvider
            
            # Obter chave via settings (centralizado)
            openrouter_key = self.settings.apis.openrouter_key or ""
            
            if openrouter_key and openrouter_key != "your_openrouter_api_key_here":'''
    
    content = content.replace(old_code, new_code)
    
    with open('app/agents/scheduling.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Importações corrigidas em scheduling.py")

if __name__ == "__main__":
    fix_scheduling_imports() 