# 冯家宝 - 个人介绍网站

> 智能体应用开发工程师 | Python · Django · FastAPI · Vue3 · LangChain

在线访问：**[https://personal-website-gl99.onrender.com](https://personal-website-gl99.onrender.com)**

---

## 项目简介

个人简历与作品展示网站，使用 **Vue3 + Element Plus** 构建前端，**FastAPI + SQLAlchemy** 作为后端，默认使用 SQLite 数据库（无需额外配置），支持一键 Docker 部署或部署到 Render 等云平台。

## 项目结构

```
personal-website/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py             # 入口文件（含种子数据）
│   │   ├── config.py           # 配置（DB_TYPE 可切换 SQLite/MySQL）
│   │   ├── database.py         # 数据库连接
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic Schema
│   │   └── routers/            # API 路由（home + contact）
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Vue3 + Vite 前端
│   ├── src/
│   │   ├── views/Home.vue      # 主页面（含所有板块）
│   │   ├── api/index.js        # API 封装
│   │   └── router/index.js     # 路由（Hash 模式）
│   ├── dist/                   # 构建产物（Git 已上传）
│   ├── package.json
│   └── Dockerfile
├── sql/init.sql                # MySQL 初始化脚本
├── render.yaml                 # Render 部署配置
├── vercel.json                 # Vercel SPA 路由规则
└── docker-compose.yml          # Docker Compose 一键部署
```

## 快速开始

### 本地运行

**后端**（一个终端）：
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> 首次启动会自动创建 SQLite 数据库并写入种子数据。
> API 文档：http://localhost:8000/docs

**前端**（另一个终端）：
```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000（Vite 自动代理 /api 到 8000 端口）。

### 或直接访问后端端口

前端 `dist/` 已配置在 FastAPI 中作为静态文件挂载，启动后端后直接访问 **http://localhost:8000** 即可：

```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# 浏览器打开 http://localhost:8000
```

## Docker Compose 一键部署

```bash
docker-compose up -d
```

启动三个服务：MySQL(3307) + 后端(8000) + 前端(80)。

## 部署到 Render（当前线上环境）

1. 在 [Render](https://render.com) 创建 Web Service，关联 GitHub 仓库
2. 配置：
   - **Root Directory**: `personal-website`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Env Variable**: `DB_TYPE = sqlite`
3. 部署后自动生成线上 URL

## 联系表单邮件通知

提交留言时会自动发送邮件到 **3498986894@qq.com**。需配置环境变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `SMTP_HOST` | SMTP 服务器 | smtp.qq.com |
| `SMTP_PORT` | SMTP 端口 | 587 |
| `SMTP_USER` | 邮箱账号 | 你的 QQ 邮箱 |
| `SMTP_PASS` | 邮箱授权码 | QQ 邮箱设置 → 账户 → 生成授权码 |

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/home | 获取首页所有数据（个人信息 + 技能 + 项目） |
| POST | /api/contact | 提交联系留言（自动发送邮件通知） |
| GET | /api/health | 健康检查 |

## 技能栈

- **前端**: Vue 3、Element Plus、Vite、Axios
- **后端**: Python、FastAPI、SQLAlchemy、Pydantic
- **数据库**: SQLite（开发）/ MySQL（生产）
- **部署**: Docker、Render、Vercel
- **AI**: LangChain、Agent 开发、RAG 系统

---

*由 [eat-less/personal-website](https://github.com/eat-less/personal-website) 自动构建部署*
