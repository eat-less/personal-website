from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.config import settings
from app.database import init_db, SessionLocal
from app.models.user_info import UserInfo
from app.models.skill import Skill
from app.models.project import Project
from app.routers import home, contact

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home.router)
app.include_router(contact.router)

@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    try:
        if db.query(UserInfo).count() > 0:
            db.query(UserInfo).delete()
            db.query(Skill).delete()
            db.query(Project).delete()
            db.commit()

        db.add(UserInfo(
            name="冯家宝",
            title="智能体应用开发工程师",
            bio="熟练掌握Python、Django、LangChain等核心技术，具备全栈开发能力和大模型应用开发经验。独立完成从需求分析到产品落地的全流程开发，擅长智能体(Agent)设计与RAG知识库系统搭建。",
            email="3498986894@qq.com",
            phone="13071766752",
            github="https://github.com/",
            location="上海"
        ))

        skills_data = [
            Skill(category="编程语言", name="Python", level=95, icon="python", sort_order=1),
            Skill(category="编程语言", name="SQL", level=88, icon="mysql", sort_order=2),
            Skill(category="后端框架", name="Django", level=90, icon="django", sort_order=3),
            Skill(category="后端框架", name="FastAPI", level=82, icon="fastapi", sort_order=4),
            Skill(category="前端技术", name="Vue.js", level=85, icon="vuejs", sort_order=5),
            Skill(category="前端技术", name="HTML/CSS/JS", level=80, icon="html5", sort_order=6),
            Skill(category="数据库", name="MySQL", level=90, icon="mysql", sort_order=7),
            Skill(category="数据库", name="Redis", level=78, icon="redis", sort_order=8),
            Skill(category="大模型/AI", name="LangChain", level=92, icon="langchain", sort_order=9),
            Skill(category="大模型/AI", name="Agent开发", level=90, icon="agent", sort_order=10),
            Skill(category="大模型/AI", name="RAG系统", level=88, icon="rag", sort_order=11),
            Skill(category="大模型/AI", name="Coze工作流", level=85, icon="coze", sort_order=12),
            Skill(category="工具/运维", name="Docker", level=82, icon="docker", sort_order=13),
            Skill(category="工具/运维", name="Git", level=88, icon="git", sort_order=14),
            Skill(category="工具/运维", name="RabbitMQ/Kafka", level=75, icon="mq", sort_order=15),
        ]
        for s in skills_data:
            db.add(s)

        projects_data = [
            Project(
                name="直播间AI智能助手",
                description="以大模型技术为核心，聚焦护肤直播电商行业弹幕处理效率低、用户响应延迟高的痛点，搭建实时弹幕问答AI智能助手系统，实现弹幕智能理解与精准回复。",
                tech_stack='["Python","LangChain","BERT","DeepSeek-V3","BGE-M3","Milvus","Chroma","RabbitMQ","Kafka","Docker","MySQL","Redis","SSE"]',
                github_url="https://github.com/",
                demo_url="",
                highlights='["意图识别准确率93%","P90延迟<3秒","AI自动回复率>65%","年省客服成本约80万元","支撑5万条/分钟弹幕峰值","LLM调用成本每场15-25元"]',
                sort_order=1
            ),
            Project(
                name="智慧农业AI大模型数字云平台",
                description="以AI大模型与数字云平台为核心，构建精准水肥药一体化智能决策管理平台，实现农业生产全流程闭环管理，破解传统设施农业粗放管理、数据缺失等痛点。",
                tech_stack='["Python","Django","MySQL","LangChain","LlamaIndex","Vue3","DeepSeek-V3"]',
                github_url="https://github.com/",
                demo_url="",
                highlights='["AI自动生成灌溉施肥方案","预计节水30%以上","节肥25%以上","可视化方案展示与管理系统","数据全流程闭环管理"]',
                sort_order=2
            ),
            Project(
                name="众创内容生态平台",
                description="以Django+Vue3为技术核心，为创作者提供内容发布、互动打赏、内容投资和任务接单的一体化线上平台，通过完善的作品管理功能提升用户参与度与内容流转效率。",
                tech_stack='["Python","Django","MySQL","Vue3","RESTful API","Redis","推荐算法","Git"]',
                github_url="https://github.com/",
                demo_url="",
                highlights='["作品曝光量提升45%","用户互动率提升38%","bug修复率98%以上","Redis缓存优化查询响应速度","沉淀标准化开发流程文档"]',
                sort_order=3
            ),
        ]
        for p in projects_data:
            db.add(p)

        db.commit()
        print("Seed data inserted successfully")
    finally:
        db.close()

frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

@app.get("/api/health")
def health():
    return {"status": "ok"}