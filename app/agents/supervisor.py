"""
Supervisor Agent - Avalia e valida respostas dos agentes antes de enviar ao usuário.

Responsabilidades:
- Avaliar TODA resposta de agente ANTES de enviar ao usuário
- Validar qualidade, precisão e tom da resposta
- Dar instruções e correções aos agentes
- Bloquear respostas inadequadas e solicitar nova resposta
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from datetime import datetime

from ..utils.logging import get_logger, log_agent_action, log_error
from ..utils.logfire_config import AgentExecutionContext
from config.settings import get_settings


class SupervisorDecision(str, Enum):
    """Decisions the supervisor can make about a response."""
    APPROVE = "approve"      # Response is good, send to user
    REVISE = "revise"        # Response needs improvement, send back to agent
    ESCALATE = "escalate"    # Serious issue, needs human intervention


class ResponseEvaluation(BaseModel):
    """Evaluation result from the supervisor."""
    decision: SupervisorDecision = Field(..., description="Decision about the response")
    score: float = Field(..., ge=0.0, le=1.0, description="Quality score 0-1")
    issues: List[str] = Field(default_factory=list, description="List of issues found")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    reasoning: str = Field(..., description="Explanation of the decision")
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentGuidance(BaseModel):
    """Guidance provided to an agent for improvement."""
    agent_name: str = Field(..., description="Name of the agent receiving guidance")
    original_response: str = Field(..., description="The original response that needs improvement")
    issues: List[str] = Field(..., description="Issues identified in the response")
    instructions: str = Field(..., description="Specific instructions for improvement")
    priority: str = Field(default="medium", description="Priority level: low, medium, high")


class ConversationHealth(BaseModel):
    """Assessment of overall conversation health."""
    is_healthy: bool = Field(..., description="Whether the conversation is progressing well")
    handoff_count: int = Field(default=0, description="Number of agent handoffs")
    issues_detected: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class SupervisorAgent:
    """
    Supervisor agent that evaluates and validates all agent responses.

    The supervisor acts as a quality gate between agents and the user,
    ensuring responses are accurate, helpful, and appropriate.
    """

    def __init__(self):
        self.logger = get_logger("supervisor_agent")
        self.settings = get_settings()
        self._agent: Optional[Agent] = None

        # Evaluation criteria
        self.quality_criteria = {
            "relevance": "Response directly addresses the user's question",
            "accuracy": "Information provided is factually correct",
            "completeness": "Response is complete and doesn't leave out important details",
            "clarity": "Response is clear and easy to understand",
            "tone": "Response is professional and appropriate",
            "actionable": "Response provides clear next steps when applicable",
        }

        # Minimum score threshold for approval
        self.approval_threshold = 0.7

    async def _get_agent(self) -> Agent:
        """Get or create the PydanticAI agent."""
        if self._agent is None:
            import os
            # Ensure GROQ_API_KEY is set in environment (required by PydanticAI GroqModel)
            if self.settings.groq.api_key:
                os.environ['GROQ_API_KEY'] = self.settings.groq.api_key
            model = GroqModel(self.settings.groq.default_model)
            self._agent = Agent(model)
        return self._agent

    async def evaluate_response(
        self,
        agent_name: str,
        response: str,
        user_query: str,
        context: Dict[str, Any] = None
    ) -> ResponseEvaluation:
        """
        Evaluate an agent's response before sending to user.

        Args:
            agent_name: Name of the agent that generated the response
            response: The response to evaluate
            user_query: The original user query
            context: Additional context (property info, conversation history, etc.)

        Returns:
            ResponseEvaluation with decision, score, and feedback
        """
        self.logger.info(f"Evaluating response from {agent_name}")

        with AgentExecutionContext("supervisor", "evaluate_response") as span:
            if span:
                span.set_attributes({
                    "supervisor.agent_evaluated": agent_name,
                    "supervisor.response_length": len(response),
                    "supervisor.query_length": len(user_query)
                })

            try:
                agent = await self._get_agent()

                # Build evaluation prompt
                context_info = ""
                if context:
                    if context.get("property_context"):
                        context_info += f"\nProperty Context: {context.get('property_context', {}).get('formattedAddress', 'N/A')}"
                    if context.get("conversation_length"):
                        context_info += f"\nConversation Length: {context.get('conversation_length')} messages"

                prompt = f"""You are a quality assurance supervisor for a real estate AI assistant.

Evaluate the following response from the '{agent_name}' agent.

USER QUERY: "{user_query}"

AGENT RESPONSE: "{response}"
{context_info}

EVALUATION CRITERIA:
1. RELEVANCE: Does it directly address the user's question?
2. ACCURACY: Is the information factually correct?
3. COMPLETENESS: Is it complete without missing important details?
4. CLARITY: Is it clear and easy to understand?
5. TONE: Is it professional and appropriate?
6. ACTIONABLE: Does it provide clear next steps?

Provide your evaluation in the following format:
- DECISION: APPROVE (good to send), REVISE (needs improvement), or ESCALATE (serious issue)
- SCORE: A number from 0.0 to 1.0
- ISSUES: List any problems found (or "None" if none)
- SUGGESTIONS: List improvements needed (or "None" if none)
- REASONING: Brief explanation of your decision

Be thorough but fair. Approve responses that are good enough, even if not perfect.
Only REVISE if there are real issues that would harm the user experience.
Only ESCALATE for serious problems like harmful content or completely wrong information."""

                eval_response = await agent.run(prompt)
                eval_text = str(eval_response.output)

                # Parse the evaluation response
                evaluation = self._parse_evaluation(eval_text, agent_name, response)

                log_agent_action(
                    agent_name="supervisor",
                    action="response_evaluated",
                    details={
                        "evaluated_agent": agent_name,
                        "decision": evaluation.decision.value,
                        "score": evaluation.score,
                        "issues_count": len(evaluation.issues)
                    }
                )

                if span:
                    span.set_attributes({
                        "supervisor.decision": evaluation.decision.value,
                        "supervisor.score": evaluation.score,
                        "supervisor.issues_count": len(evaluation.issues)
                    })

                return evaluation

            except Exception as e:
                self.logger.error(f"Error evaluating response: {e}")
                log_error(e, context={"agent": "supervisor", "operation": "evaluate_response"})

                # Default to approve on error to not block the system
                return ResponseEvaluation(
                    decision=SupervisorDecision.APPROVE,
                    score=0.7,
                    issues=["Evaluation error - defaulting to approve"],
                    suggestions=[],
                    reasoning=f"Evaluation failed with error: {str(e)[:100]}. Defaulting to approve."
                )

    def _parse_evaluation(self, eval_text: str, agent_name: str, response: str) -> ResponseEvaluation:
        """Parse the LLM evaluation response into structured format."""
        eval_lower = eval_text.lower()

        # Determine decision
        if "escalate" in eval_lower:
            decision = SupervisorDecision.ESCALATE
        elif "revise" in eval_lower:
            decision = SupervisorDecision.REVISE
        else:
            decision = SupervisorDecision.APPROVE

        # Extract score (look for numbers like 0.8, 0.85, etc.)
        import re
        score_match = re.search(r'score[:\s]*([0-9]\.[0-9]+|[01])', eval_lower)
        if score_match:
            score = float(score_match.group(1))
        else:
            # Estimate score based on decision
            score = 0.85 if decision == SupervisorDecision.APPROVE else 0.5 if decision == SupervisorDecision.REVISE else 0.2

        # Extract issues
        issues = []
        if "issues:" in eval_lower or "problems:" in eval_lower:
            issues_section = eval_text.split("ISSUES:")[-1].split("SUGGESTIONS:")[0] if "ISSUES:" in eval_text else ""
            if issues_section and "none" not in issues_section.lower():
                issues = [line.strip().strip("-•") for line in issues_section.strip().split("\n") if line.strip() and line.strip() != "-"]

        # Extract suggestions
        suggestions = []
        if "suggestions:" in eval_lower or "improvements:" in eval_lower:
            suggestions_section = eval_text.split("SUGGESTIONS:")[-1].split("REASONING:")[0] if "SUGGESTIONS:" in eval_text else ""
            if suggestions_section and "none" not in suggestions_section.lower():
                suggestions = [line.strip().strip("-•") for line in suggestions_section.strip().split("\n") if line.strip() and line.strip() != "-"]

        # Extract reasoning
        reasoning = "Evaluation completed."
        if "reasoning:" in eval_lower:
            reasoning = eval_text.split("REASONING:")[-1].strip()[:500]

        return ResponseEvaluation(
            decision=decision,
            score=score,
            issues=issues[:5],  # Limit to 5 issues
            suggestions=suggestions[:5],  # Limit to 5 suggestions
            reasoning=reasoning
        )

    async def provide_feedback(
        self,
        agent_name: str,
        response: str,
        evaluation: ResponseEvaluation
    ) -> AgentGuidance:
        """
        Provide specific feedback and guidance to an agent for improvement.

        Args:
            agent_name: Name of the agent to guide
            response: The original response that needs improvement
            evaluation: The evaluation result

        Returns:
            AgentGuidance with specific instructions
        """
        self.logger.info(f"Providing feedback to {agent_name}")

        instructions = f"""Based on the evaluation, please revise your response:

ISSUES FOUND:
{chr(10).join(f'- {issue}' for issue in evaluation.issues) if evaluation.issues else '- No specific issues listed'}

SUGGESTIONS:
{chr(10).join(f'- {suggestion}' for suggestion in evaluation.suggestions) if evaluation.suggestions else '- Follow standard guidelines'}

Please provide an improved response that:
1. Addresses all the issues mentioned above
2. Maintains a professional and helpful tone
3. Provides accurate and complete information
4. Includes clear next steps for the user"""

        priority = "high" if evaluation.decision == SupervisorDecision.ESCALATE else \
                  "medium" if evaluation.decision == SupervisorDecision.REVISE else "low"

        guidance = AgentGuidance(
            agent_name=agent_name,
            original_response=response[:500],  # Truncate for logging
            issues=evaluation.issues,
            instructions=instructions,
            priority=priority
        )

        log_agent_action(
            agent_name="supervisor",
            action="feedback_provided",
            details={
                "target_agent": agent_name,
                "priority": priority,
                "issues_count": len(evaluation.issues)
            }
        )

        return guidance

    async def validate_conversation(
        self,
        messages: List[Dict[str, Any]],
        handoff_history: List[Dict[str, Any]] = None
    ) -> ConversationHealth:
        """
        Validate the overall health of a conversation.

        Args:
            messages: List of conversation messages
            handoff_history: List of agent handoffs

        Returns:
            ConversationHealth assessment
        """
        self.logger.info("Validating conversation health")

        issues = []
        recommendations = []
        handoff_count = len(handoff_history) if handoff_history else 0

        # Check for too many handoffs
        if handoff_count > 5:
            issues.append("Too many agent handoffs - may indicate routing issues")
            recommendations.append("Review routing logic to reduce handoffs")

        # Check conversation length
        if len(messages) > 20:
            issues.append("Long conversation - user may not be getting resolution")
            recommendations.append("Consider summarizing progress and offering direct assistance")

        # Check for repeated questions (basic heuristic)
        if len(messages) >= 4:
            last_user_msgs = [m.get("content", "").lower() for m in messages[-4:] if m.get("role") == "user"]
            if len(set(last_user_msgs)) < len(last_user_msgs) * 0.7:
                issues.append("User may be repeating themselves - possible misunderstanding")
                recommendations.append("Clarify user intent before proceeding")

        is_healthy = len(issues) == 0

        health = ConversationHealth(
            is_healthy=is_healthy,
            handoff_count=handoff_count,
            issues_detected=issues,
            recommendations=recommendations
        )

        log_agent_action(
            agent_name="supervisor",
            action="conversation_validated",
            details={
                "is_healthy": is_healthy,
                "handoff_count": handoff_count,
                "issues_count": len(issues)
            }
        )

        return health

    async def get_manager_insights(self, manager_recommendations: List[str]) -> str:
        """
        Process insights from the Manager agent and incorporate them.

        Args:
            manager_recommendations: List of recommendations from Manager

        Returns:
            Processed guidance string
        """
        if not manager_recommendations:
            return ""

        insights = "\n".join(f"- {rec}" for rec in manager_recommendations[:5])
        self.logger.info(f"Received {len(manager_recommendations)} insights from Manager")

        log_agent_action(
            agent_name="supervisor",
            action="manager_insights_received",
            details={"recommendations_count": len(manager_recommendations)}
        )

        return f"\n\nMANAGER INSIGHTS:\n{insights}"


# Singleton instance
_supervisor: Optional[SupervisorAgent] = None


def get_supervisor() -> SupervisorAgent:
    """Get or create the global supervisor instance."""
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor
