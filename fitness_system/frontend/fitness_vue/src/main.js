import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import axios from 'axios'

import App from './App.vue'
import router from './router'
import store from './store'

// 配置axios默认值
axios.defaults.baseURL = 'http://localhost:8000'
axios.defaults.headers.common['Content-Type'] = 'application/json'

// 添加请求拦截器
axios.interceptors.request.use(
  config => {
    const token = store.state.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 添加响应拦截器
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    
    // 如果是401错误且不是刷新token的请求
    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/api/auth/refresh/') {
      originalRequest._retry = true
      
      try {
        // 尝试刷新token
        await store.dispatch('refreshToken')
        
        // 更新原始请求的token
        originalRequest.headers.Authorization = `Bearer ${store.state.token}`
        return axios(originalRequest)
      } catch (refreshError) {
        // 如果刷新token失败，登出用户
        store.dispatch('logout')
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(store)
app.use(Antd)

app.mount('#app')
