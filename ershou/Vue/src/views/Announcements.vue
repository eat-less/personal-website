<template>
  <div class="announcements-container">
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
        返回
      </button>
      <h1>公告通知</h1>
    </div>
    
    <div class="announcements-content">
      <div class="sidebar">
        <nav class="sidebar-nav">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">全部商品</router-link>
          <router-link to="/transactions" class="nav-item" :class="{ active: $route.path === '/transactions' }">交易信息</router-link>
          <router-link to="/messages" class="nav-item" :class="{ active: $route.path === '/messages' }">私信列表</router-link>
          <router-link to="/announcements" class="nav-item" :class="{ active: $route.path === '/announcements' }">公告通知</router-link>
          <router-link to="/profile" class="nav-item" :class="{ active: $route.path === '/profile' }">个人中心</router-link>
        </nav>
      </div>
      
      <div class="main-content">
        <div class="announcements-list">
          <h2>最新公告</h2>
          <div v-if="announcements.length > 0">
            <div 
              v-for="announcement in announcements" 
              :key="announcement.id"
              class="announcement-item"
              :class="{ unread: !announcement.is_read }"
              @click="markAsRead(announcement.id)"
            >
              <div class="announcement-header">
                <h3 class="announcement-title">{{ announcement.title }}</h3>
                <span class="announcement-date">{{ formatDate(announcement.created_at) }}</span>
              </div>
              <div class="announcement-content">{{ announcement.content }}</div>
            </div>
          </div>
          <div v-else class="empty-announcements">
            <div class="empty-icon">📢</div>
            <p>暂无公告</p>
            <p class="empty-subtitle">有新公告时会显示在这里</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../axios';

const router = useRouter();
const route = useRoute();
const announcements = ref([]);
const unreadCount = ref(0);

const fetchAnnouncements = async () => {
  try {
    const response = await api.get('/user/announcements/');
    announcements.value = response.data;
    // 计算未读公告数量
    unreadCount.value = announcements.value.filter(announcement => !announcement.is_read).length;
    // 更新 localStorage 中的未读数量，供侧边栏使用
    localStorage.setItem('unreadAnnouncements', unreadCount.value.toString());
    // 触发 storage 事件，通知其他组件更新
    window.dispatchEvent(new Event('storage'));
  } catch (error) {
    console.error('获取公告列表失败:', error);
    announcements.value = [];
    unreadCount.value = 0;
  }
};

const markAsRead = async (announcementId) => {
  try {
    await api.post('/user/announcements/read/', {
      announcement_id: announcementId
    });
    // 更新本地状态
    const announcement = announcements.value.find(a => a.id === announcementId);
    if (announcement) {
      announcement.is_read = true;
      // 重新计算未读数量
      unreadCount.value = announcements.value.filter(a => !a.is_read).length;
      localStorage.setItem('unreadAnnouncements', unreadCount.value.toString());
      window.dispatchEvent(new Event('storage'));
    }
  } catch (error) {
    console.error('标记公告为已读失败:', error);
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

const goBack = () => {
  router.back();
};

// 定时器，用于自动刷新公告列表
let refreshTimer = null;

onMounted(() => {
  fetchAnnouncements();
  // 设置定时器，每30秒自动刷新一次公告列表
  refreshTimer = setInterval(() => {
    fetchAnnouncements();
  }, 30000);
});

onUnmounted(() => {
  // 清除定时器
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
});
</script>

<style scoped>
.announcements-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.back-btn {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 50px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.back-btn:hover {
  background: linear-gradient(135deg, #2980b9 0%, #1f618d 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.back-icon {
  font-size: 16px;
  font-weight: bold;
}

.page-header h1 {
  margin: 0;
  margin-left: 20px;
  font-size: 24px;
  color: #2c3e50;
  font-weight: 600;
}

.announcements-content {
  display: flex;
  gap: 30px;
  min-height: 70vh;
}

.sidebar {
  width: 250px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  padding: 15px 20px;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
}

.nav-item:hover {
  background: linear-gradient(135deg, #f0f4f8 0%, #e9ecef 100%);
  transform: translateX(5px);
}

.nav-item.active {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
}

.main-content {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.announcements-list h2 {
  margin-top: 0;
  margin-bottom: 30px;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

.announcement-item {
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid #3498db;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.announcement-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.announcement-item.unread {
  background-color: #e3f2fd;
  border-left-color: #1976d2;
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.2);
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.announcement-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.announcement-date {
  font-size: 14px;
  color: #7f8c8d;
  white-space: nowrap;
}

.announcement-content {
  font-size: 16px;
  line-height: 1.6;
  color: #555;
  margin-top: 10px;
}

.empty-announcements {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-announcements p {
  margin: 10px 0;
  font-size: 18px;
}

.empty-subtitle {
  font-size: 14px;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .announcements-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    order: 1;
  }
  
  .main-content {
    order: 2;
  }
  
  .sidebar-nav {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 10px;
  }
  
  .nav-item {
    white-space: nowrap;
    flex-shrink: 0;
  }
}
</style>