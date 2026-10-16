from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class SourceType(str, Enum):
    WEB = "web"
    ACADEMIC = "academic"
    DOCUMENT = "document"

class ResearchSource(BaseModel):
    source_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    url: HttpUrl | None = None
    source_type: SourceType
    publisher: str | None = None
    authors: list[str] = Field(default_factory=list)
    published_at: datetime | None = None
    content: str | None = None