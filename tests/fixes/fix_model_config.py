#!/usr/bin/env python3
"""
Script para corrigir configurações de modelo no settings.py
"""

import re

def fix_model_config():
    """Corrige todas as referências ao modelo scout para maverick"""
    
    # Ler arquivo
    with open('config/settings.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir todas as ocorrências
    new_content = re.sub(
        r'meta-llama/llama-4-scout:free',
        'meta-llama/llama-4-maverick:free',
        content
    )
    
    # Verificar se houve mudanças
    if content != new_content:
        # Escrever arquivo corrigido
        with open('config/settings.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Configurações atualizadas:")
        print("   meta-llama/llama-4-scout:free → meta-llama/llama-4-maverick:free")
        
        # Contar quantas substituições foram feitas
        count = content.count('meta-llama/llama-4-scout:free')
        print(f"   {count} ocorrências corrigidas")
    else:
        print("✅ Nenhuma correção necessária - arquivo já atualizado")

if __name__ == "__main__":
    fix_model_config() 