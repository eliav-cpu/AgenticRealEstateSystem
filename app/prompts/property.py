"""
Prompts especializados para o Agente de Análise de Propriedades

Contém templates de prompts otimizados para apresentação e análise de imóveis.
"""

from typing import Dict, Any, List, Optional


class PropertyPrompts:
    """Classe com prompts especializados para análise de propriedades."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Prompt de sistema principal para o agente de propriedades."""
        return """Você é o Agente de Análise de Propriedades, especializado em apresentar 
        informações imobiliárias de forma clara, atrativa e personalizada.

        SUAS RESPONSABILIDADES:
        - Apresentar informações de imóveis de forma clara e atrativa
        - Responder perguntas específicas sobre propriedades
        - Comparar diferentes opções objetivamente
        - Destacar pontos relevantes baseados no perfil do usuário
        - Gerar descrições personalizadas e envolventes

        PADRÃO ReAct (Reasoning + Acting):
        1. REASONING: Analise a consulta e o contexto do usuário
        2. ACTING: Execute análise ou comparação apropriada
        3. OBSERVATION: Avalie os resultados da análise
        4. DECISION: Forneça resposta personalizada e acionável

        DIRETRIZES:
        - Use linguagem clara e acessível
        - Destaque vantagens E desvantagens honestamente
        - Personalize respostas baseado no perfil do usuário
        - Inclua sugestões práticas e próximos passos
        - Seja objetivo mas envolvente
        - Sempre responda em português brasileiro

        FORMATO DAS RESPOSTAS:
        - Comece com resumo executivo
        - Detalhe pontos principais
        - Inclua análise pros/contras
        - Termine com recomendações práticas

        HANDOFFS:
        - Para scheduling_agent: quando usuário quer agendar visita
        - Para search_agent: quando precisa de mais propriedades
        """

    @staticmethod
    def get_analysis_prompt(
        properties: List[Dict[str, Any]], 
        user_query: str,
        analysis_focus: str = "general"
    ) -> str:
        """Prompt para análise detalhada de propriedades."""
        
        properties_summary = "\n".join([
            f"- {prop.get('title', 'Propriedade')} em {prop.get('address', {}).get('neighborhood', 'N/A')} - {prop.get('price_formatted', 'N/A')}"
            for prop in properties[:5]  # Limitar a 5 propriedades
        ])
        
        focus_instructions = {
            "investment": "Foque em potencial de valorização, ROI, localização estratégica e oportunidades de aluguel.",
            "family": "Foque em espaço, segurança, proximidade de escolas, áreas de lazer e infraestrutura familiar.",
            "first_time": "Foque em facilidade de financiamento, custos totais, documentação e processo de compra.",
            "luxury": "Foque em exclusividade, acabamentos premium, localização privilegiada e amenidades especiais.",
            "general": "Forneça uma análise equilibrada considerando todos os aspectos importantes."
        }
        
        return f"""
        Analise as seguintes propriedades com foco em {analysis_focus}:

        PROPRIEDADES ENCONTRADAS:
        {properties_summary}

        CONSULTA DO USUÁRIO: "{user_query}"

        INSTRUÇÕES ESPECÍFICAS:
        {focus_instructions.get(analysis_focus, focus_instructions["general"])}

        ESTRUTURA DA RESPOSTA:
        1. **Resumo Executivo** (2-3 linhas sobre o que foi encontrado)
        2. **Destaque Principal** (melhor opção e por quê)
        3. **Análise Detalhada** (características importantes de cada propriedade)
        4. **Prós e Contras** (pontos positivos e de atenção)
        5. **Recomendações** (próximos passos sugeridos)

        Use emojis para tornar a resposta mais visual e atrativa.
        """

    @staticmethod
    def get_comparison_prompt(
        properties: List[Dict[str, Any]], 
        comparison_criteria: List[str] = None
    ) -> str:
        """Prompt para comparação entre propriedades."""
        
        criteria = comparison_criteria or [
            "Preço", "Localização", "Área", "Quartos", "Estado de conservação", "Infraestrutura"
        ]
        
        properties_details = []
        for i, prop in enumerate(properties, 1):
            details = f"""
            PROPRIEDADE {i}:
            - Título: {prop.get('title', 'N/A')}
            - Preço: {prop.get('price_formatted', 'N/A')}
            - Área: {prop.get('area', 'N/A')}m²
            - Quartos: {prop.get('bedrooms', 'N/A')}
            - Banheiros: {prop.get('bathrooms', 'N/A')}
            - Localização: {prop.get('address', {}).get('neighborhood', 'N/A')}
            """
            properties_details.append(details)
        
        return f"""
        Compare as seguintes propriedades usando os critérios especificados:

        {chr(10).join(properties_details)}

        CRITÉRIOS DE COMPARAÇÃO:
        {', '.join(criteria)}

        ESTRUTURA DA RESPOSTA:
        1. **Tabela Comparativa** (formato visual com os critérios principais)
        2. **Ranking** (ordem de recomendação com justificativa)
        3. **Análise por Critério** (detalhamento de cada aspecto)
        4. **Recomendação Final** (qual escolher e por quê)
        5. **Fatores Decisivos** (pontos que devem influenciar a decisão)

        Use uma tabela visual e destaque as diferenças mais importantes.
        """

    @staticmethod
    def get_description_prompt(
        property_data: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]] = None,
        style: str = "comprehensive"
    ) -> str:
        """Prompt para gerar descrição personalizada de propriedade."""
        
        style_instructions = {
            "comprehensive": "Descrição completa e detalhada com todos os aspectos importantes",
            "concise": "Descrição resumida focando nos pontos principais",
            "marketing": "Descrição atrativa e persuasiva para despertar interesse",
            "technical": "Descrição técnica com especificações detalhadas",
            "family_focused": "Descrição focada em aspectos familiares e de convivência"
        }
        
        profile_context = ""
        if user_profile:
            profile_context = f"""
            PERFIL DO USUÁRIO:
            - Orçamento: {user_profile.get('budget', 'N/A')}
            - Preferências: {user_profile.get('preferences', 'N/A')}
            - Necessidades: {user_profile.get('needs', 'N/A')}
            """
        
        return f"""
        Gere uma descrição {style} para a seguinte propriedade:

        DADOS DA PROPRIEDADE:
        - Título: {property_data.get('title', 'N/A')}
        - Tipo: {property_data.get('type', 'N/A')}
        - Preço: {property_data.get('price_formatted', 'N/A')}
        - Área: {property_data.get('area', 'N/A')}m²
        - Quartos: {property_data.get('bedrooms', 'N/A')}
        - Banheiros: {property_data.get('bathrooms', 'N/A')}
        - Localização: {property_data.get('address', {}).get('neighborhood', 'N/A')}
        - Características: {property_data.get('features', [])}

        {profile_context}

        ESTILO SOLICITADO: {style_instructions.get(style, style_instructions["comprehensive"])}

        ESTRUTURA DA DESCRIÇÃO:
        1. **Título Atrativo**
        2. **Localização e Contexto**
        3. **Características Principais**
        4. **Diferenciais e Destaques**
        5. **Chamada para Ação**

        Personalize a descrição baseada no perfil do usuário quando disponível.
        Use linguagem envolvente e destaque os pontos mais relevantes.
        """

    @staticmethod
    def get_clarification_prompt(user_query: str, missing_info: List[str]) -> str:
        """Prompt para solicitar clarificações do usuário."""
        
        missing_items = "\n".join([f"- {item}" for item in missing_info])
        
        return f"""
        O usuário fez a seguinte consulta: "{user_query}"

        Para fornecer uma análise mais precisa, preciso de algumas informações adicionais:

        INFORMAÇÕES NECESSÁRIAS:
        {missing_items}

        ESTRUTURA DA RESPOSTA:
        1. **Reconhecimento** (confirme que entendeu a solicitação)
        2. **Perguntas Específicas** (solicite as informações faltantes de forma clara)
        3. **Contexto** (explique por que essas informações são importantes)
        4. **Próximos Passos** (o que acontecerá após receber as informações)

        Seja amigável e explique como essas informações ajudarão a fornecer uma melhor recomendação.
        """

    @staticmethod
    def get_handoff_prompt(target_agent: str, reason: str, context: Dict[str, Any]) -> str:
        """Prompt para handoffs para outros agentes."""
        
        handoff_messages = {
            "scheduling_agent": "Vou transferir você para nosso especialista em agendamentos que cuidará da sua visita.",
            "search_agent": "Vou buscar mais opções que atendam melhor suas necessidades.",
            "property_agent": "Vou analisar as propriedades encontradas em detalhes para você."
        }
        
        return f"""
        HANDOFF PARA: {target_agent}
        MOTIVO: {reason}
        CONTEXTO: {context}

        MENSAGEM DE TRANSIÇÃO:
        {handoff_messages.get(target_agent, f"Transferindo para {target_agent}...")}

        Mantenha a continuidade da conversa e garanta que o contexto seja preservado.
        """

    @staticmethod
    def get_success_template(action: str, details: Dict[str, Any]) -> str:
        """Template para mensagens de sucesso."""
        
        templates = {
            "analysis_completed": """
            ✅ **Análise Concluída com Sucesso!**
            
            Analisei {property_count} propriedades baseado em seus critérios.
            
            **Próximos passos disponíveis:**
            • 📅 Agendar visita à propriedade recomendada
            • 🔍 Buscar mais opções similares
            • 📊 Comparar com outras propriedades
            • 💬 Fazer perguntas específicas sobre alguma propriedade
            
            Como posso ajudar mais?
            """,
            
            "comparison_completed": """
            ✅ **Comparação Finalizada!**
            
            Comparei {property_count} propriedades usando {criteria_count} critérios.
            
            **Recomendação:** {recommendation}
            
            **Próximos passos:**
            • 📅 Agendar visita à propriedade recomendada
            • 📋 Ver análise detalhada de alguma propriedade específica
            • 🔍 Buscar mais opções
            
            Qual propriedade despertou mais seu interesse?
            """
        }
        
        template = templates.get(action, "Ação concluída com sucesso!")
        return template.format(**details)


# Instância global para fácil acesso
property_prompts = PropertyPrompts() 