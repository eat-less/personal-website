from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='学号')
    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    bio = models.TextField(blank=True, verbose_name='简介')
    grade = models.CharField(max_length=20, blank=True, verbose_name='年级')
    address = models.CharField(max_length=200, blank=True, verbose_name='地址')
    reputation = models.IntegerField(default=100, verbose_name='信誉分')
    completed_transactions = models.IntegerField(default=0, verbose_name='成交数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return self.user.username

class EmailVerificationCode(models.Model):
    """邮箱验证码"""
    email = models.EmailField(verbose_name='邮箱')
    code = models.CharField(max_length=6, verbose_name='验证码')
    code_type = models.CharField(max_length=20, verbose_name='验证码类型', choices=(
        ('register', '注册'),
        ('reset_password', '重置密码'),
    ))
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    
    class Meta:
        verbose_name = '邮箱验证码'
        verbose_name_plural = '邮箱验证码'
    
    def __str__(self):
        return f'{self.email} - {self.code} ({self.code_type})'
    
    def is_expired(self):
        return timezone.now() > self.expires_at
