from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    SendVerificationCodeView,
    PasswordResetView,
    UserProfileView,
    RefreshTokenView,
    UserInfoView,
    AdminUserManagementView,
    AdminUserDetailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('send-verification-code/', SendVerificationCodeView.as_view(), name='send_verification_code'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh_token'),
    path('user-info/<int:user_id>/', UserInfoView.as_view(), name='user_info'),
    # 管理员用户管理
    path('admin/users/', AdminUserManagementView.as_view(), name='admin_user_management'),
    path('admin/users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
]
