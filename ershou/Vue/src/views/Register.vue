<template>
  <div class="register-container">
    <h1>校园二手商品交易平台</h1>
    <h2>用户注册</h2>
    <form @submit.prevent="register">
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          type="text" 
          id="username" 
          v-model="form.username" 
          required 
          placeholder="请输入用户名"
        >
      </div>
      
      <div class="form-group">
        <label for="email">邮箱</label>
        <div class="email-input">
          <input 
            type="email" 
            id="email" 
            v-model="form.email" 
            required 
            placeholder="请输入邮箱"
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
        <label for="student_id">学号</label>
        <input 
          type="text" 
          id="student_id" 
          v-model="form.student_id" 
          required 
          placeholder="请输入学号"
        >
      </div>
      
      <div class="form-group">
        <label for="password">密码</label>
        <div class="password-input">
          <input 
            :type="showPassword ? 'text' : 'password'" 
            id="password" 
            v-model="form.password" 
            required 
            placeholder="请输入8-16位字母数字组合"
          >
          <button 
            type="button" 
            class="password-toggle" 
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? '👁️' : '👁️‍🗨️' }}
          </button>
        </div>
      </div>
      
      <div class="form-group">
        <label for="password2">确认密码</label>
        <div class="password-input">
          <input 
            :type="showPassword2 ? 'text' : 'password'" 
            id="password2" 
            v-model="form.password2" 
            required 
            placeholder="请再次输入密码"
          >
          <button 
            type="button" 
            class="password-toggle" 
            @click="showPassword2 = !showPassword2"
          >
            {{ showPassword2 ? '👁️' : '👁️‍🗨️' }}
          </button>
        </div>
      </div>
      
      <div class="error-message" v-if="error">{{ error }}</div>
      <div class="success-message" v-if="success">{{ success }}</div>
      
      <button type="submit" class="btn-primary" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
      
      <div class="form-footer">
        <p>已有账号？<a href="/login">立即登录</a></p>
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

// 控制密码可见性
const showPassword = ref(false);
const showPassword2 = ref(false);

const form = ref({
  username: '',
  email: '',
  verification_code: '',
  student_id: '',
  password: '',
  password2: ''
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
      code_type: 'register'
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

// 注册
const register = async () => {
  if (form.value.password !== form.value.password2) {
    error.value = '两次输入的密码不一致';
    return;
  }
  
  loading.value = true;
  error.value = '';
  success.value = '';
  
  try {
    const response = await api.post('/accounts/register/', form.value);
    
    // 注册成功后跳转到登录页面
    alert('注册成功，请登录');
    router.push('/login');
  } catch (err) {
    // 收集所有错误信息
    let errorMessages = [];
    
    // 检查各字段错误
    if (err.response?.data?.password) {
      errorMessages = errorMessages.concat(err.response.data.password);
    }
    if (err.response?.data?.email) {
      errorMessages = errorMessages.concat(err.response.data.email);
    }
    if (err.response?.data?.username) {
      errorMessages = errorMessages.concat(err.response.data.username);
    }
    if (err.response?.data?.student_id) {
      errorMessages = errorMessages.concat(err.response.data.student_id);
    }
    if (err.response?.data?.verification_code) {
      errorMessages = errorMessages.concat(err.response.data.verification_code);
    }
    if (err.response?.data?.non_field_errors) {
      errorMessages = errorMessages.concat(err.response.data.non_field_errors);
    }
    
    // 如果没有具体字段错误，显示通用错误
    if (errorMessages.length === 0) {
      errorMessages.push('注册失败，请检查输入信息');
    }
    
    // 设置错误信息，使用弹窗显示
    const errorText = errorMessages.join('\n');
    error.value = errorText;
    alert(errorText);
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
.register-container {
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

.password-input {
  display: flex;
  gap: 10px;
  align-items: center;
}

.password-input input {
  flex: 1;
}

.password-toggle {
  padding: 10px 15px;
  background-color: #f1f1f1;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-toggle:hover {
  background-color: #e0e0e0;
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
