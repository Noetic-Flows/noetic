import pytest
from unittest.mock import AsyncMock
from noetic_engine.cognition.evaluator import Evaluator, EvaluationResult, LLMClient
from noetic_lang.core import Plan, PlanStep

class MockLLM(LLMClient):
    async def generate(self, prompt: str) -> EvaluationResult:
        return EvaluationResult(confidence_score=0.9, rationale="Looks good")

@pytest.mark.asyncio
async def test_evaluator_scoring():
    llm = MockLLM()
    evaluator = Evaluator(llm_client=llm)
    
    plan = Plan(steps=[
        PlanStep(skill_id="test", params={}, cost=1.0)
    ], total_cost=1.0)
    
    result = await evaluator.evaluate("Do x", plan, "Context")
    
    assert result.confidence_score == 0.9
    assert result.rationale == "Looks good"
