import axios from 'axios';

// 自动检测运行环境：
// - 开发环境（localhost:5173）：直接访问后端 8000 端口
// - 生产环境（Docker/Nginx）：使用相对路径，由 Nginx 代理
const getBaseURL = () => {
  const host = window.location.hostname;
  // 开发模式：本地开发服务器
  if (host === 'localhost' || host === '127.0.0.1') {
    return 'http://localhost:8000/api';
  }
  // 生产模式：由 Nginx 代理
  return '/api';
};

// 创建axios实例
const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器：添加token
api.interceptors.request.use(
  config => {
    const token = sessionStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理token过期等问题
api.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    if (error.response && error.response.status === 401) {
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      sessionStorage.removeItem('user');
      sessionStorage.removeItem('profile');
      sessionStorage.removeItem('user_info');
      console.error('未授权错误:', error);
    }
    return Promise.reject(error);
  }
);

export default api;
