<template>
  <div class="home-container">
    <header class="header">
      <div class="logo">校园二手商品交易平台</div>
      <div class="user-menu">
        <div class="user-dropdown">
          <button class="user-btn" @click="toggleDropdown">
            <div class="user-avatar">
              <img 
                v-if="userProfile?.avatar" 
                :src="userProfile.avatar" 
                :alt="user?.username || '用户'"
              >
              <span v-else class="avatar-placeholder">{{ user?.username?.charAt(0) || 'U' }}</span>
            </div>
            <span class="username">{{ user?.username || '用户' }}</span>
            <span class="dropdown-arrow">{{ isDropdownOpen ? '▼' : '▲' }}</span>
          </button>
          <div class="dropdown-menu" v-if="isDropdownOpen">
            <div class="dropdown-item" @click="showAccountSwitcher">
              <span class="item-icon">🔄</span>
              <span>切换账号</span>
            </div>
            <div class="dropdown-divider"></div>
            <div class="dropdown-item" @click="logout">
              <span class="item-icon">🚪</span>
              <span>退出登录</span>
            </div>
          </div>
        </div>
      </div>
      <!-- 账号切换弹窗 -->
      <div class="modal" v-if="showAccountModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>切换账号</h3>
            <button class="close-btn" @click="showAccountModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="recent-accounts" v-if="recentAccounts.length > 0">
              <h4>近期登录</h4>
              <div class="account-list">
                <div class="account-item" 
                  v-for="account in recentAccounts" 
                  :key="account.email"
                  @click="switchToAccount(account)"
                >
                  <div class="account-avatar">
                    <img 
                      v-if="account.avatar" 
                      :src="account.avatar" 
                      :alt="account.username" 
                      style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;"
                      @error="handleAvatarError($event, account)"
                    >
                    <span v-else class="avatar-placeholder">{{ account.username.charAt(0) }}</span>
                  </div>
                  <div class="account-info">
                    <div class="account-username">{{ account.username }}</div>
                    <div class="account-email">{{ account.email }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="add-account">
              <button class="btn-primary" @click="addNewAccount">
                <span class="add-icon">+</span>
                添加新账号
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
    
    <div class="main-content">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <nav class="sidebar-nav">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">全部商品</router-link>
          <router-link to="/transactions" class="nav-item" :class="{ active: $route.path === '/transactions' }">交易信息</router-link>
          <router-link to="/messages" class="nav-item" :class="{ active: $route.path === '/messages' }">私信列表</router-link>
          <router-link to="/announcements" class="nav-item" :class="{ active: $route.path === '/announcements' }">
            <span>公告通知</span>
            <span v-if="unreadAnnouncements > 0" class="unread-badge">{{ unreadAnnouncements }}</span>
          </router-link>
          <router-link to="/profile" class="nav-item" :class="{ active: $route.path === '/profile' }">个人中心</router-link>
          <router-link to="/publish" class="nav-item sell-btn" :class="{ active: $route.path === '/publish' }">卖闲置</router-link>
        </nav>
      </aside>
      
      <!-- 主内容区域 -->
      <main class="main">
        <!-- 轮播图区域 -->
        <section class="carousel-section">
          <h2 class="carousel-title">热门商品</h2>
          <div class="carousel-container">
            <div v-if="topLikedProducts.length > 0">
              <div class="carousel-slide" v-for="(product, index) in topLikedProducts" :key="product.id" :class="{ active: currentSlide === index }">
                <div class="carousel-content" @click="goToProductDetail(product.id)">
                  <div class="carousel-image">
                    <img 
                      v-if="product.images && product.images.length > 0" 
                      :src="product.images[0].image" 
                      :alt="product.title"
                    >
                    <span v-else class="placeholder">商品图片</span>
                  </div>
                </div>
              </div>
              <div class="carousel-indicators">
                <button 
                  v-for="(product, index) in topLikedProducts" 
                  :key="index"
                  class="indicator" 
                  :class="{ active: currentSlide === index }"
                  @click="currentSlide = index"
                ></button>
              </div>
            </div>
            <div v-else class="carousel-empty">
              <div class="empty-icon">📦</div>
              <p>暂无商品</p>
              <p class="empty-subtitle">商品将在这里展示</p>
            </div>
          </div>
        </section>
        
        <!-- 搜索和筛选区域 -->
        <section class="search-section">
          <div class="search-bar">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="搜索商品名称、描述、标题、分类..."
              @input="handleSearch"
            >
            <button class="search-btn" @click="handleSearch">搜索</button>
          </div>
          
          <div class="filter-section">
            <h3>价格筛选</h3>
            <div class="price-filters">
              <button 
                v-for="range in priceRanges" 
                :key="range.label"
                class="price-btn"
                :class="{ active: selectedPriceRange === range.value }"
                @click="selectPriceRange(range.value)"
              >
                {{ range.label }}
              </button>
              <div class="custom-price">
                <input type="number" v-model.number="customMinPrice" placeholder="最低价">
                <span>-</span>
                <input type="number" v-model.number="customMaxPrice" placeholder="最高价">
                <button class="price-btn" @click="applyCustomPrice">确定</button>
              </div>
            </div>
          </div>
        </section>
        
        <!-- 商品列表 -->
        <section class="products-section">
          <!-- 分类导航 -->
          <div class="category-nav">
            <button 
              class="category-btn" 
              :class="{ active: selectedCategory === 'all' }"
              @click="selectCategory('all')"
            >
              全部商品
            </button>
            <button 
              v-for="category in categories" 
              :key="category.id"
              class="category-btn" 
              :class="{ active: selectedCategory === category.id }"
              @click="selectCategory(category.id)"
            >
              {{ getCategoryName(category.name) }}
            </button>
            <button 
              class="category-btn refresh-btn"
              @click="randomizeProducts"
              title="随机排序商品"
            >
              🔄 刷新
            </button>
          </div>
          
          <div class="products-grid">
            <div class="product-card" v-for="product in products" :key="product.id" @click="goToProductDetail(product.id)">
              <div class="product-image">
                <img 
                  v-if="product.images && product.images.length > 0" 
                  :src="product.images[0].image" 
                  :alt="product.title"
                  @error="handleImageError($event)"
                >
                <span v-else class="placeholder">商品图片</span>
              </div>
              <div class="product-info">
                <h3 class="product-title">{{ product.title }}</h3>
                <p class="product-price">¥{{ product.price }}</p>
                <p class="product-description">{{ product.description }}</p>
                <div class="product-meta">
                  <!-- 卖家信息 -->
                  <div class="product-seller">
                    <div class="seller-avatar">
                      <img 
                        v-if="product.seller_avatar" 
                        :src="product.seller_avatar" 
                        :alt="product.seller_username"
                        class="seller-avatar-img"
                      >
                      <span v-else class="avatar-placeholder">{{ product.seller_username?.charAt(0) || 'U' }}</span>
                    </div>
                    <span class="seller-name">{{ product.seller_username }}</span>
                  </div>
                  
                  <!-- 配送方式 -->
                  <span class="product-delivery" :class="{ 'delivery-highlight': product.allow_delivery }">
                    {{ product.allow_delivery ? '🚚 支持配送' : '📍 买家自提' }}
                  </span>
                  
                  <!-- 浏览量 -->
                  <span class="product-views">👁️ {{ product.views }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 加载更多指示器 -->
          <div v-if="loading" class="loading-more">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>
          
          <!-- 空状态 -->
          <div v-if="products.length === 0" class="empty-state">
            <div class="empty-icon">📦</div>
            <p>暂无商品</p>
            <button class="btn-primary" @click="goToPublish">发布第一个商品</button>
          </div>
        </section>
      </main>
    </div>
    

    

    
    <!-- 回到顶部按钮 -->
    <button class="back-to-top" :class="{ 'show': showBackToTop }" @click="scrollToTop">
      ↑
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import api from '../axios';

const unreadAnnouncements = ref(0);

const updateUnreadCount = () => {
  const count = localStorage.getItem('unreadAnnouncements');
  if (count) {
    unreadAnnouncements.value = parseInt(count);
  } else {
    unreadAnnouncements.value = 0;
  }
};

// 监听 storage 事件，当未读数量变化时更新
window.addEventListener('storage', updateUnreadCount);

const router = useRouter();
const showBackToTop = ref(false);
const user = ref(() => {
  try {
    const userStr = sessionStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  } catch (error) {
    console.error('解析用户信息失败:', error);
    sessionStorage.removeItem('user');
    return null;
  }
});

// 安全解析sessionStorage中的个人资料
const userProfile = ref(null);

// 初始化userProfile
const initUserProfile = () => {
  try {
    const profileStr = sessionStorage.getItem('profile');
    userProfile.value = profileStr ? JSON.parse(profileStr) : null;
  } catch (error) {
    console.error('解析个人资料失败:', error);
    sessionStorage.removeItem('profile');
    userProfile.value = null;
  }
};

// 初始化
initUserProfile();

// 监听storage事件，当其他标签页更新sessionStorage时同步更新
window.addEventListener('storage', (event) => {
  if (event.key === 'profile') {
    initUserProfile();
    // 更新商品列表中当前用户的头像
    updateProductSellerAvatars();
  }
  if (event.key === 'user') {
    // 重新初始化用户信息
    user.value = JSON.parse(sessionStorage.getItem('user') || 'null');
    // 更新商品列表中当前用户的头像
    updateProductSellerAvatars();
  }
});

// 更新商品列表中当前用户的头像
const updateProductSellerAvatars = () => {
  const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}');
  const currentProfile = JSON.parse(sessionStorage.getItem('profile') || '{}');
  
  // 只有当本地存储中有当前用户的头像时，才更新商品头像
  if (currentUser.username && currentProfile.avatar) {
    // 遍历商品列表，只更新当前用户的商品头像
    products.value = products.value.map(product => {
      if (product.seller_username === currentUser.username) {
        return {
          ...product,
          seller_avatar: currentProfile.avatar
        };
      }
      return product;
    });
  }
};

// 下拉菜单状态
const isDropdownOpen = ref(false);
// 账号切换弹窗状态
const showAccountModal = ref(false);
// 近期登录账号
const recentAccounts = ref([]);

// 商品数据
const products = ref([]);
// 分类数据
const categories = ref([]);
// 当前选中的分类
const selectedCategory = ref('all');
// 分页参数
const currentPage = ref(1);
const pageSize = ref(20);
const hasMore = ref(true);
const loading = ref(false);

// 轮播图数据
const topLikedProducts = ref([]);
const currentSlide = ref(0);
let carouselTimer = null;

// 搜索和筛选参数
const searchQuery = ref('');
const selectedPriceRange = ref('all');
const customMinPrice = ref(null);
const customMaxPrice = ref(null);

// 价格范围选项
const priceRanges = [
  { label: '全部', value: 'all' },
  { label: '0-10', value: '0-10' },
  { label: '10-30', value: '10-30' },
  { label: '30-50', value: '30-50' },
  { label: '50-100', value: '50-100' },
  { label: '100+', value: '100+' }
];

// 获取商品列表
const getProducts = async (loadMore = false) => {
  if (loading.value) return;
  
  loading.value = true;
  try {
    let minPrice = null;
    let maxPrice = null;
    
    // 根据选择的价格范围设置价格参数
    if (selectedPriceRange.value === 'all') {
      minPrice = null;
      maxPrice = null;
    } else if (selectedPriceRange.value === '0-10') {
      minPrice = 0;
      maxPrice = 10;
    } else if (selectedPriceRange.value === '10-30') {
      minPrice = 10;
      maxPrice = 30;
    } else if (selectedPriceRange.value === '30-50') {
      minPrice = 30;
      maxPrice = 50;
    } else if (selectedPriceRange.value === '50-100') {
      minPrice = 50;
      maxPrice = 100;
    } else if (selectedPriceRange.value === '100+') {
      minPrice = 100;
      maxPrice = null;
    }
    
    // 构建请求参数
    const params = {
      search: searchQuery.value,
      page: loadMore ? currentPage.value + 1 : 1,
      page_size: pageSize.value
    };
    
    if (minPrice !== null) {
      params.min_price = minPrice;
    }
    if (maxPrice !== null) {
      params.max_price = maxPrice;
    }
    
    // 添加分类参数
    if (selectedCategory.value !== 'all') {
      params.category = selectedCategory.value;
    }
    
    // 发送请求获取商品列表
    const response = await api.get('/products/', { params });
    let productsData = response.data.results || response.data;
    
    // 检查本地存储中是否有其他用户的头像信息
    const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
    
    // 更新商品列表中的头像，包括其他用户的头像
    productsData = productsData.map(product => {
      // 检查本地存储中是否有该卖家的头像
      if (product.seller_username && userAvatars[product.seller_username]) {
        return {
          ...product,
          seller_avatar: userAvatars[product.seller_username]
        };
      }
      return product;
    });
    
    if (loadMore) {
      products.value = [...products.value, ...productsData];
      currentPage.value++;
    } else {
      products.value = productsData;
      currentPage.value = 1;
    }
    
    // 检查是否还有更多商品
    hasMore.value = productsData.length === pageSize.value;
    
    // 更新商品列表中当前用户的头像
    updateProductSellerAvatars();
  } catch (error) {
    console.error('获取商品列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 搜索处理
const handleSearch = () => {
  getProducts();
};

// 选择价格范围
const selectPriceRange = (range) => {
  selectedPriceRange.value = range;
  // 清除自定义价格
  customMinPrice.value = null;
  customMaxPrice.value = null;
  // 重置分页状态
  currentPage.value = 1;
  hasMore.value = true;
  getProducts();
};

// 选择分类
const selectCategory = (categoryId) => {
  selectedCategory.value = categoryId;
  // 重置分页状态
  currentPage.value = 1;
  hasMore.value = true;
  getProducts();
};

// 获取分类中文名称
const getCategoryName = (name) => {
  const categoryMap = {
    'books': '图书教材',
    'electronics': '电子数码',
    'clothing': '服饰鞋包',
    'sports': '运动户外',
    'jewelry': '时尚首饰',
    'food': '零食饮料',
    'beauty': '美妆护肤',
    'home': '家居日用',
    'cards': '卡包劵包',
    'other': '其他'
  };
  return categoryMap[name] || name;
};

// 获取分类列表
const getCategories = async () => {
  try {
    const response = await api.get('/categories/');
    categories.value = response.data;
  } catch (error) {
    console.error('获取分类列表失败:', error);
    // 模拟分类数据
    categories.value = [
      { id: 1, name: '电子产品' },
      { id: 2, name: '图书教材' },
      { id: 3, name: '服饰鞋包' },
      { id: 4, name: '运动户外' },
      { id: 5, name: '时尚首饰' },
      { id: 6, name: '零食饮料' },
      { id: 7, name: '美妆护肤' },
      { id: 8, name: '家居日用' },
      { id: 9, name: '卡包劵包' },
      { id: 10, name: '其他' }
    ];
  }
};

// 应用自定义价格
const applyCustomPrice = async () => {
  // 设置为自定义范围
  selectedPriceRange.value = 'custom';
  // 重置分页状态
  currentPage.value = 1;
  hasMore.value = true;
  
  await getProducts();
};

// 图片加载失败处理
const handleImageError = (event) => {
  event.target.style.display = 'none';
  event.target.nextElementSibling.style.display = 'block';
};

// 切换下拉菜单
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
};

// 显示账号切换器
const showAccountSwitcher = () => {
  isDropdownOpen.value = false;
  // 延迟一点时间再显示模态框，确保下拉菜单完全关闭
  setTimeout(() => {
    showAccountModal.value = true;
    // 加载近期登录账号
    loadRecentAccounts();
  }, 100);
};



// 加载近期登录账号
const loadRecentAccounts = () => {
  try {
    const recentAccountsStr = localStorage.getItem('recentAccounts');
    // 检查本地存储中是否有用户头像信息
    const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
    
    if (recentAccountsStr) {
      let accounts = JSON.parse(recentAccountsStr);
      // 确保所有账号都有正确的头像处理
      recentAccounts.value = accounts.map(account => {
        // 首先检查本地存储中是否有该用户的最新头像
        let avatarUrl = userAvatars[account.username] || account.avatar;
        
        if (avatarUrl && !avatarUrl.startsWith('http') && !avatarUrl.startsWith('data:image/')) {
          // 如果是相对路径，构建完整URL（使用后端域名）
          avatarUrl = 'http://127.0.0.1:8000' + avatarUrl;
        }
        
        return {
          ...account,
          avatar: avatarUrl
        };
      });
      
    } else {
      recentAccounts.value = [];
    }
  } catch (error) {
    recentAccounts.value = [];
  }
};

// 切换到指定账号
const switchToAccount = (account) => {
  showAccountModal.value = false;
  
  try {
    // 检查账号是否有保存的tokens
    if (account.tokens) {
      // 保存tokens和用户信息到会话存储
      sessionStorage.setItem('access_token', account.tokens.access);
      sessionStorage.setItem('refresh_token', account.tokens.refresh);
      
      // 检查本地存储中是否有该用户的最新头像
      const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
      const latestAvatar = userAvatars[account.username] || account.avatar;
      
      // 创建用户对象
      const userObj = {
        username: account.username,
        email: account.email,
        avatar: latestAvatar
      };
      
      // 创建profile对象
      const profileObj = {
        avatar: latestAvatar
      };
      
      // 保存用户信息和管理员状态
      sessionStorage.setItem('user', JSON.stringify(userObj));
      sessionStorage.setItem('profile', JSON.stringify(profileObj));
      sessionStorage.setItem('user_info', JSON.stringify({
        username: account.username,
        is_admin: account.is_admin || false
      }));
      
      // 根据是否为管理员跳转到不同页面
      if (account.is_admin) {
        // 跳转到管理员页面
        router.push('/admin').then(() => {
          // 强制刷新页面，确保新的用户信息生效
          window.location.reload();
        });
      } else {
        // 跳转到首页
        router.push('/').then(() => {
          // 强制刷新页面，确保新的用户信息生效
          window.location.reload();
        });
      }
    } else {
      // 如果没有保存的tokens，跳转到登录页
      // 清空当前登录信息
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      sessionStorage.removeItem('user');
      sessionStorage.removeItem('profile');
      sessionStorage.removeItem('user_info');
      
      // 跳转到登录页
      router.push('/login');
    }
  } catch (error) {
    console.error('切换账号失败:', error);
    // 切换失败时跳转到登录页
    router.push('/login');
  }
};

// 处理头像加载错误
const handleAvatarError = (event, account) => {
  // 隐藏错误的头像
  event.target.style.display = 'none';
  // 可以选择显示占位符
};

// 强制刷新近期账号
const refreshRecentAccounts = async () => {
  try {
    // 尝试从服务器获取最新的用户信息
    const response = await api.get('/accounts/profile/');
    const { user, profile } = response.data;
    
    // 更新会话存储
    sessionStorage.setItem('user', JSON.stringify(user));
    sessionStorage.setItem('profile', JSON.stringify(profile));
    
    // 重新保存到近期账号
    let recentAccounts = JSON.parse(localStorage.getItem('recentAccounts') || '[]');
    recentAccounts = recentAccounts.filter(account => account.email !== user.email);
    
    let avatarUrl = null;
    if (profile?.avatar) {
      if (profile.avatar.startsWith('http')) {
        avatarUrl = profile.avatar;
      } else {
        avatarUrl = window.location.origin + profile.avatar;
      }
    }
    
    // 获取当前用户的管理员状态
    const userInfo = JSON.parse(sessionStorage.getItem('user_info') || '{}');
    
    recentAccounts.unshift({
      username: user.username,
      email: user.email,
      avatar: avatarUrl,
      tokens: {
        access: sessionStorage.getItem('access_token'),
        refresh: sessionStorage.getItem('refresh_token')
      },
      is_admin: userInfo.is_admin || false
    });
    
    if (recentAccounts.length > 5) {
      recentAccounts = recentAccounts.slice(0, 5);
    }
    
    localStorage.setItem('recentAccounts', JSON.stringify(recentAccounts));
    loadRecentAccounts();
    console.log('Recent accounts refreshed');
  } catch (error) {
    console.error('Error refreshing recent accounts:', error);
  }
};

// 添加新账号
const addNewAccount = () => {
  showAccountModal.value = false;
  // 清空当前登录信息
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('refresh_token');
  sessionStorage.removeItem('user');
  sessionStorage.removeItem('profile');
  sessionStorage.removeItem('user_info');
  // 跳转到登录页
  router.push('/login');
};

// 退出登录
const logout = () => {
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('refresh_token');
  sessionStorage.removeItem('user');
  sessionStorage.removeItem('profile');
  sessionStorage.removeItem('user_info');
  router.push('/login');
};

// 跳转到发布页面
const goToPublish = () => {
  router.push('/publish');
};

// 跳转到商品详情页面
const goToProductDetail = (productId) => {
  router.push(`/product/${productId}`);
};

// 获取最新的用户信息
const fetchUserProfile = async () => {
  try {
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
    
    // 更新会话存储
    sessionStorage.setItem('user', JSON.stringify(updatedUser));
    sessionStorage.setItem('profile', JSON.stringify(updatedProfile));
    
    // 更新响应式数据
    user.value = updatedUser;
    userProfile.value = updatedProfile;
  } catch (err) {
    console.error('获取用户信息失败:', err);
  }
};

// 定时器，用于自动刷新商品列表
let refreshTimer = null;

// 页面挂载时获取商品列表
onMounted(() => {
  getProducts();
  getCategories();
  fetchUserProfile();
  getTopLikedProducts();
  // 添加滚动事件监听
  window.addEventListener('scroll', handleScroll);
  
  // 启动轮播图自动切换
  startCarousel();
  
  // 初始化未读公告数量
  updateUnreadCount();
  
  // 设置定时器，每30秒自动刷新一次商品列表和轮播图数据
  refreshTimer = setInterval(() => {
    getProducts();
    getTopLikedProducts();
  }, 30000);
});

onUnmounted(() => {
  // 清除滚动事件监听
  window.removeEventListener('scroll', handleScroll);
  // 清除定时器
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
  // 停止轮播图自动切换
  stopCarousel();
});

// 点击页面其他地方关闭下拉菜单
document.addEventListener('click', (event) => {
  const dropdown = document.querySelector('.user-dropdown');
  if (dropdown && !dropdown.contains(event.target)) {
    isDropdownOpen.value = false;
  }
});

// 滚动事件监听
const handleScroll = () => {
  showBackToTop.value = window.scrollY > 300;
  
  // 检测是否滚动到页面底部
  if (hasMore.value && !loading.value) {
    const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight;
    const clientHeight = document.documentElement.clientHeight || window.innerHeight;
    
    if (scrollTop + clientHeight >= scrollHeight - 300) {
      getProducts(true);
    }
  }
};

// 回到顶部
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
};

// 随机排序商品
const randomizeProducts = () => {
  // 打乱商品数组
  for (let i = products.value.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [products.value[i], products.value[j]] = [products.value[j], products.value[i]];
  }
};

// 获取点赞量最高的商品
const getTopLikedProducts = async () => {
  try {
    // 发送请求获取商品列表
    const response = await api.get('/products/');
    let productsData = response.data.results || response.data;
    
    // 检查本地存储中是否有其他用户的头像信息
    const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
    
    // 更新商品列表中的头像，包括其他用户的头像
    productsData = productsData.map(product => {
      // 检查本地存储中是否有该卖家的头像
      if (product.seller_username && userAvatars[product.seller_username]) {
        return {
          ...product,
          seller_avatar: userAvatars[product.seller_username]
        };
      }
      return product;
    });
    
    // 按点赞量排序，点赞数相同时随机排序
    productsData.sort((a, b) => {
      // 首先按点赞数降序排序，优先使用likes_count字段
      const likeDifference = (b.likes_count || b.likes || 0) - (a.likes_count || a.likes || 0);
      if (likeDifference !== 0) {
        return likeDifference;
      }
      // 点赞数相同时随机排序
      return Math.random() - 0.5;
    });
    
    // 取前3个商品，即使它们的点赞数为0
    topLikedProducts.value = productsData.slice(0, 3);
  } catch (error) {
    console.error('获取点赞量最高的商品失败:', error);
    topLikedProducts.value = [];
  }
};

// 启动轮播图自动切换
const startCarousel = () => {
  // 清除之前的定时器
  if (carouselTimer) {
    clearInterval(carouselTimer);
  }
  
  // 设置新的定时器，每5秒切换一次
  carouselTimer = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % topLikedProducts.value.length;
  }, 5000);
};

// 停止轮播图自动切换
const stopCarousel = () => {
  if (carouselTimer) {
    clearInterval(carouselTimer);
    carouselTimer = null;
  }
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.logo {
  font-size: 28px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo::before {
  content: '🛍️';
  font-size: 24px;
}

.user-menu {
  position: relative;
}

/* 用户下拉菜单 */
.user-dropdown {
  position: relative;
  display: inline-block;
}

/* 用户按钮 */
.user-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 用户头像 */
.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.user-avatar:hover img {
  transform: scale(1.1);
}

.avatar-placeholder {
  color: white;
  font-weight: bold;
  font-size: 18px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 用户名 */
.username {
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 下拉箭头 */
.dropdown-arrow {
  font-size: 12px;
  transition: transform 0.3s ease;
}

.user-btn:hover .dropdown-arrow {
  transform: rotate(180deg);
}

/* 下拉菜单 */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  min-width: 300px;
  z-index: 9999;
  overflow: visible;
  animation: dropdownFadeIn 0.3s ease;
  max-height: 400px;
  overflow-y: auto;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 下拉菜单项 */
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.dropdown-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.dropdown-item:hover::before {
  left: 100%;
}

.dropdown-item:hover {
  background: #f0f8ff;
  color: #667eea;
  transform: translateX(5px);
}

.dropdown-item:first-child {
  border-radius: 12px 12px 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 12px 12px;
}

/* 菜单项图标 */
.item-icon {
  font-size: 18px;
  flex-shrink: 0;
}

/* 分隔线 */
.dropdown-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
  margin: 4px 0;
}

/* 模态框 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(5px);
  margin: 0;
  padding: 0;
}

.modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 450px;
  max-height: 80vh;
  overflow-y: auto;
  animation: modalFadeIn 0.4s ease;
  position: relative;
  z-index: 10000;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 模态框头部 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px 16px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

/* 关闭按钮 */
.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #666;
  transform: rotate(90deg);
}

/* 模态框主体 */
.modal-body {
  padding: 24px;
}

/* 近期登录账号 */
.recent-accounts h4 {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 16px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.recent-accounts h4::before {
  content: '📋';
  font-size: 18px;
}

/* 账号列表 */
.account-list {
  margin-bottom: 24px;
}

/* 账号项 */
.account-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f9f9f9;
}

.account-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
  background: white;
}

/* 账号头像 */
.account-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.account-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  transition: transform 0.3s ease;
}

.account-avatar:hover img {
  transform: scale(1.1);
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 账号信息 */
.account-info {
  flex: 1;
}

.account-username {
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  font-size: 16px;
}

.account-email {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

/* 添加账号 */
.add-account {
  display: flex;
  justify-content: center;
}

/* 添加按钮 */
.add-account .btn-primary {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.add-account .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4191 100%);
}

/* 添加图标 */
.add-icon {
  font-size: 18px;
  font-weight: bold;
}

/* 主内容区域 */
.main-content {
  display: flex;
  flex: 1;
  background: transparent;
}

/* 左侧导航栏 */
.sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid #e0e0e0;
  padding: 30px 0;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 90px;
  height: calc(100vh - 90px);
  overflow-y: auto;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: block;
  padding: 16px 24px;
  color: #333;
  text-decoration: none;
  font-size: 16px;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.nav-item:hover::before {
  left: 100%;
}

.nav-item:hover,
.nav-item.active {
  background: #f0f8ff;
  color: #667eea;
  border-left-color: #667eea;
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.unread-badge {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border-radius: 50%;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
  margin-left: 8px;
  box-shadow: 0 2px 4px rgba(231, 76, 60, 0.3);
}

.sell-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  font-weight: 600;
  font-size: 16px;
  padding: 15px 20px;
  margin-top: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
  transition: all 0.3s ease;
}

.sell-btn:hover {
  background: linear-gradient(135deg, #ee5a6f 0%, #d34d5c 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(255, 107, 107, 0.4);
}

.sell-btn.active {
  background: linear-gradient(135deg, #d34d5c 0%, #c0392b 100%);
  box-shadow: 0 2px 4px rgba(211, 77, 92, 0.5);
}

.nav-item:nth-child(1)::before {
  content: '🏠';
  font-size: 18px;
}

.nav-item:nth-child(2)::before {
  content: '📊';
  font-size: 18px;
}

.nav-item:nth-child(3)::before {
  content: '💬';
  font-size: 18px;
}

.nav-item:nth-child(4)::before {
  content: '👤';
  font-size: 18px;
}

/* 主内容 */
.main {
  flex: 1;
  padding: 40px 60px;
  background: transparent;
}

/* 轮播图区域 */
.carousel-section {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  position: relative;
  overflow: hidden;
}

.carousel-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #ff6b6b, #ee5a6f, #f9ca24, #6ab04c);
}

.carousel-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 24px;
  color: #333;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.carousel-title::before,
.carousel-title::after {
  content: '❤️';
  font-size: 20px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

.carousel-container {
  position: relative;
  height: 400px;
  overflow: hidden;
  border-radius: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.carousel-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.5s ease;
  pointer-events: none;
}

.carousel-slide.active {
  opacity: 1;
  pointer-events: auto;
}

.carousel-content {
  height: 100%;
  cursor: pointer;
  transition: transform 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.carousel-content:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.carousel-image {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.carousel-image::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  z-index: 1;
}

.carousel-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
  position: relative;
  z-index: 0;
}

.carousel-content:hover .carousel-image img {
  transform: scale(1.05);
}

.carousel-indicators {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 10;
}

.indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.5);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.indicator:hover {
  background: rgba(102, 126, 234, 0.8);
  transform: scale(1.2);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.indicator.active {
  background: #667eea;
  transform: scale(1.3);
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.8);
}

/* 轮播图空状态 */
.carousel-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px;
}

.carousel-empty .empty-icon {
  font-size: 60px;
  margin-bottom: 20px;
  animation: bounce 2s infinite;
}

.carousel-empty p {
  font-size: 20px;
  font-weight: 600;
  color: #666;
  margin-bottom: 12px;
}

.carousel-empty .empty-subtitle {
  font-size: 16px;
  color: #999;
  margin-bottom: 0;
}

/* 搜索区域 */
.search-section {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  position: relative;
  overflow: hidden;
}

.search-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #f5576c);
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  align-items: center;
}

.search-bar input {
  flex: 1;
  padding: 14px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 30px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #f9f9f9;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.search-bar input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.search-btn {
  padding: 14px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4191 100%);
}

.search-btn::before {
  content: '🔍';
  font-size: 16px;
}

/* 筛选区域 */
.filter-section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-section h3::before {
  content: '🎯';
  font-size: 20px;
}

.price-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.price-btn {
  padding: 10px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.price-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.price-btn:hover::before {
  left: 100%;
}

.price-btn:hover,
.price-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.custom-price {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 24px;
  background: #f9f9f9;
  padding: 10px 16px;
  border-radius: 25px;
  border: 1px solid #e0e0e0;
}

.custom-price input {
  width: 100px;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.custom-price input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.custom-price span {
  color: #666;
  font-weight: 500;
}

/* 商品列表 */
.products-section {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.products-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #4CAF50, #8BC34A, #CDDC39, #FFEB3B);
}

/* 分类导航 */
.category-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
  align-items: center;
}

.category-btn {
  padding: 10px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  background: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.category-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.category-btn:hover::before {
  left: 100%;
}

.category-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f0f8ff;
  transform: translateY(-2px);
}

.category-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
}

/* 刷新按钮样式 */
.refresh-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border-color: #4CAF50;
  margin-left: auto;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.refresh-btn:hover {
  background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
  border-color: #45a049;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
}

.refresh-btn:active {
  transform: scale(0.95);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

/* 加载更多指示器 */
.loading-more {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  margin-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-more p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.product-card {
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  background: white;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.product-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.05), transparent);
  transition: left 0.5s ease;
}

.product-card:hover::before {
  left: 100%;
}

.product-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-5px);
  border-color: #667eea;
}

.product-image {
  height: 220px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
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

.placeholder {
  color: #999;
  font-size: 16px;
  font-weight: 500;
  text-align: center;
  padding: 20px;
}

.product-info {
  padding: 20px;
}

.product-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #333;
  height: 48px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  font-weight: 600;
  line-height: 1.4;
}

.product-price {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: bold;
  color: #f44336;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.product-description {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #666;
  height: 48px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

/* 商品元信息 */
.product-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* 卖家信息 */
.product-seller {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 120px;
}

.seller-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  font-weight: bold;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.seller-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  transition: transform 0.3s ease;
}

.seller-avatar:hover .seller-avatar-img {
  transform: scale(1.1);
}

.seller-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  transition: color 0.3s ease;
}

.product-card:hover .seller-name {
  color: #667eea;
}

/* 配送方式 */
.product-delivery {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  flex-shrink: 0;
  transition: all 0.3s ease;
  background: #f0f8ff;
  color: #1976D2;
  border: 1px solid #e3f2fd;
}

/* 支持配送高亮样式 */
.product-delivery.delivery-highlight {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
  animation: pulse 2s infinite;
  transform: scale(1.05);
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
  }
  50% {
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.6);
  }
}

/* 浏览量 */
.product-views {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #666;
  flex-shrink: 0;
  background: #f9f9f9;
  padding: 6px 12px;
  border-radius: 15px;
  transition: all 0.3s ease;
}

.product-card:hover .product-views {
  background: #f0f8ff;
  color: #667eea;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 0;
  color: #999;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  margin-top: 20px;
}

.empty-state .empty-icon {
  font-size: 80px;
  margin-bottom: 24px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-20px);
  }
  60% {
    transform: translateY(-10px);
  }
}

.empty-state p {
  font-size: 20px;
  margin-bottom: 16px;
  color: #666;
  font-weight: 600;
}

.empty-state .btn-primary {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.empty-state .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4191 100%);
}

/* 回到顶部按钮 */
.back-to-top {
  position: fixed;
  bottom: 120px;
  right: 40px;
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
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.back-to-top:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4191 100%);
  transform: translateY(-5px) scale(1.1);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.back-to-top.show {
  opacity: 1;
  visibility: visible;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 16px 24px;
  }
  
  .logo {
    font-size: 24px;
  }
  
  .main {
    padding: 20px;
  }
  
  .sidebar {
    width: 180px;
    padding: 20px 0;
  }
  
  .nav-item {
    padding: 12px 16px;
    font-size: 14px;
  }
  
  .search-section {
    padding: 20px;
  }
  
  .products-section {
    padding: 20px;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
  
  .product-image {
    height: 180px;
  }
  
  .sell-button {
    bottom: 30px;
    right: 30px;
    padding: 12px 24px;
    font-size: 16px;
  }
  
  .back-to-top {
    bottom: 100px;
    right: 30px;
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}
</style>
