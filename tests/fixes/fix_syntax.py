#!/usr/bin/env python3
"""
Script para corrigir erro de sintaxe no swarm.py
"""

def fix_syntax_error():
    """Corrige o erro de sintaxe no arquivo swarm.py"""
    
    # Ler arquivo
    with open('app/orchestration/swarm.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir a indentação problemática na linha ~184
    # Trocar "    else:" por "        else:" para alinhar com o if anterior
    content = content.replace(
        "What specific aspect would you like to know more about? *Details from {data_mode} listing*\"\"\"\n    else:",
        "What specific aspect would you like to know more about? *Details from {data_mode} listing*\"\"\"\n        else:"
    )
    
    # Escrever arquivo corrigido
    with open('app/orchestration/swarm.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Erro de sintaxe corrigido no swarm.py")
    print("   - Corrigida indentação do 'else:' na função generate_intelligent_response")

if __name__ == "__main__":
    fix_syntax_error() 