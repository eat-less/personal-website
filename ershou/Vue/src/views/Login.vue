<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-header">
        <div class="logo-icon">🏫</div>
        <h1>校园二手商品交易平台</h1>
        <h2>用户登录</h2>
      </div>
      
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <div class="input-wrapper">
            <span class="input-icon">👤</span>
            <input 
              type="text" 
              id="username" 
              v-model="form.username" 
              required 
              placeholder="请输入用户名"
              class="form-input"
            >
          </div>
        </div>
        
        <div class="form-group">
          <div class="input-wrapper">
            <span class="input-icon">🔒</span>
            <input 
              type="password" 
              id="password" 
              v-model="form.password" 
              required 
              placeholder="请输入密码"
              class="form-input"
            >
          </div>
        </div>
        
        <div class="error-message" v-if="error">{{ error }}</div>
        
        <button type="submit" class="btn-primary" :disabled="loading">
          <span class="btn-text">{{ loading ? '登录中...' : '登录' }}</span>
          <span class="btn-icon" v-if="!loading">→</span>
          <span class="btn-loader" v-else></span>
        </button>
        
        <div class="form-footer">
          <p>还没有账号？<a href="/register" class="footer-link">立即注册</a></p>
          <p><a href="/password-reset" class="footer-link">忘记密码？</a></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../axios';

const router = useRouter();
const loading = ref(false);
const error = ref('');
const form = ref({
  username: '',
  password: ''
});

const login = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const response = await api.post('/accounts/login/', form.value);
    
    // 保存token和用户信息到会话存储（sessionStorage），这样每个标签页都有独立的会话
    sessionStorage.setItem('access_token', response.data.tokens.access);
    sessionStorage.setItem('refresh_token', response.data.tokens.refresh);
    sessionStorage.setItem('user', JSON.stringify(response.data.user));
    sessionStorage.setItem('profile', JSON.stringify(response.data.profile));
    sessionStorage.setItem('user_info', JSON.stringify({
      username: response.data.user.username,
      is_admin: response.data.is_admin
    }));
    
    // 保存到近期登录账号（仍然使用localStorage，因为这是跨会话的）
    saveRecentAccount(response.data.user, response.data.profile, response.data.tokens, response.data.is_admin);
    
    // 根据是否为管理员跳转到不同页面
    if (response.data.is_admin) {
      router.push('/admin');
    } else {
      router.push('/');
    }
  } catch (err) {
    error.value = err.response?.data?.error || '登录失败，请检查用户名和密码';
  } finally {
    loading.value = false;
  }
};

// 保存近期登录账号
const saveRecentAccount = (user, profile, tokens, isAdmin) => {
  try {
    // 获取现有近期账号
    let recentAccounts = JSON.parse(localStorage.getItem('recentAccounts') || '[]');
    
    // 移除已存在的相同邮箱账号
    recentAccounts = recentAccounts.filter(account => account.email !== user.email);
    
    // 确保avatar URL是完整的
    let avatarUrl = null;
    
    if (profile?.avatar) {
      // 检查是否是完整URL
      if (profile.avatar.startsWith('http')) {
        // 直接使用后端返回的完整URL
        avatarUrl = profile.avatar;
      } else {
        // 如果是相对路径，构建完整URL（使用后端域名）
        avatarUrl = 'http://127.0.0.1:8000' + profile.avatar;
      }
    } else if (user?.avatar) {
      // 检查用户对象中是否有avatar
      if (user.avatar.startsWith('http')) {
        avatarUrl = user.avatar;
      } else {
        avatarUrl = 'http://127.0.0.1:8000' + user.avatar;
      }
    }
    
    // 添加新账号到开头
    const newAccount = {
      username: user.username,
      email: user.email,
      avatar: avatarUrl,
      tokens: tokens,
      is_admin: isAdmin
    };
    
    recentAccounts.unshift(newAccount);
    
    // 限制最多保存5个近期账号
    if (recentAccounts.length > 5) {
      recentAccounts = recentAccounts.slice(0, 5);
    }
    
    // 保存回本地存储
    localStorage.setItem('recentAccounts', JSON.stringify(recentAccounts));
  } catch (error) {
    // 静默处理错误
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  50% {
    transform: translate(20px, 20px) rotate(180deg);
  }
}

.login-wrapper {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 450px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideIn 0.6s ease-out;
  position: relative;
  z-index: 10;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  font-size: 60px;
  margin-bottom: 20px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-15px);
  }
  60% {
    transform: translateY(-8px);
  }
}

.login-header h1 {
  color: #333;
  margin-bottom: 12px;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.login-header h2 {
  color: #666;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  position: relative;
}

.input-wrapper {
  position: relative;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
  backdrop-filter: blur(5px);
}

.input-wrapper:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  background: white;
  transform: translateY(-2px);
}

.input-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: #666;
  z-index: 2;
}

.form-input {
  width: 100%;
  padding: 16px 20px 16px 50px;
  border: none;
  border-radius: 16px;
  font-size: 16px;
  background: transparent;
  color: #333;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  background: transparent;
}

.form-input::placeholder {
  color: #999;
  font-weight: 500;
}

.error-message {
  background: linear-gradient(135deg, #ff6b6b 0%, #f5576c 100%);
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  text-align: center;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
  animation: shake 0.3s ease-in-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16px;
  padding: 16px 24px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4298 100%);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  background: #cccccc;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-text {
  transition: all 0.3s ease;
}

.btn-icon {
  font-size: 20px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.btn-primary:hover .btn-icon {
  transform: translateX(5px);
}

.btn-loader {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.form-footer {
  text-align: center;
  margin-top: 16px;
}

.form-footer p {
  margin: 8px 0;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.footer-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
}

.footer-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.footer-link:hover {
  color: #764ba2;
  transform: translateY(-1px);
}

.footer-link:hover::after {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-wrapper {
    padding: 30px 24px;
    margin: 20px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
  
  .login-header h2 {
    font-size: 18px;
  }
  
  .form-input {
    padding: 14px 16px 14px 45px;
    font-size: 15px;
  }
  
  .btn-primary {
    padding: 14px 20px;
    font-size: 16px;
  }
  
  .form-footer p {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: 10px;
  }
  
  .login-wrapper {
    padding: 24px 20px;
    border-radius: 20px;
  }
  
  .logo-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .login-header h1 {
    font-size: 22px;
  }
  
  .login-header h2 {
    font-size: 16px;
  }
  
  .form-input {
    padding: 12px 14px 12px 40px;
    font-size: 14px;
  }
  
  .input-icon {
    font-size: 16px;
    left: 16px;
  }
  
  .btn-primary {
    padding: 12px 18px;
    font-size: 15px;
  }
}
</style>
