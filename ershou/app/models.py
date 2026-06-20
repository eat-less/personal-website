from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# 用户扩展模型
class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, primary_key=True)
    student_id = models.CharField(max_length=20, unique=True, verbose_name='学号')
    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    bio = models.TextField(blank=True, verbose_name='简介')
    grade = models.CharField(max_length=20, blank=True, verbose_name='年级')
    reputation = models.IntegerField(default=0, verbose_name='信誉分')
    completed_transactions = models.IntegerField(default=0, verbose_name='成交数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

# 商品分类模型
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
    
    def __str__(self):
        return self.name

# 商品模型
class Product(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已上架'),
        ('rejected', '已拒绝'),
        ('sold_out', '已售罄'),
        ('removed', '已下架'),
    )
    
    seller = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='products', verbose_name='卖家')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='分类')
    title = models.CharField(max_length=200, verbose_name='商品标题')
    description = models.TextField(verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    quantity = models.IntegerField(default=1, verbose_name='数量')
    allow_delivery = models.BooleanField(default=False, verbose_name='允许配送')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    views = models.IntegerField(default=0, verbose_name='浏览量')
    likes_count = models.IntegerField(default=0, verbose_name='点赞数')
    favorites_count = models.IntegerField(default=0, verbose_name='收藏数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
    
    def __str__(self):
        return self.title

# 商品图片模型
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='商品')
    image = models.ImageField(upload_to='products/', verbose_name='图片')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = '商品图片'

# 商品点赞模型
class Like(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='likes', verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes', verbose_name='商品')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        verbose_name = '商品点赞'
        verbose_name_plural = '商品点赞'
        unique_together = ('user', 'product')

# 商品收藏模型
class Favorite(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites', verbose_name='商品')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')
    
    class Meta:
        verbose_name = '商品收藏'
        verbose_name_plural = '商品收藏'
        unique_together = ('user', 'product')

# 商品评论模型
class Comment(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='comments', verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name='商品')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='comments', blank=True, null=True, verbose_name='关联订单')
    content = models.TextField(blank=True, verbose_name='评论内容')
    rating = models.IntegerField(blank=True, null=True, verbose_name='评分')
    image = models.ImageField(upload_to='comments/', blank=True, null=True, verbose_name='评价图片')
    reply_to = models.CharField(max_length=100, blank=True, null=True, verbose_name='回复对象')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    
    class Meta:
        verbose_name = '商品评论'
        verbose_name_plural = '商品评论'
        ordering = ['created_at']

# 浏览记录模型
class ViewHistory(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='view_history', verbose_name='用户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='viewed_by', verbose_name='商品')
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name='浏览时间')
    
    class Meta:
        verbose_name = '浏览记录'
        verbose_name_plural = '浏览记录'
        ordering = ['-viewed_at']

# 订单模型
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('shipping', '配送中'),
        ('delivered', '已送达'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('return_requested', '申请退货'),
        ('returned', '已退货'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('online', '在线支付'),
        ('cash', '现金支付'),
    )
    
    DELIVERY_METHOD_CHOICES = (
        ('self_pickup', '自提'),
        ('delivery', '配送'),
    )
    
    buyer = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='purchases', verbose_name='买家')
    seller = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='sales', verbose_name='卖家')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='支付方式')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES, verbose_name='配送方式')
    delivery_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='配送费')
    service_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='服务费')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'

# 订单项模型
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name='商品')
    quantity = models.IntegerField(verbose_name='数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    
    class Meta:
        verbose_name = '订单项'
        verbose_name_plural = '订单项'

# # 盲盒模型
# class BlindBox(models.Model):
#     PRICE_CHOICES = (
#         (5.00, '5元'),
#         (10.00, '10元'),
#         (15.00, '15元'),
#         (20.00, '20元'),
#     )
#
#     name = models.CharField(max_length=100, verbose_name='盲盒名称')
#     description = models.TextField(verbose_name='盲盒描述')
#     price = models.DecimalField(max_digits=5, decimal_places=2, choices=PRICE_CHOICES, verbose_name='价格')
#     available_quantity = models.IntegerField(verbose_name='可用数量')
#     is_active = models.BooleanField(default=True, verbose_name='是否激活')
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#     updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
#
#     class Meta:
#         verbose_name = '盲盒'
#         verbose_name_plural = '盲盒'
#
#     def __str__(self):
#         return f'{self.name} - {self.price}元'
#
# # 盲盒商品模型
# class BlindBoxItem(models.Model):
#     blind_box = models.ForeignKey(BlindBox, on_delete=models.CASCADE, related_name='items', verbose_name='所属盲盒')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='blind_box_items', verbose_name='商品')
#     probability = models.FloatField(verbose_name='出现概率')
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#
#     class Meta:
#         verbose_name = '盲盒商品'
#         verbose_name_plural = '盲盒商品'
#
# # 盲盒订单模型
# class BlindBoxOrder(models.Model):
#     STATUS_CHOICES = (
#         ('pending', '待付款'),
#         ('paid', '已付款'),
#         ('completed', '已完成'),
#         ('cancelled', '已取消'),
#     )
#
#     user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='blind_box_orders', verbose_name='用户')
#     blind_box = models.ForeignKey(BlindBox, on_delete=models.CASCADE, related_name='orders', verbose_name='盲盒')
#     received_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_as_blind_box', verbose_name='收到的商品')
#     amount = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='金额')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#     updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
#
#     class Meta:
#         verbose_name = '盲盒订单'
#         verbose_name_plural = '盲盒订单'

# 私信模型
class Message(models.Model):
    sender = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')
    content = models.TextField(verbose_name='消息内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    
    class Meta:
        verbose_name = '私信'
        verbose_name_plural = '私信'
        ordering = ['-created_at']

# 关注模型
class Follow(models.Model):
    follower = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='following', verbose_name='关注者')
    followed = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='followers', verbose_name='被关注者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')
    
    class Meta:
        verbose_name = '关注'
        verbose_name_plural = '关注'
        unique_together = ('follower', 'followed')

# 数据统计模型
class Statistics(models.Model):
    date = models.DateField(unique=True, verbose_name='统计日期')
    total_orders = models.IntegerField(default=0, verbose_name='总订单数')
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name='总销售额')
    platform_income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name='平台总收入')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '数据统计'
        verbose_name_plural = '数据统计'
    
    def __str__(self):
        return str(self.date)

# 公告模型
class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name='公告标题')
    content = models.TextField(verbose_name='公告内容')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '公告'
        verbose_name_plural = '公告'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

# 公告阅读记录模型
class AnnouncementRead(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='announcement_reads', verbose_name='用户')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='reads', verbose_name='公告')
    read_at = models.DateTimeField(auto_now_add=True, verbose_name='阅读时间')
    
    class Meta:
        verbose_name = '公告阅读记录'
        verbose_name_plural = '公告阅读记录'
        unique_together = ('user', 'announcement')
