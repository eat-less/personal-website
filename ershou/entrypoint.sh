#!/bin/sh

# 等待 MySQL 数据库准备就绪
echo "等待数据库准备就绪..."
count=0
while [ $count -lt 30 ]; do
    if mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT 1;" > /dev/null 2>&1; then
        echo "数据库连接成功！"
        break
    fi
    echo "数据库未就绪，等待 2 秒后重试... ($((count+1))/30)"
    sleep 2
    count=$((count + 1))
done

if [ $count -eq 30 ]; then
    echo "警告：数据库连接超时，仍尝试继续..."
fi

# 执行数据库迁移
echo "执行数据库迁移..."
python manage.py makemigrations accounts app --noinput 2>&1 || true
python manage.py migrate --noinput

# 创建 media 目录
mkdir -p /app/media/avatars /app/media/products /app/media/comments

# 检查是否有超级用户，没有则创建（可选）
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ershou.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print('已创建默认管理员: admin / admin123456')
else:
    print('管理员已存在')
" 2>&1

# 启动 Gunicorn（多进程）
echo "启动 Gunicorn 服务器，监听 0.0.0.0:8000..."
exec gunicorn ershou.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
