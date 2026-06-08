from pydantic import BaseModel
from typing import Optional

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    tech_stack: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    highlights: Optional[str] = None
    sort_order: int
    class Config:
        from_attributes = True