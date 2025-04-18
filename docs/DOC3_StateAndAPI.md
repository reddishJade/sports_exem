# 体测管理系统前端状态管理与API集成文档

## 状态管理设计

前端应用采用Vuex实现集中式状态管理，确保数据流的可预测性和组件间的高效通信。

### Vuex 架构

状态管理采用模块化结构，将不同功能领域的状态分离为独立模块：

```
store/
├── index.js              # Vuex 入口文件
├── modules/              # 状态模块
│   ├── auth.js           # 认证状态模块
│   ├── student.js        # 学生数据模块
│   ├── testResult.js     # 体测结果模块
│   ├── news.js           # 新闻模块
│   └── ...
└── plugins/              # Vuex 插件
    └── persistState.js   # 状态持久化插件
```

### 核心状态模块

#### 认证模块 (auth.js)

认证模块负责管理用户登录状态、权限和个人信息。

**状态设计**:
- `token`: JWT认证令牌
- `userInfo`: 用户基本信息，包括用户名和类型
- `isAuthenticated`: 登录状态标识

**技术实现要点**:
- 使用localStorage持久化令牌和用户信息
- 提供计算属性判断用户角色和权限
- 封装登录、注销和令牌校验等操作

**关键状态管理代码**:
```javascript
// 状态
const state = {
  token: localStorage.getItem('token') || null,
  userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}')
};

// Getters
const getters = {
  isAuthenticated: state => !!state.token,
  isAdmin: state => state.userInfo.user_type === 'admin',
  isStudent: state => state.userInfo.user_type === 'student',
  isParent: state => state.userInfo.user_type === 'parent',
  userType: state => state.userInfo.user_type
};

// Actions
const actions = {
  async login({ commit }, credentials) {
    const response = await authService.login(credentials);
    commit('SET_TOKEN', response.token);
    commit('SET_USER_INFO', {
      username: response.username,
      user_type: response.user_type
    });
  },
  
  logout({ commit }) {
    commit('CLEAR_AUTH');
  }
};
```

#### 学生数据模块 (student.js)

管理学生信息和相关操作。

**状态设计**:
- `students`: 学生列表数据
- `currentStudent`: 当前选中的学生
- `loading`: 数据加载状态

**技术实现要点**:
- 封装学生数据的CRUD操作
- 实现数据缓存和按需加载
- 提供数据过滤和排序功能

#### 体测结果模块 (testResult.js)

管理体测结果数据和分析功能。

**状态设计**:
- `results`: 体测结果列表
- `standards`: 体测标准数据
- `currentResult`: 当前查看的结果详情

**技术实现要点**:
- 关联学生信息和体测计划
- 实现成绩计算和合格判断
- 支持历史数据比较和趋势分析

### 状态管理最佳实践

#### 1. 模块化设计

将状态分割为独立模块，便于维护和扩展：

```javascript
export default createStore({
  modules: {
    auth: authModule,
    student: studentModule,
    testResult: testResultModule,
    news: newsModule
  },
  plugins: [persistStatePlugin]
});
```

#### 2. 类型安全（TypeScript支持）

为状态提供类型定义，增强代码可靠性：

```typescript
// 定义状态类型
interface AuthState {
  token: string | null;
  userInfo: {
    username: string;
    user_type: 'student' | 'parent' | 'admin';
  };
}

// 使用类型
const state: AuthState = {
  token: localStorage.getItem('token') || null,
  userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}')
};
```

#### 3. 状态持久化

使用Vuex插件实现状态持久化，保存用户会话：

```javascript
// persistState.js
export default function createPersistStatePlugin() {
  return store => {
    // 初始化时从localStorage恢复状态
    const savedAuth = localStorage.getItem('auth');
    if (savedAuth) {
      store.replaceState({
        ...store.state,
        auth: JSON.parse(savedAuth)
      });
    }

    // 状态变化时保存到localStorage
    store.subscribe((mutation, state) => {
      if (mutation.type.startsWith('auth/')) {
        localStorage.setItem('auth', JSON.stringify(state.auth));
      }
    });
  };
}
```

## API集成设计

前端通过Axios HTTP客户端与后端API通信，封装统一的服务层处理数据请求。

### API服务架构

```
services/
├── api.js              # Axios配置和拦截器
├── authService.js      # 认证相关API
├── studentService.js   # 学生数据API
├── resultService.js    # 体测结果API
├── newsService.js      # 新闻API
└── ...
```

### API基础配置

API基础配置集中管理API请求的共同特性：

```javascript
// api.js
import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器：添加认证token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// 响应拦截器：处理常见错误
api.interceptors.response.use(response => {
  return response.data;
}, error => {
  // 处理401未授权错误，跳转到登录页
  if (error.response && error.response.status === 401) {
    localStorage.removeItem('token');
    router.push('/login');
  }
  return Promise.reject(error);
});

export default api;
```

### 认证服务

认证服务封装用户登录和注册等操作：

```javascript
// authService.js
import api from './api';

export default {
  login(username, password) {
    return api.post('/users/login/', { username, password });
  },
  
  register(userData) {
    return api.post('/users/', userData);
  },
  
  verifyToken() {
    return api.post('/token/verify/');
  }
};
```

### 体测结果服务

体测结果服务封装体测数据的获取和管理：

```javascript
// resultService.js
import api from './api';

export default {
  getResults(params) {
    return api.get('/test-results/', { params });
  },
  
  getResultById(id) {
    return api.get(`/test-results/${id}/`);
  },
  
  createResult(data) {
    return api.post('/test-results/', data);
  },
  
  // 获取健康报告
  getHealthReport(resultId) {
    return api.get(`/health-reports/?test_result=${resultId}`);
  }
};
```

### 评论服务

评论服务处理测试结果和新闻的评论功能，实现了业务规则：

```javascript
// commentService.js
import api from './api';

export default {
  // 添加测试结果评论
  addTestComment(data) {
    return api.post('/comments/', data);
  },
  
  // 添加新闻评论
  addNewsComment(data) {
    return api.post('/news-comments/', data);
  },
  
  // 获取新闻评论
  getNewsComments(newsId) {
    return api.get(`/news/${newsId}/comments/`);
  }
};
```

### API集成最佳实践

#### 1. 错误处理统一化

实现统一的错误处理机制：

```javascript
// 在组件中使用
async fetchData() {
  try {
    this.loading = true;
    const data = await studentService.getStudents();
    this.students = data;
  } catch (error) {
    // 使用统一的错误处理函数
    this.handleApiError(error);
  } finally {
    this.loading = false;
  }
},

// 统一错误处理
handleApiError(error) {
  if (error.response) {
    // 服务器返回错误
    const status = error.response.status;
    const message = error.response.data.error || '操作失败';
    
    // 根据状态码处理不同类型的错误
    switch (status) {
      case 400: this.$message.error(`请求错误: ${message}`); break;
      case 401: this.$message.error('请重新登录'); break;
      case 403: this.$message.error('没有操作权限'); break;
      case 404: this.$message.error('请求的资源不存在'); break;
      default: this.$message.error(`操作失败: ${message}`);
    }
  } else {
    // 网络错误或请求被取消
    this.$message.error('网络错误，请检查您的连接');
  }
}
```

#### 2. 请求缓存和防抖

优化频繁API请求，减少服务器负载：

```javascript
// 简化版缓存服务
const cache = {
  data: new Map(),
  timeout: new Map(),
  
  get(key) {
    return this.data.get(key);
  },
  
  set(key, value, expireMs = 60000) {
    this.data.set(key, value);
    
    // 设置过期时间
    const timeoutId = setTimeout(() => {
      this.data.delete(key);
      this.timeout.delete(key);
    }, expireMs);
    
    this.timeout.set(key, timeoutId);
  },
  
  has(key) {
    return this.data.has(key);
  }
};

// 在服务中使用缓存
async function getStudents(forceRefresh = false) {
  const cacheKey = 'students';
  
  if (!forceRefresh && cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }
  
  const response = await api.get('/students/');
  cache.set(cacheKey, response, 300000); // 缓存5分钟
  return response;
}
```

#### 3. 请求取消

支持取消正在进行的请求，避免竞态条件：

```javascript
// 组件内使用
data() {
  return {
    cancelTokenSource: null
  };
},

methods: {
  async searchStudents(query) {
    // 取消之前的请求
    if (this.cancelTokenSource) {
      this.cancelTokenSource.cancel('New search initiated');
    }
    
    // 创建新的取消令牌
    this.cancelTokenSource = axios.CancelToken.source();
    
    try {
      const result = await studentService.searchStudents(query, {
        cancelToken: this.cancelTokenSource.token
      });
      this.searchResults = result;
    } catch (error) {
      if (!axios.isCancel(error)) {
        this.handleApiError(error);
      }
    }
  }
},

beforeUnmount() {
  // 组件销毁时取消未完成的请求
  if (this.cancelTokenSource) {
    this.cancelTokenSource.cancel('Component unmounted');
  }
}
```

## 用户认证与授权管理

系统实现了基于JWT的用户认证和基于角色的授权管理。

### 认证流程

1. **用户登录**: 提交用户名和密码到后端API
2. **令牌获取**: 获取JWT令牌并存储在localStorage
3. **请求授权**: 每次请求自动附加令牌
4. **令牌过期**: 处理令牌过期情况，跳转到登录页

### 授权控制

系统根据用户角色控制功能访问权限：

**路由级授权**:
```javascript
// 路由配置中定义需要的权限
{
  path: '/students',
  component: StudentList,
  meta: { requiresAuth: true, requiresAdmin: true }
}

// 全局路由守卫检查权限
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  const isAdmin = store.getters['auth/isAdmin'];

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next('/login');
    } else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
      next('/'); // 重定向到首页
    } else {
      next();
    }
  } else {
    next();
  }
});
```

**组件级授权**:
```javascript
// 条件渲染仅对管理员可见的组件
<admin-panel v-if="isAdmin" />

// 在计算属性中检查权限
computed: {
  ...mapGetters('auth', ['isAdmin', 'isStudent', 'isParent']),
  canAddComment() {
    // 只有学生用户可以添加评论，且需要有关联的学生信息
    return this.isStudent && this.hasStudentProfile;
  }
}
```

### 评论系统权限控制

根据系统要求，评论功能只对学生用户开放，且必须有关联的学生个人资料：

```javascript
// 评论组件中的判断逻辑
computed: {
  canComment() {
    const userType = this.$store.getters['auth/userType'];
    // 检查是否为学生用户类型
    if (userType !== 'student') {
      return false;
    }
    
    // 检查是否有学生个人资料
    const hasStudentProfile = !!this.$store.state.student.currentUserProfile;
    return hasStudentProfile;
  },
  
  commentErrorMessage() {
    const userType = this.$store.getters['auth/userType'];
    if (userType !== 'student') {
      return '只有学生可以发表评论';
    }
    if (!this.$store.state.student.currentUserProfile) {
      return '未找到您的学生信息，无法发表评论';
    }
    return '';
  }
},

methods: {
  async submitComment() {
    if (!this.canComment) {
      this.$message.error(this.commentErrorMessage);
      return;
    }
    
    // 提交评论逻辑
    try {
      await commentService.addNewsComment({
        news: this.newsId,
        content: this.commentContent
      });
      this.$message.success('评论提交成功，等待审核');
      this.commentContent = '';
      this.loadComments();
    } catch (error) {
      this.handleApiError(error);
    }
  }
}
```

## 前后端交互优化

### 数据加载状态管理

实现加载状态指示器，提升用户体验：

```javascript
// 组件内使用Loading指示器
data() {
  return {
    loading: {
      students: false,
      results: false
    }
  };
},

methods: {
  async fetchStudents() {
    this.loading.students = true;
    try {
      const data = await studentService.getStudents();
      this.students = data;
    } catch (error) {
      this.handleError(error);
    } finally {
      this.loading.students = false;
    }
  }
}

// 模板中使用
<template>
  <div>
    <el-table v-loading="loading.students" :data="students">
      <!-- 表格内容 -->
    </el-table>
  </div>
</template>
```

### 表单验证与提交

实现统一的表单验证和提交处理：

```javascript
// 表单验证
data() {
  return {
    form: {
      name: '',
      student_id: '',
      gender: 'M',
      class_name: ''
    },
    rules: {
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' },
        { min: 2, max: 20, message: '长度在2到20个字符', trigger: 'blur' }
      ],
      student_id: [
        { required: true, message: '请输入学号', trigger: 'blur' },
        { pattern: /^\d{8,12}$/, message: '学号格式不正确', trigger: 'blur' }
      ],
      gender: [
        { required: true, message: '请选择性别', trigger: 'change' }
      ],
      class_name: [
        { required: true, message: '请输入班级', trigger: 'blur' }
      ]
    }
  };
},

methods: {
  submitForm() {
    this.$refs.form.validate(async valid => {
      if (valid) {
        try {
          this.submitting = true;
          await studentService.createStudent(this.form);
          this.$message.success('添加成功');
          this.$emit('created');
          this.resetForm();
        } catch (error) {
          this.handleApiError(error);
        } finally {
          this.submitting = false;
        }
      }
    });
  },
  
  resetForm() {
    this.$refs.form.resetFields();
  }
}
```
