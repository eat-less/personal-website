<template>
  <div class="transactions-container">
    <!-- 页面头部 -->
    <div class="transactions-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1>交易信息</h1>
    </div>
    
    <!-- 标签页导航 -->
    <div class="transactions-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>
    
    <!-- 内容区域 -->
    <div class="transactions-content">
      <!-- 我的发布 -->
      <div v-if="activeTab === 'my-products'" class="tab-content">
        <h2 class="tab-title">我的发布</h2>
        
        <!-- 商品列表 -->
        <div class="products-grid" v-if="myProducts.length > 0">
          <div 
            v-for="product in myProducts" 
            :key="product.id"
            class="product-card"
            @click="goToProductDetail(product.id)"
          >
            <div class="product-image">
              <img 
                v-if="product.images && product.images.length > 0" 
                :src="product.images[0]" 
                :alt="product.title"
              >
              <span v-else class="no-image">暂无图片</span>
              <div 
                class="product-status" 
                :class="`status-${product.status}`"
              >
                {{ getStatusText(product.status) }}
              </div>
            </div>
            <div class="product-info">
              <h3 class="product-title">{{ product.title }}</h3>
              <p class="product-price">¥{{ product.price.toFixed(2) }}</p>
              <div class="product-meta">
                <span class="product-quantity">库存: {{ product.quantity }}</span>
                <span class="product-date">{{ formatDate(product.created_at) }}</span>
              </div>
            </div>
            <div class="product-actions">
              <button 
                class="action-btn下架" 
                @click.stop="toggleProductStatus(product)"
                :disabled="product.status === 'removed'"
              >
                {{ product.status === 'removed' ? '已下架' : '下架' }}
              </button>
              <button 
                class="action-btn-delete" 
                @click.stop="deleteRecord('product', product.id, product)"
              >
                删除
              </button>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div class="empty-state" v-else>
          <div class="empty-icon">📦</div>
          <p>你还没有发布任何商品</p>
          <button class="publish-btn" @click="goToPublish">去发布</button>
        </div>
      </div>
      
      <!-- 已卖出订单 -->
      <div v-if="activeTab === 'sold-orders'" class="tab-content">
        <h2 class="tab-title">已卖出订单</h2>
        
        <!-- 订单列表 -->
        <div class="orders-list" v-if="soldOrders.length > 0">
          <div 
            v-for="order in soldOrders" 
            :key="order.id"
            class="order-card"
          >
            <div class="order-header">
              <h3 class="order-id">订单号: {{ order.id }}</h3>
              <span 
                class="order-status" 
                :class="`status-${order.status}`"
              >
                {{ getOrderStatusText(order.status) }}
              </span>
            </div>
            
            <div class="order-items">
              <div 
                v-for="item in order.items" 
                :key="item.id"
                class="order-item"
                @click="goToProductDetail(item.product.id)"
              >
                <div class="order-item-image">
                  <img 
                    v-if="item.product.images && item.product.images.length > 0" 
                    :src="item.product.images[0]" 
                    :alt="item.product.title"
                  >
                  <span v-else class="no-image">暂无图片</span>
                </div>
                <div class="order-item-info">
                  <h4 class="order-item-title">{{ item.product.title }}</h4>
                  <div class="order-item-price">¥{{ item.unit_price.toFixed(2) }} x {{ item.quantity }}</div>
                </div>
              </div>
            </div>
            
            <div class="order-footer">
              <div class="order-buyer">买家: {{ order.buyer.username }}</div>
              <div class="order-total">总金额: ¥{{ order.total_amount.toFixed(2) }}</div>
              <div class="order-date">{{ formatDate(order.created_at) }}</div>
            </div>
            
            <!-- 退货申请处理 -->
            <div class="order-actions">
              <button class="action-btn-accept" @click="handleReturnRequest(order, true)" v-if="order.status === 'return_requested'">
                同意退货
              </button>
              <button class="action-btn-reject" @click="handleReturnRequest(order, false)" v-if="order.status === 'return_requested'">
                拒绝退货
              </button>
              <button class="action-btn-delete" @click="deleteRecord('order', order.id, order)">
                删除
              </button>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div class="empty-state" v-else>
          <div class="empty-icon">📤</div>
          <p>你还没有卖出任何商品</p>
        </div>
      </div>
      
      <!-- 已买到订单 -->
      <div v-if="activeTab === 'bought-orders'" class="tab-content">
        <h2 class="tab-title">已买到订单</h2>
        
        <!-- 订单列表 -->
        <div class="orders-list" v-if="boughtOrders.length > 0">
          <div 
            v-for="order in boughtOrders" 
            :key="order.id"
            class="order-card"
          >
            <div class="order-header">
              <h3 class="order-id">订单号: {{ order.id }}</h3>
              <span 
                class="order-status" 
                :class="`status-${order.status}`"
              >
                {{ getOrderStatusText(order.status) }}
              </span>
            </div>
            
            <div class="order-items">
              <div 
                v-for="item in order.items" 
                :key="item.id"
                class="order-item"
                @click="goToProductDetail(item.product.id)"
              >
                <div class="order-item-image">
                  <img 
                    v-if="item.product.images && item.product.images.length > 0" 
                    :src="item.product.images[0]" 
                    :alt="item.product.title"
                  >
                  <span v-else class="no-image">暂无图片</span>
                </div>
                <div class="order-item-info">
                  <h4 class="order-item-title">{{ item.product.title }}</h4>
                  <div class="order-item-price">¥{{ item.unit_price.toFixed(2) }} x {{ item.quantity }}</div>
                </div>
              </div>
            </div>
            
            <div class="order-footer">
              <div class="order-seller">卖家: {{ order.seller.username }}</div>
              <div class="order-total">总金额: ¥{{ order.total_amount.toFixed(2) }}</div>
              <div class="order-date">{{ formatDate(order.created_at) }}</div>
            </div>
            
            <!-- 订单操作 -->
            <div class="order-actions">
              <!-- 确认收货按钮 -->
              <button 
                class="action-btn-confirm" 
                @click="confirmReceipt(order)"
                v-if="order.status === 'delivered'"
              >
                确认收货
              </button>
              
              <!-- 退货申请按钮 -->
              <button 
                class="action-btn-return" 
                @click="requestReturn(order)"
                v-if="order.status === 'delivered'"
              >
                申请退货
              </button>
              
              <!-- 删除按钮 -->
              <button class="action-btn-delete" @click="deleteRecord('order', order.id, order)">
                删除
              </button>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div class="empty-state" v-else>
          <div class="empty-icon">📥</div>
          <p>你还没有购买任何商品</p>
        </div>
      </div>
    </div>
    
    <!-- 评价窗口 -->
    <div v-if="showReviewModal" class="review-modal-overlay" @click="closeReviewModal">
      <div class="review-modal" @click.stop>
        <div class="review-modal-header">
          <h3>评价商品</h3>
          <button class="close-btn" @click="closeReviewModal">×</button>
        </div>
        <div class="review-modal-content">
          <!-- 商品信息 -->
          <div class="review-product-info" v-if="reviewOrder">
            <div class="review-product-image">
              <img 
                v-if="reviewOrder.items[0].product.images && reviewOrder.items[0].product.images.length > 0" 
                :src="reviewOrder.items[0].product.images[0]" 
                :alt="reviewOrder.items[0].product.title"
              >
              <span v-else class="no-image">暂无图片</span>
            </div>
            <div class="review-product-details">
              <h4>{{ reviewOrder.items[0].product.title }}</h4>
              <p>¥{{ reviewOrder.items[0].unit_price.toFixed(2) }} x {{ reviewOrder.items[0].quantity }}</p>
            </div>
          </div>
          
          <!-- 评分 -->
          <div class="review-rating">
            <label>评分：</label>
            <div class="stars">
              <span 
                v-for="star in 5" 
                :key="star"
                :class="['star', { active: rating >= star }]"
                @click="rating = star"
              >
                ★
              </span>
            </div>
          </div>
          
          <!-- 评价内容 -->
          <div class="review-content">
            <label>评价：</label>
            <textarea 
              v-model="reviewContent" 
              placeholder="请输入您的评价..."
              rows="4"
            ></textarea>
          </div>
          
          <!-- 图片上传 -->
          <div class="review-image-upload">
            <label>上传图片：</label>
            <div class="image-upload-area">
              <input 
                type="file" 
                ref="fileInput"
                accept="image/*"
                @change="handleImageUpload"
                style="display: none"
              >
              <button class="upload-btn" @click="$refs.fileInput.click()">选择图片</button>
              <div v-if="reviewImage" class="preview-image">
                <img :src="reviewImage" alt="预览">
                <button class="remove-image" @click="removeImage">×</button>
              </div>
            </div>
          </div>
          
          <!-- 提交按钮 -->
          <div class="review-actions">
            <button class="cancel-btn" @click="closeReviewModal">取消</button>
            <button class="submit-btn" @click="submitReview" :disabled="!rating">提交评价</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import api from '../axios';

const router = useRouter();

// 标签页配置
const tabs = [
  { key: 'my-products', label: '我的发布' },
  { key: 'sold-orders', label: '已卖出' },
  { key: 'bought-orders', label: '已买到' }
];

const activeTab = ref('my-products');

// 数据状态
const myProducts = ref([]);
const soldOrders = ref([]);
const boughtOrders = ref([]);

// 评价相关状态
const showReviewModal = ref(false);
const reviewOrder = ref(null);
const rating = ref(0);
const reviewContent = ref('');
const reviewImage = ref(null);
const fileInput = ref(null);

// 页面加载时获取数据
onMounted(() => {
  fetchData();
});

// 监听activeTab变化，切换标签页时刷新数据
watch(activeTab, () => {
  fetchData();
});

// 获取交易数据
const fetchData = async () => {
  try {
    if (activeTab.value === 'my-products') {
      await fetchMyProducts();
    } else if (activeTab.value === 'sold-orders') {
      await fetchSoldOrders();
    } else if (activeTab.value === 'bought-orders') {
      await fetchBoughtOrders();
    }
  } catch (error) {
    console.error('获取交易数据失败:', error);
  }
};

// 获取我的发布商品
const fetchMyProducts = async () => {
  try {
    const response = await api.get('/transactions/my-products/');
    myProducts.value = response.data;
  } catch (error) {
    console.error('获取我的发布商品失败:', error);
  }
};

// 获取已卖出订单
const fetchSoldOrders = async () => {
  try {
    const response = await api.get('/transactions/sold-orders/');
    soldOrders.value = response.data;
  } catch (error) {
    console.error('获取已卖出订单失败:', error);
  }
};

// 获取已买到订单
const fetchBoughtOrders = async () => {
  try {
    const response = await api.get('/transactions/bought-orders/');
    boughtOrders.value = response.data;
  } catch (error) {
    console.error('获取已买到订单失败:', error);
  }
};

// 下架/上架商品
const toggleProductStatus = async (product) => {
  try {
    const newStatus = product.status === 'removed' ? 'approved' : 'removed';
    await api.patch(`/products/${product.id}/`, { status: newStatus });
    product.status = newStatus;
  } catch (error) {
    console.error('更新商品状态失败:', error);
  }
};

// 确认收货
const confirmReceipt = async (order) => {
  try {
    await api.patch(`/transactions/orders/${order.id}/confirm-receipt/`);
    order.status = 'completed';
    
    // 显示评价窗口
    reviewOrder.value = order;
    rating.value = 5; // 默认5星
    reviewContent.value = '';
    reviewImage.value = null;
    showReviewModal.value = true;
  } catch (error) {
    console.error('确认收货失败:', error);
  }
};

// 关闭评价窗口
const closeReviewModal = () => {
  showReviewModal.value = false;
  reviewOrder.value = null;
  rating.value = 0;
  reviewContent.value = '';
  reviewImage.value = null;
};

// 处理图片上传
const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      reviewImage.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

// 移除图片
const removeImage = () => {
  reviewImage.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

// 提交评价
const submitReview = async () => {
  if (!rating.value) return;
  
  try {
    const formData = new FormData();
    formData.append('product', reviewOrder.value.items[0].product.id);
    formData.append('order', reviewOrder.value.id);
    formData.append('content', reviewContent.value);
    formData.append('rating', rating.value);
    
    // 如果有图片，添加到formData
    if (fileInput.value && fileInput.value.files[0]) {
      formData.append('image', fileInput.value.files[0]);
    }
    
    await api.post('/comments/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    // 关闭评价窗口
    closeReviewModal();
    alert('评价成功！');
  } catch (error) {
    console.error('提交评价失败:', error);
    alert('评价失败，请重试。');
  }
};

// 申请退货
const requestReturn = async (order) => {
  try {
    await api.patch(`/transactions/orders/${order.id}/request-return/`);
    order.status = 'return_requested';
  } catch (error) {
    console.error('申请退货失败:', error);
  }
};

// 处理退货申请
const handleReturnRequest = async (order, accept) => {
  try {
    await api.patch(`/transactions/orders/${order.id}/handle-return/`, { accept });
    order.status = accept ? 'returned' : 'completed';
  } catch (error) {
    console.error('处理退货申请失败:', error);
  }
};

// 删除交易记录
const deleteRecord = async (recordType, recordId, record) => {
  if (!confirm('确定要删除这条记录吗？此操作不可恢复。')) {
    return;
  }
  
  try {
    await api.delete(`/transactions/delete/${recordType}/${recordId}/`);
    
    // 从相应的数据数组中移除记录
    if (recordType === 'product') {
      const index = myProducts.value.findIndex(p => p.id === recordId);
      if (index > -1) {
        myProducts.value.splice(index, 1);
      }
    } else if (recordType === 'order') {
      // 检查是已卖出还是已买到的订单
      const soldIndex = soldOrders.value.findIndex(o => o.id === recordId);
      if (soldIndex > -1) {
        soldOrders.value.splice(soldIndex, 1);
      }
      
      const boughtIndex = boughtOrders.value.findIndex(o => o.id === recordId);
      if (boughtIndex > -1) {
        boughtOrders.value.splice(boughtIndex, 1);
      }
    }
  } catch (error) {
    console.error('删除记录失败:', error);
  }
};

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};

// 获取商品状态文本
const getStatusText = (status) => {
  const statusMap = {
    'pending': '待审核',
    'approved': '已上架',
    'rejected': '已拒绝',
    'sold_out': '已售罄',
    'removed': '已下架'
  };
  return statusMap[status] || status;
};

// 获取订单状态文本
const getOrderStatusText = (status) => {
  const statusMap = {
    'pending': '待付款',
    'paid': '已付款',
    'shipping': '配送中',
    'delivered': '已送达',
    'completed': '已完成',
    'cancelled': '已取消',
    'return_requested': '申请退货',
    'returned': '已退货'
  };
  return statusMap[status] || status;
};

// 跳转到商品详情
const goToProductDetail = (productId) => {
  router.push(`/product/${productId}`);
};

// 跳转到发布页面
const goToPublish = () => {
  router.push('/publish');
};

// 返回首页
const goBack = () => {
  router.push('/');
};
</script>

<style scoped>
.transactions-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 页面头部 */
.transactions-header {
  display: flex;
  align-items: center;
  padding: 20px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 24px;
  color: white;
  cursor: pointer;
  margin-right: 20px;
  padding: 8px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.transactions-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

/* 标签页导航 */
.transactions-tabs {
  display: flex;
  background: white;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 85px;
  z-index: 90;
  backdrop-filter: blur(10px);
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin: 0 4px;
}

.tab-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.tab-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 内容区域 */
.transactions-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.tab-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

/* 商品列表 */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.product-image {
  height: 200px;
  background: #f8f9fa;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.no-image {
  font-size: 48px;
  color: #ccc;
}

.product-status {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  backdrop-filter: blur(10px);
}

.status-approved { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); }
.status-removed { background: linear-gradient(135deg, #f44336 0%, #da190b 100%); }
.status-pending { background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); }
.status-sold_out { background: linear-gradient(135deg, #9e9e9e 0%, #757575 100%); }
.status-rejected { background: linear-gradient(135deg, #f44336 0%, #da190b 100%); }

.product-info {
  padding: 16px;
  flex: 1;
}

.product-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  height: 48px;
}

.product-price {
  font-size: 20px;
  font-weight: 700;
  color: #667eea;
  margin: 0 0 12px 0;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.product-actions {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 12px;
}

.action-btn下架 {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn下架:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.action-btn下架:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

/* 订单列表 */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 20px;
}

.order-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.order-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.order-id {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.order-status {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.status-pending { background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); }
.status-paid { background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); }
.status-shipping { background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%); }
.status-delivered { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); }
.status-completed { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); }
.status-cancelled { background: linear-gradient(135deg, #f44336 0%, #da190b 100%); }
.status-return_requested { background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); }
.status-returned { background: linear-gradient(135deg, #f44336 0%, #da190b 100%); }

.order-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.order-item {
  display: flex;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 12px;
  border-radius: 8px;
}

.order-item:hover {
  background: rgba(102, 126, 234, 0.05);
}

.order-item-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
  flex-shrink: 0;
}

.order-item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.order-item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.order-item-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.order-item-price {
  font-size: 16px;
  font-weight: 700;
  color: #667eea;
  margin: 0;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 14px;
  color: #666;
}

.order-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.action-btn-confirm, .action-btn-return, .action-btn-accept, .action-btn-reject, .action-btn-delete {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
}

.action-btn-confirm {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.action-btn-return {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}

.action-btn-accept {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.action-btn-reject {
  background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
}

.action-btn-delete {
  background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
}

.action-btn-confirm:hover, .action-btn-return:hover, .action-btn-accept:hover, .action-btn-reject:hover, .action-btn-delete:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  padding: 40px;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.empty-state p {
  font-size: 18px;
  color: #666;
  margin: 0 0 24px 0;
  font-weight: 500;
}

.publish-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.publish-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 评价窗口样式 */
.review-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.review-modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

.review-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
}

.review-modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: white;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.review-modal-content {
  padding: 24px;
}

.review-product-info {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
}

.review-product-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
  flex-shrink: 0;
}

.review-product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.review-product-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.review-product-details h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.review-product-details p {
  margin: 0;
  font-size: 14px;
  color: #667eea;
  font-weight: 600;
}

.review-rating {
  margin-bottom: 20px;
}

.review-rating label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.stars {
  display: flex;
  gap: 8px;
}

.star {
  font-size: 24px;
  color: #ccc;
  cursor: pointer;
  transition: all 0.3s ease;
}

.star:hover, .star.active {
  color: #ffd700;
  transform: scale(1.1);
}

.review-content {
  margin-bottom: 20px;
}

.review-content label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.review-content textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  font-size: 14px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  transition: border-color 0.3s ease;
}

.review-content textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.review-image-upload {
  margin-bottom: 24px;
}

.review-image-upload label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.image-upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-btn {
  padding: 10px 20px;
  border: 1px solid #667eea;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  background: #667eea;
  color: white;
}

.preview-image {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  transition: all 0.3s ease;
}

.remove-image:hover {
  background: #f44336;
  color: white;
}

.review-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn, .submit-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #ccc;
  color: white;
}

.cancel-btn:hover {
  background: #999;
}

.submit-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .transactions-header {
    padding: 16px 20px;
  }
  
  .transactions-content {
    padding: 16px;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .order-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .order-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .review-modal {
    width: 95%;
    margin: 20px;
  }
  
  .review-modal-content {
    padding: 20px;
  }
  
  .review-product-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .stars {
    justify-content: center;
  }
  
  .image-upload-area {
    flex-direction: column;
    align-items: stretch;
  }
  
  .preview-image {
    align-self: center;
  }
  
  .review-actions {
    flex-direction: column;
  }
}
</style>