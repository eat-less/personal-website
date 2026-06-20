<template>
  <div class="admin-dashboard">
    <div class="sidebar">
      <h2>管理员中心</h2>
      <ul>
        <li @click="activeModule = 'users'" :class="{ active: activeModule === 'users' }">
          <span class="icon">👥</span>
          <span>用户管理</span>
        </li>
        <li @click="activeModule = 'products'" :class="{ active: activeModule === 'products' }">
          <span class="icon">📦</span>
          <span>商品管理</span>
        </li>
        <li @click="activeModule = 'orders'" :class="{ active: activeModule === 'orders' }">
          <span class="icon">📋</span>
          <span>订单管理</span>
        </li>
        <li @click="activeModule = 'announcements'" :class="{ active: activeModule === 'announcements' }">
          <span class="icon">📢</span>
          <span>公告管理</span>
        </li>
        <li @click="activeModule = 'statistics'" :class="{ active: activeModule === 'statistics' }">
          <span class="icon">📊</span>
          <span>数据统计</span>
        </li>
        <li @click="activeModule = 'comments'" :class="{ active: activeModule === 'comments' }">
          <span class="icon">💬</span>
          <span>评论管理</span>
        </li>
        <li @click="logout" class="logout">
          <span class="icon">🚪</span>
          <span>退出登录</span>
        </li>
      </ul>
    </div>
    <div class="main-content">
      <div class="header">
        <h1>管理员控制台</h1>
        <div class="user-info">
          <span>欢迎，{{ username }}</span>
        </div>
      </div>
      <div class="module-content">
        <UserManagement v-if="activeModule === 'users'" />
        <ProductManagement v-else-if="activeModule === 'products'" />
        <OrderManagement v-else-if="activeModule === 'orders'" />
        <AnnouncementManagement v-else-if="activeModule === 'announcements'" />
        <StatisticsManagement v-else-if="activeModule === 'statistics'" />
        <CommentManagement v-else-if="activeModule === 'comments'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import UserManagement from './admin/UserManagement.vue';
import ProductManagement from './admin/ProductManagement.vue';
import OrderManagement from './admin/OrderManagement.vue';
import AnnouncementManagement from './admin/AnnouncementManagement.vue';
import StatisticsManagement from './admin/StatisticsManagement.vue';
import CommentManagement from './admin/CommentManagement.vue';

const router = useRouter();
const activeModule = ref('users');
const username = ref('');

onMounted(() => {
  // 检查是否为管理员
  const userInfo = JSON.parse(sessionStorage.getItem('user_info'));
  if (!userInfo || !userInfo.is_admin) {
    router.push('/');
    return;
  }
  username.value = userInfo.username;
});

const logout = () => {
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('refresh_token');
  sessionStorage.removeItem('user');
  sessionStorage.removeItem('profile');
  sessionStorage.removeItem('user_info');
  router.push('/login');
};
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: white;
  padding: 20px 0;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.sidebar h2 {
  text-align: center;
  margin-bottom: 40px;
  font-size: 1.5rem;
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  padding: 15px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.sidebar li:hover {
  background-color: #34495e;
}

.sidebar li.active {
  background-color: #3498db;
  border-left: 4px solid #2980b9;
}

.sidebar .icon {
  margin-right: 15px;
  font-size: 1.2rem;
}

.sidebar .logout {
  margin-top: 40px;
  color: #e74c3c;
}

.sidebar .logout:hover {
  background-color: rgba(231, 76, 60, 0.1);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background-color: white;
  padding: 20px 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  font-size: 1.8rem;
  color: #2c3e50;
}

.user-info {
  font-size: 1rem;
  color: #7f8c8d;
}

.module-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
}
</style>