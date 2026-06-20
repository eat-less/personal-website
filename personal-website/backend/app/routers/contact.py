from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactCreate, ContactResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

router = APIRouter(prefix="/api", tags=["Contact"])

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
TO_EMAIL = "3498986894@qq.com"

def send_email_notification(name: str, sender_email: str, subject: str, content: str):
    """给管理员发送邮件通知"""
    if not SMTP_USER or not SMTP_PASS:
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = TO_EMAIL
        msg["Subject"] = f"[个人网站] 来自 {name} 的新留言"
        body = f"""访客姓名: {name}
访客邮箱: {sender_email}
主题: {subject or "无"}
内容:
{content}
"""
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

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

    # 尝试发送邮件通知（不阻塞接口）
    send_email_notification(msg.name, msg.email, msg.subject, msg.content)

    return ContactResponse(
        id=record.id,
        name=record.name,
        email=record.email,
        subject=record.subject,
        content=record.content,
        is_read=record.is_read,
        created_at=record.created_at.strftime("%Y-%m-%d %H:%M:%S")
    )
