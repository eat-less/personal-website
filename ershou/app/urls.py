from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    ProductLikeView,
    ProductFavoriteView,
    ProductCommentView,
    CheckUserActionView,
    UserFollowView,
    CheckFollowView,
    OrderCreateView,
    UserLikesView,
    UserFavoritesView,
    UserViewHistoryView,
    UserFollowingView,
    UserProductsView,
    UserSoldOrdersView,
    CategoryListView,
    MessageListView,
    TransactionView,
    OrderActionView,
    CommentCreateView,
    CommentListView,
    AdminProductManagementView,
    AdminStatisticsView,
    AdminOrderManagementView,
    AdminAnnouncementView,
    UserAnnouncementView,
    AnnouncementReadView,
    AdminCommentManagementView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('admin/products/', AdminProductManagementView.as_view(), name='admin-product-management'),
    path('admin/statistics/', AdminStatisticsView.as_view(), name='admin-statistics'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:product_id>/toggle-like/', ProductLikeView.as_view(), name='product-toggle-like'),
    path('products/<int:product_id>/toggle-favorite/', ProductFavoriteView.as_view(), name='product-toggle-favorite'),
    path('products/<int:product_id>/comments/', ProductCommentView.as_view(), name='product-comments'),
    path('products/<int:product_id>/comments/<int:comment_id>/', ProductCommentView.as_view(), name='product-comment-detail'),
    path('products/<int:product_id>/check-<str:action>/', CheckUserActionView.as_view(), name='check-user-action'),
    
    # 用户相关路由
    path('users/<int:user_id>/toggle-follow/', UserFollowView.as_view(), name='user-toggle-follow'),
    path('users/<int:user_id>/check-follow/', CheckFollowView.as_view(), name='check-follow'),
    
    # 订单相关路由
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    
    # 互动记录相关路由
    path('user/likes/', UserLikesView.as_view(), name='user-likes'),
    path('user/favorites/', UserFavoritesView.as_view(), name='user-favorites'),
    path('user/view-history/', UserViewHistoryView.as_view(), name='user-view-history'),
    path('user/following/', UserFollowingView.as_view(), name='user-following'),
    
    # 用户商品和订单相关路由
    path('users/<int:user_id>/products/', UserProductsView.as_view(), name='user-products'),
    path('users/<int:user_id>/sold-orders/', UserSoldOrdersView.as_view(), name='user-sold-orders'),
    
    # 私信相关路由
    path('messages/', MessageListView.as_view(), name='message-list'),
    path('messages/<int:user_id>/', MessageListView.as_view(), name='message-detail'),
    
    # 交易信息相关路由
    path('transactions/', TransactionView.as_view(), name='transaction-list'),
    path('transactions/<str:endpoint>/', TransactionView.as_view(), name='transaction-detail'),
    path('transactions/delete/<str:record_type>/<int:record_id>/', TransactionView.as_view(), name='transaction-delete'),
    path('transactions/orders/<int:order_id>/<str:action>/', OrderActionView.as_view(), name='order-action'),
    
    # 评价相关路由
    path('comments/create/', CommentCreateView.as_view(), name='comment-create'),
    path('products/<int:product_id>/reviews/', CommentListView.as_view(), name='product-reviews'),
    
    # 公告相关路由
    path('admin/announcements/', AdminAnnouncementView.as_view(), name='admin-announcements'),
    path('admin/announcements/<int:pk>/', AdminAnnouncementView.as_view(), name='admin-announcement-detail'),
    # 订单管理路由
    path('admin/orders/', AdminOrderManagementView.as_view(), name='admin-order-management'),
    path('admin/orders/<int:order_id>/', AdminOrderManagementView.as_view(), name='admin-order-detail'),
    path('admin/comments/', AdminCommentManagementView.as_view(), name='admin-comment-management'),
    path('admin/comments/<int:comment_id>/', AdminCommentManagementView.as_view(), name='admin-comment-detail'),
    path('user/announcements/', UserAnnouncementView.as_view(), name='user-announcements'),
    path('user/announcements/read/', AnnouncementReadView.as_view(), name='announcement-read')
]
