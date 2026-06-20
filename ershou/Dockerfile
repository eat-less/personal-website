# 使用官方 Python 镜像作为基础镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 设置工作目录
WORKDIR /app

# 安装系统依赖（MySQL 客户端库、gcc 等）
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个 Django 项目到容器
COPY . /app/

# 收集静态文件
RUN python manage.py collectstatic --noinput || true

# 启动入口脚本
RUN chmod +x /app/entrypoint.sh

# 暴露端口
EXPOSE 8000

# 容器启动命令（使用 Gunicorn）
CMD ["sh", "/app/entrypoint.sh"]
