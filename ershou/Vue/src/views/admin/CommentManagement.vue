<template>
  <div class="comment-management">
    <h2 class="page-title">评论管理</h2>
    
    <!-- 搜索和筛选 -->
    <div class="search-filter-section">
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索评论内容、用户或商品..."
          @input="handleSearch"
        >
        <button class="search-btn" @click="handleSearch">搜索</button>
      </div>
    </div>
    
    <!-- 评论列表 -->
    <div class="comment-list">
      <table class="comment-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户</th>
            <th>评论内容</th>
            <th>评分</th>
            <th>评论时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="comment in comments" :key="comment.id" class="comment-item">
            <td>{{ comment.id }}</td>
            <td class="user-info">
              <span class="username">{{ comment.user_username }}</span>
            </td>
            <td class="comment-content">
              <div class="content-text">{{ comment.content }}</div>
              <div v-if="comment.image" class="comment-image">
                <img :src="comment.image" :alt="'评论图片'" class="review-image">
              </div>
            </td>
            <td class="rating">
              <div v-if="comment.rating" class="stars">
                <span 
                  v-for="star in 5" 
                  :key="star"
                  :class="['star', { active: comment.rating >= star }]"
                >
                  ★
                </span>
              </div>
              <span v-else>-</span>
            </td>
            <td>{{ formatDate(comment.created_at) }}</td>
            <td class="actions">
              <button class="btn-danger" @click="deleteComment(comment.id)">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 空状态 -->
      <div v-if="comments.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">💬</div>
        <p>暂无评论</p>
        <p class="empty-subtitle">用户发表的评论将显示在这里</p>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
    </div>
    
    <!-- 分页 -->
    <div v-if="totalComments > pageSize" class="pagination">
      <button 
        class="btn-secondary" 
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        上一页
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
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

// 响应式数据
const comments = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const totalComments = ref(0);

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(totalComments.value / pageSize.value);
});

// 获取评论列表
const fetchComments = async () => {
  loading.value = true;
  try {
    const response = await api.get('/admin/comments/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value
      }
    });
    comments.value = response.data.results || [];
    totalComments.value = response.data.count || 0;
  } catch (error) {
    console.error('获取评论列表失败:', error);
    // 模拟数据
    comments.value = [
      {
        id: 1,
        user_username: 'user1',
        user_avatar: null,
        product: { title: '二手 iPhone 13' },
        content: '商品很好，卖家很靠谱！',
        rating: 5,
        created_at: '2026-02-12T09:00:00Z'
      },
      {
        id: 2,
        user_username: 'user2',
        user_avatar: null,
        product: { title: '大学物理教材' },
        content: '教材很新，价格合理',
        rating: 4,
        created_at: '2026-02-11T16:00:00Z'
      }
    ];
    totalComments.value = comments.value.length;
  } finally {
    loading.value = false;
  }
};

// 搜索评论
const handleSearch = () => {
  currentPage.value = 1;
  fetchComments();
};

// 切换页码
const changePage = (page) => {
  currentPage.value = page;
  fetchComments();
};

// 删除评论
const deleteComment = async (commentId) => {
  if (confirm('确定要删除该评论吗？')) {
    try {
    await api.delete(`/admin/comments/${commentId}/`);
    // 重新获取评论列表
    fetchComments();
  } catch (error) {
    console.error('删除评论失败:', error);
    alert('删除评论失败，请稍后重试');
  }
  }
};

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// 页面挂载时获取评论列表
onMounted(() => {
  fetchComments();
});
</script>

<style scoped>
.comment-management {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin: 20px 0;
  position: relative;
  overflow: hidden;
}

.comment-management::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #4CAF50, #8BC34A, #CDDC39, #FFEB3B);
}

.page-title {
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

.page-title::before,
.page-title::after {
  content: '💬';
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

/* 搜索和筛选区域 */
.search-filter-section {
  margin-bottom: 24px;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
}

.search-bar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-bar input {
  flex: 1;
  padding: 14px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 30px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.search-bar input:focus {
  outline: none;
  border-color: #4CAF50;
  background: white;
  box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.15);
  transform: translateY(-2px);
}

.search-btn {
  padding: 14px 28px;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
  background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
}

.search-btn::before {
  content: '🔍';
  font-size: 16px;
}

/* 评论列表 */
.comment-list {
  margin-bottom: 24px;
  overflow-x: auto;
}

.comment-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comment-table th,
.comment-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.comment-table th {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  font-weight: 600;
  color: #333;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.comment-table tr:hover {
  background: #f8f9fa;
  transition: background 0.3s ease;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
}

.username {
  font-weight: 500;
  color: #333;
}



/* 评论内容 */
.comment-content {
  max-width: 300px;
}

.content-text {
  font-size: 14px;
  line-height: 1.4;
  color: #666;
  margin-bottom: 8px;
}

.comment-image {
  margin-top: 8px;
}

.review-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 评分 */
.rating {
  min-width: 100px;
}

.stars {
  display: flex;
  gap: 4px;
}

.star {
  color: #ddd;
  font-size: 16px;
  transition: color 0.3s ease;
}

.star.active {
  color: #ffc107;
}

/* 操作按钮 */
.actions {
  min-width: 100px;
}

.btn-danger {
  padding: 8px 16px;
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.4);
  background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background: #f9f9f9;
  border-radius: 12px;
  border: 2px dashed #e0e0e0;
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 20px;
  animation: bounce 2s infinite;
}

.empty-state p {
  font-size: 20px;
  font-weight: 600;
  color: #666;
  margin-bottom: 12px;
}

.empty-subtitle {
  font-size: 16px;
  color: #999;
  margin-bottom: 0;
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

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.btn-secondary {
  padding: 10px 20px;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  color: #333;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-secondary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.page-info {
  font-size: 14px;
  font-weight: 500;
  color: #666;
  min-width: 80px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .comment-management {
    padding: 20px;
  }
  
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-bar input {
    width: 100%;
  }
  
  .search-btn {
    width: 100%;
    justify-content: center;
  }
  
  .comment-table {
    font-size: 14px;
  }
  
  .comment-table th,
  .comment-table td {
    padding: 12px;
  }
  
  .user-info {
    align-items: flex-start;
  }
  
  .comment-content {
    max-width: 250px;
  }
  
  .actions {
    min-width: 80px;
  }
  
  .btn-danger {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>