<template>
  <div class="info-management">
    <h2>信息管理</h2>
    <div class="tabs">
      <button 
        :class="['tab-button', { active: activeTab === 'messages' }]"
        @click="activeTab = 'messages'"
      >
        私信管理
      </button>
      <button 
        :class="['tab-button', { active: activeTab === 'comments' }]"
        @click="activeTab = 'comments'"
      >
        评论管理
      </button>
    </div>
    
    <!-- 私信管理 -->
    <div v-if="activeTab === 'messages'" class="messages-section">
      <div class="search-bar">
        <input 
          type="text" 
          v-model="messageSearchQuery"
          placeholder="搜索消息内容或用户"
          @input="searchMessages"
        />
        <button class="btn-primary">搜索</button>
      </div>
      <div class="message-list">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>发送者</th>
              <th>接收者</th>
              <th>消息内容</th>
              <th>是否已读</th>
              <th>发送时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="message in messages" :key="message.id">
              <td>{{ message.id }}</td>
              <td>{{ message.sender.username }}</td>
              <td>{{ message.receiver.username }}</td>
              <td>{{ message.content }}</td>
              <td>
                <span :class="['status-badge', message.is_read ? 'read' : 'unread']">
                  {{ message.is_read ? '已读' : '未读' }}
                </span>
              </td>
              <td>{{ formatDate(message.created_at) }}</td>
              <td>
                <button class="btn-danger" @click="deleteMessage(message.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination" v-if="totalMessages > pageSize">
        <button 
          class="btn-secondary" 
          :disabled="currentMessagePage === 1"
          @click="changeMessagePage(currentMessagePage - 1)"
        >
          上一页
        </button>
        <span>{{ currentMessagePage }} / {{ totalMessagePages }}</span>
        <button 
          class="btn-secondary" 
          :disabled="currentMessagePage === totalMessagePages"
          @click="changeMessagePage(currentMessagePage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
    
    <!-- 评论管理 -->
    <div v-if="activeTab === 'comments'" class="comments-section">
      <div class="search-bar">
        <input 
          type="text" 
          v-model="commentSearchQuery"
          placeholder="搜索评论内容或用户"
          @input="searchComments"
        />
        <button class="btn-primary">搜索</button>
      </div>
      <div class="comment-list">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>用户</th>
              <th>商品</th>
              <th>评论内容</th>
              <th>评分</th>
              <th>评论时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="comment in comments" :key="comment.id">
              <td>{{ comment.id }}</td>
              <td>{{ comment.user.username }}</td>
              <td>{{ comment.product.title }}</td>
              <td>{{ comment.content }}</td>
              <td>{{ comment.rating || '-' }}</td>
              <td>{{ formatDate(comment.created_at) }}</td>
              <td>
                <button class="btn-danger" @click="deleteComment(comment.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination" v-if="totalComments > pageSize">
        <button 
          class="btn-secondary" 
          :disabled="currentCommentPage === 1"
          @click="changeCommentPage(currentCommentPage - 1)"
        >
          上一页
        </button>
        <span>{{ currentCommentPage }} / {{ totalCommentPages }}</span>
        <button 
          class="btn-secondary" 
          :disabled="currentCommentPage === totalCommentPages"
          @click="changeCommentPage(currentCommentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const activeTab = ref('messages');
const pageSize = ref(10);

// 私信相关
const messages = ref([]);
const messageSearchQuery = ref('');
const currentMessagePage = ref(1);
const totalMessages = ref(0);

// 评论相关
const comments = ref([]);
const commentSearchQuery = ref('');
const currentCommentPage = ref(1);
const totalComments = ref(0);

const totalMessagePages = computed(() => {
  return Math.ceil(totalMessages.value / pageSize.value);
});

const totalCommentPages = computed(() => {
  return Math.ceil(totalComments.value / pageSize.value);
});

// 私信管理方法
const fetchMessages = async () => {
  try {
    const response = await axios.get('/api/admin/messages/', {
      params: {
        page: currentMessagePage.value,
        page_size: pageSize.value,
        search: messageSearchQuery.value
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    messages.value = response.data.results;
    totalMessages.value = response.data.count;
  } catch (error) {
    console.error('获取消息列表失败:', error);
    // 模拟数据
    messages.value = [
      {
        id: 1,
        sender: { username: 'user1' },
        receiver: { username: 'user2' },
        content: '你好，这个商品还在吗？',
        is_read: true,
        created_at: '2026-02-12T10:00:00Z'
      },
      {
        id: 2,
        sender: { username: 'user2' },
        receiver: { username: 'user1' },
        content: '在的，你什么时候方便取货？',
        is_read: false,
        created_at: '2026-02-12T10:30:00Z'
      }
    ];
    totalMessages.value = messages.value.length;
  }
};

const searchMessages = () => {
  currentMessagePage.value = 1;
  fetchMessages();
};

const changeMessagePage = (page) => {
  currentMessagePage.value = page;
  fetchMessages();
};

const deleteMessage = (messageId) => {
  if (confirm('确定要删除该消息吗？')) {
    console.log('删除消息:', messageId);
  }
};

// 评论管理方法
const fetchComments = async () => {
  try {
    const response = await axios.get('/api/admin/comments/', {
      params: {
        page: currentCommentPage.value,
        page_size: pageSize.value,
        search: commentSearchQuery.value
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    comments.value = response.data.results;
    totalComments.value = response.data.count;
  } catch (error) {
    console.error('获取评论列表失败:', error);
    // 模拟数据
    comments.value = [
      {
        id: 1,
        user: { username: 'user1' },
        product: { title: '二手 iPhone 13' },
        content: '商品很好，卖家很靠谱！',
        rating: 5,
        created_at: '2026-02-12T09:00:00Z'
      },
      {
        id: 2,
        user: { username: 'user2' },
        product: { title: '大学物理教材' },
        content: '教材很新，价格合理',
        rating: 4,
        created_at: '2026-02-11T16:00:00Z'
      }
    ];
    totalComments.value = comments.value.length;
  }
};

const searchComments = () => {
  currentCommentPage.value = 1;
  fetchComments();
};

const changeCommentPage = (page) => {
  currentCommentPage.value = page;
  fetchComments();
};

const deleteComment = (commentId) => {
  if (confirm('确定要删除该评论吗？')) {
    console.log('删除评论:', commentId);
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

onMounted(() => {
  fetchMessages();
  fetchComments();
});
</script>

<style scoped>
.info-management {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tabs {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.tab-button {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.tab-button:hover {
  background-color: #f5f5f5;
}

.tab-button.active {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
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

.message-list,
.comment-list {
  overflow-x: auto;
}

.message-list table,
.comment-list table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.message-list th,
.message-list td,
.comment-list th,
.comment-list td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.message-list th,
.comment-list th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.message-list tr:hover,
.comment-list tr:hover {
  background-color: #f5f5f5;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.read {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.unread {
  background-color: #fff3cd;
  color: #856404;
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