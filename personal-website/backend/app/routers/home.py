from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_info import UserInfo
from app.models.skill import Skill
from app.models.project import Project
from app.schemas.home import HomeResponse

router = APIRouter(prefix="/api", tags=["Home"])

@router.get("/home", response_model=HomeResponse)
def get_home(db: Session = Depends(get_db)):
    user = db.query(UserInfo).first()
    skills = db.query(Skill).order_by(Skill.sort_order).all()
    projects = db.query(Project).order_by(Project.sort_order).all()
    return HomeResponse(user=user, skills=skills, projects=projects)