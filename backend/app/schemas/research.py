from enum import Enum
from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints

class ResearchMode(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"

# Type alias for normalized, non-empty query string
QueryString = Annotated[
    str, 
    StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)
]

class ResearchRequest(BaseModel):
    query: QueryString
    mode: ResearchMode = ResearchMode.STANDARD

class ResearchSubQuestion(BaseModel):
    id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1, max_length=1000)
    purpose: str = Field(..., min_length=1, max_length=1000)

class ResearchPlan(BaseModel):
    original_query: QueryString
    sub_questions: list[ResearchSubQuestion] = Field(..., min_length=1, max_length=20)
    mode: ResearchMode