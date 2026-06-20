# ============================================
# 第一阶段：构建 Vue 应用
# ============================================
FROM node:18-alpine AS build

# 设置工作目录
WORKDIR /app

# 复制 package 文件并安装依赖
COPY package*.json ./
RUN npm install

# 复制所有源码并构建
COPY . .
RUN npm run build

# ============================================
# 第二阶段：使用 Nginx 提供静态文件服务
# ============================================
FROM nginx:alpine

# 复制构建产物到 Nginx 静态文件目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
