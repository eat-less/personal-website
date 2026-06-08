from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base

class UserInfo(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    title = Column(String(128))
    avatar_url = Column(String(512))
    bio = Column(Text)
    email = Column(String(128))
    phone = Column(String(32))
    github = Column(String(256))
    linkedin = Column(String(256))
    location = Column(String(128))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())