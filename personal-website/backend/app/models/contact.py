from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base

class ContactMessage(Base):
    __tablename__ = "contact_message"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    email = Column(String(128), nullable=False)
    subject = Column(String(256))
    content = Column(Text, nullable=False)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())