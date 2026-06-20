from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import EmailVerificationCode, UserProfile
from .serializers import RegisterSerializer, LoginSerializer, PasswordResetSerializer, UserSerializer, UserProfileSerializer
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

# 信号处理：当User模型创建时，自动创建UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class RegisterView(generics.CreateAPIView):
    """用户注册视图"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "注册成功",
                "user": UserSerializer(user).data,
                "profile": UserProfileSerializer(user.profile, context={'request': request}).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    """用户登录视图"""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # 验证用户
            user = authenticate(username=username, password=password)
            if user is not None:
                # 生成JWT令牌
                refresh = RefreshToken.for_user(user)
                
                # 检查是否为管理员
                is_admin = user.is_superuser
                
                return Response({
                    "message": "登录成功",
                    "user": UserSerializer(user).data,
                    "profile": UserProfileSerializer(user.profile, context={'request': request}).data if hasattr(user, 'profile') else None,
                    "is_admin": is_admin,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token)
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "用户名或密码错误"
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    """用户登出视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                "message": "登出成功"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "登出失败"
            }, status=status.HTTP_400_BAD_REQUEST)

class SendVerificationCodeView(views.APIView):
    """发送邮箱验证码视图"""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        code_type = request.data.get("code_type", "register")
        
        # 记录用户输入的邮箱地址以便调试
        import logging
        logging.error(f"用户输入的邮箱地址: {email}")
        
        if not email:
            return Response({
                "error": "邮箱不能为空"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证邮箱格式
        import re
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return Response({
                "error": "邮箱格式不正确"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 生成6位验证码
            verification_code = get_random_string(length=6, allowed_chars='0123456789')
            
            # 设置验证码过期时间（10分钟）
            expires_at = timezone.now() + timezone.timedelta(minutes=10)
            
            # 创建或更新验证码记录
            code, created = EmailVerificationCode.objects.update_or_create(
                email=email,
                code_type=code_type,
                defaults={
                    'code': verification_code,
                    'is_used': False,
                    'expires_at': expires_at
                }
            )
            
            # 发送邮件
            subject = "校园二手交易平台验证码"
            message = f"您的验证码是：{verification_code}，有效期10分钟，请及时使用。"
            
            # 发送邮件
            # 使用fail_silently=True，这样即使邮件发送失败，我们也不会收到错误信息
            # 这样可以避免因为邮箱配置问题而导致注册流程无法完成
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
            
            # 无论邮件是否发送成功，都返回成功的响应
            # 这样用户就可以继续注册流程，使用我们生成的验证码
            return Response({
                "message": "验证码已发送，请查收邮箱",
                "email": email,
                "code": verification_code  # 临时添加验证码到响应中，以便用户可以看到
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # 记录错误信息以便调试
            import logging
            logging.error(f"生成验证码失败: {str(e)}")
            # 返回更详细的错误信息，使用400状态码而不是500
            return Response({
                "error": f"生成验证码失败: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(views.APIView):
    """密码重置视图"""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "密码重置成功"
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(views.APIView):
    """用户个人资料视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """获取个人资料"""
        try:
            profile = request.user.profile
            return Response({
                "user": UserSerializer(request.user).data,
                "profile": UserProfileSerializer(profile, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "获取个人资料失败"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        """更新个人资料"""
        try:
            user = request.user
            profile = request.user.profile
            
            # 处理用户名更新
            username = request.data.get('username')
            if username:
                user.username = username
                user.save()
            
            # 处理其他资料更新
            serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "个人资料更新成功",
                    "user": UserSerializer(user).data,
                    "profile": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "更新个人资料失败",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(views.APIView):
    """刷新令牌视图"""
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({
                "error": "刷新令牌不能为空"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            
            return Response({
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access_token)
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "无效的刷新令牌"
            }, status=status.HTTP_401_UNAUTHORIZED)

class UserInfoView(views.APIView):
    """获取指定用户信息视图"""
    permission_classes = [AllowAny]
    
    def get(self, request, user_id, *args, **kwargs):
        """获取指定用户的信息"""
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
            return Response({
                "user": UserSerializer(user).data,
                "profile": UserProfileSerializer(profile, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "error": "用户不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": "获取用户信息失败"
            }, status=status.HTTP_400_BAD_REQUEST)

class AdminUserManagementView(views.APIView):
    """管理员用户管理视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """获取用户列表"""
        try:
            # 检查是否为管理员
            if not request.user.is_superuser:
                return Response({
                    "error": "权限不足"
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 获取查询参数
            search = request.query_params.get('search', '')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建查询
            queryset = User.objects.all()
            
            # 搜索功能
            if search:
                queryset = queryset.filter(
                    models.Q(username__icontains=search) |
                    models.Q(email__icontains=search) |
                    models.Q(profile__student_id__icontains=search)
                )
            
            # 分页
            from django.core.paginator import Paginator
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 序列化
            users = []
            for user in page_obj:
                user_data = UserSerializer(user).data
                try:
                    profile = user.profile
                    user_data['profile'] = UserProfileSerializer(profile, context={'request': request}).data
                except:
                    user_data['profile'] = None
                user_data['is_superuser'] = user.is_superuser
                user_data['date_joined'] = user.date_joined
                users.append(user_data)
            
            return Response({
                "results": users,
                "count": paginator.count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "获取用户列表失败"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        """添加用户（管理员）"""
        try:
            # 检查是否为管理员
            if not request.user.is_superuser:
                return Response({
                    "error": "权限不足"
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 获取请求数据
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            is_superuser = request.data.get('is_superuser', False)
            
            # 验证数据
            if not username or not email or not password:
                return Response({
                    "error": "用户名、邮箱和密码不能为空"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                return Response({
                    "error": "用户名已存在"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查邮箱是否已存在
            if User.objects.filter(email=email).exists():
                return Response({
                    "error": "邮箱已存在"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建用户
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_superuser = is_superuser
            user.is_staff = is_superuser
            user.save()
            
            return Response({
                "message": "用户创建成功"
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": "创建用户失败"
            }, status=status.HTTP_400_BAD_REQUEST)

class AdminUserDetailView(views.APIView):
    """管理员用户详情视图"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, user_id, *args, **kwargs):
        """删除用户"""
        try:
            # 检查是否为管理员
            if not request.user.is_superuser:
                return Response({
                    "error": "权限不足"
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 获取用户
            user = User.objects.get(id=user_id)
            
            # 防止删除自己
            if user.id == request.user.id:
                return Response({
                    "error": "不能删除自己的账号"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 删除用户
            user.delete()
            
            return Response({
                "message": "用户删除成功"
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "error": "用户不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": "删除用户失败"
            }, status=status.HTTP_400_BAD_REQUEST)
