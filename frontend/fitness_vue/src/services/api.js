import axios from 'axios';
import store from '@/store';
import router from '@/router';

/**
 * 创建一个axios实例
 */
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',  // 使用127.0.0.1而不是localhost，避免某些浏览器的HTTPS自动升级
  timeout: 30000,  // 请求超时时间
  headers: {
    'Content-Type': 'application/json',
  }
});

/**
 * 请求拦截器 - 添加认证令牌
 */
api.interceptors.request.use(
  config => {
    // 从store中获取token
    const token = store.state.token;
    if (token) {
      // 将token添加到请求头
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

/**
 * 响应拦截器 - 处理401错误（令牌过期）
 */
api.interceptors.response.use(
  response => response,  // 正常响应直接返回
  async error => {
    // 如果没有响应，直接返回错误
    if (!error.response) {
      return Promise.reject(error);
    }
    
    const { status } = error.response;
    
    // 处理401错误 - 令牌可能已过期
    if (status === 401) {
      const originalRequest = error.config;
      
      // 防止无限循环刷新令牌
      if (!originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          // 尝试刷新令牌
          await store.dispatch('refreshToken');
          
          // 更新原始请求的令牌
          const token = store.state.token;
          if (token) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          
          // 重新发送原始请求
          return api(originalRequest);
        } catch (refreshError) {
          // 如果刷新令牌失败，登出用户并重定向到登录页面
          store.dispatch('logout');
          router.push('/login');
          return Promise.reject(refreshError);
        }
      }
    }
    
    // 对于其他错误，直接返回错误
    return Promise.reject(error);
  }
);

export default api;
