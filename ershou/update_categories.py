#!/usr/bin/env python
"""更新分类名称为中文"""

import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ershou.settings')
django.setup()

from app.models import Category

# 更新现有分类名称
Category.objects.filter(name='books').update(name='图书教材')
Category.objects.filter(name='electronics').update(name='电子产品')
Category.objects.filter(name='sports').update(name='运动户外')
Category.objects.filter(name='clothing').update(name='服饰鞋包')
Category.objects.filter(name='other').update(name='其他')

# 添加新分类
new_categories = ['时尚首饰', '零食饮料', '美妆护肤', '家居日用', '卡包劵包']
for category_name in new_categories:
    Category.objects.get_or_create(name=category_name)

# 验证更新结果
print('更新后的分类列表:')
for category in Category.objects.all():
    print(f'ID: {category.id}, Name: {category.name}')

print('分类更新完成！')
