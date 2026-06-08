from pydantic import BaseModel
from typing import Optional

class ContactCreate(BaseModel):
    name: str
    email: str
    subject: Optional[str] = None
    content: str

class ContactResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: Optional[str] = None
    content: str
    is_read: int
    created_at: str
    class Config:
        from_attributes = True