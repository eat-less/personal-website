from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class Skill(Base):
    __tablename__ = "skill"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    level = Column(Integer, default=80)
    icon = Column(String(64))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())