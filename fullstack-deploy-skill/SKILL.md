---
name: fullstack-deploy
description: >
  Deploy Vue3 + FastAPI full-stack projects to Render and Vercel, including:
  (1) Pre-deployment checklist: rewrite main.py seed data encoding, upgrade requirements.txt for Python 3.14 compatibility, exclude "dist/" from .gitignore for static file upload
  (2) Render Web Service configuration (rootDir, startCommand, env vars) and troubleshooting build/deploy failures (Rust compile, pydantic-core, 404 static mount)
  (3) Vercel SPA rewrites for hash/history mode routing
  (4) SSH Git push fixes for Chinese Windows usernames (GIT_SSH_COMMAND workaround)
  (5) Resource links for official docs and common error patterns
  Use when deploying Python+Vue SPA projects to cloud platforms.
---

# Fullstack Deploy Fixes

> 经验总结: Vue3 + FastAPI + SQLite 全栈项目部署到 Render/Vercel 的完整踩坑修复记录。

本技能记录了一个 `personal-website` 全栈项目从本地到外网部署的**完整过程、所有踩过的坑以及精准的修复方案**。当遇到类似的 SPA 全栈项目部署任务时，遵循下面的检查清单和故障排除表。

---

## 1. Pre-Deployment Checklist

### 1.1 后端 main.py 种子数据

- [ ] **检查中文编码** — `main.py` 中的中文文本必须可读。如果看到乱码（如 `鍐瀹?`），立即重写整个文件
- [ ] **添加 dist 路径调试日志** — 在静态文件挂载前后添加 `logging.info`，否则 Render 上无法确认 dist 是否被正确发现
```python
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "frontend", "dist")
logger.info(f"frontend_dist = {frontend_dist}")
logger.info(f"frontend_dist exists = {os.path.isdir(frontend_dist)}")
```

### 1.2 requirements.txt 兼容性

- [ ] **版本不能锁死** — Render 默认 Python 3.14，旧版 `pydantic==2.5.2`（依赖 `pydantic-core==2.14.5`）需要 Rust 编译且会因 `/usr/local/cargo` 只读而失败
- [ ] **使用范围版本**
```text
fastapi>=0.115.0,<1.0.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.30
pydantic>=2.9.0
pydantic-settings>=2.5.0
python-multipart>=0.0.9
```

### 1.3 .gitignore

- [ ] **前端构建产物必须上传** — 如果 `.gitignore` 包含 `dist/`（全局），前端的 `frontend/dist/` 会被 Git 排除，Render 拉不到静态文件
- [ ] **Fix:** 将 `dist/` 行改为 `frontend/dist/` 或直接移除全局 `dist/` 规则

### 1.4 render.yaml 配置

```yaml
services:
  - type: web
    name: personal-website
    runtime: python
    rootDir: personal-website          # 必须精确到子项目根目录
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DB_TYPE
        value: sqlite
```

> 注意: Render Dashboard 手动设置会**覆盖** `render.yaml`，部署前确认 Dashboard 设置一致。

### 1.5 vercel.json（如部署到 Vercel）

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

## 2. Common Error Patterns & Fixes

| 错误日志 | 根因 | 修复 |
|----------|------|------|
| `ERROR: Could not open requirements file: backend/requirements.txt` | rootDir 未配置或路径错误 | 添加 `rootDir: personal-website/backend` 或将 Build Command 改为相对路径 |
| `Could not resolve vite.config.js` / `Cannot read directory` | `vite.config.js` 中 `fs.allow` 含无效绝对路径（中文乱码） | 移除 `fs.allow` 行，只保留必备配置 |
| `pydantic-core-2.14.5.tar.gz` 编译失败 / `Cargo metadata failed` / `Read-only file system` | Python 3.14 + 旧版 pydantic 需要 Rust 编译 Cargo 依赖，但 Render 文件系统只读 | 升级 requirements.txt 到 >=2.9.0 |
| `Seed data inserted successfully` + `404 Not Found`（GET /） | `dist/` 未上传或路径推导失败 | 检查 `.gitignore` 中 `dist/` 排除规则；加调试日志确认 `os.path.isdir(frontend_dist)` |
| `Unable to access` / `Could not connect to server` | HTTPS 被墙或 Git 端口被屏蔽 | 改用 SSH: `git remote set-url origin git@github.com:eat-less/personal-website.git` |
| `Permission denied (publickey)` | SSH Key 未配置或路径编码异常 | 生成 Key → 加到 GitHub → 设置 `$env:GIT_SSH_COMMAND` |
| `Identity file ... not accessible` / `\267\353\274\322\261\246` | Windows 中文用户名导致 Git 内部 SSH 路径编码错误 | 用正斜杠: `$env:GIT_SSH_COMMAND = "ssh -i C:/Users/xxx/.ssh/id_ed25519 -o IdentitiesOnly=yes"` |

---

## 3. SSH Git Push for Chinese Windows Users

关键变通——`ssh test` 成功但 `git push` 失败时：

```powershell
$env:GIT_SSH_COMMAND = "ssh -i C:/Users/冯家宝/.ssh/id_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=no"
$env:HOME = "C:/Users/冯家宝"
git push origin main
```

**原理:** 中文用户名 `冯家宝` 在 Git 内部被转码为 `\267\353\274\322\261\246`，无法找到 `.ssh/`。设置 `$env:GIT_SSH_COMMAND` 让 Git 使用系统的 OpenSSH，绕过这个 bug。

---

## 4. Render 部署调试流程

1. 看 Build 日志 — 构建失败先看依赖是否兼容 Python 3.14
2. 看 Deploy 日志 — 应用启动后看 `Uvicorn running on` 和 `Seed data inserted` 等标记
3. 检查 `frontend_dist exists = True/False` — 没有这个日志说明 `main.py` 还没更新
4. 访问 `https://你的服务.onrender.com/docs` — 如果能打开 API 文档，说明后端运行正常，前端的 `dist/` 没挂上
5. 访问 `https://你的服务.onrender.com/api/health` — 返回 `{"status":"ok"}` 证实后端无误

---

## 5. 最终验证链接

- Render: `https://personal-website-gl99.onrender.com`
- API Docs: `https://personal-website-gl99.onrender.com/docs`
- Health: `https://personal-website-gl99.onrender.com/api/health`
