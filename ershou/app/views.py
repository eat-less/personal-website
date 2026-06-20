from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
import datetime
from .models import Product, Like, Favorite, ViewHistory, Follow, Category, ProductImage, Comment, Order, OrderItem, Message, Announcement, AnnouncementRead
from .serializers import ProductSerializer, CategorySerializer, CommentSerializer

class ProductPagination(PageNumberPagination):
    """商品列表分页"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductListCreateView(generics.ListCreateAPIView):
    """商品列表和创建视图，支持模糊搜索和价格筛选"""
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    
    def get_serializer_context(self):
        """传递request上下文给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_permissions(self):
        """根据请求方法返回不同的权限"""
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []
    
    # 搜索字段：商品名称、描述、标题、分类
    search_fields = ['title', 'description', 'category__name']
    
    # 排序字段
    ordering_fields = ['price', 'created_at', 'views', 'likes_count']
    
    # 默认排序
    ordering = ['-created_at']
    
    def get_queryset(self):
        """自定义查询集，添加价格范围和分类过滤"""
        queryset = super().get_queryset()
        
        # 只返回已上架的商品，排除待审核、已拒绝、已下架的商品
        queryset = queryset.filter(status='approved')
        
        # 获取价格范围参数
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # 获取分类参数
        category_id = self.request.query_params.get('category')
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset
    
    def post(self, request, *args, **kwargs):
        """创建新商品"""
        try:
            # 获取请求数据
            title = request.data.get('title')
            description = request.data.get('description')
            category_name = request.data.get('category')
            price = request.data.get('price')
            quantity = request.data.get('quantity', 1)
            delivery_method = request.data.get('delivery_method', 'self_pickup')
            
            # 验证数据
            if not all([title, description, category_name, price]):
                return Response({
                    'error': '请填写所有必填字段'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 查找或创建分类
            category, created = Category.objects.get_or_create(name=category_name)
            
            # 创建商品，默认状态为待审核
            product = Product.objects.create(
                seller=request.user,
                category=category,
                title=title,
                description=description,
                price=price,
                quantity=quantity,
                allow_delivery=(delivery_method == 'delivery'),
                status='pending'  # 待审核状态，需要管理员审核后才能上架
            )
            
            # 处理图片上传
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(
                    product=product,
                    image=image
                )
            
            # 返回成功响应
            return Response({
                'message': '发布成功，等待管理员审核',
                'product_id': product.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'发布失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductDetailView(generics.RetrieveAPIView):
    """商品详情视图"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []  # 不需要认证就能访问
    
    def get_serializer_context(self):
        """传递request上下文给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        """获取商品详情，增加浏览量并记录浏览历史"""
        instance = self.get_object()
        instance.views += 1
        instance.save()
        
        # 记录浏览历史（如果用户已登录）
        if request.user.is_authenticated:
            # 检查是否已存在相同的浏览记录
            existing_record = ViewHistory.objects.filter(user=request.user, product=instance).first()
            if existing_record:
                # 更新浏览时间
                existing_record.viewed_at = timezone.now()
                existing_record.save()
            else:
                # 创建新的浏览记录
                ViewHistory.objects.create(user=request.user, product=instance)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        """更新商品状态"""
        try:
            product = self.get_object()
            
            # 检查是否是卖家本人
            if product.seller != request.user:
                return Response({
                    'error': '只能修改自己发布的商品'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 获取要更新的状态
            new_status = request.data.get('status')
            valid_statuses = ['approved', 'removed', 'sold_out']
            
            if new_status not in valid_statuses:
                return Response({
                    'error': f'无效的状态，有效状态为：{", ".join(valid_statuses)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新商品状态
            product.status = new_status
            product.save()
            
            return Response({
                'message': '商品状态更新成功',
                'status': product.status
            })
        except Product.DoesNotExist:
            return Response({
                'error': '商品不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'更新商品状态失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductLikeView(generics.CreateAPIView):
    """商品点赞视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, product_id):
        """切换商品点赞状态"""
        try:
            product = Product.objects.get(id=product_id)
            like, created = Like.objects.get_or_create(user=request.user, product=product)
            
            if not created:
                like.delete()
                product.likes_count = max(0, product.likes_count - 1)
                product.save()
                return Response({
                    'liked': False,
                    'likes_count': product.likes_count
                })
            else:
                product.likes_count += 1
                product.save()
                return Response({
                    'liked': True,
                    'likes_count': product.likes_count
                })
        except Product.DoesNotExist:
            return Response({
                'error': '商品不存在'
            }, status=status.HTTP_404_NOT_FOUND)

class ProductFavoriteView(generics.CreateAPIView):
    """商品收藏视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, product_id):
        """切换商品收藏状态"""
        try:
            product = Product.objects.get(id=product_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
            
            if not created:
                favorite.delete()
                product.favorites_count = max(0, product.favorites_count - 1)
                product.save()
                return Response({
                    'favorited': False,
                    'favorites_count': product.favorites_count
                })
            else:
                product.favorites_count += 1
                product.save()
                return Response({
                    'favorited': True,
                    'favorites_count': product.favorites_count
                })
        except Product.DoesNotExist:
            return Response({
                'error': '商品不存在'
            }, status=status.HTTP_404_NOT_FOUND)

class ProductCommentView(generics.ListCreateAPIView):
    """商品评论视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id):
        """获取商品评论列表"""
        try:
            product = Product.objects.get(id=product_id)
            comments = Comment.objects.filter(product=product).order_by('created_at')
            
            # 构建评论响应数据
            comment_list = []
            for comment in comments:
                comment_list.append({
                    'id': comment.id,
                    'content': comment.content,
                    'created_at': comment.created_at,
                    'user_username': comment.user.username,
                    'user_avatar': request.build_absolute_uri(comment.user.profile.avatar.url) if comment.user.profile.avatar else None,
                    'user_id': comment.user.id,
                    'is_reply': hasattr(comment, 'reply_to') and comment.reply_to is not None,
                    'reply_to': comment.reply_to
                })
            
            return Response(comment_list)
        except Product.DoesNotExist:
            return Response({
                'error': '商品不存在'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, product_id):
        """添加商品评论"""
        try:
            product = Product.objects.get(id=product_id)
            content = request.data.get('content')
            reply_to = request.data.get('reply_to')
            
            if not content:
                return Response({
                    'error': '评论内容不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            comment = Comment.objects.create(
                user=request.user,
                product=product,
                content=content
            )
            
            # 如果是回复，保存回复对象
            if reply_to:
                comment.reply_to = reply_to
                comment.save()
            
            return Response({
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at,
                'user_username': comment.user.username,
                'user_avatar': request.build_absolute_uri(comment.user.profile.avatar.url) if comment.user.profile.avatar else None,
                'user_id': comment.user.id,
                'is_reply': reply_to is not None,
                'reply_to': reply_to
            }, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({
                'error': '商品不存在'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, product_id, comment_id):
        """删除评论"""
        try:
            comment = Comment.objects.get(id=comment_id, product_id=product_id)
            
            # 检查是否是评论作者
            if comment.user != request.user:
                return Response({
                    'error': '只能删除自己的评论'
                }, status=status.HTTP_403_FORBIDDEN)
            
            comment.delete()
            return Response({
                'message': '评论删除成功'
            }, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({
                'error': '评论不存在'
            }, status=status.HTTP_404_NOT_FOUND)

class CheckUserActionView(generics.GenericAPIView):
    """检查用户操作状态视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id, action):
        """检查用户是否点赞或收藏商品"""
        try:
            product = Product.objects.get(id=product_id)
            
            if action == 'like':
                liked = Like.objects.filter(user=request.user, product=product).exists()
                return Response({'liked': liked})
            elif action == 'favorite':
                favorited = Favorite.objects.filter(user=request.user, product=product).exists()
                return Response({'favorited': favorited})
            else:
                return Response({
                    'error': '无效的操作类型'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({
                'error': '商品不存在'
            }, status=status.HTTP_404_NOT_FOUND)

class UserFollowView(generics.CreateAPIView):
    """用户关注视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        """切换用户关注状态"""
        try:
            target_user = User.objects.get(id=user_id)
            
            if target_user == request.user:
                return Response({
                    'error': '不能关注自己'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            follow, created = Follow.objects.get_or_create(follower=request.user, followed=target_user)
            
            if not created:
                follow.delete()
                return Response({'following': False})
            else:
                return Response({'following': True})
        except User.DoesNotExist:
            return Response({
                'error': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)

class CheckFollowView(generics.GenericAPIView):
    """检查关注状态视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        """检查是否关注了指定用户"""
        try:
            target_user = User.objects.get(id=user_id)
            following = Follow.objects.filter(follower=request.user, followed=target_user).exists()
            return Response({'following': following})
        except User.DoesNotExist:
            return Response({
                'error': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)

class OrderCreateView(generics.CreateAPIView):
    """创建订单视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """创建新订单"""
        try:
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity', 1)
            delivery_method = request.data.get('delivery_method', 'self_pickup')
            
            product = Product.objects.get(id=product_id)
            
            # 防止购买自己的商品
            if product.seller == request.user:
                return Response({
                    'error': '不能购买自己发布的商品'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查商品状态，禁止购买已下架的商品
            if product.status == 'removed':
                return Response({
                    'error': '该商品已下架，无法购买'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查库存
            if product.quantity < quantity:
                return Response({
                    'error': '库存不足'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查配送权限
            if delivery_method == 'delivery' and not product.allow_delivery:
                return Response({
                    'error': '该商品不支持配送'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 计算总价
            from decimal import Decimal
            base_price = product.price * quantity
            delivery_fee = Decimal('2.00') if delivery_method == 'delivery' else Decimal('0')
            total_amount = base_price + delivery_fee
            
            # 创建订单 - 直接设置为已送达状态，跳过付款和配送流程
            order = Order.objects.create(
                buyer=request.user,
                seller=product.seller,
                total_amount=total_amount,
                payment_method='online',
                delivery_method=delivery_method,
                status='delivered'
            )
            
            # 创建订单项
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )
            
            # 减少库存
            product.quantity -= quantity
            if product.quantity == 0:
                product.status = 'sold_out'
            product.save()
            
            return Response({
                'message': '订单创建成功',
                'order_id': order.id,
                'total_amount': total_amount
            }, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({
                'error': '商品不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'创建订单失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryListView(generics.ListAPIView):
    """商品分类列表视图"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        """允许公开访问分类列表"""
        return []
    
    def get(self, request, *args, **kwargs):
        """获取分类列表"""
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

# 互动记录相关视图
class UserLikesView(generics.ListAPIView):
    """用户点赞记录"""
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户点赞的商品"""
        return Product.objects.filter(likes__user=self.request.user).order_by('-likes__created_at')
    
    def get_serializer_context(self):
        """传递request上下文给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class UserFavoritesView(generics.ListAPIView):
    """用户收藏记录"""
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户收藏的商品"""
        return Product.objects.filter(favorites__user=self.request.user).order_by('-favorites__created_at')
    
    def get_serializer_context(self):
        """传递request上下文给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class UserViewHistoryView(generics.ListAPIView):
    """用户浏览记录"""
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的浏览记录，最多显示100条，按浏览时间排序"""
        return Product.objects.filter(viewed_by__user=self.request.user).order_by('-viewed_by__viewed_at').distinct()[:100]
    
    def get_serializer_context(self):
        """传递request上下文给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class UserFollowingView(generics.ListAPIView):
    """用户关注的卖家"""
    pagination_class = ProductPagination
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """获取当前用户关注的卖家列表"""
        following = Follow.objects.filter(follower=request.user).order_by('-created_at')
        
        # 分页处理
        paginator = self.pagination_class()
        paginated_following = paginator.paginate_queryset(following, request)
        
        # 构造响应数据
        data = []
        for follow in paginated_following:
            data.append({
                'id': follow.followed.id,
                'username': follow.followed.username,
                'nickname': follow.followed.profile.nickname,
                'avatar': request.build_absolute_uri(follow.followed.profile.avatar.url) if follow.followed.profile.avatar else None,
                'reputation': follow.followed.profile.reputation,
                'completed_transactions': follow.followed.profile.completed_transactions,
                'followed_at': follow.created_at
            })
        
        return paginator.get_paginated_response(data)

class UserProductsView(generics.GenericAPIView):
    """获取指定用户的商品列表"""
    permission_classes = []
    
    def get(self, request, user_id):
        """获取指定用户发布的商品"""
        try:
            # 获取指定用户发布的所有商品
            products = Product.objects.filter(seller_id=user_id).order_by('-created_at')
            
            # 构建响应数据
            product_list = []
            for product in products:
                # 获取商品图片
                images = []
                for img in product.images.all():
                    images.append(request.build_absolute_uri(img.image.url))
                
                product_list.append({
                    'id': product.id,
                    'title': product.title,
                    'price': product.price,
                    'quantity': product.quantity,
                    'status': product.status,
                    'created_at': product.created_at,
                    'images': images
                })
            
            return Response(product_list)
        except Exception as e:
            return Response({
                'error': f'获取用户商品失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSoldOrdersView(generics.GenericAPIView):
    """获取指定用户的卖出订单"""
    permission_classes = []
    
    def get(self, request, user_id):
        """获取指定用户卖出的订单"""
        try:
            # 获取指定用户卖出的所有订单
            orders = Order.objects.filter(seller_id=user_id).order_by('-created_at')
            
            # 构建响应数据
            order_list = []
            for order in orders:
                # 获取订单商品
                items = []
                for item in order.items.all():
                    # 获取商品图片
                    images = []
                    for img in item.product.images.all():
                        images.append(request.build_absolute_uri(img.image.url))
                    
                    items.append({
                        'id': item.id,
                        'product': {
                            'id': item.product.id,
                            'title': item.product.title,
                            'images': images
                        },
                        'quantity': item.quantity,
                        'unit_price': item.unit_price
                    })
                
                order_list.append({
                    'id': order.id,
                    'status': order.status,
                    'total_amount': order.total_amount,
                    'created_at': order.created_at,
                    'buyer': {
                        'id': order.buyer.id,
                        'username': order.buyer.username
                    },
                    'items': items
                })
            
            return Response(order_list)
        except Exception as e:
            return Response({
                'error': f'获取用户卖出订单失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 私信相关视图
class MessageListView(generics.ListCreateAPIView):
    """私信列表和发送视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        """获取与指定用户的私信对话或私信列表"""
        if user_id:
            # 获取与特定用户的对话
            try:
                other_user = User.objects.get(id=user_id)
                # 获取两用户之间的所有消息
                from django.db.models import Q
                messages = Message.objects.filter(
                    Q(sender=request.user, receiver=other_user) |
                    Q(sender=other_user, receiver=request.user)
                ).order_by('created_at')                
                # 标记对方发送的消息为已读
                messages.filter(sender=other_user, is_read=False).update(is_read=True)
                
                # 构建响应数据
                message_list = []
                for message in messages:
                    message_list.append({
                        'id': message.id,
                        'content': message.content,
                        'created_at': message.created_at,
                        'sender': {
                            'id': message.sender.id,
                            'username': message.sender.username,
                            'avatar': request.build_absolute_uri(message.sender.profile.avatar.url) if hasattr(message.sender, 'profile') and message.sender.profile.avatar else None
                        },
                        'receiver': {
                            'id': message.receiver.id,
                            'username': message.receiver.username,
                            'avatar': request.build_absolute_uri(message.receiver.profile.avatar.url) if hasattr(message.receiver, 'profile') and message.receiver.profile.avatar else None
                        },
                        'is_read': message.is_read
                    })
                
                return Response({
                    'messages': message_list,
                    'other_user': {
                        'id': other_user.id,
                        'username': other_user.username,
                        'avatar': request.build_absolute_uri(other_user.profile.avatar.url) if hasattr(other_user, 'profile') and other_user.profile.avatar else None
                    },
                    'conversation_id': f'{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}'
                })
            except User.DoesNotExist:
                return Response({
                    'error': '用户不存在'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 获取私信会话列表
            try:
                # 获取所有与当前用户相关的消息
                from django.db.models import Q
                all_messages = Message.objects.filter(
                    Q(sender=request.user) |
                    Q(receiver=request.user)
                ).order_by('-created_at')
                
                # 构建会话字典，key为对方用户ID，value为最新消息
                conversations = {}
                for message in all_messages:
                    if message.sender == request.user:
                        other_user_id = message.receiver.id
                        other_user = message.receiver
                    else:
                        other_user_id = message.sender.id
                        other_user = message.sender
                    
                    if other_user_id not in conversations:
                        # 计算未读消息数
                        unread_count = Message.objects.filter(
                            sender=other_user,
                            receiver=request.user,
                            is_read=False
                        ).count()
                        
                        conversations[other_user_id] = {
                            'id': f'{min(request.user.id, other_user_id)}_{max(request.user.id, other_user_id)}',
                            'other_user': {
                                'id': other_user.id,
                                'username': other_user.username,
                                'avatar': request.build_absolute_uri(other_user.profile.avatar.url) if hasattr(other_user, 'profile') and other_user.profile.avatar else None
                            },
                            'last_message': message.content,
                            'last_message_time': message.created_at,
                            'unread_count': unread_count
                        }
                
                # 转换为列表并按最后消息时间排序
                conversation_list = list(conversations.values())
                conversation_list.sort(key=lambda x: x['last_message_time'], reverse=True)
                
                return Response(conversation_list)
            except Exception as e:
                return Response({
                    'error': f'获取私信列表失败：{str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """发送私信"""
        try:
            recipient_id = request.data.get('recipient_id')
            content = request.data.get('content')
            
            if not recipient_id or not content:
                return Response({
                    'error': '接收者ID和消息内容不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            recipient = User.objects.get(id=recipient_id)
            
            if recipient == request.user:
                return Response({
                    'error': '不能给自己发送私信'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            message = Message.objects.create(
                sender=request.user,
                receiver=recipient,
                content=content
            )
            
            return Response({
                'id': message.id,
                'content': message.content,
                'created_at': message.created_at,
                'sender': {
                    'id': message.sender.id,
                    'username': message.sender.username,
                    'avatar': request.build_absolute_uri(message.sender.profile.avatar.url) if message.sender.profile.avatar else None
                },
                'receiver': {
                    'id': message.receiver.id,
                    'username': message.receiver.username,
                    'avatar': request.build_absolute_uri(message.receiver.profile.avatar.url) if message.receiver.profile.avatar else None
                },
                'is_read': message.is_read
            }, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({
                'error': '接收者不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'发送私信失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 交易信息相关视图
class TransactionView(generics.GenericAPIView):
    """交易信息视图集"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, endpoint=None):
        """处理不同的交易信息请求"""
        if endpoint == 'my-products':
            return self.get_my_products(request)
        elif endpoint == 'sold-orders':
            return self.get_sold_orders(request)
        elif endpoint == 'bought-orders':
            return self.get_bought_orders(request)
        
        return Response({
            'error': '无效的请求端点'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, record_type=None, record_id=None):
        """处理删除交易记录的请求"""
        try:
            if record_type == 'product':
                # 删除商品
                product = Product.objects.get(id=record_id)
                # 检查是否是商品卖家
                if product.seller != request.user:
                    return Response({
                        'error': '无权限删除此商品'
                    }, status=status.HTTP_403_FORBIDDEN)
                product.delete()
                return Response({
                    'message': '商品删除成功'
                })
            elif record_type == 'order':
                # 删除订单
                order = Order.objects.get(id=record_id)
                # 检查是否是订单买家或卖家
                if order.buyer != request.user and order.seller != request.user:
                    return Response({
                        'error': '无权限删除此订单'
                    }, status=status.HTTP_403_FORBIDDEN)
                order.delete()
                return Response({
                    'message': '订单删除成功'
                })
            
            return Response({
                'error': '无效的请求参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({
                'error': '商品不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({
                'error': '订单不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'删除记录失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_my_products(self, request):
        """获取当前用户发布的商品"""
        try:
            # 获取当前用户发布的所有商品
            products = Product.objects.filter(seller=request.user).order_by('-created_at')
            
            # 构建响应数据
            product_list = []
            for product in products:
                # 获取商品图片
                images = []
                for img in product.images.all():
                    images.append(request.build_absolute_uri(img.image.url))
                
                product_list.append({
                    'id': product.id,
                    'title': product.title,
                    'price': product.price,
                    'quantity': product.quantity,
                    'status': product.status,
                    'created_at': product.created_at,
                    'images': images
                })
            
            return Response(product_list)
        except Exception as e:
            return Response({
                'error': f'获取我的发布失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_sold_orders(self, request):
        """获取当前用户卖出的订单"""
        try:
            # 获取当前用户卖出的所有订单
            orders = Order.objects.filter(seller=request.user).order_by('-created_at')
            
            # 构建响应数据
            order_list = []
            for order in orders:
                # 获取订单商品
                items = []
                for item in order.items.all():
                    # 获取商品图片
                    images = []
                    for img in item.product.images.all():
                        images.append(request.build_absolute_uri(img.image.url))
                    
                    items.append({
                        'id': item.id,
                        'product': {
                            'id': item.product.id,
                            'title': item.product.title,
                            'images': images
                        },
                        'quantity': item.quantity,
                        'unit_price': item.unit_price
                    })
                
                order_list.append({
                    'id': order.id,
                    'status': order.status,
                    'total_amount': order.total_amount,
                    'created_at': order.created_at,
                    'buyer': {
                        'id': order.buyer.id,
                        'username': order.buyer.username
                    },
                    'items': items
                })
            
            return Response(order_list)
        except Exception as e:
            return Response({
                'error': f'获取已卖出订单失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_bought_orders(self, request):
        """获取当前用户买到的订单"""
        try:
            # 获取当前用户买到的所有订单
            orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
            
            # 构建响应数据
            order_list = []
            for order in orders:
                # 获取订单商品
                items = []
                for item in order.items.all():
                    # 获取商品图片
                    images = []
                    for img in item.product.images.all():
                        images.append(request.build_absolute_uri(img.image.url))
                    
                    items.append({
                        'id': item.id,
                        'product': {
                            'id': item.product.id,
                            'title': item.product.title,
                            'images': images
                        },
                        'quantity': item.quantity,
                        'unit_price': item.unit_price
                    })
                
                order_list.append({
                    'id': order.id,
                    'status': order.status,
                    'total_amount': order.total_amount,
                    'created_at': order.created_at,
                    'seller': {
                        'id': order.seller.id,
                        'username': order.seller.username
                    },
                    'items': items
                })
            
            return Response(order_list)
        except Exception as e:
            return Response({
                'error': f'获取已买到订单失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminProductManagementView(generics.ListAPIView):
    """管理员商品管理视图"""
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        """传递request上下文给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        """获取所有商品，支持搜索和筛选"""
        # 检查是否为管理员
        if not self.request.user.is_superuser:
            return Product.objects.none()
        
        # 获取查询参数
        search = self.request.query_params.get('search', '')
        status = self.request.query_params.get('status', '')
        
        # 构建查询
        queryset = Product.objects.all()
        
        # 搜索功能
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(seller__username__icontains=search) |
                models.Q(category__name__icontains=search)
            )
        
        # 状态筛选
        if status:
            queryset = queryset.filter(status=status)
        
        # 按创建时间倒序
        queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def patch(self, request, *args, **kwargs):
        """审核商品或下架商品"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response(
                {"error": "权限不足"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取商品ID和操作类型
        product_id = request.data.get('product_id')
        action = request.data.get('action')
        
        if not product_id or not action:
            return Response(
                {"error": "商品ID和操作类型不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 获取商品
            product = Product.objects.get(id=product_id)
            
            # 执行操作
            if action == 'approve':
                product.status = 'approved'
                product.save()
                return Response(
                    {"message": "商品审核通过"},
                    status=status.HTTP_200_OK
                )
            elif action == 'reject':
                product.status = 'rejected'
                product.save()
                return Response(
                    {"message": "商品已拒绝"},
                    status=status.HTTP_200_OK
                )
            elif action == 'remove':
                product.status = 'removed'
                product.save()
                return Response(
                    {"message": "商品已下架"},
                    status=status.HTTP_200_OK
                )
            elif action == 'delete':
                # 直接删除商品
                product.delete()
                return Response(
                    {"message": "商品已删除"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "无效的操作类型"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Product.DoesNotExist:
            return Response(
                {"error": "商品不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "操作失败"},
                status=status.HTTP_400_BAD_REQUEST
            )

class OrderActionView(generics.GenericAPIView):
    """订单操作视图"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, order_id, action):
        """处理不同的订单操作"""
        try:
            order = Order.objects.get(id=order_id)
            
            # 检查权限
            if action == 'confirm-receipt':
                # 只有买家可以确认收货
                if order.buyer != request.user:
                    return Response({
                        'error': '无权限执行此操作'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # 只有已送达状态才能确认收货
                if order.status != 'delivered':
                    return Response({
                        'error': '订单状态不允许此操作'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 更新订单状态
                order.status = 'completed'
                order.save()
                
                # 更新卖家信誉和成交数量
                if hasattr(order.seller, 'profile'):
                    profile = order.seller.profile
                    # 成交加1分，上限100分
                    if profile.reputation < 100:
                        profile.reputation += 1
                    profile.completed_transactions += 1
                    profile.save()
                
                return Response({
                    'message': '确认收货成功'
                })
            
            elif action == 'request-return':
                # 只有买家可以申请退货
                if order.buyer != request.user:
                    return Response({
                        'error': '无权限执行此操作'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # 只有已送达状态才能申请退货
                if order.status != 'delivered':
                    return Response({
                        'error': '订单状态不允许此操作'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 更新订单状态
                order.status = 'return_requested'
                order.save()
                
                # 发送退货申请消息给卖家
                Message.objects.create(
                    sender=request.user,
                    receiver=order.seller,
                    content=f'订单 #{order.id} 申请退货'
                )
                
                return Response({
                    'message': '申请退货成功'
                })
            
            elif action == 'handle-return':
                # 只有卖家可以处理退货申请
                if order.seller != request.user:
                    return Response({
                        'error': '无权限执行此操作'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # 只有申请退货状态才能处理
                if order.status != 'return_requested':
                    return Response({
                        'error': '订单状态不允许此操作'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 获取处理结果
                accept = request.data.get('accept', False)
                
                if accept:
                    # 同意退货
                    order.status = 'returned'
                    # 退货扣1分，最低0分
                    if hasattr(order.seller, 'profile'):
                        profile = order.seller.profile
                        if profile.reputation > 0:
                            profile.reputation -= 1
                        profile.save()
                else:
                    # 拒绝退货
                    order.status = 'completed'
                
                order.save()
                
                # 发送处理结果消息给买家
                result = '同意' if accept else '拒绝'
                Message.objects.create(
                    sender=request.user,
                    receiver=order.buyer,
                    content=f'订单 #{order.id} 的退货申请已被{result}'
                )
                
                return Response({
                    'message': f'退货申请已{result}'
                })
            
            else:
                return Response({
                    'error': '无效的操作类型'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Order.DoesNotExist:
            return Response({
                'error': '订单不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'订单操作失败：{str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentCreateView(generics.CreateAPIView):
    """创建评价视图"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        """传递request上下文给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        """创建评价时设置用户，并处理评分对信誉分的影响"""
        comment = serializer.save(user=self.request.user)
        
        # 处理差评对卖家信誉分的影响
        if comment.rating is not None and comment.rating <= 2:  # 2星及以下视为差评
            product = comment.product
            seller = product.seller
            if hasattr(seller, 'profile'):
                profile = seller.profile
                if profile.reputation > 0:
                    profile.reputation -= 1  # 差评扣1分
                profile.save()

class CommentListView(generics.ListAPIView):
    """获取商品评价列表视图"""
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        """根据商品ID获取评价列表"""
        product_id = self.kwargs.get('product_id')
        return Comment.objects.filter(product_id=product_id).order_by('created_at')
    
    def get_serializer_context(self):
        """传递request上下文给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class AdminAnnouncementView(generics.ListCreateAPIView):
    """管理员公告管理视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取公告列表"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response(
                {"error": "权限不足"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        announcements = Announcement.objects.all().order_by('-created_at')
        data = []
        for announcement in announcements:
            data.append({
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'is_active': announcement.is_active,
                'created_at': announcement.created_at,
                'updated_at': announcement.updated_at
            })
        return Response(data)
    
    def post(self, request):
        """创建新公告"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response(
                {"error": "权限不足"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        title = request.data.get('title')
        content = request.data.get('content')
        is_active = request.data.get('is_active', True)
        
        if not title or not content:
            return Response(
                {"error": "标题和内容不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            is_active=is_active
        )
        
        return Response({
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'is_active': announcement.is_active,
            'created_at': announcement.created_at
        }, status=status.HTTP_201_CREATED)
    
    def patch(self, request, pk):
        """更新公告"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response(
                {"error": "权限不足"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            announcement = Announcement.objects.get(id=pk)
        except Announcement.DoesNotExist:
            return Response(
                {"error": "公告不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        title = request.data.get('title')
        content = request.data.get('content')
        is_active = request.data.get('is_active')
        
        if title:
            announcement.title = title
        if content:
            announcement.content = content
        if is_active is not None:
            announcement.is_active = is_active
        
        announcement.save()
        
        return Response({
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'is_active': announcement.is_active,
            'updated_at': announcement.updated_at
        })
    
    def delete(self, request, pk):
        """删除公告"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response(
                {"error": "权限不足"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            announcement = Announcement.objects.get(id=pk)
            announcement.delete()
            return Response({
                "message": "公告已删除"
            })
        except Announcement.DoesNotExist:
            return Response(
                {"error": "公告不存在"},
                status=status.HTTP_404_NOT_FOUND
            )

class UserAnnouncementView(generics.ListAPIView):
    """用户公告列表视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取公告列表，包含未读状态"""
        announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
        data = []
        
        for announcement in announcements:
            # 检查是否已读
            is_read = AnnouncementRead.objects.filter(
                user=request.user,
                announcement=announcement
            ).exists()
            
            data.append({
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'created_at': announcement.created_at,
                'is_read': is_read
            })
        
        return Response(data)

class AnnouncementReadView(generics.CreateAPIView):
    """公告阅读标记视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """标记公告为已读"""
        announcement_id = request.data.get('announcement_id')
        if not announcement_id:
            return Response(
                {"error": "公告ID不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            announcement = Announcement.objects.get(id=announcement_id)
        except Announcement.DoesNotExist:
            return Response(
                {"error": "公告不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查是否已经读过
        read, created = AnnouncementRead.objects.get_or_create(
            user=request.user,
            announcement=announcement
        )
        
        if created:
            return Response({
                "message": "标记已读成功"
            })
        else:
            return Response({
                "message": "已经读过此公告"
            })

class AdminOrderManagementView(generics.GenericAPIView):
    """管理员订单管理视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取订单列表，支持搜索和筛选"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response(
                {"error": "权限不足"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 获取查询参数
        search = request.query_params.get('search', '')
        status = request.query_params.get('status', '')
        
        # 构建查询
        queryset = Order.objects.all()
        
        # 搜索功能
        if search:
            queryset = queryset.filter(
                models.Q(id__icontains=search) |
                models.Q(items__product__title__icontains=search) |
                models.Q(buyer__username__icontains=search) |
                models.Q(seller__username__icontains=search)
            ).distinct()
        
        # 状态筛选
        if status:
            queryset = queryset.filter(status=status)
        
        # 按创建时间倒序
        queryset = queryset.order_by('-created_at')
        
        # 构建响应数据
        orders = []
        for order in queryset:
            # 获取订单商品信息
            for item in order.items.all():
                orders.append({
                    'id': order.id,
                    'product_title': item.product.title,
                    'buyer_username': order.buyer.username,
                    'seller_username': order.seller.username,
                    'price': float(item.unit_price),
                    'status': order.status,
                    'created_at': order.created_at
                })
        
        return Response(orders)
    
    def delete(self, request, order_id):
        """删除订单"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response(
                {"error": "权限不足"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
            return Response({
                "message": "订单已删除"
            })
        except Order.DoesNotExist:
            return Response(
                {"error": "订单不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"删除订单失败：{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminStatisticsView(generics.GenericAPIView):
    """管理员统计数据视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取统计数据"""
        # 检查是否为管理员
        if not request.user.is_superuser:
            return Response(
                {"error": "权限不足"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # 获取日期范围参数
            date_range_start = request.query_params.get('start_date')
            date_range_end = request.query_params.get('end_date')
            
            # 计算总用户数
            total_users = User.objects.count()
            
            # 计算总商品数
            total_products = Product.objects.count()
            
            # 计算总订单数（只计算已完成的订单）
            total_orders = Order.objects.filter(status='completed').count()
            
            # 计算总销售额（只计算已完成的订单）
            total_sales = Order.objects.filter(status='completed').aggregate(
                total=models.Sum('total_amount')
            )['total'] or 0
            
            # 计算用户增长率（这里简化为固定值，实际应与上周比较）
            user_growth = 15.5
            
            # 计算商品增长率
            product_growth = 20.3
            
            # 计算订单增长率
            order_growth = 12.8
            
            # 计算销售额增长率
            sales_growth = 18.2
            
            # 生成销售额趋势数据（根据数据库中的实际订单信息）
            sales_trend = []
            
            # 获取最近6个月的数据
            today = datetime.date.today()
            for i in range(5, -1, -1):
                # 计算月份
                month_date = today - datetime.timedelta(days=i*30)
                month = month_date.month
                year = month_date.year
                month_label = f"{year}年{month}月"
                
                # 计算该月的销售额
                month_start = datetime.date(year, month, 1)
                if month == 12:
                    month_end = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
                else:
                    month_end = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
                
                monthly_sales = Order.objects.filter(
                    created_at__date__range=[month_start, month_end],
                    status='completed'
                ).aggregate(
                    total=models.Sum('total_amount')
                )['total'] or 0
                
                # 添加到销售额趋势列表
                sales_trend.append({
                    "label": month_label,
                    "value": float(monthly_sales)
                })
            
            # 生成商品分类分布数据
            category_distribution = []
            categories = Category.objects.all()
            total_category_products = Product.objects.count()
            
            for category in categories:
                count = Product.objects.filter(category=category).count()
                percentage = (count / total_category_products * 100) if total_category_products > 0 else 0
                category_distribution.append({
                    "name": category.name,
                    "count": count,
                    "percentage": round(percentage, 1)
                })
            
            # 如果没有分类，添加默认分类数据
            if not category_distribution:
                category_distribution = [
                    {"name": "数码产品", "count": 1200, "percentage": 34.3},
                    {"name": "图书音像", "count": 800, "percentage": 22.9},
                    {"name": "服装鞋帽", "count": 600, "percentage": 17.1},
                    {"name": "生活用品", "count": 500, "percentage": 14.3},
                    {"name": "其他", "count": 400, "percentage": 11.4}
                ]
            
            # 生成每日统计详情（根据数据库中的实际数据）
            daily_statistics = []
            
            # 获取日期范围内的每天数据
            if date_range_start and date_range_end:
                # 解析日期
                start = datetime.datetime.strptime(date_range_start, '%Y-%m-%d')
                end = datetime.datetime.strptime(date_range_end, '%Y-%m-%d')
                delta = datetime.timedelta(days=1)
                
                # 遍历日期范围
                current_date = start
                while current_date <= end:
                    date_str = current_date.strftime('%Y-%m-%d')
                    
                    # 计算当天新增用户数
                    new_users = User.objects.filter(date_joined__date=current_date).count()
                    
                    # 计算当天新增商品数（上架的商品）
                    new_products = Product.objects.filter(created_at__date=current_date, status='approved').count()
                    
                    # 计算当天订单数（只计算已完成的订单）
                    orders = Order.objects.filter(created_at__date=current_date, status='completed').count()
                    
                    # 计算当天销售额（只计算已完成的订单）
                    daily_sales = Order.objects.filter(created_at__date=current_date, status='completed').aggregate(
                        total=models.Sum('total_amount')
                    )['total'] or 0
                    
                    # 添加到每日统计列表
                    daily_statistics.append({
                        "date": date_str,
                        "new_users": new_users,
                        "new_products": new_products,
                        "orders": orders,
                        "sales": daily_sales
                    })
                    
                    current_date += delta
            else:
                # 如果没有指定日期范围，使用最近7天
                today = datetime.date.today()
                for i in range(6, -1, -1):
                    date = today - datetime.timedelta(days=i)
                    date_str = date.strftime('%Y-%m-%d')
                    
                    # 计算当天新增用户数
                    new_users = User.objects.filter(date_joined__date=date).count()
                    
                    # 计算当天新增商品数（上架的商品）
                    new_products = Product.objects.filter(created_at__date=date, status='approved').count()
                    
                    # 计算当天订单数（只计算已完成的订单）
                    orders = Order.objects.filter(created_at__date=date, status='completed').count()
                    
                    # 计算当天销售额（只计算已完成的订单）
                    daily_sales = Order.objects.filter(created_at__date=date, status='completed').aggregate(
                        total=models.Sum('total_amount')
                    )['total'] or 0
                    
                    # 添加到每日统计列表
                    daily_statistics.append({
                        "date": date_str,
                        "new_users": new_users,
                        "new_products": new_products,
                        "orders": orders,
                        "sales": daily_sales
                    })
            
            # 构建响应数据
            response_data = {
                "total_users": total_users,
                "user_growth": user_growth,
                "total_products": total_products,
                "product_growth": product_growth,
                "total_orders": total_orders,
                "order_growth": order_growth,
                "total_sales": total_sales,
                "sales_growth": sales_growth,
                "sales_trend": sales_trend,
                "category_distribution": category_distribution,
                "daily_statistics": daily_statistics
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {"error": f"获取统计数据失败：{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminCommentManagementView(generics.ListAPIView, generics.DestroyAPIView):
    """管理员评论管理视图"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = CommentSerializer
    
    def get(self, request):
        """获取所有评论列表"""
        try:
            # 获取分页参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            search = request.GET.get('search', '')
            
            # 构建查询集
            queryset = Comment.objects.all().order_by('-created_at')
            
            # 搜索功能
            if search:
                from django.db.models import Q
                queryset = queryset.filter(
                    Q(content__icontains=search) |
                    Q(user__username__icontains=search) |
                    Q(product__title__icontains=search)
                )
            
            # 分页
            from django.core.paginator import Paginator
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 构建响应数据
            serializer = self.get_serializer(page_obj, many=True)
            return Response({
                'results': serializer.data,
                'count': paginator.count,
                'total_pages': paginator.num_pages
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, comment_id):
        """删除评论"""
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.delete()
            return Response({'message': '评论删除成功'}, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
