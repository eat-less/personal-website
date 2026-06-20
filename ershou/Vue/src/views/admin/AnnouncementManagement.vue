<template>
  <div class="announcement-management">
    <h2>公告管理</h2>
    <div class="add-announcement">
      <h3>添加新公告</h3>
      <div class="form-group">
        <label for="title">标题</label>
        <input type="text" id="title" v-model="newAnnouncement.title" placeholder="请输入公告标题" />
      </div>
      <div class="form-group">
        <label for="content">内容</label>
        <textarea id="content" v-model="newAnnouncement.content" placeholder="请输入公告内容" rows="4"></textarea>
      </div>
      <button class="btn-primary" @click="addAnnouncement">添加公告</button>
    </div>
    <div class="announcement-list">
      <h3>公告列表</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>标题</th>
            <th>内容</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="announcement in announcements" :key="announcement.id">
            <td>{{ announcement.id }}</td>
            <td>{{ announcement.title }}</td>
            <td>{{ truncateContent(announcement.content, 50) }}</td>
            <td>
              <span :class="['status-badge', announcement.is_active ? 'active' : 'inactive']">
                {{ announcement.is_active ? '活跃' : '已禁用' }}
              </span>
            </td>
            <td>{{ formatDate(announcement.created_at) }}</td>
            <td>
              <button class="btn-secondary" @click="toggleStatus(announcement.id, !announcement.is_active)">
                {{ announcement.is_active ? '禁用' : '启用' }}
              </button>
              <button class="btn-danger" @click="deleteAnnouncement(announcement.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '../../axios';

const announcements = ref([]);
const newAnnouncement = ref({
  title: '',
  content: ''
});

const fetchAnnouncements = async () => {
  try {
    const response = await api.get('/admin/announcements/');
    announcements.value = response.data;
  } catch (error) {
    console.error('获取公告列表失败:', error);
    announcements.value = [];
    alert('获取公告列表失败，请检查网络连接或权限');
  }
};

const addAnnouncement = async () => {
  if (!newAnnouncement.value.title || !newAnnouncement.value.content) {
    alert('请填写标题和内容');
    return;
  }
  
  try {
    await api.post('/admin/announcements/', {
      title: newAnnouncement.value.title,
      content: newAnnouncement.value.content,
      is_active: true
    });
    // 重新获取公告列表
    fetchAnnouncements();
    // 清空表单
    newAnnouncement.value = {
      title: '',
      content: ''
    };
    alert('公告添加成功');
  } catch (error) {
    console.error('添加公告失败:', error);
    alert('添加公告失败，请检查网络连接或权限');
  }
};

const deleteAnnouncement = async (announcementId) => {
  if (confirm('确定要删除该公告吗？此操作不可恢复！')) {
    try {
      await api.delete(`/admin/announcements/${announcementId}/`);
      // 重新获取公告列表
      fetchAnnouncements();
      alert('公告已删除');
    } catch (error) {
      console.error('删除公告失败:', error);
      alert('删除公告失败，请检查网络连接或权限');
    }
  }
};

const toggleStatus = async (announcementId, isActive) => {
  try {
    await api.patch(`/admin/announcements/${announcementId}/`, {
      is_active: isActive
    });
    // 重新获取公告列表
    fetchAnnouncements();
    alert(`公告已${isActive ? '启用' : '禁用'}`);
  } catch (error) {
    console.error('修改公告状态失败:', error);
    alert('修改公告状态失败，请检查网络连接或权限');
  }
};

const truncateContent = (content, maxLength) => {
  if (content.length <= maxLength) {
    return content;
  }
  return content.substring(0, maxLength) + '...';
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
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
.announcement-management {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.add-announcement {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.add-announcement h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
}

.announcement-list {
  margin-top: 20px;
}

.announcement-list h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.announcement-list table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.announcement-list th,
.announcement-list td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.announcement-list th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.announcement-list tr:hover {
  background-color: #f5f5f5;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background-color: #f8d7da;
  color: #721c24;
}

.btn-primary {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-right: 8px;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #2980b9 0%, #1f618d 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-right: 8px;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #7f8c8d 0%, #6c757d 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn-danger {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-right: 8px;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>