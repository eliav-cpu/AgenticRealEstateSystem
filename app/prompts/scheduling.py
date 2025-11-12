"""
Prompts especializados para o Agente de Agendamento

Contém templates de prompts otimizados para agendamento de visitas e gestão temporal.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, time


class SchedulingPrompts:
    """Classe com prompts especializados para agendamento."""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Prompt de sistema principal para o agente de agendamento."""
        return """Você é o Agente de Agendamento, especialista em inteligência temporal avançada.
        
        RESPONSABILIDADES:
        1. INTERPRETAR referências temporais em linguagem natural
        2. VALIDAR horários comerciais (segunda a sexta, 9h às 18h)
        3. CALCULAR datas relativas (amanhã, próxima semana, etc.)
        4. SUGERIR alternativas quando necessário
        5. AGENDAR visitas a propriedades
        
        REGRAS TEMPORAIS:
        - Horário comercial: Segunda a Sexta, 9:00 às 18:00
        - Não agendar fins de semana ou feriados
        - Considerar fuso horário Brasil (America/Sao_Paulo)
        - Sugerir horários próximos ao solicitado se inválido
        
        INTERPRETAÇÃO DE LINGUAGEM NATURAL:
        - "amanhã" = próximo dia útil
        - "próxima semana" = segunda-feira da próxima semana
        - "sexta que vem" = próxima sexta-feira
        - "depois de amanhã" = dia após amanhã se for dia útil
        - "pela manhã" = entre 9h e 12h
        - "à tarde" = entre 13h e 18h
        
        VALIDAÇÕES:
        - Data não pode ser no passado
        - Horário deve estar no range comercial
        - Considerar apenas dias úteis
        
        HANDOFFS:
        - Para property_agent: quando usuário quer ver mais propriedades
        - Para search_agent: quando usuário quer nova busca
        
        Sempre responda em português brasileiro de forma clara e amigável.
        """

    @staticmethod
    def get_scheduling_request_prompt(
        user_request: str,
        property_info: Dict[str, Any],
        available_slots: List[Dict[str, Any]] = None
    ) -> str:
        """Prompt para processar solicitação de agendamento."""
        
        slots_text = ""
        if available_slots:
            slots_text = "\n".join([
                f"• {slot.get('date', 'N/A')} às {slot.get('time', 'N/A')} - {slot.get('status', 'Disponível')}"
                for slot in available_slots
            ])
        
        return f"""
        Processe esta solicitação de agendamento:

        SOLICITAÇÃO DO USUÁRIO: "{user_request}"

        PROPRIEDADE SELECIONADA:
        - Título: {property_info.get('title', 'N/A')}
        - Endereço: {property_info.get('address', {}).get('street', 'N/A')}
        - Bairro: {property_info.get('address', {}).get('neighborhood', 'N/A')}
        - Preço: {property_info.get('price_formatted', 'N/A')}

        HORÁRIOS DISPONÍVEIS:
        {slots_text if slots_text else "• Amanhã às 14h00\n• Quinta-feira às 10h30\n• Sexta-feira às 16h00"}

        TAREFAS:
        1. **Interpretar** a referência temporal na solicitação
        2. **Validar** se o horário está dentro das regras comerciais
        3. **Sugerir** alternativas se necessário
        4. **Confirmar** os detalhes do agendamento

        ESTRUTURA DA RESPOSTA:
        1. **Confirmação** (reconheça a solicitação)
        2. **Interpretação Temporal** (explique como entendeu a data/hora)
        3. **Validação** (confirme se está dentro das regras)
        4. **Proposta** (apresente o agendamento ou alternativas)
        5. **Próximos Passos** (o que acontece após confirmação)

        Use linguagem amigável e seja claro sobre datas e horários.
        """

    @staticmethod
    def get_time_interpretation_prompt(time_expression: str) -> str:
        """Prompt para interpretar expressões temporais."""
        
        return f"""
        Interprete a seguinte expressão temporal em português:

        EXPRESSÃO: "{time_expression}"

        CONTEXTO TEMPORAL:
        - Data atual: {datetime.now().strftime('%d/%m/%Y')}
        - Dia da semana: {datetime.now().strftime('%A')}
        - Horário atual: {datetime.now().strftime('%H:%M')}

        REGRAS DE INTERPRETAÇÃO:
        - "amanhã" = próximo dia útil
        - "hoje" = hoje se ainda há tempo, senão próximo dia útil
        - "manhã" = entre 9h e 12h
        - "tarde" = entre 13h e 18h
        - "próxima semana" = segunda-feira da próxima semana
        - Horários específicos devem ser validados (9h-18h)

        RESULTADO ESPERADO:
        1. **Data calculada** (formato DD/MM/YYYY)
        2. **Horário sugerido** (formato HH:MM)
        3. **Confiança** (alta/média/baixa)
        4. **Validação** (dentro das regras comerciais?)
        5. **Alternativas** (se necessário)

        Seja preciso na interpretação e explique seu raciocínio.
        """

    @staticmethod
    def get_validation_prompt(
        proposed_date: str,
        proposed_time: str,
        validation_rules: Dict[str, Any]
    ) -> str:
        """Prompt para validar data e horário propostos."""
        
        return f"""
        Valide o seguinte agendamento proposto:

        DATA PROPOSTA: {proposed_date}
        HORÁRIO PROPOSTO: {proposed_time}

        REGRAS DE VALIDAÇÃO:
        - Horário comercial: {validation_rules.get('business_hours', '9h às 18h')}
        - Dias úteis: {validation_rules.get('business_days', 'Segunda a Sexta')}
        - Antecedência mínima: {validation_rules.get('min_advance', '2 horas')}
        - Duração da visita: {validation_rules.get('visit_duration', '60 minutos')}

        VERIFICAÇÕES NECESSÁRIAS:
        1. ✓ Data não está no passado
        2. ✓ É dia útil (segunda a sexta)
        3. ✓ Está no horário comercial
        4. ✓ Tem antecedência mínima
        5. ✓ Não conflita com outros agendamentos

        RESULTADO DA VALIDAÇÃO:
        - **Status:** (Válido/Inválido)
        - **Motivo:** (se inválido, explicar por quê)
        - **Alternativas:** (sugerir horários próximos se inválido)
        - **Confirmação:** (detalhes finais se válido)

        Se inválido, sugira 3 alternativas próximas que atendam às regras.
        """

    @staticmethod
    def get_confirmation_prompt(
        appointment_details: Dict[str, Any],
        user_contact: Optional[str] = None
    ) -> str:
        """Prompt para confirmar agendamento."""
        
        return f"""
        Confirme os detalhes do agendamento:

        DETALHES DO AGENDAMENTO:
        📅 Data: {appointment_details.get('date', 'N/A')}
        🕐 Horário: {appointment_details.get('time', 'N/A')}
        🏠 Propriedade: {appointment_details.get('property_title', 'N/A')}
        📍 Endereço: {appointment_details.get('address', 'N/A')}
        👤 Corretor: {appointment_details.get('agent_name', 'João Silva')}
        📞 Contato: {appointment_details.get('agent_phone', '(21) 99999-9999')}

        CONTATO DO CLIENTE: {user_contact or 'A ser fornecido'}

        ESTRUTURA DA CONFIRMAÇÃO:
        1. **Resumo do Agendamento** (todos os detalhes importantes)
        2. **Instruções** (como chegar, o que levar, etc.)
        3. **Contatos** (corretor responsável e emergência)
        4. **Lembretes** (confirmação por email/SMS)
        5. **Próximos Passos** (o que esperar da visita)

        INFORMAÇÕES ADICIONAIS:
        - Duração estimada: 60 minutos
        - Documentos necessários: RG e comprovante de renda
        - Lembrete será enviado 1 hora antes
        - Reagendamento pode ser feito até 2 horas antes

        Use tom profissional mas amigável, e inclua todos os detalhes importantes.
        """

    @staticmethod
    def get_reschedule_prompt(
        current_appointment: Dict[str, Any],
        new_request: str
    ) -> str:
        """Prompt para reagendamento."""
        
        return f"""
        Processe esta solicitação de reagendamento:

        AGENDAMENTO ATUAL:
        - Data: {current_appointment.get('date', 'N/A')}
        - Horário: {current_appointment.get('time', 'N/A')}
        - Propriedade: {current_appointment.get('property_title', 'N/A')}

        NOVA SOLICITAÇÃO: "{new_request}"

        PROCESSO DE REAGENDAMENTO:
        1. **Interpretar** nova data/horário solicitado
        2. **Validar** disponibilidade e regras comerciais
        3. **Confirmar** cancelamento do agendamento atual
        4. **Criar** novo agendamento
        5. **Notificar** todas as partes envolvidas

        ESTRUTURA DA RESPOSTA:
        1. **Reconhecimento** (confirme o reagendamento)
        2. **Cancelamento** (confirme cancelamento do atual)
        3. **Nova Proposta** (apresente novo horário)
        4. **Validação** (confirme se atende às regras)
        5. **Confirmação Final** (detalhes do novo agendamento)

        Seja empático e eficiente no processo de reagendamento.
        """

    @staticmethod
    def get_cancellation_prompt(appointment_details: Dict[str, Any], reason: str = None) -> str:
        """Prompt para cancelamento de agendamento."""
        
        return f"""
        Processe o cancelamento do seguinte agendamento:

        AGENDAMENTO A CANCELAR:
        - Data: {appointment_details.get('date', 'N/A')}
        - Horário: {appointment_details.get('time', 'N/A')}
        - Propriedade: {appointment_details.get('property_title', 'N/A')}
        - Cliente: {appointment_details.get('client_name', 'N/A')}

        MOTIVO DO CANCELAMENTO: {reason or 'Não informado'}

        PROCESSO DE CANCELAMENTO:
        1. **Confirmar** intenção de cancelamento
        2. **Registrar** motivo (se fornecido)
        3. **Notificar** corretor responsável
        4. **Liberar** horário na agenda
        5. **Oferecer** reagendamento se apropriado

        ESTRUTURA DA RESPOSTA:
        1. **Confirmação** (reconheça a solicitação)
        2. **Processamento** (confirme o cancelamento)
        3. **Notificações** (quem será informado)
        4. **Alternativas** (ofereça reagendamento se apropriado)
        5. **Próximos Passos** (como proceder se mudar de ideia)

        POLÍTICA DE CANCELAMENTO:
        - Cancelamento gratuito até 2 horas antes
        - Notificação automática para todas as partes
        - Possibilidade de reagendamento imediato

        Seja compreensivo e ofereça suporte para futuras necessidades.
        """

    @staticmethod
    def get_availability_prompt(
        date_range: Dict[str, str],
        preferences: Dict[str, Any] = None
    ) -> str:
        """Prompt para consultar disponibilidade."""
        
        prefs_text = ""
        if preferences:
            prefs_text = f"""
            PREFERÊNCIAS DO USUÁRIO:
            - Período preferido: {preferences.get('preferred_time', 'Qualquer horário')}
            - Dias da semana: {preferences.get('preferred_days', 'Qualquer dia útil')}
            - Duração: {preferences.get('duration', '60 minutos')}
            """
        
        return f"""
        Consulte a disponibilidade para agendamento:

        PERÍODO SOLICITADO:
        - Data inicial: {date_range.get('start_date', 'N/A')}
        - Data final: {date_range.get('end_date', 'N/A')}

        {prefs_text}

        HORÁRIOS COMERCIAIS:
        - Segunda a Sexta: 9h às 18h
        - Intervalos de 30 minutos
        - Duração padrão: 60 minutos

        ESTRUTURA DA RESPOSTA:
        1. **Período Consultado** (confirme as datas)
        2. **Horários Disponíveis** (liste opções por dia)
        3. **Recomendações** (melhores horários baseado nas preferências)
        4. **Alternativas** (se poucas opções disponíveis)
        5. **Próximos Passos** (como confirmar um horário)

        Apresente as opções de forma clara e organizada por dia da semana.
        """

    @staticmethod
    def get_reminder_prompt(appointment_details: Dict[str, Any], reminder_type: str) -> str:
        """Prompt para lembretes de agendamento."""
        
        reminder_templates = {
            "24h": "Lembrete: Você tem uma visita agendada para amanhã",
            "2h": "Lembrete: Sua visita será em 2 horas",
            "30min": "Lembrete: Sua visita será em 30 minutos"
        }
        
        return f"""
        Gere um lembrete de agendamento:

        TIPO DE LEMBRETE: {reminder_type}
        TEMPLATE: {reminder_templates.get(reminder_type, 'Lembrete de agendamento')}

        DETALHES DO AGENDAMENTO:
        - Data: {appointment_details.get('date', 'N/A')}
        - Horário: {appointment_details.get('time', 'N/A')}
        - Propriedade: {appointment_details.get('property_title', 'N/A')}
        - Endereço: {appointment_details.get('address', 'N/A')}
        - Corretor: {appointment_details.get('agent_name', 'N/A')}

        ESTRUTURA DO LEMBRETE:
        1. **Saudação** (personalizada com nome se disponível)
        2. **Detalhes da Visita** (data, hora, local)
        3. **Instruções** (como chegar, contatos)
        4. **Preparação** (documentos, perguntas)
        5. **Contatos** (emergência, reagendamento)

        Use tom amigável e inclua todas as informações práticas necessárias.
        """


# Instância global para fácil acesso
scheduling_prompts = SchedulingPrompts() 