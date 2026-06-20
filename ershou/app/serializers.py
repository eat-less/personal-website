from rest_framework import serializers
from .models import Product, Category, ProductImage, Comment

class CategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductImageSerializer(serializers.ModelSerializer):
    """商品图片序列化器"""
    image = serializers.ImageField(use_url=True)
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    """商品序列化器"""
    category = CategorySerializer()
    images = ProductImageSerializer(many=True, read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    seller_avatar = serializers.SerializerMethodField()
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'quantity', 'allow_delivery',
            'status', 'views', 'likes_count', 'favorites_count', 'created_at',
            'updated_at', 'category', 'seller_id', 'seller_username', 'seller_avatar', 'images'
        ]
        read_only_fields = ['id', 'views', 'likes_count', 'favorites_count', 'created_at', 'updated_at']
    
    def get_seller_avatar(self, obj):
        """获取卖家头像"""
        request = self.context.get('request')
        if obj.seller.profile and obj.seller.profile.avatar:
            return request.build_absolute_uri(obj.seller.profile.avatar.url)
        return None

class CommentSerializer(serializers.ModelSerializer):
    """评价序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=True, required=False)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'user_username', 'user_avatar', 'product', 'order',
            'content', 'rating', 'image', 'reply_to', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def get_user_avatar(self, obj):
        """获取用户头像"""
        request = self.context.get('request')
        if obj.user.profile and obj.user.profile.avatar:
            return request.build_absolute_uri(obj.user.profile.avatar.url)
        return None
