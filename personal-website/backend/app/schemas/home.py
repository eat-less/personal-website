from pydantic import BaseModel
from typing import List, Optional
from app.schemas.user import UserInfoResponse
from app.schemas.skill import SkillResponse
from app.schemas.project import ProjectResponse

class HomeResponse(BaseModel):
    user: Optional[UserInfoResponse] = None
    skills: List[SkillResponse] = []
    projects: List[ProjectResponse] = []