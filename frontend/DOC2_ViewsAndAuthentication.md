# 体测管理系统前端技术文档 - 第2部分：视图与认证

## 目录

1. [视图组件设计](#视图组件设计)
2. [用户认证流程](#用户认证流程)
3. [权限控制实现](#权限控制实现)
4. [登录与身份验证](#登录与身份验证)

## 视图组件设计

系统的各个功能模块通过视图组件实现，存储在`views`目录下。每个视图组件对应一个路由页面，负责特定功能的UI呈现和业务逻辑处理。

### 登录视图

```vue
<!-- views/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-form">
      <h2>体测管理系统</h2>
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          placeholder="请输入用户名"
        >
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          placeholder="请输入密码"
        >
      </div>
      <div class="error-message" v-if="error">{{ error }}</div>
      <button 
        class="login-button" 
        @click="handleLogin" 
        :disabled="loading"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'LoginView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const loading = ref(false)
    
    const handleLogin = async () => {
      if (!username.value || !password.value) {
        error.value = '请输入用户名和密码'
        return
      }
      
      error.value = ''
      loading.value = true
      
      try {
        await store.dispatch('login', {
          username: username.value,
          password: password.value
        })
        
        // 登录成功后重定向
        const redirectPath = route.query.redirect || '/'
        router.push(redirectPath)
      } catch (err) {
        error.value = err.response?.data?.error || '登录失败，请检查用户名和密码'
      } finally {
        loading.value = false
      }
    }
    
    return {
      username,
      password,
      error,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f6f8;
}

.login-form {
  width: 380px;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #4c6ef5;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.error-message {
  color: #e74c3c;
  margin-bottom: 15px;
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #4c6ef5;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover {
  background-color: #364fc7;
}

.login-button:disabled {
  background-color: #a5b4fc;
  cursor: not-allowed;
}
</style>
```

### 首页视图

```vue
<!-- views/HomeView.vue -->
<template>
  <div class="home">
    <h1>欢迎使用体测管理系统</h1>
    
    <div class="dashboard-stats">
      <div class="stat-card" v-if="isAdmin || isStudent">
        <h3>体测计划</h3>
        <div class="stat-value">{{ stats.testPlans }}</div>
      </div>
      <div class="stat-card" v-if="isAdmin || isStudent">
        <h3>测试成绩</h3>
        <div class="stat-value">{{ stats.testResults }}</div>
      </div>
      <div class="stat-card" v-if="isAdmin">
        <h3>学生总数</h3>
        <div class="stat-value">{{ stats.students }}</div>
      </div>
      <div class="stat-card">
        <h3>体育新闻</h3>
        <div class="stat-value">{{ stats.news }}</div>
      </div>
    </div>
    
    <div class="section" v-if="pendingTests.length > 0 && isStudent">
      <h2>即将到来的体测计划</h2>
      <el-table :data="pendingTests" stripe>
        <el-table-column prop="title" label="标题"></el-table-column>
        <el-table-column prop="test_date" label="测试日期">
          <template #default="scope">
            {{ formatDate(scope.row.test_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="location" label="测试地点"></el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" @click="viewTestDetail(scope.row.id)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <div class="section">
      <h2>最新体育新闻</h2>
      <div class="news-list">
        <div 
          v-for="item in latestNews" 
          :key="item.id" 
          class="news-card"
          @click="viewNewsDetail(item.id)"
        >
          <div class="news-image" v-if="item.featured_image">
            <img :src="item.featured_image" :alt="item.title">
          </div>
          <div class="news-content">
            <h3>{{ item.title }}</h3>
            <div class="news-meta">
              <span>{{ formatDate(item.pub_date) }}</span>
              <span>{{ item.source_name }}</span>
              <span>浏览: {{ item.views }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { formatDate } from '@/utils/formatter'

export default {
  name: 'HomeView',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const stats = ref({
      testPlans: 0,
      testResults: 0,
      students: 0,
      news: 0
    })
    
    const pendingTests = ref([])
    const latestNews = ref([])
    
    const isAdmin = computed(() => store.getters.isAdmin)
    const isStudent = computed(() => store.getters.isStudent)
    
    const fetchDashboardData = async () => {
      try {
        // 获取统计数据
        const statsData = await request.get('/dashboard/stats')
        stats.value = statsData
        
        // 获取即将到来的测试计划
        if (isStudent.value) {
          const testsData = await request.get('/test-plans/pending')
          pendingTests.value = testsData
        }
        
        // 获取最新新闻
        const newsData = await request.get('/news')
        latestNews.value = newsData.slice(0, 4) // 只显示前4条
      } catch (error) {
        console.error('获取首页数据失败', error)
      }
    }
    
    const viewTestDetail = (id) => {
      router.push(`/test-plans/${id}`)
    }
    
    const viewNewsDetail = (id) => {
      router.push(`/news/${id}`)
    }
    
    onMounted(fetchDashboardData)
    
    return {
      stats,
      pendingTests,
      latestNews,
      isAdmin,
      isStudent,
      viewTestDetail,
      viewNewsDetail,
      formatDate
    }
  }
}
</script>

<style scoped>
/* 样式省略 */
</style>
```

### 新闻详情视图

```vue
<!-- views/NewsDetail.vue -->
<template>
  <div class="news-detail">
    <div class="loading" v-if="loading">加载中...</div>
    <div v-else>
      <div class="news-header">
        <h1>{{ news.title }}</h1>
        <div class="news-meta">
          <span>发布时间: {{ formatDate(news.pub_date) }}</span>
          <span v-if="news.source_name">来源: {{ news.source_name }}</span>
          <span>浏览量: {{ news.views }}</span>
        </div>
      </div>
      
      <div class="featured-image" v-if="news.featured_image">
        <img :src="news.featured_image" :alt="news.title">
      </div>
      
      <div class="news-content">
        {{ news.content }}
      </div>
      
      <div class="comments-section">
        <h2>评论 ({{ comments.length }})</h2>
        
        <div class="comment-form" v-if="isStudent">
          <h3>发表评论</h3>
          <textarea 
            v-model="commentContent" 
            placeholder="请输入您的评论..."
            rows="4"
          ></textarea>
          <div class="form-actions">
            <button 
              @click="submitComment" 
              :disabled="commentSubmitting"
            >
              {{ commentSubmitting ? '提交中...' : '提交评论' }}
            </button>
          </div>
          <div class="comment-note">注意: 评论需要管理员审核后才会显示</div>
        </div>
        
        <div class="comments-list">
          <div v-if="comments.length === 0" class="no-comments">
            暂无评论
          </div>
          <div 
            v-for="comment in comments" 
            :key="comment.id" 
            class="comment-item"
          >
            <div class="comment-header">
              <span class="comment-author">{{ comment.student_name }}</span>
              <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
            </div>
            <div class="comment-content">
              {{ comment.content }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import request from '@/utils/request'
import { formatDate } from '@/utils/formatter'

export default {
  name: 'NewsDetail',
  props: {
    id: {
      type: String,
      required: false
    }
  },
  setup(props) {
    const store = useStore()
    const route = useRoute()
    
    const newsId = computed(() => props.id || route.params.id)
    const isStudent = computed(() => store.getters.isStudent)
    
    const news = ref({})
    const comments = ref([])
    const loading = ref(true)
    const commentContent = ref('')
    const commentSubmitting = ref(false)
    
    const fetchNewsDetail = async () => {
      try {
        loading.value = true
        // 获取新闻详情
        const newsData = await request.get(`/news/${newsId.value}`)
        news.value = newsData
        
        // 增加浏览次数
        await request.post(`/news/${newsId.value}/increment_views/`)
        
        // 获取评论
        const commentsData = await request.get(`/news/${newsId.value}/comments/`)
        comments.value = commentsData
      } catch (error) {
        console.error('获取新闻详情失败', error)
      } finally {
        loading.value = false
      }
    }
    
    const submitComment = async () => {
      if (!commentContent.value.trim()) {
        return
      }
      
      try {
        commentSubmitting.value = true
        await request.post('/news-comments/', {
          news: newsId.value,
          content: commentContent.value
        })
        
        commentContent.value = ''
        alert('评论提交成功，将在管理员审核后显示')
      } catch (error) {
        console.error('提交评论失败', error)
        alert('提交评论失败: ' + (error.response?.data?.detail || '未知错误'))
      } finally {
        commentSubmitting.value = false
      }
    }
    
    onMounted(fetchNewsDetail)
    
    return {
      news,
      comments,
      loading,
      isStudent,
      commentContent,
      commentSubmitting,
      submitComment,
      formatDate
    }
  }
}
</script>

<style scoped>
/* 样式省略 */
</style>
```

## 用户认证流程

系统用户认证流程由登录、权限验证和身份管理组成，通过Vuex统一管理认证状态。

### 登录流程图

```
用户输入用户名密码 -> 前端验证输入有效性 -> 调用后端API登录接口 
    -> 后端验证身份返回token -> 前端存储token和用户信息 -> 重定向到目标页面
```

### 认证模块状态管理

认证状态管理通过Vuex实现：

```javascript
// store/modules/auth.js
import request from '@/utils/request'

const state = {
  token: localStorage.getItem('token') || '',
  userType: localStorage.getItem('userType') || '',
  username: localStorage.getItem('username') || ''
}

const getters = {
  isAuthenticated: state => !!state.token,
  isAdmin: state => state.userType === 'admin',
  isStudent: state => state.userType === 'student',
  isParent: state => state.userType === 'parent'
}

const mutations = {
  SET_AUTH(state, { token, userType, username }) {
    state.token = token
    state.userType = userType
    state.username = username
    
    // 持久化存储
    localStorage.setItem('token', token)
    localStorage.setItem('userType', userType)
    localStorage.setItem('username', username)
  },
  
  CLEAR_AUTH(state) {
    state.token = ''
    state.userType = ''
    state.username = ''
    
    // 清除本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('userType')
    localStorage.removeItem('username')
  }
}

const actions = {
  // 登录
  async login({ commit }, { username, password }) {
    try {
      const response = await request.post('/users/login/', { username, password })
      
      const { token, user_type, username: name } = response
      
      commit('SET_AUTH', {
        token,
        userType: user_type,
        username: name
      })
      
      return response
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  },
  
  // 登出
  logout({ commit }) {
    commit('CLEAR_AUTH')
  },
  
  // 检查认证状态
  checkAuth({ commit, state }) {
    if (!state.token) {
      return Promise.reject(new Error('No token found'))
    }
    
    // 可以实现token有效性检查
    return Promise.resolve()
  }
}

export default {
  state,
  getters,
  mutations,
  actions
}
```

## 权限控制实现

系统根据用户类型（学生、家长、管理员）实现不同级别的权限控制。

### 路由级权限控制

路由守卫确保只有具有相应权限的用户才能访问特定页面：

```javascript
// router/index.js
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated
  const isAdmin = store.getters.isAdmin

  // 需要认证的路由
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } 
    // 需要管理员权限的路由
    else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
      next('/')
    } 
    else {
      next()
    }
  } else {
    next()
  }
})
```

### 组件级权限控制

在组件内部使用计算属性控制UI元素的显示：

```javascript
// 在组件内部实现权限控制
const isAdmin = computed(() => store.getters.isAdmin)
const isStudent = computed(() => store.getters.isStudent)
const isParent = computed(() => store.getters.isParent)

// 在模板中使用
// <div v-if="isAdmin">管理员专属内容</div>
```

### 权限相关辅助函数

可以封装权限检查函数，简化组件中的权限控制逻辑：

```javascript
// utils/permission.js
import store from '@/store'

export function checkPermission(userTypes) {
  const currentUserType = store.state.auth.userType
  return userTypes.includes(currentUserType)
}

// 使用示例:
// const hasPermission = checkPermission(['admin', 'student'])
```

## 登录与身份验证

### 登录实现

登录功能通过调用后端API接口实现，成功后存储token和用户信息：

```javascript
// 登录方法示例
const login = async (username, password) => {
  try {
    const response = await request.post('/users/login/', {
      username,
      password
    })
    
    // 存储认证信息
    store.commit('SET_AUTH', {
      token: response.token,
      userType: response.user_type,
      username: response.username
    })
    
    return response
  } catch (error) {
    console.error('Login failed:', error)
    throw error
  }
}
```

### Token处理

系统使用token进行用户身份验证，通过Axios请求拦截器自动添加到每个请求的头部：

```javascript
// 请求拦截器中添加token
service.interceptors.request.use(
  config => {
    // 添加token到请求头
    if (store.getters.isAuthenticated) {
      config.headers['Authorization'] = `Bearer ${store.state.auth.token}`
    }
    return config
  }
)
```

### 会话管理

会话状态通过localStorage持久化存储，实现页面刷新后的状态保持：

```javascript
// 存储认证信息
localStorage.setItem('token', token)
localStorage.setItem('userType', userType)
localStorage.setItem('username', username)

// 获取认证信息
const token = localStorage.getItem('token')
const userType = localStorage.getItem('userType')
const username = localStorage.getItem('username')

// 清除认证信息
localStorage.removeItem('token')
localStorage.removeItem('userType')
localStorage.removeItem('username')
```

### 自动登录

应用初始化时检查localStorage中的认证信息，实现自动登录：

```javascript
// main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

const app = createApp(App)

// 应用初始化时检查认证状态
const initAuth = async () => {
  if (store.getters.isAuthenticated) {
    try {
      // 可以实现token验证逻辑
      await store.dispatch('checkAuth')
    } catch (error) {
      // token无效，清除认证状态
      store.dispatch('logout')
    }
  }
}

initAuth().then(() => {
  app.use(store).use(router).mount('#app')
})
```
