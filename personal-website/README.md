# 个人介绍网站

## 项目结构

```
personal-website/
├── sql/init.sql              # 数据库初始化脚本
├── backend/                   # Python FastAPI 后端
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # 入口文件
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic Schema
│   │   └── routers/           # API路由
│   └── ...
└── frontend/                  # Vue3 前端
    ├── src/
    │   ├── App.vue            # 主组件(含导航)
    │   ├── views/Home.vue     # 首页(含所有板块)
    │   ├── api/               # API封装
    │   └── router/            # 路由
    └── ...
```

## 本地运行

### 1. 数据库

安装 MySQL，执行 sql/init.sql：

```bash
mysql -u root -p < sql/init.sql
```

### 2. 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API文档：http://localhost:8000/docs

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:3000

## 部署上线

### 方案一：Docker Compose（推荐）

创建 docker-compose.yml：

```yaml
version: '3.8'
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: personal_website
    volumes:
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### 方案二：分开部署

**后端**部署到服务器（如阿里云/腾讯云）：

```bash
# 安装依赖
pip install -r backend/requirements.txt
# 使用 gunicorn 运行
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000
# 配合 nginx 反向代理
```

**前端**打包后部署到静态服务：

```bash
cd frontend
npm run build
# 将 dist/ 目录上传到服务器 nginx/html 目录
```

### 方案三：免费部署（推荐新手）

- **后端**：部署到 [Render](https://render.com) 或 [Railway](https://railway.app)（支持Python）
- **数据库**：使用 [PlanetScale](https://planetscale.com)（免费MySQL）或 [TiDB Cloud](https://tidbcloud.com)
- **前端**：部署到 [Vercel](https://vercel.com) 或 [Netlify](https://netlify.com)

### 数据库配置

部署时修改 backend/app/config.py 中的数据库连接信息，或通过环境变量覆盖：

```bash
export DB_HOST=你的数据库地址
export DB_PORT=3306
export DB_USER=你的用户名
export DB_PASSWORD=你的密码
export DB_NAME=personal_website
```

## API接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/home | 获取首页所有数据 |
| POST | /api/contact | 提交联系留言 |
