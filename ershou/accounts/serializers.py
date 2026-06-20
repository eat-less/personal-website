from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, EmailVerificationCode
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    """用户扩展信息序列化器"""
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['student_id', 'nickname', 'avatar', 'bio', 'grade', 'address', 'reputation', 'completed_transactions']
    
    def get_avatar(self, obj):
        """获取头像绝对URL"""
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None

class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    student_id = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'student_id', 'verification_code']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "密码不匹配"})
        
        # 验证学号不为空
        if not attrs['student_id']:
            raise serializers.ValidationError({"student_id": "学号不能为空"})
        
        # 验证验证码
        try:
            code = EmailVerificationCode.objects.get(
                email=attrs['email'],
                code=attrs['verification_code'],
                code_type='register',
                is_used=False
            )
            if code.is_expired():
                raise serializers.ValidationError({"verification_code": "验证码已过期"})
        except EmailVerificationCode.DoesNotExist:
            raise serializers.ValidationError({"verification_code": "验证码无效"})
        
        # 验证学号唯一性
        if UserProfile.objects.filter(student_id=attrs['student_id']).exists():
            raise serializers.ValidationError({"student_id": "该学号已注册"})
        
        # 验证邮箱唯一性
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "该邮箱已注册"})
        
        return attrs
    
    def create(self, validated_data):
        # 提取学号，避免在create_user中传递
        student_id = validated_data.pop('student_id')
        verification_code = validated_data.pop('verification_code')
        
        # 创建用户，使用create_user方法自动处理密码哈希
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # 显式保存用户
        user.save()
        
        # 确保用户扩展信息被创建，使用明确的赋值
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.student_id = student_id
        profile.save()
        
        # 标记验证码为已使用
        # 由于我们暂时禁用了验证码验证，所以这个操作可能会失败
        # 因此，我们需要添加异常处理
        try:
            code = EmailVerificationCode.objects.get(
                email=user.email,
                code=verification_code,
                code_type='register'
            )
            code.is_used = True
            code.save()
        except EmailVerificationCode.DoesNotExist:
            # 如果验证码不存在，忽略这个错误
            pass
        
        return user

class LoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class PasswordResetSerializer(serializers.Serializer):
    """密码重置序列化器"""
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "密码不匹配"})
        
        # 验证验证码
        try:
            code = EmailVerificationCode.objects.get(
                email=attrs['email'],
                code=attrs['verification_code'],
                code_type='reset_password',
                is_used=False
            )
            if code.is_expired():
                raise serializers.ValidationError({"verification_code": "验证码已过期"})
        except EmailVerificationCode.DoesNotExist:
            raise serializers.ValidationError({"verification_code": "验证码无效"})
        
        # 验证用户是否存在
        if not User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "该邮箱未注册"})
        
        return attrs
    
    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        verification_code = self.validated_data['verification_code']
        
        # 更新用户密码
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        
        # 标记验证码为已使用
        code = EmailVerificationCode.objects.get(
            email=email,
            code=verification_code,
            code_type='reset_password'
        )
        code.is_used = True
        code.save()
        
        return user

class EmailVerificationCodeSerializer(serializers.ModelSerializer):
    """邮箱验证码序列化器"""
    class Meta:
        model = EmailVerificationCode
        fields = ['email', 'code_type']
