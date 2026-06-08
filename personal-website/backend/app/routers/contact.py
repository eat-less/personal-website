from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactCreate, ContactResponse

router = APIRouter(prefix="/api", tags=["Contact"])

@router.post("/contact", response_model=ContactResponse)
def submit_contact(msg: ContactCreate, db: Session = Depends(get_db)):
    record = ContactMessage(
        name=msg.name,
        email=msg.email,
        subject=msg.subject,
        content=msg.content
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return ContactResponse(
        id=record.id,
        name=record.name,
        email=record.email,
        subject=record.subject,
        content=record.content,
        is_read=record.is_read,
        created_at=record.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )