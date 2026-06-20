# Docker Django+Vue 部署技能

## 适用场景

本地用 Docker Compose 部署 Django + Vue + MySQL 项目（校园二手交易平台等类似架构）。

## 前置条件

- Docker Desktop 已安装
- 项目包含 docker-compose.yml、后端 Dockerfile、前端 Dockerfile（Vue Nginx 多阶段构建）

## 部署步骤

### 1. 配置 Docker 镜像加速

中国网络需配置镜像源。Docker Desktop → Settings → Docker Engine，加入：

```json
"registry-mirrors": ["https://docker.1ms.run", "https://docker.xuanyuan.me"]
```

Apply & restart 后生效。

### 2. 准备 .env 文件

```cmd
copy .env.example .env
```

编辑 .env，确保：
- `DB_USER` 不是 `root`（MySQL 8.0 不允许 MYSQL_USER=root）
- `DB_PASSWORD` 与 docker-compose.yml 中 MYSQL_ROOT_PASSWORD 一致
- 邮箱配置填入真实 QQ 邮箱和授权码

### 3. 端口冲突处理

如果本机已有 MySQL 占 3306，修改 docker-compose.yml：
```yaml
ports:
  - "3307:3306"
```

### 4. Node 版本兼容

Vite 7 需要 Node 20+，前端 Dockerfile 必须用：
```dockerfile
FROM node:22-alpine AS build
```

### 5. 构建与启动

```cmd
docker compose down -v
docker compose up -d --build
```

`-v` 首次部署或修改密码后必须用，清掉旧数据卷让 MySQL 重新初始化。

### 6. 验证

```cmd
docker compose ps
```

三个容器 `campus-mysql`、`campus-backend`、`campus-frontend` 均为 running 即可。

- 前端：http://localhost
- Django Admin：http://localhost/admin/
- 默认管理员：admin / admin123456

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `MYSQL_USER="root"` 报错 | MySQL 8.0 不允许普通用户叫 root | .env 中 DB_USER 改非 root |
| `crypto.hash is not a function` | Node 18 不兼容 Vite 7 | 前端 Dockerfile 用 node:22-alpine |
| `Access denied for user 'root'` | .env 密码与 MYSQL_ROOT_PASSWORD 不一致 | 统一为 root123 或一致值 |
| `ports are not available` 3306 | 本机 MySQL 占用 | 改端口映射 3307:3306 |
| 验证码收不到 | .env 邮箱是占位符 | 填真实 QQ 邮箱+授权码 |
| 镜像拉取超时 | Docker Hub 被墙 | 配置国内镜像源 |
| 数据库连接超时 30/30 | MySQL healthcheck 失败 | 密码不一致或 DB_USER=root |

## 分享镜像

给别人用不需要源码，推送镜像到 Docker Hub：

```cmd
docker login
docker tag biyesheji-backend 你的用户名/campus-backend:latest
docker tag biyesheji-frontend 你的用户名/campus-frontend:latest
docker push 你的用户名/campus-backend:latest
docker push 你的用户名/campus-frontend:latest
```

接收方只需 docker-compose.yml（用 image 替代 build）+ .env，执行 `docker compose up -d` 即可。

## 注意事项

- .env 中的 QQ 授权码不要提交 Git 或分享
- 容器重启不会丢数据（mysql_data 卷持久化）
- 邮箱 `fail_silently=True` 会吞错误，建议改为 `fail_silently=False` 便于调试
- settings.py 中不要硬编码真实邮箱凭据作为默认值
