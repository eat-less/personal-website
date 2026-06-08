from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base

class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    cover_url = Column(String(512))
    tech_stack = Column(String(256))
    github_url = Column(String(256))
    demo_url = Column(String(256))
    highlights = Column(Text)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())