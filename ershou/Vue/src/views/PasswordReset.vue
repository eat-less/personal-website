<template>
  <div class="password-reset-container">
    <h1>校园二手商品交易平台</h1>
    <h2>重置密码</h2>
    <form @submit.prevent="resetPassword">
      <div class="form-group">
        <label for="email">邮箱</label>
        <div class="email-input">
          <input 
            type="email" 
            id="email" 
            v-model="form.email" 
            required 
            placeholder="请输入注册邮箱"
            @input="resetCountdown"
          >
          <button 
            type="button" 
            class="btn-secondary" 
            @click="sendVerificationCode" 
            :disabled="countdown > 0 || loading"
          >
            {{ countdown > 0 ? `${countdown}秒后重发` : '发送验证码' }}
          </button>
        </div>
      </div>
      
      <div class="form-group">
        <label for="verification_code">验证码</label>
        <input 
          type="text" 
          id="verification_code" 
          v-model="form.verification_code" 
          required 
          placeholder="请输入验证码"
        >
      </div>
      
      <div class="form-group">
        <label for="new_password">新密码</label>
        <input 
          type="password" 
          id="new_password" 
          v-model="form.new_password" 
          required 
          placeholder="请输入8-16位字母数字组合"
        >
      </div>
      
      <div class="form-group">
        <label for="new_password2">确认新密码</label>
        <input 
          type="password" 
          id="new_password2" 
          v-model="form.new_password2" 
          required 
          placeholder="请再次输入新密码"
        >
      </div>
      
      <div class="error-message" v-if="error">{{ error }}</div>
      <div class="success-message" v-if="success">{{ success }}</div>
      
      <button type="submit" class="btn-primary" :disabled="loading">
        {{ loading ? '重置中...' : '重置密码' }}
      </button>
      
      <div class="form-footer">
        <p><a href="/login">返回登录</a></p>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../axios';

const router = useRouter();
const loading = ref(false);
const error = ref('');
const success = ref('');
const countdown = ref(0);
let countdownTimer = null;

const form = ref({
  email: '',
  verification_code: '',
  new_password: '',
  new_password2: ''
});

// 发送验证码
const sendVerificationCode = async () => {
  if (!form.value.email) {
    error.value = '请输入邮箱';
    return;
  }
  
  loading.value = true;
  error.value = '';
  
  try {
    await api.post('/accounts/send-verification-code/', {
      email: form.value.email,
      code_type: 'reset_password'
    });
    
    success.value = '验证码已发送，请查收邮箱';
    startCountdown();
  } catch (err) {
    error.value = err.response?.data?.error || '验证码发送失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

// 开始倒计时
const startCountdown = () => {
  countdown.value = 60;
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--;
    }
  }, 1000);
};

// 重置倒计时
const resetCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer);
    countdown.value = 0;
  }
};

// 重置密码
const resetPassword = async () => {
  if (form.value.new_password !== form.value.new_password2) {
    error.value = '两次输入的密码不一致';
    return;
  }
  
  loading.value = true;
  error.value = '';
  success.value = '';
  
  try {
    await api.post('/accounts/password-reset/', form.value);
    
    success.value = '密码重置成功，请登录';
    
    // 3秒后跳转到登录页面
    setTimeout(() => {
      router.push('/login');
    }, 3000);
  } catch (err) {
    error.value = err.response?.data?.non_field_errors?.[0] || 
                  err.response?.data?.email?.[0] || 
                  err.response?.data?.verification_code?.[0] || 
                  '密码重置失败，请检查输入信息';
  } finally {
    loading.value = false;
  }
};

// 清理定时器
onMounted(() => {
  if (countdown.value > 0) {
    startCountdown();
  }
});

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer);
  }
});
</script>

<style scoped>
.password-reset-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 10px;
}

h2 {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.email-input {
  display: flex;
  gap: 10px;
}

.email-input input {
  flex: 1;
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1976D2;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 10px 15px;
  background-color: #f1f1f1;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.btn-secondary:disabled {
  background-color: #f9f9f9;
  color: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #f44336;
  margin-bottom: 15px;
  text-align: center;
}

.success-message {
  color: #2196F3;
  margin-bottom: 15px;
  text-align: center;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
}

.form-footer p {
  margin: 10px 0;
  color: #666;
}

.form-footer a {
  color: #2196F3;
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style>
