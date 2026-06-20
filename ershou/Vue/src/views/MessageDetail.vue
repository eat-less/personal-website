<template>
  <div class="message-detail-container">
    <div class="message-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
        <span class="back-text">返回</span>
      </button>
      <div class="message-user-info">
        <div class="message-user-avatar">
          <img 
            v-if="otherUser.avatar" 
            :src="otherUser.avatar" 
            :alt="otherUser.username"
          >
          <span v-else class="avatar-placeholder">{{ otherUser.username?.charAt(0) || 'U' }}</span>
        </div>
        <div class="user-info">
          <h2 class="message-username">{{ otherUser.username }}</h2>
          <div class="user-status">
            <span class="status-dot"></span>
            <span class="status-text">在线</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="message-body" ref="messageBody">
      <div 
        v-for="message in messages" 
        :key="message.id"
        class="message-item"
        :class="{ 'message-sent': message.sender.id === currentUserId, 'message-received': message.sender.id !== currentUserId }"
      >
        <div class="message-content">
          {{ message.content }}
        </div>
        <div class="message-time">{{ formatTime(message.created_at) }}</div>
      </div>
    </div>
    
    <div class="message-input-area">
      <div class="input-wrapper">
        <input 
          type="text" 
          v-model="messageText" 
          placeholder="输入消息..."
          @keyup.enter="sendMessage"
          class="message-input"
        >
        <button class="send-btn" @click="sendMessage" :disabled="!messageText.trim()">
          <span class="send-icon">→</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../axios';

const router = useRouter();
const route = useRoute();
const messageBody = ref(null);

const currentUserId = computed(() => {
  const userStr = sessionStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr).id;
    } catch (e) {
      return null;
    }
  }
  return null;
});

const otherUserId = ref(route.params.userId);
const conversationId = ref(route.query.conversation_id || null);
const messages = ref([]);
const messageText = ref('');
const otherUser = ref({});

const fetchMessages = async () => {
  try {
    const response = await api.get(`/messages/${otherUserId.value}/`);
    messages.value = response.data.messages;
    otherUser.value = response.data.other_user;
    
    // 检查本地存储中是否有该用户的头像信息
    const userAvatars = JSON.parse(localStorage.getItem('userAvatars') || '{}');
    if (otherUser.value.username && userAvatars[otherUser.value.username]) {
      otherUser.value.avatar = userAvatars[otherUser.value.username];
    }
    
    if (!conversationId.value && response.data.conversation_id) {
      conversationId.value = response.data.conversation_id;
    }
    // 滚动到底部
    setTimeout(() => {
      scrollToBottom();
    }, 100);
  } catch (error) {
    console.error('获取消息失败:', error);
  }
};

const sendMessage = async () => {
  if (!messageText.value.trim()) return;
  
  try {
    const response = await api.post('/messages/', {
      recipient_id: otherUserId.value,
      content: messageText.value
    });
    
    messages.value.push(response.data);
    messageText.value = '';
    // 滚动到底部
    scrollToBottom();
  } catch (error) {
    console.error('发送消息失败:', error);
  }
};

const goBack = () => {
  router.push('/messages');
};

const scrollToBottom = () => {
  if (messageBody.value) {
    messageBody.value.scrollTop = messageBody.value.scrollHeight;
  }
};

const formatTime = (timeString) => {
  const date = new Date(timeString);
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

onMounted(() => {
  fetchMessages();
});

// 监听路由参数变化
watch(() => route.params.userId, (newUserId) => {
  if (newUserId) {
    otherUserId.value = newUserId;
    conversationId.value = route.query.conversation_id || null;
    fetchMessages();
  }
});
</script>

<style scoped>
.message-detail-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.message-header {
  display: flex;
  align-items: center;
  padding: 20px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.message-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  cursor: pointer;
  margin-right: 20px;
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 1;
  font-weight: 600;
  font-size: 14px;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.back-btn:active {
  transform: translateX(-2px) scale(0.98);
  transition: all 0.1s ease;
}

.back-icon {
  font-size: 18px;
  font-weight: bold;
}

.message-user-info {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 1;
}

.message-user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 16px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.message-user-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.message-user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 24px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-username {
  font-size: 20px;
  font-weight: 700;
  color: white;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.user-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4CAF50;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

.status-text {
  font-size: 14px;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.message-body {
  flex: 1;
  padding: 40px 30px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(102, 126, 234, 0.1) 0%, transparent 20%),
    radial-gradient(circle at 90% 80%, rgba(118, 75, 162, 0.1) 0%, transparent 20%);
}

.message-item {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.4s ease;
  position: relative;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-sent {
  align-self: flex-end;
}

.message-received {
  align-self: flex-start;
}

.message-content {
  padding: 18px 24px;
  border-radius: 24px;
  word-wrap: break-word;
  font-size: 16px;
  line-height: 1.5;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.message-sent .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 8px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.message-received .message-content {
  background: white;
  color: #333;
  border-bottom-left-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.message-time {
  font-size: 13px;
  color: #999;
  margin-top: 8px;
  align-self: flex-end;
  opacity: 0.8;
  background: rgba(255, 255, 255, 0.8);
  padding: 4px 12px;
  border-radius: 12px;
  backdrop-filter: blur(5px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.message-sent .message-time {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.message-input-area {
  padding: 24px 30px;
  background: white;
  border-top: 1px solid #e0e0e0;
  flex-shrink: 0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
  position: relative;
}

.message-input-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 800px;
  margin: 0 auto;
  position: relative;
}

.message-input {
  flex: 1;
  padding: 16px 24px;
  border: 2px solid #e0e0e0;
  border-radius: 30px;
  font-size: 16px;
  transition: all 0.3s;
  background: #f9f9f9;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.send-btn {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.send-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.send-btn:hover:not(:disabled)::before {
  left: 100%;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.send-btn:disabled {
  background: linear-gradient(135deg, #cccccc 0%, #999999 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.send-icon {
  font-size: 20px;
  font-weight: bold;
  transition: transform 0.3s ease;
}

.send-btn:hover:not(:disabled) .send-icon {
  transform: translateX(2px);
}

/* 滚动条样式 */
.message-body::-webkit-scrollbar {
  width: 10px;
}

.message-body::-webkit-scrollbar-track {
  background: rgba(241, 241, 241, 0.8);
  border-radius: 10px;
}

.message-body::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.message-body::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4191 100%);
  transform: scaleY(1.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-header {
    padding: 16px 20px;
  }
  
  .back-btn {
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .message-user-avatar {
    width: 50px;
    height: 50px;
  }
  
  .message-username {
    font-size: 18px;
  }
  
  .message-body {
    padding: 30px 20px;
    gap: 20px;
  }
  
  .message-item {
    max-width: 80%;
  }
  
  .message-content {
    padding: 16px 20px;
    font-size: 15px;
  }
  
  .message-input-area {
    padding: 20px;
  }
  
  .input-wrapper {
    gap: 10px;
  }
  
  .message-input {
    padding: 14px 20px;
    font-size: 15px;
  }
  
  .send-btn {
    width: 50px;
    height: 50px;
  }
}
</style>