from pydantic import BaseModel
from typing import Optional

class SkillResponse(BaseModel):
    id: int
    category: str
    name: str
    level: int
    icon: Optional[str] = None
    sort_order: int
    class Config:
        from_attributes = True