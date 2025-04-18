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
    // 从store中获取token，如果没有则从localStorage中获取
    let token = store.state.token;
    if (!token) {
      // 如果store中没有token，尝试从localStorage中获取
      token = localStorage.getItem('token');
      // 如果从localStorage找到了token，将其同步到store
      if (token && store.commit) {
        store.commit('setToken', { access: token, refresh: localStorage.getItem('refreshToken') });
      }
    }

    if (token) {
      // 将token添加到请求头
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

/**
 * 响应拦截器 - 处理401错误（令牌过期）和其他错误
 */
api.interceptors.response.use(
  response => response,  // 正常响应直接返回
  async error => {
    // 如果没有响应，可能是网络错误
    if (!error.response) {
      console.error('网络错误，请检查您的网络连接：', error);
      return Promise.reject({
        ...error,
        userMessage: '网络连接失败，请检查您的网络连接并刷新页面'
      });
    }

    const { status, data } = error.response;

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
          console.error('令牌刷新失败，需要重新登录：', refreshError);

          // 如果刷新令牌失败，登出用户并重定向到登录页面
          store.dispatch('logout');

          // 如果不是在登录页面，才进行重定向
          if (router.currentRoute.value.path !== '/login') {
            router.push({
              path: '/login',
              query: { redirect: router.currentRoute.value.fullPath }
            });
          }

          return Promise.reject({
            ...refreshError,
            userMessage: '登录已过期，请重新登录'
          });
        }
      }
    }

    // 处理其他常见错误码
    let userMessage = '请求失败';

    switch (status) {
      case 400:
        userMessage = data?.error || '请求参数错误';
        break;
      case 403:
        userMessage = '没有权限访问此资源';
        break;
      case 404:
        userMessage = '请求的资源不存在';
        break;
      case 500:
        userMessage = '服务器内部错误，请稍后再试';
        break;
      default:
        userMessage = data?.error || `请求失败 (${status})`;
    }

    // 对于其他错误，添加用户友好的错误信息
    return Promise.reject({
      ...error,
      userMessage
    });
  }
);

export default api;
