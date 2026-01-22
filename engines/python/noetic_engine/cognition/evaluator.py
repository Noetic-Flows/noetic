from typing import Protocol, Any
from pydantic import BaseModel
from noetic_engine.stanzas.schema import Plan

class EvaluationResult(BaseModel):
    confidence_score: float
    rationale: str

class LLMClient(Protocol):
    async def generate(self, prompt: str) -> EvaluationResult:
        ...

class Evaluator:
    """
    Red Teaming Evaluator.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def evaluate(self, goal: str, plan: Plan, context: str) -> EvaluationResult:
        """
        Runs an adversarial check on the proposed plan.
        Returns a confidence float (0.0 - 1.0) and a critique string.
        """
        prompt = self._build_adversarial_prompt(goal, plan, context)
        return await self.llm.generate(prompt)

    def _build_adversarial_prompt(self, goal: str, plan: Plan, context: str) -> str:
        plan_str = "\n".join([f"- {s.skill_id} (params={s.params})" for s in plan.steps])
        
        return f"""
        ROLE: Critical Security Auditor.
        TASK: Review the proposed plan for Goal: \"{goal}\".
        
        CONTEXT:
        {context}
        
        PLAN:
        {plan_str}
        
        CHECKLIST:
        1. Does the plan rely on assumptions not in the Context?
        2. Are there irreversible side effects?
        3. Is the tool usage correct for the API version?

        OUTPUT:
        - Confidence Score (0.0 to 1.0)
        - Reason for deduction.
        """
