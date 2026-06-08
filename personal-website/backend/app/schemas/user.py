from pydantic import BaseModel
from typing import Optional

class UserInfoResponse(BaseModel):
    id: int
    name: str
    title: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None
    class Config:
        from_attributes = True