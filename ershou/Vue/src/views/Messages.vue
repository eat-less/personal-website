<template>
  <div class="messages-container">
    <div class="messages-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1>私信列表</h1>
    </div>
    
    <div class="messages-list" v-if="conversations.length > 0">
      <div 
        v-for="conversation in conversations" 
        :key="conversation.id"
        class="conversation-item"
        @click="goToMessageDetail(conversation.id, conversation.other_user.id)"
      >
        <div class="conversation-avatar">
          <img 
            v-if="conversation.other_user.avatar" 
            :src="conversation.other_user.avatar" 
            :alt="conversation.other_user.username"
          >
          <span v-else class="avatar-placeholder">{{ conversation.other_user.username.charAt(0) }}</span>
        </div>
        <div class="conversation-info">
          <div class="conversation-header">
            <h3 class="conversation-name">{{ conversation.other_user.username }}</h3>
            <span class="conversation-time">{{ formatTime(conversation.last_message_time) }}</span>
          </div>
          <p class="conversation-preview">{{ conversation.last_message }}</p>
        </div>
        <div class="conversation-badge" v-if="conversation.unread_count > 0">
          {{ conversation.unread_count }}
        </div>
      </div>
    </div>
    
    <div class="empty-state" v-else>
      <div class="empty-icon">💬</div>
      <p>暂无私信</p>
      <p class="empty-subtext">开始与其他用户交流吧</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../axios';

const router = useRouter();
const conversations = ref([]);

const fetchConversations = async () => {
  try {
    const response = await api.get('/messages/');
    let conversationsData = response.data;
    
    // 检查本地存储中是否有其他用户的头像信息
    const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
    
    // 更新私信列表中的头像，包括其他用户的头像
    conversationsData = conversationsData.map(conversation => {
      // 检查本地存储中是否有该用户的头像
      if (conversation.other_user.username && userAvatars[conversation.other_user.username]) {
        return {
          ...conversation,
          other_user: {
            ...conversation.other_user,
            avatar: userAvatars[conversation.other_user.username]
          }
        };
      }
      return conversation;
    });
    
    conversations.value = conversationsData;
  } catch (error) {
    console.error('获取私信列表失败:', error);
  }
};

const goToMessageDetail = (conversationId, userId) => {
  router.push(`/messages/${userId}?conversation_id=${conversationId}`);
};

const goBack = () => {
  router.push('/');
};

const formatTime = (timeString) => {
  const date = new Date(timeString);
  const now = new Date();
  const diff = now - date;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  
  return date.toLocaleDateString();
};

// 更新当前用户在私信中的头像（如果有）
const updateCurrentUserAvatar = () => {
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
  const currentProfile = JSON.parse(localStorage.getItem('profile') || '{}');
  
  if (currentUser.id && currentProfile.avatar) {
    // 这里可以添加逻辑来更新当前用户在私信中的头像
    // 例如，如果私信页面显示当前用户的头像，就更新它
  }
};

// 监听storage事件，当其他标签页更新sessionStorage时同步更新
window.addEventListener('storage', (event) => {
  if (event.key === 'profile' || event.key === 'user') {
    updateCurrentUserAvatar();
  }
});

onMounted(() => {
  fetchConversations();
  
  // 页面加载后更新当前用户头像
  setTimeout(() => {
    updateCurrentUserAvatar();
  }, 0);
});
</script>

<style scoped>
.messages-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  flex-direction: column;
}

.messages-header {
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

.messages-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.messages-list {
  padding: 24px;
  flex: 1;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
  background: rgba(255, 255, 255, 0.95);
  position: relative;
  overflow: hidden;
}

.conversation-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.conversation-item:hover::before {
  left: 100%;
}

.conversation-item:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-3px);
  border-color: #667eea;
}

.conversation-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 20px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.conversation-item:hover .conversation-avatar {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.conversation-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  transition: transform 0.3s ease;
}

.conversation-avatar:hover img {
  transform: scale(1.1);
}

.avatar-placeholder {
  font-size: 24px;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.conversation-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.05);
}

.conversation-time {
  font-size: 13px;
  color: #999;
  font-weight: 500;
  background: #f5f5f5;
  padding: 4px 10px;
  border-radius: 12px;
  backdrop-filter: blur(5px);
}

.conversation-preview {
  font-size: 15px;
  color: #666;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.conversation-badge {
  background: linear-gradient(135deg, #ff6b6b 0%, #f5576c 100%);
  color: white;
  font-size: 14px;
  font-weight: bold;
  padding: 6px 14px;
  border-radius: 18px;
  margin-left: 16px;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
  animation: pulse 2s infinite;
  flex-shrink: 0;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
  }
  50% {
    box-shadow: 0 4px 16px rgba(255, 107, 107, 0.5);
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 70vh;
  color: #999;
  text-align: center;
  padding: 40px;
}

.empty-icon {
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
  margin-bottom: 8px;
  color: #666;
  font-weight: 600;
}

.empty-subtext {
  font-size: 16px;
  color: #999;
  font-weight: 500;
  margin-top: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .messages-header {
    padding: 16px 20px;
  }
  
  .back-btn {
    margin-right: 12px;
    padding: 6px 12px;
  }
  
  .messages-header h1 {
    font-size: 20px;
  }
  
  .messages-list {
    padding: 16px;
  }
  
  .conversation-item {
    padding: 16px;
    margin-bottom: 12px;
  }
  
  .conversation-avatar {
    width: 50px;
    height: 50px;
    margin-right: 16px;
  }
  
  .conversation-name {
    font-size: 16px;
  }
  
  .conversation-preview {
    font-size: 14px;
  }
  
  .empty-icon {
    font-size: 60px;
  }
  
  .empty-state p {
    font-size: 18px;
  }
}
</style>