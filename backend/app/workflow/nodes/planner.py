import json
from pydantic import ValidationError
from app.schemas.research import ResearchPlan
from app.services.llm.base import LLMProvider, LLMProviderError
from app.workflow.state import ResearchState

class PlannerError(Exception):
    """Raised when the planner node fails to generate or parse a valid research plan."""
    pass

def clean_json_string(raw_text: str) -> str:
    """Removes markdown code fences from the LLM output to safely extract JSON."""
    text = raw_text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline:].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    return text

async def run_planner(state: ResearchState, llm_provider: LLMProvider) -> dict:
    """
    Analyzes the research query and generates a structured research plan.
    """
    query = state["query"]
    mode = state["mode"].value

    prompt = f"""You are an expert research planning agent.
Your task is to analyze the user's research question and break it down into useful research sub-questions.
Do NOT answer the research question itself. Only create the research plan.
You must return ONLY valid JSON matching the exact schema below. Do not include any other text.

Expected JSON Schema:
{{
    "original_query": "The exact user query",
    "sub_questions": [
        {{
            "id": "q1",
            "question": "First sub-question text",
            "purpose": "Why this question is important for the research"
        }}
    ],
    "mode": "quick | standard | deep"
}}

Instructions:
- Generate between 3 and 10 useful sub-questions depending on complexity.
- Never exceed 20.
- For simple questions, fewer are acceptable.

User's Research Question:
{query}

Requested Mode:
{mode}
"""
    try:
        raw_response = await llm_provider.generate_text(prompt)
        cleaned_json = clean_json_string(raw_response)
        parsed_data = json.loads(cleaned_json)
        
        # Validate against existing Pydantic contract
        plan = ResearchPlan.model_validate(parsed_data)
        
        return {"plan": plan, "error": None}
        
    except LLMProviderError as e:
        raise PlannerError(f"LLM Provider failed during planning: {str(e)}") from e
    except json.JSONDecodeError as e:
        raise PlannerError(f"Failed to parse LLM response as JSON: {str(e)}") from e
    except ValidationError as e:
        raise PlannerError(f"Failed to validate ResearchPlan schema: {str(e)}") from e
    except Exception as e:
        raise PlannerError(f"Unexpected error in planner node: {str(e)}") from e