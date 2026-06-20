<template>
  <div class="user-management">
    <h2>用户管理</h2>
    <div class="action-bar">
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜索用户名、邮箱或学号"
          @input="searchUsers"
        />
        <button class="btn-primary">搜索</button>
      </div>
      <button class="btn-success" @click="showAddAdminDialog = true">添加管理员账号</button>
    </div>
    
    <!-- 添加管理员对话框 -->
    <div v-if="showAddAdminDialog" class="dialog-overlay">
      <div class="dialog">
        <div class="dialog-header">
          <h3>添加管理员账号</h3>
          <button class="dialog-close" @click="showAddAdminDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>用户名</label>
            <input type="text" v-model="newAdmin.username" placeholder="请输入用户名" />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input type="email" v-model="newAdmin.email" placeholder="请输入邮箱" />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input type="password" v-model="newAdmin.password" placeholder="请输入密码" />
          </div>
          <div class="form-group">
            <label>确认密码</label>
            <input type="password" v-model="newAdmin.password2" placeholder="请确认密码" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showAddAdminDialog = false">取消</button>
          <button class="btn-success" @click="addAdmin">添加</button>
        </div>
      </div>
    </div>
    <div class="user-list">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>学号</th>
            <th>昵称</th>
            <th>信誉分</th>
            <th>成交数量</th>
            <th>注册时间</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.profile?.student_id || '-' }}</td>
            <td>{{ user.profile?.nickname || '-' }}</td>
            <td>{{ user.profile?.reputation || 0 }}</td>
            <td>{{ user.profile?.completed_transactions || 0 }}</td>
            <td>{{ formatDate(user.date_joined) }}</td>
            <td>
              <span :class="['status-badge', user.is_superuser ? 'admin' : 'user']">
                {{ user.is_superuser ? '管理员' : '用户' }}
              </span>
            </td>
            <td>
              <button class="btn-danger" @click="deleteUser(user.id)" v-if="user.username !== 'admin'">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pagination" v-if="totalUsers > pageSize">
      <button 
        class="btn-secondary" 
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        上一页
      </button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button 
        class="btn-secondary" 
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../../axios';

const users = ref([]);
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const totalUsers = ref(0);
const showAddAdminDialog = ref(false);
const newAdmin = ref({
  username: '',
  email: '',
  password: '',
  password2: ''
});

const totalPages = computed(() => {
  return Math.ceil(totalUsers.value / pageSize.value);
});

const fetchUsers = async () => {
  try {
    const response = await api.get('/accounts/admin/users/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value
      }
    });
    users.value = response.data.results;
    totalUsers.value = response.data.count;
  } catch (error) {
    console.error('获取用户列表失败:', error);
    users.value = [];
    totalUsers.value = 0;
    alert('获取用户列表失败，请检查网络连接或权限');
  }
};

const searchUsers = () => {
  currentPage.value = 1;
  fetchUsers();
};

const changePage = (page) => {
  currentPage.value = page;
  fetchUsers();
};

const viewUserDetails = (userId) => {
  // 查看用户详情
  console.log('查看用户详情:', userId);
};

const deleteUser = async (userId) => {
  if (confirm('确定要删除该用户吗？')) {
    try {
      await api.delete(`/accounts/admin/users/${userId}/`);
      // 重新获取用户列表
      fetchUsers();
      alert('用户删除成功');
    } catch (error) {
      console.error('删除用户失败:', error);
      alert('删除用户失败，请检查网络连接或权限');
    }
  }
};

const addAdmin = async () => {
  // 验证表单
  if (!newAdmin.value.username || !newAdmin.value.email || !newAdmin.value.password) {
    alert('请填写完整的管理员信息');
    return;
  }
  
  if (newAdmin.value.password !== newAdmin.value.password2) {
    alert('两次输入的密码不一致');
    return;
  }
  
  try {
    await api.post('/accounts/admin/users/', {
      username: newAdmin.value.username,
      email: newAdmin.value.email,
      password: newAdmin.value.password,
      is_superuser: true
    });
    // 重新获取用户列表
    fetchUsers();
    // 关闭对话框并重置表单
    showAddAdminDialog.value = false;
    newAdmin.value = {
      username: '',
      email: '',
      password: '',
      password2: ''
    };
    alert('管理员账号添加成功');
  } catch (error) {
    console.error('添加管理员失败:', error);
    alert('添加管理员失败，请检查网络连接或权限');
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.user-management {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.search-bar {
  display: flex;
  gap: 10px;
  flex: 1;
  min-width: 300px;
}

.search-bar input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn-primary {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 5px;
  transition: background-color 0.3s ease;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s ease;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-success {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.btn-success:hover {
  background-color: #229954;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background-color: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f8f9fa;
}

.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.dialog-close:hover {
  background-color: #e9ecef;
}

.dialog-body {
  padding: 20px;
}

.dialog-body .form-group {
  margin-bottom: 15px;
}

.dialog-body label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: 500;
  color: #495057;
}

.dialog-body input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.dialog-body input:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background-color: #f8f9fa;
}

.user-list {
  overflow-x: auto;
}

.user-list table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.user-list th,
.user-list td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.user-list th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.user-list tr:hover {
  background-color: #f5f5f5;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.admin {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.user {
  background-color: #d1ecf1;
  color: #0c5460;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>