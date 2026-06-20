<template>
  <div class="profile-container" ref="profileContainer">
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
        返回
      </button>
      <h1>{{ isOwnProfile ? '个人中心' : '用户资料' }}</h1>
    </div>
    
    <div class="profile-content">
      <div class="sidebar">
        <div class="user-info">
          <div class="avatar-container">
            <div class="avatar">
              <img 
                v-if="profile?.avatar" 
                :src="profile.avatar" 
                :alt="user?.username || '用户'"
                class="avatar-img"
              >
              <span 
                v-else 
                class="avatar-placeholder"
              >{{ user?.username?.charAt(0) || 'U' }}</span>
            </div>
            <label v-if="isOwnProfile" for="avatar-upload" class="avatar-upload-btn">
              <span class="upload-icon">📷</span>
              <input 
                type="file" 
                id="avatar-upload" 
                ref="avatarInput"
                accept="image/*" 
                @change="handleAvatarUpload"
                style="display: none"
              >
            </label>
            <!-- 头像预览 -->
            <div v-if="avatarPreview && isOwnProfile" class="avatar-preview-modal" @click="closeAvatarPreview">
              <div class="avatar-preview-content" @click.stop>
                <img :src="avatarPreview" alt="头像预览" class="preview-img">
                <div class="preview-actions">
                  <button class="btn-primary" @click="confirmAvatarUpload">确认上传</button>
                  <button class="btn-secondary" @click="closeAvatarPreview">取消</button>
                </div>
              </div>
            </div>
          </div>
          <h2>{{ user?.username || '用户' }}</h2>
          <p class="student-id">{{ profile?.student_id || '未设置学号' }}</p>
        </div>
        
        <nav class="sidebar-nav">
          <!-- 只在查看自己的资料时显示所有标签 -->
          <template v-if="isOwnProfile">
            <a href="#" class="nav-item" :class="{ active: activeTab === 'basic' }" @click.prevent="switchTab('basic')">基本信息</a>
            <a href="#" class="nav-item" :class="{ active: activeTab === 'interactions' }" @click.prevent="switchTab('interactions')">互动记录</a>
            <a href="#" class="nav-item" :class="{ active: activeTab === 'products' }" @click.prevent="switchTab('products')">我的商品</a>
            <a href="#" class="nav-item" :class="{ active: activeTab === 'security' }" @click.prevent="switchTab('security')">安全设置</a>
          </template>
          <!-- 查看其他用户的资料时只显示在售商品 -->
          <template v-else>
            <a href="#" class="nav-item" :class="{ active: activeTab === 'products' }" @click.prevent="switchTab('products')">在售商品</a>
          </template>
        </nav>
      </div>
      
      <div class="main-content">
        <!-- 只在查看自己的资料时显示完整的个人中心内容 -->
        <template v-if="isOwnProfile">
          <!-- 基本信息 -->
          <div v-if="activeTab === 'basic'" class="tab-content">
            <div class="section">
              <h3>基本信息</h3>
              <form @submit.prevent="updateProfile">
                <div class="form-row">
                  <div class="form-group">
                    <label for="username">用户名</label>
                    <input 
                      type="text" 
                      id="username" 
                      v-model="form.username" 
                      placeholder="用户名"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label for="email">邮箱</label>
                    <input 
                      type="email" 
                      id="email" 
                      v-model="form.email" 
                      disabled
                      placeholder="邮箱"
                    >
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label for="student_id">学号</label>
                    <input 
                      type="text" 
                      id="student_id" 
                      v-model="form.student_id" 
                      placeholder="学号"
                    >
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label for="grade">年级</label>
                    <input 
                      type="text" 
                      id="grade" 
                      v-model="form.grade" 
                      placeholder="请输入年级"
                    >
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label for="address">地址</label>
                    <input 
                      type="text" 
                      id="address" 
                      v-model="form.address" 
                      placeholder="请输入地址"
                    >
                  </div>
                </div>
                
                <div class="form-group">
                  <label for="bio">个人简介</label>
                  <textarea 
                    id="bio" 
                    v-model="form.bio" 
                    rows="4" 
                    placeholder="请输入个人简介"
                  ></textarea>
                </div>
                
                <div class="form-actions">
                  <button type="submit" class="btn-primary" :disabled="loading">
                    {{ loading ? '保存中...' : '保存修改' }}
                  </button>
                </div>
              </form>
            </div>
            
            <div class="section">
              <h3>账户统计</h3>
              <div class="stats-grid">
                <div class="stat-item">
                  <span class="stat-label">信誉分</span>
                  <span class="stat-value">{{ profile?.reputation || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">成交数量</span>
                  <span class="stat-value">{{ completedTransactions || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 互动记录 -->
          <div v-else-if="activeTab === 'interactions'" class="tab-content">
            <div class="interactions-tabs">
              <button 
                class="interaction-tab" 
                :class="{ active: activeInteractionTab === 'likes' }"
                @click="switchInteractionTab('likes')"
              >
                点赞记录
              </button>
              <button 
                class="interaction-tab" 
                :class="{ active: activeInteractionTab === 'favorites' }"
                @click="switchInteractionTab('favorites')"
              >
                收藏记录
              </button>
              <button 
                class="interaction-tab" 
                :class="{ active: activeInteractionTab === 'viewHistory' }"
                @click="switchInteractionTab('viewHistory')"
              >
                浏览记录
              </button>
              <button 
                class="interaction-tab" 
                :class="{ active: activeInteractionTab === 'following' }"
                @click="switchInteractionTab('following')"
              >
                关注卖家
              </button>
            </div>
            
            <div class="interaction-content">
              <!-- 点赞记录 -->
              <div v-if="activeInteractionTab === 'likes'" class="interaction-section">
                <h3>点赞记录</h3>
                <div v-if="likes.length > 0" class="products-grid">
                  <div 
                    class="product-card" 
                    v-for="product in likes" 
                    :key="product.id"
                    @click="navigateToProduct(product.id)"
                    style="cursor: pointer"
                  >
                    <div class="product-image">
                      <img 
                        v-if="product.images && product.images.length > 0" 
                        :src="product.images[0].image" 
                        :alt="product.title"
                      >
                      <span v-else class="placeholder">商品图片</span>
                    </div>
                    <div class="product-info">
                      <h4 class="product-title">{{ product.title }}</h4>
                      <p class="product-price">¥{{ product.price }}</p>
                      <p class="product-category">{{ product.category.name }}</p>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-state">
                  <p>暂无点赞记录</p>
                </div>
              </div>
              
              <!-- 收藏记录 -->
              <div v-else-if="activeInteractionTab === 'favorites'" class="interaction-section">
                <h3>收藏记录</h3>
                <div v-if="favorites.length > 0" class="products-grid">
                  <div 
                    class="product-card" 
                    v-for="product in favorites" 
                    :key="product.id"
                    @click="navigateToProduct(product.id)"
                    style="cursor: pointer"
                  >
                    <div class="product-image">
                      <img 
                        v-if="product.images && product.images.length > 0" 
                        :src="product.images[0].image" 
                        :alt="product.title"
                      >
                      <span v-else class="placeholder">商品图片</span>
                    </div>
                    <div class="product-info">
                      <h4 class="product-title">{{ product.title }}</h4>
                      <p class="product-price">¥{{ product.price }}</p>
                      <p class="product-category">{{ product.category.name }}</p>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-state">
                  <p>暂无收藏记录</p>
                </div>
              </div>
              
              <!-- 浏览记录 -->
              <div v-else-if="activeInteractionTab === 'viewHistory'" class="interaction-section">
                <h3>浏览记录</h3>
                <div v-if="viewHistory.length > 0" class="products-grid">
                  <div 
                    class="product-card" 
                    v-for="product in viewHistory" 
                    :key="product.id"
                    @click="navigateToProduct(product.id)"
                    style="cursor: pointer"
                  >
                    <div class="product-image">
                      <img 
                        v-if="product.images && product.images.length > 0" 
                        :src="product.images[0].image" 
                        :alt="product.title"
                      >
                      <span v-else class="placeholder">商品图片</span>
                    </div>
                    <div class="product-info">
                      <h4 class="product-title">{{ product.title }}</h4>
                      <p class="product-price">¥{{ product.price }}</p>
                      <p class="product-category">{{ product.category.name }}</p>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-state">
                  <p>暂无浏览记录</p>
                </div>
              </div>
              
              <!-- 关注卖家 -->
              <div v-else-if="activeInteractionTab === 'following'" class="interaction-section">
                <h3>关注卖家</h3>
                <div v-if="following.length > 0" class="sellers-grid">
                  <div 
                    class="seller-card" 
                    v-for="seller in following" 
                    :key="seller.id"
                    @click="navigateToSellerProfile(seller.id)"
                    style="cursor: pointer"
                  >
                    <div class="seller-avatar">
                      <img 
                        v-if="seller.avatar" 
                        :src="seller.avatar" 
                        :alt="seller.username"
                      >
                      <span v-else class="avatar-placeholder">{{ seller.username.charAt(0) }}</span>
                    </div>
                    <div class="seller-info">
                      <h4 class="seller-name">{{ seller.nickname || seller.username }}</h4>
                      <p class="seller-stats">信誉分: {{ seller.reputation }} | 成交: {{ seller.completed_transactions }}</p>
                      <p class="follow-time">关注于: {{ formatDate(seller.followed_at) }}</p>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-state">
                  <p>暂无关注的卖家</p>
                </div>
              </div>
            </div>
          </div>
          

          
          <!-- 安全设置 -->
          <div v-else-if="activeTab === 'security'" class="tab-content">
            <div class="section">
              <h3>修改密码</h3>
              <form @submit.prevent="handlePasswordReset">
                <div class="form-row">
                  <div class="form-group">
                    <label for="email">邮箱</label>
                    <div class="input-with-btn">
                      <input 
                        type="email" 
                        id="email" 
                        v-model="passwordForm.email" 
                        placeholder="请输入注册邮箱"
                      >
                      <button 
                        type="button" 
                        class="btn-secondary" 
                        :disabled="sendingCode"
                        @click="sendVerificationCode"
                      >
                        {{ sendingCode ? '发送中...' : `发送验证码 (${countdown}s)` }}
                      </button>
                    </div>
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label for="verification_code">验证码</label>
                    <input 
                      type="text" 
                      id="verification_code" 
                      v-model="passwordForm.verification_code" 
                      placeholder="请输入验证码"
                    >
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label for="new_password">新密码</label>
                    <input 
                      type="password" 
                      id="new_password" 
                      v-model="passwordForm.new_password" 
                      placeholder="请输入新密码（8-16位，包含字母和数字）"
                    >
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label for="new_password2">确认新密码</label>
                    <input 
                      type="password" 
                      id="new_password2" 
                      v-model="passwordForm.new_password2" 
                      placeholder="请再次输入新密码"
                    >
                  </div>
                </div>
                
                <div class="form-actions">
                  <button 
                    type="submit" 
                    class="btn-primary" 
                    :disabled="passwordLoading"
                  >
                    {{ passwordLoading ? '修改中...' : '修改密码' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
          
          <!-- 我的商品 -->
          <div v-else-if="activeTab === 'products'" class="tab-content">
            <div class="section">
              <h3>我的商品</h3>
              <div v-if="products.length > 0" class="products-grid">
                <div 
                  class="product-card" 
                  v-for="product in products" 
                  :key="product.id"
                  @click="navigateToProduct(product.id)"
                  style="cursor: pointer"
                >
                  <div class="product-image">
                    <img 
                      v-if="product.images && product.images.length > 0" 
                      :src="product.images[0]" 
                      :alt="product.title"
                    >
                    <span v-else class="placeholder">商品图片</span>
                  </div>
                  <div class="product-info">
                    <h4 class="product-title">{{ product.title }}</h4>
                    <p class="product-price">¥{{ product.price }}</p>
                    <p class="product-status">{{ product.status === 'approved' ? '在售' : product.status === 'removed' ? '已下架' : '已售罄' }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <p>暂无发布的商品</p>
              </div>
            </div>
          </div>
          

        </template>
        
        <!-- 查看其他用户的资料时只显示商品和卖出记录 -->
        <template v-else>
          <!-- 在售商品 -->
          <div v-if="activeTab === 'products'" class="tab-content">
            <div class="section">
              <h3>在售商品</h3>
              <div v-if="loadingProducts" class="loading-state">
                <p>加载中...</p>
              </div>
              <div v-else-if="products.length > 0" class="products-grid">
                <div 
                  class="product-card" 
                  v-for="product in products" 
                  :key="product.id"
                  @click="navigateToProduct(product.id)"
                  style="cursor: pointer"
                >
                  <div class="product-image">
                    <img 
                      v-if="product.images && product.images.length > 0" 
                      :src="product.images[0]" 
                      :alt="product.title"
                    >
                    <span v-else class="placeholder">商品图片</span>
                  </div>
                  <div class="product-info">
                    <h4 class="product-title">{{ product.title }}</h4>
                    <p class="product-price">¥{{ product.price }}</p>
                    <p class="product-status">{{ product.status === 'approved' ? '在售' : product.status === 'removed' ? '已下架' : '已售罄' }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <p>暂无在售商品</p>
              </div>
            </div>
          </div>
          

        </template>
      </div>
    </div>
    
    <!-- 回到顶部按钮 -->
    <button 
      class="back-to-top" 
      :class="{ show: showBackToTop }"
      @click="scrollToTop"
      title="回到顶部"
    >
      ↑
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../axios';

// 响应式数据
const profileContainer = ref(null);
const activeTab = ref('basic');
const activeInteractionTab = ref('likes');
const showBackToTop = ref(false);
const loading = ref(false);
const passwordLoading = ref(false);
const sendingCode = ref(false);
const countdown = ref(0);
const avatarPreview = ref(null);
const avatarInput = ref(null);
const router = useRouter();
const route = useRoute();

// 获取URL参数中的用户ID
const userId = computed(() => route.params.id);

// 计算是否是自己的个人中心
const isOwnProfile = computed(() => {
  const currentUser = JSON.parse(localStorage.getItem('user'));
  return !userId.value || (currentUser && currentUser.id === parseInt(userId.value));
});

// 用户信息和个人资料
const user = ref(null);
const profile = ref(null);
// 成交数量（根据已卖出订单实时计算）
const completedTransactions = ref(0);

// 基本信息表单
const form = ref({
  username: '',
  email: '',
  student_id: '',
  nickname: '',
  grade: '',
  address: '',
  bio: ''
});

// 密码修改表单
const passwordForm = ref({
  email: '',
  verification_code: '',
  new_password: '',
  new_password2: ''
});

// 互动记录数据
const likes = ref([]);
const favorites = ref([]);
const viewHistory = ref([]);
const following = ref([]);

// 商品数据
const products = ref([]);
const loadingProducts = ref(false);

// 切换标签页
const switchTab = (tab) => {
  activeTab.value = tab;
  // 如果切换到互动记录标签，加载对应数据
  if (tab === 'interactions') {
    loadInteractionData();
  } else if (tab === 'products') {
    // 如果切换到商品标签，加载商品数据
    fetchUserProducts();
  } else if (tab === 'basic') {
    // 如果切换到基本信息标签，重新加载用户信息
    fetchUserProfile();
  }
};

// 切换互动记录子标签
const switchInteractionTab = (tab) => {
  activeInteractionTab.value = tab;
};

// 更新个人资料
const updateProfile = async () => {
  loading.value = true;
  
  try {
    // 发送请求更新个人资料
    const response = await api.put('/accounts/profile/', {
      username: form.value.username,
      student_id: form.value.student_id,
      grade: form.value.grade,
      address: form.value.address,
      bio: form.value.bio
    });
    
    // 更新本地存储
    const updatedProfile = response.data.profile;
    localStorage.setItem('profile', JSON.stringify(updatedProfile));
    profile.value = updatedProfile;
    
    // 更新用户信息
    const userResponse = await api.get('/accounts/profile/');
    const updatedUser = userResponse.data.user;
    localStorage.setItem('user', JSON.stringify(updatedUser));
    user.value = updatedUser;
    
    // 刷新其他相关数据
    if (activeTab.value === 'interactions') {
      loadInteractionData();
    } else if (activeTab.value === 'products') {
      fetchUserProducts();
    }
    
    alert('个人资料更新成功');
  } catch (err) {
    console.error('更新失败:', err);
    alert('更新失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 头像上传处理
const handleAvatarUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件');
      return;
    }
    
    // 检查文件大小（最大2MB）
    if (file.size > 2 * 1024 * 1024) {
      alert('图片大小不能超过2MB');
      return;
    }
    
    // 生成预览
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

// 确认头像上传
const confirmAvatarUpload = async () => {
  if (!avatarPreview.value) return;
  
  loading.value = true;
  
  try {
    // 从input中获取文件
    const file = avatarInput.value.files[0];
    if (!file) {
      throw new Error('没有选择文件');
    }
    
    console.log('准备上传头像:', file.name, file.size, file.type);
    
    // 直接使用FileReader读取文件并转换为Base64
    const reader = new FileReader();
    
    // 读取文件完成后的回调
    reader.onload = (e) => {
      try {
        // 使用Base64字符串作为头像URL
        const base64Avatar = e.target.result;
        console.log('Base64头像URL生成成功');
        
        // 更新本地存储和响应式数据
        const profileToUpdate = { ...profile.value };
        profileToUpdate.avatar = base64Avatar;
        
        // 更新localStorage和sessionStorage
        localStorage.setItem('profile', JSON.stringify(profileToUpdate));
        sessionStorage.setItem('profile', JSON.stringify(profileToUpdate));
        
        // 同时更新用户信息中的头像（如果存在）
        const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
        if (userInfo) {
          const updatedUser = { ...userInfo };
          updatedUser.avatar = base64Avatar;
          localStorage.setItem('user', JSON.stringify(updatedUser));
          sessionStorage.setItem('user', JSON.stringify(updatedUser));
          
          // 将头像信息保存到userAvatars对象中，以便其他用户登录时也能看到该用户的最新头像
          const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
          userAvatars[userInfo.username] = base64Avatar;
          localStorage.setItem('userAvatars', JSON.stringify(userAvatars));
        }
        
        // 强制更新响应式数据
        profile.value = null;
        setTimeout(() => {
          profile.value = { ...profileToUpdate };
          console.log('强制更新后的profile.value:', profile.value);
        }, 0);
        
        console.log('本地存储更新完成，使用Base64作为头像');
        
        // 关闭预览
        closeAvatarPreview();
        alert('头像上传成功，已更新显示');
      } catch (err) {
        console.error('处理Base64头像失败:', err);
        alert('头像处理失败，请稍后重试');
      } finally {
        loading.value = false;
      }
    };
    
    // 读取文件为Base64
    reader.readAsDataURL(file);
    
  } catch (err) {
    console.error('头像上传失败:', err);
    console.error('错误详情:', err.response?.data || err.message);
    alert(`头像上传失败: ${err.response?.data?.detail || err.message || '请稍后重试'}`);
    loading.value = false;
  }
};

// 关闭头像预览
const closeAvatarPreview = () => {
  avatarPreview.value = null;
  // 重置文件输入
  if (avatarInput.value) {
    avatarInput.value.value = '';
  }
};

// 加载互动记录数据
const loadInteractionData = async () => {
  try {
    // 加载点赞记录
    const likesResponse = await api.get('/user/likes/');
    likes.value = likesResponse.data.results || likesResponse.data;
    
    // 加载收藏记录
    const favoritesResponse = await api.get('/user/favorites/');
    favorites.value = favoritesResponse.data.results || favoritesResponse.data;
    
    // 加载浏览记录
    const viewHistoryResponse = await api.get('/user/view-history/');
    viewHistory.value = viewHistoryResponse.data.results || viewHistoryResponse.data;
    
    // 加载关注卖家
    const followingResponse = await api.get('/user/following/');
    // 检查响应数据结构
    let followingData = [];
    if (followingResponse.data && followingResponse.data.results) {
      followingData = followingResponse.data.results;
    } else if (Array.isArray(followingResponse.data)) {
      followingData = followingResponse.data;
    } else {
      followingData = [];
    }
    
    // 检查本地存储中是否有关注卖家的头像信息
    const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
    
    // 更新关注卖家中的头像，包括其他用户的最新头像
    followingData = followingData.map(seller => {
      // 检查本地存储中是否有该卖家的最新头像
      if (seller.username && userAvatars[seller.username]) {
        return {
          ...seller,
          avatar: userAvatars[seller.username]
        };
      }
      return seller;
    });
    
    following.value = followingData;
  } catch (err) {
    console.error('加载互动记录失败:', err);
  }
};

// 发送验证码
const sendVerificationCode = async () => {
  if (!passwordForm.value.email) {
    alert('请输入邮箱');
    return;
  }
  
  if (countdown.value > 0) return;
  
  sendingCode.value = true;
  
  try {
    await api.post('/accounts/send-verification-code/', {
      email: passwordForm.value.email,
      code_type: 'reset_password'
    });
    
    alert('验证码发送成功，请查收邮箱');
    // 开始倒计时
    countdown.value = 60;
    const timer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);
  } catch (err) {
    console.error('发送验证码失败:', err);
    alert('发送验证码失败，请稍后重试');
  } finally {
    sendingCode.value = false;
  }
};

// 处理密码重置
const handlePasswordReset = async () => {
  if (!passwordForm.value.email || !passwordForm.value.verification_code || !passwordForm.value.new_password) {
    alert('请填写完整信息');
    return;
  }
  
  if (passwordForm.value.new_password !== passwordForm.value.new_password2) {
    alert('两次输入的密码不一致');
    return;
  }
  
  passwordLoading.value = true;
  
  try {
    await api.post('/accounts/password-reset/', {
      email: passwordForm.value.email,
      verification_code: passwordForm.value.verification_code,
      new_password: passwordForm.value.new_password,
      new_password2: passwordForm.value.new_password2
    });
    
    alert('密码修改成功，请重新登录');
    // 重置表单
    passwordForm.value = {
      email: user.value?.email || '',
      verification_code: '',
      new_password: '',
      new_password2: ''
    };
    // 可以选择跳转到登录页
  } catch (err) {
    console.error('修改密码失败:', err);
    alert('修改密码失败，请检查验证码是否正确');
  } finally {
    passwordLoading.value = false;
  }
};

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

// 返回上一页
const goBack = () => {
  window.history.back();
};

// 跳转到商品详情页
const navigateToProduct = (productId) => {
  router.push(`/product/${productId}`);
};

// 跳转到卖家个人资料页面
const navigateToSellerProfile = (sellerId) => {
  router.push(`/profile/${sellerId}`);
};

// 滚动事件监听
const handleScroll = () => {
  if (profileContainer.value) {
    const scrollTop = profileContainer.value.scrollTop;
    showBackToTop.value = scrollTop > 300;
  }
};

// 回到顶部
const scrollToTop = () => {
  if (profileContainer.value) {
    profileContainer.value.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
};



// 获取最新的用户信息
const fetchUserProfile = async () => {
  try {
    if (isOwnProfile.value) {
      // 获取自己的信息
      const response = await api.get('/accounts/profile/');
      let { user: updatedUser, profile: updatedProfile } = response.data;
      
      // 检查本地存储中是否有Base64格式的头像，并且确保是当前用户的头像
      const localProfile = JSON.parse(localStorage.getItem('profile') || '{}');
      const localUser = JSON.parse(localStorage.getItem('user') || '{}');
      const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
      
      // 优先从userAvatars中获取最新的头像
      if (updatedUser.username && userAvatars[updatedUser.username]) {
        updatedProfile.avatar = userAvatars[updatedUser.username];
        updatedUser.avatar = userAvatars[updatedUser.username];
      } else if (localProfile.avatar && localProfile.avatar.startsWith('data:image/') && 
                 (localUser.id === updatedUser.id || localUser.username === updatedUser.username)) {
        // 其次从localStorage的profile中获取
        updatedProfile.avatar = localProfile.avatar;
      } else if (localUser.avatar && localUser.avatar.startsWith('data:image/') && 
                 (localUser.id === updatedUser.id || localUser.username === updatedUser.username)) {
        // 最后从localStorage的user中获取
        updatedUser.avatar = localUser.avatar;
      }
      
      // 更新本地存储
      localStorage.setItem('user', JSON.stringify(updatedUser));
      localStorage.setItem('profile', JSON.stringify(updatedProfile));
      
      // 更新响应式数据
      user.value = updatedUser;
      profile.value = updatedProfile;
    } else {
      // 获取指定用户的信息
      const response = await api.get(`/accounts/user-info/${userId.value}/`);
      let { user: updatedUser, profile: updatedProfile } = response.data;
      
      // 检查本地存储中是否有该用户的最新头像
      const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
      if (updatedUser.username && userAvatars[updatedUser.username]) {
        updatedUser.avatar = userAvatars[updatedUser.username];
        updatedProfile.avatar = userAvatars[updatedUser.username];
      }
      
      // 更新响应式数据
      user.value = updatedUser;
      profile.value = updatedProfile;
    }
    
    // 更新表单数据
    form.value = {
      username: user.value?.username || '',
      email: user.value?.email || '',
      student_id: profile.value?.student_id || '',
      grade: profile.value?.grade || '',
      address: profile.value?.address || '',
      bio: profile.value?.bio || ''
    };
    
    // 更新密码表单的邮箱
    passwordForm.value.email = user.value?.email || '';
  } catch (err) {
    console.error('获取用户信息失败:', err);
  }
};

// 定时刷新用户信息，确保信誉分和成交数量实时更新
const refreshIntervalRef = ref(null);

const startRefreshUserInfo = () => {
  if (!isOwnProfile.value) {
    // 清除之前的定时器
    if (refreshIntervalRef.value) {
      clearInterval(refreshIntervalRef.value);
    }
    // 每30秒刷新一次用户信息
    refreshIntervalRef.value = setInterval(() => {
      fetchUserProfile();
    }, 30000);
  }
};

// 获取用户的商品
const fetchUserProducts = async () => {
  loadingProducts.value = true;
  try {
    if (userId.value) {
      // 获取指定用户的商品
      const response = await api.get(`/users/${userId.value}/products/`);
      products.value = response.data;
    } else {
      // 获取自己的商品
      const response = await api.get('/transactions/my-products/');
      products.value = response.data;
    }
  } catch (err) {
    console.error('获取用户商品失败:', err);
    products.value = [];
  } finally {
    loadingProducts.value = false;
  }
};

// 获取已卖出订单并计算成交数量
const fetchCompletedTransactions = async () => {
  try {
    if (userId.value) {
      // 获取指定用户的卖出订单
      const response = await api.get(`/users/${userId.value}/sold-orders/`);
      const orders = response.data;
      // 计算已完成的订单数量
      completedTransactions.value = orders.filter(order => order.status === 'completed').length;
    } else {
      // 获取自己的卖出订单
      const response = await api.get('/transactions/sold-orders/');
      const orders = response.data;
      // 计算已完成的订单数量
      completedTransactions.value = orders.filter(order => order.status === 'completed').length;
    }
  } catch (err) {
    console.error('获取成交数量失败:', err);
    completedTransactions.value = 0;
  }
};



// 清理函数引用
const cleanupRef = ref(null);

// 页面挂载
onMounted(() => {
  // 添加滚动事件监听
  if (profileContainer.value) {
    profileContainer.value.addEventListener('scroll', handleScroll);
  }
  
  // 添加存储事件监听器
  window.addEventListener('storage', handleStorageChange);
  
  // 加载数据
  loadData();
  
  // 监听路由参数变化
  watch(() => route.params.id, () => {
    // 路由参数变化时重新加载数据
    loadData();
  });
});

// 存储事件监听器，用于实时更新头像
const handleStorageChange = (event) => {
  if (event.key === 'userAvatars') {
    // 当userAvatars发生变化时，更新相关头像
    if (activeTab.value === 'interactions' && activeInteractionTab.value === 'following') {
      // 如果当前在关注卖家标签页，重新加载关注卖家数据
      loadInteractionData();
    } else if (!isOwnProfile.value) {
      // 如果当前在查看其他用户的个人资料，重新加载用户信息
      fetchUserProfile();
    } else if (isOwnProfile.value) {
      // 如果当前在查看自己的个人资料，重新加载用户信息
      fetchUserProfile();
    }
  }
};

// 组件卸载时执行清理
onUnmounted(() => {
  if (cleanupRef.value) {
    cleanupRef.value();
  }
  if (refreshIntervalRef.value) {
    clearInterval(refreshIntervalRef.value);
  }
  // 移除存储事件监听器
  window.removeEventListener('storage', handleStorageChange);
});

// 加载数据函数
const loadData = async () => {
  // 先获取用户信息，确保isOwnProfile的值是最新的
  await fetchUserProfile();
  
  // 加载成交数量
  await fetchCompletedTransactions();
  
  // 加载互动记录数据（只在查看自己的资料时加载）
  if (isOwnProfile.value) {
    loadInteractionData();
  }
  
  // 如果是查看其他用户的资料，默认显示商品列表
  if (!isOwnProfile.value) {
    activeTab.value = 'products';
    fetchUserProducts();
    // 启动定时刷新用户信息，确保信誉分和成交数量实时更新
    startRefreshUserInfo();
  } else {
    // 为自己的个人中心添加定时刷新
    cleanupRef.value = startPersonalCenterRefresh();
  }
};

// 个人中心定时刷新
const startPersonalCenterRefresh = () => {
  // 每30秒刷新一次数据
  const refreshInterval = setInterval(() => {
    // 刷新用户信息
    fetchUserProfile();
    
    // 刷新成交数量
    fetchCompletedTransactions();
    
    // 根据当前标签页刷新对应数据
    if (activeTab.value === 'interactions') {
      loadInteractionData();
    } else if (activeTab.value === 'products') {
      fetchUserProducts();
    }
  }, 30000);
  
  // 组件卸载时清除定时器
  return () => {
    clearInterval(refreshInterval);
  };
};
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

.profile-container {
  max-width: 1200px;
  margin: 30px auto;
  padding: 30px;
  min-height: calc(100vh - 60px);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  overflow-y: auto;
  position: relative;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 3px solid linear-gradient(90deg, #667eea, #764ba2);
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

/* 返回按钮 */
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

/* 自定义滚动条 */
.profile-container::-webkit-scrollbar {
  width: 10px;
}

.profile-container::-webkit-scrollbar-track {
  background: rgba(241, 241, 241, 0.8);
  border-radius: 10px;
}

.profile-container::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.profile-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 标题样式 */
.page-header h1 {
  color: #333;
  margin: 0;
  font-size: 28px;
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

.profile-content {
  display: flex;
  gap: 30px;
  animation: fadeInUp 0.6s ease-out;
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

.sidebar {
  width: 280px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 25px;
  position: sticky;
  top: 20px;
  align-self: flex-start;
  transition: all 0.3s ease;
}

.sidebar:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.user-info {
  text-align: center;
  margin-bottom: 30px;
  position: relative;
}

/* 头像容器 */
.avatar-container {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.avatar {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 40px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* 头像上传按钮 */
.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: linear-gradient(135deg, #ff4757 0%, #ff6b81 100%);
  color: white;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
  border: 3px solid white;
}

.avatar-upload-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(255, 71, 87, 0.4);
}

/* 头像预览模态框 */
.avatar-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
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

.avatar-preview-content {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 30px;
  border-radius: 20px;
  text-align: center;
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

.preview-img {
  max-width: 300px;
  max-height: 300px;
  margin-bottom: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.preview-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.user-info h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 22px;
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.student-id {
  margin: 0;
  color: #666;
  font-size: 16px;
  background: rgba(255, 255, 255, 0.8);
  padding: 8px 16px;
  border-radius: 20px;
  display: inline-block;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nav-item {
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.8);
  color: #333;
  text-decoration: none;
  border-radius: 10px;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.nav-item:hover {
  transform: translateX(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.9);
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.nav-item.active:hover {
  transform: translateX(10px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 5px;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: all 0.3s ease;
}

.nav-item:hover::before {
  opacity: 1;
}

.nav-item.active::before {
  opacity: 1;
  width: 8px;
}

.main-content {
  flex: 1;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 30px;
  transition: all 0.3s ease;
}

.main-content:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.section {
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.9);
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 2px solid linear-gradient(90deg, #667eea, #764ba2);
  padding-bottom: 10px;
  position: relative;
}

.section h3::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 250px;
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 600;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 16px;
  box-sizing: border-box;
  background-color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.input-with-btn {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.input-with-btn input {
  flex: 1;
  min-width: 200px;
}

.form-group input:disabled {
  background-color: rgba(240, 240, 240, 0.8);
  cursor: not-allowed;
  color: #999;
  border-color: #ccc;
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
  background-color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.form-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-start;
  gap: 15px;
}

.btn-primary {
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  padding: 12px 30px;
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(149, 165, 166, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.btn-secondary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(149, 165, 166, 0.4);
  background: linear-gradient(135deg, #7f8c8d 0%, #95a5a6 100%);
}

.btn-primary:disabled,
.btn-secondary:disabled {
  background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%);
  cursor: not-allowed;
  color: #666;
  transform: none;
  box-shadow: none;
}

/* 互动记录样式 */
.interactions-tabs {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 15px;
  flex-wrap: wrap;
}

.interaction-tab {
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.8);
  color: #333;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.interaction-tab:hover,
.interaction-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.interaction-section {
  margin-bottom: 30px;
}

/* 商品网格 */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 25px;
}

.product-card {
  border: none;
  border-radius: 15px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.product-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.product-image {
  height: 180px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 15px 15px 0 0;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

.product-card:hover .product-image img {
  transform: scale(1.1);
}

.product-info {
  padding: 15px;
}

.product-title {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  font-weight: 500;
}

.product-price {
  margin: 0 0 10px 0;
  font-size: 20px;
  font-weight: bold;
  color: #ff4757;
  text-shadow: 0 1px 3px rgba(255, 71, 87, 0.3);
}

.product-category {
  font-size: 14px;
  color: #666;
  margin: 0 0 10px 0;
  background: rgba(245, 245, 245, 0.8);
  padding: 5px 10px;
  border-radius: 10px;
  display: inline-block;
}

.product-status {
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  padding: 8px 16px;
  border-radius: 20px;
  display: inline-block;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.product-status:contains('在售') {
  background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
  color: white;
}

.product-status:contains('已下架') {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  color: white;
}

.product-status:contains('已售罄') {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
}

.product-status:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 卖家网格 */
.sellers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
}

.seller-card {
  display: flex;
  gap: 20px;
  padding: 20px;
  border: none;
  border-radius: 15px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.seller-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 1);
}

.seller-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.seller-card:hover .seller-avatar {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.seller-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.seller-info {
  flex: 1;
}

.seller-name {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.seller-stats {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #666;
  background: rgba(245, 245, 245, 0.8);
  padding: 8px 16px;
  border-radius: 20px;
  display: inline-block;
}

.follow-time {
  margin: 0;
  font-size: 14px;
  color: #999;
  background: rgba(240, 240, 240, 0.8);
  padding: 5px 12px;
  border-radius: 15px;
  display: inline-block;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 30px;
  color: #999;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.empty-state:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.empty-state p {
  font-size: 18px;
  margin: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 60px 30px;
  color: #666;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.loading-state:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
}

.loading-state p {
  font-size: 18px;
  margin: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.6;
  }
}

/* 回到顶部按钮 */
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0;
  visibility: hidden;
  z-index: 100;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-to-top.show {
  opacity: 1;
  visibility: visible;
  animation: fadeInUp 0.5s ease;
}

.back-to-top:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-8px) scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.back-to-top:active {
  transform: translateY(-5px) scale(0.95);
}

/* 统计信息 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 25px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.stat-label {
  font-size: 16px;
  color: #666;
  margin-bottom: 15px;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}
</style>