<template>
  <div class="product-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
        返回
      </button>
      <h1>商品详情</h1>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
      <button class="back-btn" @click="goBack">返回</button>
    </div>
    
    <!-- 商品不存在状态 -->
    <div v-else-if="!productData" class="error-container">
      <p>商品不存在或已被删除</p>
      <button class="back-btn" @click="goBack">返回</button>
    </div>
    
    <!-- 商品详情内容 -->
    <div v-else class="product-content">
      <!-- 卖家信息 -->
      <div class="seller-info">
        <div class="seller-header">
          <div class="seller-avatar" @click="viewSellerProfile">
            <img 
              v-if="productData.seller_avatar" 
              :src="productData.seller_avatar" 
              :alt="productData.seller_username"
            >
            <span v-else class="avatar-placeholder">{{ productData.seller_username?.charAt(0) || 'U' }}</span>
          </div>
          <div class="seller-details">
            <h3 class="seller-name">{{ productData.seller_username }}</h3>
            <div class="seller-stats">
              <span class="stat-item">信誉分: {{ productData.seller_reputation || 0 }}</span>
              <span class="stat-item">成交: {{ productData.seller_completed_transactions || 0 }}</span>
              <span v-if="productData.seller_address" class="stat-item">地址: {{ productData.seller_address }}</span>
            </div>
          </div>
          <div class="seller-actions">
            <button 
              class="follow-btn" 
              :class="{ 'following': isFollowing }"
              @click="toggleFollow"
            >
              {{ isFollowing ? '已关注' : '关注' }}
            </button>
            <button class="message-btn" @click="sendMessage">
              📩 私信
            </button>
          </div>
        </div>
      </div>
      
      <!-- 商品图片和信息 -->
      <div class="product-main">
        <!-- 商品图片 -->
        <div class="product-images">
          <div class="main-image">
            <img 
              v-if="productData.images && productData.images.length > 0" 
              :src="getImageUrl(productData.images[0].image)" 
              :alt="productData.title"
              class="main-img"
            >
            <span v-else class="image-placeholder">暂无图片</span>
          </div>
          <div class="thumbnail-list" v-if="productData.images && productData.images.length > 1">
            <div 
              class="thumbnail-item" 
              v-for="(image, index) in productData.images" 
              :key="index"
              :class="{ active: activeImageIndex === index }"
              @click="activeImageIndex = index"
            >
              <img :src="getImageUrl(image.image)" :alt="`商品图片${index+1}`">
            </div>
          </div>
        </div>
        
        <!-- 商品信息 -->
        <div class="product-info">
          <h2 class="product-title">{{ productData.title }}</h2>
          <p class="product-price">¥{{ productData.price }}</p>
          
          <div class="product-meta">
            <span class="meta-item">
              <span class="meta-label">分类:</span>
              <span class="meta-value">{{ productData.category?.name || '未分类' }}</span>
            </span>
            <span class="meta-item">
              <span class="meta-label">发布时间:</span>
              <span class="meta-value">{{ formatDate(productData.created_at) }}</span>
            </span>
            <span class="meta-item">
              <span class="meta-label">浏览:</span>
              <span class="meta-value">{{ productData.views }}</span>
            </span>
          </div>
          
          <!-- 配送信息 -->
          <div class="delivery-info">
            <div class="delivery-status" :class="{ 'delivery-enabled': productData.allow_delivery }">
              {{ productData.allow_delivery ? '🚚 支持配送' : '📍 买家自提' }}
            </div>
            <p v-if="productData.allow_delivery" class="delivery-fee">配送费: ¥2.00</p>
            <p class="stock-info">
              <span class="stock-label">库存:</span>
              <span :class="{ 'stock-low': productData.quantity <= 5, 'stock-out': productData.quantity === 0 }">
                {{ productData.quantity }} 件
                <span v-if="productData.quantity === 0" class="sold-out">已售罄</span>
              </span>
            </p>
            <p v-if="productData.status === 'removed'" class="product-status removed">
              ⚠️ 商品已下架
            </p>
          </div>
          
          <!-- 商品描述 -->
          <div class="product-description">
            <h3>商品描述</h3>
            <p>{{ productData.description }}</p>
          </div>
          
          <!-- 商品操作 -->
          <div class="product-actions">
            <button 
              class="action-btn like-btn" 
              :class="{ 'liked': isLiked }"
              @click="toggleLike"
            >
              <span class="action-icon">{{ isLiked ? '❤️' : '🤍' }}</span>
              <span class="action-text">{{ productData.likes_count || 0 }}</span>
            </button>
            <button 
              class="action-btn favorite-btn" 
              :class="{ 'favorited': isFavorited }"
              @click="toggleFavorite"
            >
              <span class="action-icon">{{ isFavorited ? '⭐' : '☆' }}</span>
              <span class="action-text">{{ productData.favorites_count || 0 }}</span>
            </button>
          </div>
          
          <!-- 购买区域 -->
          <div class="purchase-section">
            <div class="quantity-control">
              <label for="quantity">数量:</label>
              <div class="quantity-input">
                <button 
                  class="quantity-btn" 
                  @click="decreaseQuantity" 
                  :disabled="quantity <= 1"
                >-</button>
                <input 
                  type="number" 
                  id="quantity" 
                  v-model.number="quantity" 
                  min="1" 
                  :max="productData.quantity"
                  :disabled="productData.quantity === 0"
                >
                <button 
                  class="quantity-btn" 
                  @click="increaseQuantity" 
                  :disabled="quantity >= productData.quantity || productData.quantity === 0"
                >+</button>
              </div>
            </div>
            
            <!-- 配送方式选择 -->
            <div class="delivery-options" v-if="productData.allow_delivery">
              <label>配送方式:</label>
              <div class="delivery-radio">
                <label class="radio-option">
                  <input type="radio" v-model="deliveryMethod" value="self_pickup">
                  <span>买家自提</span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="deliveryMethod" value="delivery">
                  <span>支持配送 (+¥2.00)</span>
                </label>
              </div>
            </div>
            
            <!-- 购买按钮 -->
            <button 
              class="purchase-btn" 
              @click="showPurchaseModal = true"
              :disabled="productData.quantity === 0 || productData.status === 'removed'"
            >
              {{ productData.status === 'removed' ? '已下架' : (productData.quantity === 0 ? '已售罄' : '立即购买') }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 评论区 -->
      <div class="comments-section">
        <h3>商品评论</h3>
        
        <!-- 评论列表 -->
        <div class="comments-list" v-if="comments.length > 0">
          <div 
            v-for="comment in displayedComments" 
            :key="comment.id" 
            class="comment-item"
          >
            <div class="comment-header">
              <div class="comment-user">
                <div class="user-avatar">
                  <img v-if="comment.user_avatar" :src="comment.user_avatar" :alt="comment.user_username">
                  <span v-else class="avatar-placeholder">{{ comment.user_username?.charAt(0) || 'U' }}</span>
                </div>
                <span class="user-name">{{ comment.user_username }}</span>
                <span v-if="comment.is_reply && comment.reply_to" class="reply-to">
                  回复 {{ comment.reply_to }}
                </span>
              </div>
              <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
              <div v-if="isOwnComment(comment)" class="comment-actions">
                <button class="delete-btn" @click="deleteComment(comment.id)">
                  删除
                </button>
              </div>
            </div>
            
            <!-- 评分 -->
            <div v-if="comment.rating" class="comment-rating">
              <div class="stars">
                <span 
                  v-for="star in 5" 
                  :key="star"
                  :class="['star', { active: comment.rating >= star }]"
                >
                  ★
                </span>
              </div>
            </div>
            
            <div class="comment-content">{{ comment.content }}</div>
            
            <!-- 评价图片 -->
            <div v-if="comment.image" class="comment-image">
              <img :src="comment.image" :alt="'评价图片'" class="review-image">
            </div>
            
            <div class="comment-footer">
              <button class="reply-btn" @click="showReplyForm(comment.id, comment.user_username)">
                回复
              </button>
            </div>
            
            <!-- 回复表单 -->
            <div v-if="replyingTo === comment.id" class="reply-form">
              <textarea 
                v-model="replyContent" 
                :placeholder="'回复 ' + comment.user_username + '...'"
                rows="2"
              ></textarea>
              <div class="reply-actions">
                <div class="image-upload-btn" @click="handleReplyImageUploadClick(comment.id)">
                  <span class="upload-icon">+</span>
                  <input 
                    type="file" 
                    :ref="el => { if (el) replyFileInputs[comment.id] = el }"
                    accept="image/*"
                    @change="handleReplyImageUpload"
                    style="display: none"
                  >
                </div>
                <button class="cancel-reply-btn" @click="cancelReply">
                  取消
                </button>
                <button class="submit-reply-btn" @click="submitReply(comment.id, comment.user_username)" :disabled="!replyContent.trim() && !replyImage">
                  发表回复
                </button>
              </div>
              <!-- 回复图片预览 -->
              <div v-if="replyImage" class="comment-image-preview">
                <img :src="replyImage" :alt="'回复图片'" class="preview-image">
                <button class="remove-image-btn" @click="removeReplyImage">×</button>
              </div>
            </div>
          </div>
          
          <!-- 展开/收起评论 -->
          <div v-if="comments.length > 2" class="expand-comments">
            <button @click="toggleComments" class="expand-btn">
              {{ showAllComments ? '收起评论' : `查看全部 ${comments.length} 条评论` }}
            </button>
          </div>
        </div>
        
        <!-- 无评论状态 -->
        <div v-else class="empty-comments">
          <p>暂无评论，快来发表第一条评论吧！</p>
        </div>
        
        <!-- 评论输入 -->
        <div class="comment-input-section">
          <textarea 
            v-model="commentContent" 
            placeholder="写下你的评论..."
            rows="3"
          ></textarea>
          <div class="comment-input-actions">
            <div class="image-upload-btn" @click="handleCommentImageUploadClick">
              <span class="upload-icon">+</span>
              <input 
                type="file" 
                ref="commentFileInput"
                accept="image/*"
                @change="handleCommentImageUpload"
                style="display: none"
              >
            </div>
            <button class="submit-comment-btn" @click="submitComment" :disabled="!commentContent.trim() && !commentImage">
              发表评论
            </button>
          </div>
          <!-- 评论图片预览 -->
          <div v-if="commentImage" class="comment-image-preview">
            <img :src="commentImage" :alt="'评论图片'" class="preview-image">
            <button class="remove-image-btn" @click="removeCommentImage">×</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 购买确认模态框 -->
    <div class="modal" v-if="showPurchaseModal" @click="closePurchaseModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>确认购买</h3>
          <button class="close-btn" @click="closePurchaseModal">&times;</button>
        </div>
        <div class="modal-body">
          <!-- 购买提醒 -->
          <div class="purchase-warning">
            <p class="warning-text">⚠️ 现场验货，确认收货后概不负责</p>
          </div>
          
          <!-- 订单信息 -->
          <div class="order-info">
            <div class="order-item">
              <span class="order-label">商品名称:</span>
              <span class="order-value">{{ productData?.title || '' }}</span>
            </div>
            <div class="order-item">
              <span class="order-label">单价:</span>
              <span class="order-value">¥{{ productData?.price || '0.00' }}</span>
            </div>
            <div class="order-item">
              <span class="order-label">数量:</span>
              <span class="order-value">{{ quantity }}</span>
            </div>
            <div v-if="productData?.allow_delivery && deliveryMethod === 'delivery'" class="order-item">
              <span class="order-label">配送费:</span>
              <span class="order-value">¥2.00</span>
            </div>
            <div class="order-total">
              <span class="order-label">总计:</span>
              <span class="order-value total-price">¥{{ calculateTotalPrice() }}</span>
            </div>
          </div>
          
          <!-- 配送方式 -->
          <div class="order-delivery">
            <h4>配送方式:</h4>
            <p>{{ deliveryMethod === 'delivery' ? '支持配送' : '买家自提' }}</p>
          </div>
          
          <!-- 支付方式 -->
          <div class="payment-options">
            <h4>支付方式:</h4>
            <div class="payment-radio">
              <label class="radio-option">
                <input type="radio" v-model="paymentMethod" value="wechat" checked>
                <img src="@/assets/wxPay.png" class="payment-image wechat-image" alt="微信支付">
                <span>微信支付</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="paymentMethod" value="alipay">
                <img src="@/assets/aliPay.png" class="payment-image alipay-image" alt="支付宝支付">
                <span>支付宝支付</span>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closePurchaseModal">取消</button>
          <button 
            class="btn-primary" 
            @click="confirmPurchase"
            :disabled="!productData || productData.status === 'removed' || (productData.quantity < quantity)"
          >
            {{ !productData ? '加载中...' : productData.status === 'removed' ? '已下架' : (productData.quantity < quantity ? '库存不足' : '确认购买') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../axios';

const route = useRoute();
const router = useRouter();
const productId = route.params.id;

// 响应式数据
const loading = ref(true);
const error = ref('');
const productData = ref(null);
const comments = ref([]);
const quantity = ref(1);
const deliveryMethod = ref('self_pickup');
const paymentMethod = ref('wechat'); // 默认微信支付
const commentContent = ref('');
const commentImage = ref('');
const replyContent = ref('');
const replyImage = ref('');
const showPurchaseModal = ref(false);
const isLiked = ref(false);
const isFavorited = ref(false);
const isFollowing = ref(false);
const activeImageIndex = ref(0);
const replyingTo = ref(null);
const replyTo = ref(null);
const showAllComments = ref(false);
const commentFileInput = ref(null);
const replyFileInputs = ref({}); // 使用对象存储每个评论的回复文件输入ref



// 计算总价
const calculateTotalPrice = () => {
  if (!productData.value) return '0.00';
  const basePrice = parseFloat(productData.value.price) * quantity.value;
  const deliveryFee = productData.value.allow_delivery && deliveryMethod.value === 'delivery' ? 2.00 : 0;
  return (basePrice + deliveryFee).toFixed(2);
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
};

// 数量控制
const increaseQuantity = () => {
  if (productData.value && quantity.value < productData.value.quantity) {
    quantity.value++;
  }
};

const decreaseQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--;
  }
};

// 获取商品详情
const fetchProductDetail = async () => {
  try {
    const response = await api.get(`/products/${productId}/`);
    productData.value = response.data;
    
    // 检查本地存储中是否有该卖家的头像信息
    const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
    if (productData.value.seller_username && userAvatars[productData.value.seller_username]) {
      productData.value.seller_avatar = userAvatars[productData.value.seller_username];
    }
    
    // 初始化配送方式
    if (productData.value.allow_delivery) {
      deliveryMethod.value = 'self_pickup';
    }
    
    // 获取卖家的最新信息，确保信誉分和成交数量与个人中心同步
    if (productData.value && productData.value.seller_id) {
      try {
        const sellerResponse = await api.get(`/accounts/user-info/${productData.value.seller_id}/`);
        if (sellerResponse.data && sellerResponse.data.profile) {
          // 更新卖家的信誉分和成交数量
          productData.value.seller_reputation = sellerResponse.data.profile.reputation;
          productData.value.seller_completed_transactions = sellerResponse.data.profile.completed_transactions;
          // 更新卖家的地址
          productData.value.seller_address = sellerResponse.data.profile.address;
        }
      } catch (sellerError) {
        console.error('获取卖家信息失败:', sellerError);
        // 如果获取卖家信息失败，不影响商品详情的显示
      }
    }
    
    // 检查用户操作状态
    checkUserActions();
  } catch (error) {
    if (error.response?.status === 404) {
      error.value = '商品不存在或已被删除';
    } else {
      error.value = '获取商品详情失败，请稍后重试';
    }
  } finally {
    loading.value = false;
  }
};

// 获取评论
const fetchComments = async () => {
  try {
    const response = await api.get(`/products/${productId}/reviews/`);
    let commentsData = response.data;
    
    // 检查本地存储中是否有评论用户的头像信息
    const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
    
    // 更新评论中的头像，包括其他用户的头像
    commentsData = commentsData.map(comment => {
      // 检查本地存储中是否有该评论用户的头像
      if (comment.user_username && userAvatars[comment.user_username]) {
        return {
          ...comment,
          user_avatar: userAvatars[comment.user_username]
        };
      }
      return comment;
    });
    
    comments.value = commentsData;
    
    // 评论加载完成后更新评论头像
    updateCommentAvatars();
  } catch (error) {
    console.error('获取评论失败:', error);
  }
};

// 检查用户操作状态
const checkUserActions = async () => {
  try {
    // 检查点赞状态
    const likeResponse = await api.get(`/products/${productId}/check-like/`);
    isLiked.value = likeResponse.data.liked;
    
    // 检查收藏状态
    const favoriteResponse = await api.get(`/products/${productId}/check-favorite/`);
    isFavorited.value = favoriteResponse.data.favorited;
    
    // 检查关注状态
    if (productData.value && productData.value.seller_id) {
      const followResponse = await api.get(`/users/${productData.value.seller_id}/check-follow/`);
      isFollowing.value = followResponse.data.following;
    }
  } catch (error) {
  }
};

// 切换点赞
const toggleLike = async () => {
  try {
    const response = await api.post(`/products/${productId}/toggle-like/`);
    isLiked.value = response.data.liked;
    if (productData.value) {
      productData.value.likes_count = response.data.likes_count;
    }
  } catch (error) {
  }
};

// 切换收藏
const toggleFavorite = async () => {
  try {
    const response = await api.post(`/products/${productId}/toggle-favorite/`);
    isFavorited.value = response.data.favorited;
    if (productData.value) {
      productData.value.favorites_count = response.data.favorites_count;
    }
  } catch (error) {
  }
};

// 切换关注
const toggleFollow = async () => {
  try {
    if (!productData.value) return;
    const response = await api.post(`/users/${productData.value.seller_id}/toggle-follow/`);
    isFollowing.value = response.data.following;
  } catch (error) {
  }
};

// 发送私信
const sendMessage = () => {
  if (!productData.value) return;
  router.push(`/messages/${productData.value.seller_id}`);
};

// 查看卖家资料
const viewSellerProfile = () => {
  if (!productData.value) return;
  router.push(`/profile/${productData.value.seller_id}`);
};

// 计算显示的评论
const displayedComments = computed(() => {
  if (showAllComments.value || comments.value.length <= 2) {
    return comments.value;
  }
  return comments.value.slice(0, 2);
});

// 检查是否是自己的评论
const isOwnComment = (comment) => {
  const user = JSON.parse(localStorage.getItem('user'));
  return user && (comment.user_id === user.id || comment.user === user.id);
};

// 显示回复表单
const showReplyForm = (commentId, replyToUsername) => {
  replyingTo.value = commentId;
  replyTo.value = replyToUsername;
};

// 处理回复图片上传按钮点击
const handleReplyImageUploadClick = (commentId) => {
  const fileInput = replyFileInputs.value[commentId];
  if (fileInput && typeof fileInput.click === 'function') {
    fileInput.click();
  }
};

// 处理回复图片上传
const handleReplyImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      replyImage.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

// 移除回复图片
const removeReplyImage = () => {
  replyImage.value = '';
  if (replyingTo.value && replyFileInputs.value[replyingTo.value]) {
    replyFileInputs.value[replyingTo.value].value = '';
  }
};

// 取消回复
const cancelReply = () => {
  if (replyingTo.value && replyFileInputs.value[replyingTo.value]) {
    replyFileInputs.value[replyingTo.value].value = '';
  }
  replyingTo.value = null;
  replyContent.value = '';
  replyTo.value = null;
  replyImage.value = '';
};

// 提交回复
const submitReply = async (commentId, replyToUsername) => {
  const replyFileInput = replyFileInputs.value[commentId];
  if (!replyContent.value.trim() && !replyFileInput?.files[0]) return;
  
  try {
    const formData = new FormData();
    formData.append('product', productId);
    formData.append('content', replyContent.value.trim() || '');
    formData.append('reply_to', replyToUsername);
    
    // 如果有图片，添加到formData
    if (replyFileInput && replyFileInput.files[0]) {
      formData.append('image', replyFileInput.files[0]);
    }
    
    const response = await api.post('/comments/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    const newComment = {
      ...response.data,
      is_reply: true,
      reply_to: replyToUsername
    };
    
    // 找到被回复评论的位置，在其后面插入回复
    const commentIndex = comments.value.findIndex(comment => comment.id === commentId);
    if (commentIndex !== -1) {
      comments.value.splice(commentIndex + 1, 0, newComment);
    } else {
      // 如果找不到被回复的评论，就添加到末尾
      comments.value.push(newComment);
    }
    
    replyContent.value = '';
    replyImage.value = '';
    replyingTo.value = null;
    // 清空replyFileInputs中对应的元素
    if (replyFileInputs.value[commentId]) {
      replyFileInputs.value[commentId].value = '';
    }
  } catch (error) {
    console.error('提交回复失败:', error);
    console.error('错误详情:', error.response?.data);
    console.error('请求URL:', error.config?.url);
    console.error('请求数据:', {
      product: productId,
      content: replyContent.value.trim() || '',
      reply_to: replyToUsername,
      hasImage: !!replyFileInputs.value[commentId]?.files[0]
    });
    alert('提交回复失败，请稍后重试');
  }
};

// 删除评论
const deleteComment = async (commentId) => {
  if (!confirm('确定要删除这条评论吗？')) return;
  
  try {
    const response = await api.delete(`/products/${productId}/comments/${commentId}/`);
    comments.value = comments.value.filter(comment => comment.id !== commentId);
  } catch (error) {
    alert('删除评论失败，请稍后重试');
  }
};

// 切换评论显示
const toggleComments = () => {
  showAllComments.value = !showAllComments.value;
};

// 处理评论图片上传按钮点击
const handleCommentImageUploadClick = () => {
  if (commentFileInput.value) {
    commentFileInput.value.click();
  }
};

// 处理评论图片上传
const handleCommentImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      commentImage.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

// 移除评论图片
const removeCommentImage = () => {
  commentImage.value = '';
  if (commentFileInput.value) {
    commentFileInput.value.value = '';
  }
};

// 提交评论
const submitComment = async () => {
  if (!commentContent.value.trim() && !commentFileInput.value?.files[0]) return;
  
  try {
    const formData = new FormData();
    formData.append('product', productId);
    formData.append('content', commentContent.value.trim() || '');
    
    // 如果有图片，添加到formData
    if (commentFileInput.value && commentFileInput.value.files[0]) {
      formData.append('image', commentFileInput.value.files[0]);
    }
    
    await api.post('/comments/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    // 重新获取所有评论以保持正确顺序
    await fetchComments();
    commentContent.value = '';
    commentImage.value = '';
    if (commentFileInput.value) {
      commentFileInput.value.value = '';
    }
  } catch (error) {
    alert('提交评论失败，请稍后重试');
  }
};

// 关闭购买模态框
const closePurchaseModal = () => {
  showPurchaseModal.value = false;
};

// 确认购买
const confirmPurchase = async () => {
  try {
    // 先检查商品状态
    if (productData.value.status === 'removed') {
      alert('该商品已下架，无法购买');
      return;
    }
    
    // 检查库存
    if (productData.value.quantity < quantity.value) {
      alert('库存不足，无法购买');
      return;
    }
    
    const response = await api.post('/orders/create/', {
      product_id: parseInt(productId),
      quantity: parseInt(quantity.value),
      delivery_method: deliveryMethod.value,
      payment_method: paymentMethod.value
    });
    alert('购买成功！');
    showPurchaseModal.value = false;
    // 跳转到交易信息页面，查看已买到的订单
    router.push('/transactions');
  } catch (error) {
    // 尝试获取错误信息
    const errorMessage = error.response?.data?.error || '购买失败，请稍后重试';
    alert(errorMessage);
  }
};

// 更新卖家头像（如果是当前登录用户）
const updateSellerAvatar = () => {
  if (!productData.value) return;
  
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
  const currentProfile = JSON.parse(localStorage.getItem('profile') || '{}');
  
  // 检查当前商品的卖家是否是当前登录用户，并且本地存储中有当前用户的头像
  if (currentUser.username && currentUser.username === productData.value.seller_username && currentProfile.avatar) {
    // 更新卖家头像为本地存储中的Base64头像
    productData.value.seller_avatar = currentProfile.avatar;
  }
};

// 更新评论中的用户头像
const updateCommentAvatars = () => {
  if (!comments.value || comments.value.length === 0) return;
  
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
  const currentProfile = JSON.parse(localStorage.getItem('profile') || '{}');
  
  // 只有当本地存储中有当前用户的头像时，才更新评论头像
  if (currentUser.username && currentProfile.avatar) {
    // 遍历评论列表，只更新当前用户的评论头像
    comments.value = comments.value.map(comment => {
      if (comment.user_username === currentUser.username) {
        return {
          ...comment,
          user_avatar: currentProfile.avatar
        };
      }
      return comment;
    });
  }
};

// 更新所有头像
const updateAllAvatars = () => {
  updateSellerAvatar();
  updateCommentAvatars();
};

// 监听storage事件，当其他标签页更新sessionStorage时同步更新
window.addEventListener('storage', (event) => {
  if (event.key === 'profile' || event.key === 'user') {
    updateAllAvatars();
  }
});

// 获取卖家的最新信息
const fetchSellerInfo = async () => {
  if (!productData.value || !productData.value.seller_id) return;
  
  try {
    const sellerResponse = await api.get(`/accounts/user-info/${productData.value.seller_id}/`);
    if (sellerResponse.data && sellerResponse.data.profile) {
      // 更新卖家的信誉分
      productData.value.seller_reputation = sellerResponse.data.profile.reputation;
      // 更新卖家的地址
      productData.value.seller_address = sellerResponse.data.profile.address;
      
      // 获取卖家的卖出订单并计算已完成的数量
      try {
        const soldOrdersResponse = await api.get(`/users/${productData.value.seller_id}/sold-orders/`);
        const orders = soldOrdersResponse.data;
        // 计算已完成的订单数量
        productData.value.seller_completed_transactions = orders.filter(order => order.status === 'completed').length;
      } catch (ordersError) {
        console.error('获取卖家卖出订单失败:', ordersError);
      }
    }
  } catch (sellerError) {
    console.error('获取卖家信息失败:', sellerError);
  }
};

// 定时刷新卖家信息
const startSellerInfoRefresh = () => {
  // 每30秒刷新一次卖家信息
  const refreshInterval = setInterval(() => {
    fetchSellerInfo();
  }, 30000);
  
  // 组件卸载时清除定时器
  return () => {
    clearInterval(refreshInterval);
  };
};

// 获取图片完整URL
const getImageUrl = (imagePath) => {
  if (!imagePath) return '';
  // 检查是否已经是完整的绝对路径
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  // 如果是相对路径，添加后端服务器基础URL
  return `http://127.0.0.1:8000${imagePath}`;
};

// 页面挂载
onMounted(() => {
  fetchProductDetail();
  fetchComments();
  
  // 页面加载后更新所有头像
  setTimeout(() => {
    updateAllAvatars();
  }, 0);
  
  // 启动定时刷新卖家信息
  startSellerInfoRefresh();
});


</script>

<style scoped>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.product-detail-container {
  max-width: 1200px;
  margin: 30px auto;
  padding: 30px;
  min-height: calc(100vh - 60px);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  text-align: center;
  background-color: #fff5f5;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.error-container p {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid linear-gradient(90deg, #667eea, #764ba2);
  position: relative;
}

.page-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.back-icon {
  font-size: 18px;
  font-weight: bold;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  animation: fadeInDown 0.5s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卖家信息 */
.seller-info {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 25px;
  border-radius: 15px;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.6s ease-out;
}

.seller-header {
  display: flex;
  align-items: center;
  gap: 25px;
}

.seller-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  position: relative;
}

.seller-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.seller-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.seller-details {
  flex: 1;
}

.seller-name {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 22px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.seller-stats {
  display: flex;
  gap: 25px;
  font-size: 16px;
  color: #666;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 15px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.seller-actions {
  display: flex;
  gap: 15px;
}

.follow-btn, .message-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.follow-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.follow-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
}

.follow-btn.following {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.message-btn {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.message-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(67, 233, 123, 0.4);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 商品主体 */
.product-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}

/* 商品图片 */
.product-images {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: fadeInUp 0.7s ease-out;
}

.main-image {
  width: 100%;
  height: 500px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: all 0.3s ease;
}

.main-image:hover {
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.main-img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  transition: all 0.5s ease;
  border-radius: 10px;
}

.main-image:hover .main-img {
  transform: scale(1.05);
}

.image-placeholder {
  color: #666;
  font-size: 18px;
  font-weight: 500;
  padding: 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.thumbnail-list {
  display: flex;
  gap: 15px;
  overflow-x: auto;
  padding: 15px 0;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.thumbnail-list::-webkit-scrollbar {
  height: 6px;
}

.thumbnail-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.thumbnail-list::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
}

.thumbnail-item {
  width: 100px;
  height: 100px;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  border: 3px solid transparent;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.thumbnail-item:hover {
  border-color: #667eea;
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.thumbnail-item.active {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.thumbnail-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

.thumbnail-item:hover img {
  transform: scale(1.1);
}

/* 商品信息 */
.product-info {
  display: flex;
  flex-direction: column;
  gap: 25px;
  animation: fadeInUp 0.8s ease-out;
}

.product-title {
  margin: 0;
  font-size: 28px;
  color: #333;
  font-weight: 700;
  line-height: 1.3;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.product-price {
  margin: 0;
  font-size: 36px;
  color: #ff4757;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(255, 71, 87, 0.3);
  display: flex;
  align-items: center;
  gap: 10px;
}

.product-price::before {
  content: '';
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%);
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
}

.product-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.meta-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.meta-label {
  font-weight: 600;
  color: #333;
}

/* 配送信息 */
.delivery-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 25px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.delivery-status {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.delivery-enabled {
  color: #27ae60;
  background: rgba(39, 174, 96, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(39, 174, 96, 0.3);
}

.delivery-fee {
  margin: 0;
  font-size: 16px;
  color: #666;
  background: rgba(255, 255, 255, 0.8);
  padding: 8px 16px;
  border-radius: 20px;
  align-self: flex-start;
}

.stock-info {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.stock-low {
  color: #e67e22;
  background: rgba(230, 126, 34, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(230, 126, 34, 0.3);
}

.stock-out {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
}

.sold-out {
  margin-left: 10px;
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  font-size: 14px;
  padding: 5px 12px;
  border-radius: 20px;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
}

.product-status {
  font-weight: bold;
  margin-top: 10px;
  padding: 10px 20px;
  border-radius: 20px;
  display: inline-block;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.product-status.removed {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
}

/* 商品描述 */
.product-description {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 25px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.product-description h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.product-description p {
  margin: 0;
  font-size: 16px;
  color: #666;
  line-height: 1.8;
  background: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 商品操作 */
.product-actions {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  flex: 1;
  justify-content: center;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.action-btn.liked {
  background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
}

.action-btn.favorited {
  background: linear-gradient(135deg, #f39c12 0%, #f1c40f 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
}

.action-btn:not(.liked):not(.favorited) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-icon {
  font-size: 20px;
}

.action-text {
  font-weight: 600;
}

/* 购买区域 */
.purchase-section {
  display: flex;
  flex-direction: column;
  gap: 25px;
  padding: 30px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.quantity-control label {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  background: rgba(255, 255, 255, 0.8);
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quantity-input {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.8);
  padding: 10px 20px;
  border-radius: 50px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.quantity-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.quantity-btn:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.quantity-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.quantity-input input {
  width: 80px;
  height: 40px;
  border: 2px solid #667eea;
  border-radius: 20px;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quantity-input input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.delivery-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.delivery-options label {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.delivery-radio {
  display: flex;
  gap: 25px;
  flex-wrap: wrap;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  padding: 10px 20px;
  background: #f8f9fa;
  border-radius: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.radio-option:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: #e9ecef;
}

.radio-option input[type="radio"] {
  width: 18px;
  height: 18px;
  accent-color: #667eea;
}

.purchase-btn {
  padding: 20px;
  border: none;
  border-radius: 50px;
  font-size: 20px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(255, 71, 87, 0.3);
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.purchase-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #ff6b81 0%, #ff4757 100%);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(255, 71, 87, 0.4);
}

.purchase-btn:disabled {
  background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  text-shadow: none;
}

/* 评论区 */
.comments-section {
  margin-top: 40px;
  padding-top: 40px;
  border-top: 3px solid linear-gradient(90deg, #667eea, #764ba2);
  position: relative;
  animation: fadeInUp 0.9s ease-out;
}

.comments-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
}

.comments-section h3 {
  margin: 0 0 30px 0;
  font-size: 24px;
  color: #333;
  font-weight: 700;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
}

.comments-section h3::before {
  content: '';
  width: 10px;
  height: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 5px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
  margin-bottom: 40px;
}

.comment-item {
  padding: 25px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.comment-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 15px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.user-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.reply-to {
  font-size: 14px;
  color: #666;
  background: rgba(255, 255, 255, 0.8);
  padding: 5px 12px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comment-time {
  font-size: 14px;
  color: #999;
  background: rgba(255, 255, 255, 0.8);
  padding: 5px 12px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comment-actions {
  display: flex;
  gap: 10px;
}

.delete-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
}

.delete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 71, 87, 0.4);
}

.comment-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  margin: 10px 0;
  background: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 评论评分 */
.comment-rating {
  margin: 10px 0;
  background: rgba(255, 255, 255, 0.8);
  padding: 10px 20px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  align-self: flex-start;
}

.comment-rating .stars {
  display: flex;
  gap: 8px;
}

.comment-rating .star {
  font-size: 20px;
  color: #ccc;
  transition: all 0.3s ease;
}

.comment-rating .star.active {
  color: #ffd700;
  text-shadow: 0 2px 4px rgba(255, 215, 0, 0.5);
}

/* 评论图片 */
.comment-image {
  margin: 15px 0;
}

.review-image {
  max-width: 250px;
  max-height: 250px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  overflow: hidden;
}

/* 强制隐藏滚动条 */
.modal-content {
  /* 隐藏滚动条但保持功能 */
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

.modal-content::-webkit-scrollbar {
  display: none;  /* Chrome, Safari and Opera */
}

.modal-content {
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 600px;
  min-height: 600px;
  height: auto;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 15px 15px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 20px;
  overflow: hidden;
  height: auto;
  min-height: 400px;
}

.purchase-warning {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
}

.warning-text {
  margin: 0;
  color: #856404;
  font-size: 14px;
  font-weight: 500;
}

.order-info {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
}

.order-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.order-label {
  font-weight: 600;
  color: #495057;
}

.order-value {
  color: #212529;
}

.order-total {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 2px solid #dee2e6;
  font-weight: 600;
}

.total-price {
  color: #dc3545;
  font-size: 18px;
}

.order-delivery {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
}

.order-delivery h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #495057;
}

.order-delivery p {
  margin: 0;
  color: #212529;
}

.payment-options {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
}

.payment-options h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #495057;
}

.payment-radio {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.payment-radio .radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #495057;
  cursor: pointer;
  padding: 8px 16px;
  background: white;
  border-radius: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.payment-radio .radio-option:hover {
  background: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.payment-radio .radio-option input[type="radio"] {
  width: 16px;
  height: 16px;
  accent-color: #667eea;
}

.payment-image {
  width: 24px;
  height: 24px;
  margin-right: 8px;
  vertical-align: middle;
  border-radius: 4px;
}

.payment-radio .radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #495057;
  cursor: pointer;
  padding: 10px 20px;
  background: white;
  border-radius: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px;
  border-top: 1px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 0 0 15px 15px;
}

.btn-secondary {
  padding: 12px 24px;
  border: 1px solid #ced4da;
  border-radius: 25px;
  background: white;
  color: #495057;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.btn-primary {
  padding: 12px 24px;
  border: none;
  border-radius: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.review-image:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.comment-footer {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 2px solid #f0f0f0;
}

.reply-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.reply-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* 回复表单 */
.reply-form {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.reply-form textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #667eea;
  border-radius: 10px;
  font-size: 16px;
  resize: vertical;
  min-height: 100px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.reply-form textarea:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.reply-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  justify-content: flex-end;
}

.reply-actions .image-upload-btn {
  margin-right: auto;
}

.cancel-reply-btn, .submit-reply-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.cancel-reply-btn {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
}

.cancel-reply-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(149, 165, 166, 0.4);
}

.submit-reply-btn {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
}

.submit-reply-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
}

.submit-reply-btn:disabled {
  background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 展开/收起评论 */
.expand-comments {
  margin: 30px 0;
  text-align: center;
}

.expand-btn {
  padding: 12px 30px;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.expand-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* 无评论状态 */
.empty-comments {
  padding: 60px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 15px;
  text-align: center;
  margin-bottom: 40px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.empty-comments p {
  margin: 0;
  font-size: 18px;
  color: #666;
  background: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 评论输入 */
.comment-input-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 30px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.comment-input-section textarea {
  width: 100%;
  padding: 20px;
  border: 2px solid #667eea;
  border-radius: 10px;
  font-size: 16px;
  resize: vertical;
  min-height: 150px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comment-input-section textarea:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.comment-input-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  justify-content: flex-end;
}

/* 图片上传按钮 */
.image-upload-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.image-upload-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.upload-icon {
  font-size: 24px;
  font-weight: bold;
  color: white;
}

.submit-comment-btn {
  padding: 12px 30px;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}

.submit-comment-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
}

.submit-comment-btn:disabled {
  background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 评论图片预览 */
.comment-image-preview {
  position: relative;
  display: inline-block;
  margin: 15px 0;
}

.comment-image-preview .preview-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.comment-image-preview .preview-image:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.remove-image-btn {
  position: absolute;
  top: -12px;
  right: -12px;
  background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
}

.remove-image-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(255, 71, 87, 0.4);
}

/* 回复表单 */
.reply-form {
  margin-top: 15px;
  padding: 15px;
  background-color: #f0f0f0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reply-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
}

.reply-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
}

.reply-actions .image-upload-btn {
  margin-right: auto;
}

.cancel-reply-btn, .submit-reply-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-reply-btn {
  background-color: white;
  color: #333;
}

.cancel-reply-btn:hover {
  background-color: #f0f0f0;
}

.submit-reply-btn {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

.submit-reply-btn:hover:not(:disabled) {
  background-color: #2980b9;
}

.submit-reply-btn:disabled {
  background-color: #bdc3c7;
  border-color: #bdc3c7;
  cursor: not-allowed;
}

/* 模态框 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 25px;
  border-bottom: 2px solid #f0f0f0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px 20px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: white;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: white;
  transition: all 0.3s ease;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.close-btn:hover {
  transform: rotate(90deg);
  color: #f0f0f0;
}

.modal-body {
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.purchase-warning {
  padding: 20px;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border: none;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(255, 234, 167, 0.3);
}

.warning-text {
  margin: 0;
  font-size: 16px;
  color: #856404;
  font-weight: 500;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: rgba(255, 255, 255, 0.8);
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(249, 249, 249, 0.8);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.order-item:hover {
  background: rgba(240, 240, 240, 0.8);
  transform: translateX(5px);
}

.order-label {
  font-weight: 600;
  color: #666;
  font-size: 16px;
}

.order-value {
  font-weight: 700;
  color: #333;
  font-size: 16px;
}

.order-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 15px;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-radius: 10px;
  margin-top: 10px;
  box-shadow: 0 4px 15px rgba(187, 222, 251, 0.3);
}

.total-price {
  font-size: 20px;
  color: #ff4757;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(255, 71, 87, 0.3);
}

.order-delivery {
  padding: 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.order-delivery h4 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.order-delivery p {
  margin: 0;
  font-size: 16px;
  color: #666;
  background: rgba(249, 249, 249, 0.8);
  padding: 10px 15px;
  border-radius: 10px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 25px;
  border-top: 2px solid #f0f0f0;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0 0 20px 20px;
}

.btn-secondary, .btn-primary {
  padding: 12px 24px;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-secondary {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(149, 165, 166, 0.4);
}

.btn-primary {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
}

.btn-primary:disabled {
  background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .product-detail-container {
    margin: 10px auto;
    padding: 20px;
    min-height: calc(100vh - 20px);
  }
  
  .page-header {
    margin-bottom: 20px;
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .back-btn {
    padding: 10px 16px;
    font-size: 14px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .seller-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .seller-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .follow-btn, .message-btn {
    flex: 1;
    text-align: center;
  }
  
  .product-main {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .main-image {
    height: 300px;
  }
  
  .product-title {
    font-size: 24px;
  }
  
  .product-price {
    font-size: 28px;
  }
  
  .product-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .quantity-control {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .product-actions {
    flex-wrap: wrap;
  }
  
  .action-btn {
    flex: 1;
    min-width: 120px;
    padding: 10px 16px;
  }
  
  .purchase-btn {
    padding: 16px;
    font-size: 18px;
  }
  
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-header {
    padding: 20px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-footer {
    padding: 20px;
  }
  
  .comment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .comment-content {
    padding: 15px;
  }
  
  .reply-form {
    padding: 15px;
  }
  
  .comment-input-section {
    padding: 20px;
  }
  
  .comment-input-section textarea {
    min-height: 120px;
  }
  
  .submit-comment-btn {
    padding: 10px 24px;
  }
}
</style>