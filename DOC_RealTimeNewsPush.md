# 体测系统实时新闻推送功能文档

## 目录
1. [功能概述](#功能概述)
2. [技术架构](#技术架构)
3. [后端实现](#后端实现)
4. [前端实现](#前端实现)
5. [权限控制](#权限控制)
6. [部署说明](#部署说明)
7. [使用指南](#使用指南)
8. [常见问题](#常见问题)

## 功能概述

实时新闻推送功能允许体测系统在有新内容（如新闻、通知、体测计划）发布时，即时地将这些内容推送到用户的浏览器，无需用户手动刷新页面。这大大提升了系统的实时性和用户体验。

### 主要特点

- **实时性**：新内容发布后立即推送至前端
- **用户分组**：根据用户类型和角色分发不同的通知
- **低延迟**：使用WebSocket持久连接，减少通信延迟
- **减少服务器负载**：相比传统轮询方式，显著降低服务器请求次数
- **兼容现有认证系统**：完全集成现有的用户权限模型

## 技术架构

实时推送功能采用了基于WebSocket的架构设计，主要组件包括：

### 后端组件
- **Django Channels**：提供WebSocket支持的Django扩展
- **ASGI Server (Daphne)**：支持异步WebSocket连接的应用服务器
- **Channel Layers**：管理不同用户组的消息分发
- **Consumer**：处理WebSocket连接和消息

### 前端组件
- **WebSocket客户端**：建立与服务器的持久连接
- **Vuex Store**：管理通知状态和数据更新
- **通知组件**：显示实时通知的UI组件

### 架构图

```
┌─────────────┐      WebSocket      ┌─────────────┐
│             │◄─────连接/认证─────►│             │
│   前端应用   │                     │  ASGI服务器  │
│  (Vue.js)   │◄─────消息推送─────►│  (Daphne)   │
│             │                     │             │
└─────────────┘                     └──────┬──────┘
                                          │
                                    ┌─────▼──────┐
                                    │ Channels   │
                                    │ Consumer   │
                                    └─────┬──────┘
                                          │
                                    ┌─────▼──────┐
                                    │ Channel    │
                                    │ Layers     │
                                    └─────┬──────┘
                                          │
                                    ┌─────▼──────┐
                                    │ Django     │
                                    │ 应用逻辑    │
                                    └─────┬──────┘
                                          │
                                    ┌─────▼──────┐
                                    │ 数据库      │
                                    └────────────┘
```

## 后端实现

### 配置 Django Channels

1. **安装依赖**

```bash
pip install channels daphne
```

2. **添加应用配置**

在 `settings.py` 中添加 Channels 配置：

```python
# 添加Channels到已安装应用
INSTALLED_APPS = [
    # ... 其他应用
    'channels',
]

# Channels配置
ASGI_APPLICATION = 'fitness_backend.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

3. **配置ASGI**

修改 `asgi.py` 文件以支持WebSocket：

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import fitness.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                fitness.routing.websocket_urlpatterns
            )
        )
    ),
})
```

### WebSocket 路由配置

创建 `fitness/routing.py` 文件配置WebSocket URL路由：

```python
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/news/', consumers.NewsConsumer.as_asgi()),
]
```

### WebSocket Consumer 实现

在 `fitness/consumers.py` 创建WebSocket消费者类：

```python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import User, Student

class NewsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 获取Token并验证用户
        headers = dict(self.scope['headers'])
        token = None
        
        # 从请求头中获取令牌
        if b'authorization' in headers:
            auth_header = headers[b'authorization'].decode('utf-8')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # 验证令牌并获取用户
        self.user = await self.get_user_from_token(token) if token else None
        
        if not self.user:
            await self.close()
            return
        
        # 根据用户类型加入不同的组
        self.news_group = 'news_general'
        await self.channel_layer.group_add(
            self.news_group,
            self.channel_name
        )
        
        # 管理员和学生用户加入特定组
        if self.user.user_type == 'admin':
            await self.channel_layer.group_add(
                'news_admin',
                self.channel_name
            )
        elif self.user.user_type == 'student':
            # 检查学生是否有关联的学生档案
            student = await self.get_student_profile(self.user)
            if student:
                self.student_id = student.id
                # 学生特定组
                await self.channel_layer.group_add(
                    f'news_student_{self.student_id}',
                    self.channel_name
                )
        
        await self.accept()

    async def disconnect(self, close_code):
        # 离开新闻组
        if hasattr(self, 'news_group'):
            await self.channel_layer.group_discard(
                self.news_group,
                self.channel_name
            )
        
        # 根据用户类型离开特定组
        if hasattr(self, 'user'):
            if self.user.user_type == 'admin':
                await self.channel_layer.group_discard(
                    'news_admin',
                    self.channel_name
                )
            elif self.user.user_type == 'student' and hasattr(self, 'student_id'):
                await self.channel_layer.group_discard(
                    f'news_student_{self.student_id}',
                    self.channel_name
                )

    # 接收来自WebSocket的消息
    async def receive(self, text_data):
        # 客户端通常不需要向服务器发送消息，此处仅作记录
        pass

    # 接收来自组的消息
    async def news_message(self, event):
        # 发送消息到WebSocket
        await self.send(text_data=json.dumps({
            'type': 'news',
            'message': event['message']
        }))
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """从令牌获取用户"""
        try:
            # 使用JWT验证
            from rest_framework_simplejwt.tokens import AccessToken
            token_obj = AccessToken(token)
            user_id = token_obj.payload.get('user_id')
            return User.objects.get(id=user_id)
        except Exception:
            return None
    
    @database_sync_to_async
    def get_student_profile(self, user):
        """获取用户关联的学生档案"""
        try:
            return Student.objects.get(user=user)
        except Student.DoesNotExist:
            return None
```

### 发送通知的信号处理

创建 `fitness/signals.py` 文件，实现新闻更新时的通知发送：

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SportsNews
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

@receiver(post_save, sender=SportsNews)
def send_news_notification(sender, instance, created, **kwargs):
    """当新闻被创建或更新时发送WebSocket通知"""
    if instance.status == 'published':
        channel_layer = get_channel_layer()
        
        # 准备要发送的数据
        news_data = {
            'id': instance.id,
            'title': instance.title,
            'pub_date': instance.pub_date.isoformat() if instance.pub_date else None,
            'featured_image': instance.featured_image,
            'is_featured': instance.is_featured,
        }
        
        # 发送给所有人
        async_to_sync(channel_layer.group_send)(
            'news_general',
            {
                'type': 'news_message',
                'message': {
                    'action': 'new' if created else 'update',
                    'news': news_data
                }
            }
        )
```

### 注册信号

在 `fitness/apps.py` 中注册信号：

```python
from django.apps import AppConfig

class FitnessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fitness'
    
    def ready(self):
        import fitness.signals  # 导入信号模块
```

## 前端实现

### WebSocket客户端服务

在Vue项目中创建 `src/utils/websocket.js`：

```javascript
// src/utils/websocket.js
import store from '@/store';

class NewsWebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000; // 3秒
  }

  connect() {
    if (this.socket) {
      this.disconnect();
    }

    const token = store.getters['auth/token'];
    if (!token) {
      console.error('无法建立WebSocket连接：未登录');
      return;
    }

    // 使用后端WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsBaseUrl = process.env.VUE_APP_WS_URL || `${wsProtocol}//${window.location.host}`;
    const wsUrl = `${wsBaseUrl}/ws/news/`;

    this.socket = new WebSocket(wsUrl);

    // 连接建立时发送认证令牌
    this.socket.onopen = (event) => {
      console.log('WebSocket连接已建立');
      this.connected = true;
      this.reconnectAttempts = 0;
      
      // 发送认证令牌
      this.socket.send(JSON.stringify({
        type: 'auth',
        token: token
      }));
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'news') {
          this.handleNewsMessage(data.message);
        }
      } catch (error) {
        console.error('处理WebSocket消息时出错:', error);
      }
    };

    this.socket.onclose = (event) => {
      this.connected = false;
      console.log('WebSocket连接已关闭');
      
      // 尝试重新连接
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), this.reconnectInterval);
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.connected = false;
    }
  }

  handleNewsMessage(message) {
    const { action, news } = message;
    
    // 根据消息类型分发不同的Vuex操作
    if (action === 'new') {
      store.dispatch('news/addNewsItem', news);
      
      // 显示新闻通知
      this.showNewsNotification(news);
    } else if (action === 'update') {
      store.dispatch('news/updateNewsItem', news);
    }
  }
  
  showNewsNotification(news) {
    // 使用浏览器通知API显示新闻通知
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('新体育资讯', {
        body: news.title,
        icon: news.featured_image || '/icon.png'
      });
    }
    
    // 如果使用Element UI，也可以使用它的通知组件
    if (window.$message) {
      window.$message({
        message: `新体育资讯: ${news.title}`,
        type: 'info',
        duration: 5000
      });
    }
  }
}

export default new NewsWebSocketService();
```

### Vuex状态管理

在 `src/store/modules/news.js` 中添加处理实时更新的逻辑：

```javascript
// src/store/modules/news.js
import newsService from '@/services/newsService';

export default {
  namespaced: true,
  
  state: {
    newsList: [],
    currentNews: null,
    loading: false,
    totalItems: 0,
    recentNotifications: []
  },
  
  mutations: {
    SET_NEWS_LIST(state, news) {
      state.newsList = news;
    },
    SET_CURRENT_NEWS(state, news) {
      state.currentNews = news;
    },
    SET_LOADING(state, status) {
      state.loading = status;
    },
    SET_TOTAL_ITEMS(state, total) {
      state.totalItems = total;
    },
    ADD_NEWS_ITEM(state, news) {
      // 防止重复添加
      if (!state.newsList.some(item => item.id === news.id)) {
        // 置顶新闻放在最前面
        if (news.is_featured) {
          state.newsList.unshift(news);
        } else {
          state.newsList.push(news);
        }
      }
    },
    UPDATE_NEWS_ITEM(state, updatedNews) {
      const index = state.newsList.findIndex(n => n.id === updatedNews.id);
      if (index !== -1) {
        state.newsList.splice(index, 1, {...state.newsList[index], ...updatedNews});
      }
      
      // 如果当前正在查看的是这条新闻，也更新当前新闻
      if (state.currentNews && state.currentNews.id === updatedNews.id) {
        state.currentNews = {...state.currentNews, ...updatedNews};
      }
    },
    ADD_NOTIFICATION(state, notification) {
      // 限制最多保存10条通知
      if (state.recentNotifications.length >= 10) {
        state.recentNotifications.pop();
      }
      state.recentNotifications.unshift(notification);
    }
  },
  
  actions: {
    // 获取新闻列表
    async fetchNewsList({ commit }, params = {}) {
      commit('SET_LOADING', true);
      try {
        const response = await newsService.getNewsList(params);
        commit('SET_NEWS_LIST', response.results);
        commit('SET_TOTAL_ITEMS', response.count);
        return response;
      } catch (error) {
        console.error('获取新闻列表出错:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 获取单条新闻详情
    async fetchNewsDetail({ commit }, newsId) {
      commit('SET_LOADING', true);
      try {
        const news = await newsService.getNewsById(newsId);
        commit('SET_CURRENT_NEWS', news);
        return news;
      } catch (error) {
        console.error('获取新闻详情出错:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 添加新闻（通过WebSocket接收到新新闻时）
    addNewsItem({ commit }, news) {
      commit('ADD_NEWS_ITEM', news);
      commit('ADD_NOTIFICATION', {
        id: Date.now(),
        type: 'news',
        title: '新体育资讯',
        content: news.title,
        timestamp: new Date(),
        news_id: news.id
      });
    },
    
    // 更新新闻（通过WebSocket接收到新闻更新时）
    updateNewsItem({ commit }, news) {
      commit('UPDATE_NEWS_ITEM', news);
    }
  },
  
  getters: {
    featuredNews: state => state.newsList.filter(n => n.is_featured),
    regularNews: state => state.newsList.filter(n => !n.is_featured),
    newsById: state => id => state.newsList.find(n => n.id === id),
    latestNotifications: state => state.recentNotifications.slice(0, 5)
  }
};
```

### 通知UI组件

创建通知UI组件 `src/components/NewsNotifications.vue`：

```vue
<template>
  <div class="news-notifications">
    <el-popover
      placement="bottom"
      title="最新通知"
      width="300"
      trigger="click"
      v-model="showNotifications"
    >
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" slot="reference">
        <el-button icon="el-icon-bell" circle></el-button>
      </el-badge>
      
      <div class="notifications-container">
        <div v-if="notifications.length === 0" class="no-notifications">
          暂无新通知
        </div>
        <div v-else class="notification-list">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="notification-item"
            :class="{ 'is-read': notification.read }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-content">{{ notification.content }}</div>
            <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
          </div>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';

export default {
  name: 'NewsNotifications',
  
  data() {
    return {
      showNotifications: false,
      readNotifications: new Set()
    };
  },
  
  computed: {
    ...mapGetters('news', ['latestNotifications']),
    
    notifications() {
      return this.latestNotifications.map(notification => ({
        ...notification,
        read: this.readNotifications.has(notification.id)
      }));
    },
    
    unreadCount() {
      return this.notifications.filter(n => !n.read).length;
    }
  },
  
  methods: {
    handleNotificationClick(notification) {
      // 标记为已读
      this.readNotifications.add(notification.id);
      
      // 根据通知类型执行不同操作
      if (notification.type === 'news' && notification.news_id) {
        this.$router.push(`/news/${notification.news_id}`);
        this.showNotifications = false;
      }
    },
    
    formatTime(timestamp) {
      const date = new Date(timestamp);
      return moment(date).fromNow();
    }
  }
};
</script>

<style scoped>
.notifications-container {
  max-height: 300px;
  overflow-y: auto;
}

.no-notifications {
  text-align: center;
  color: #999;
  padding: 20px 0;
}

.notification-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.notification-item:hover {
  background-color: #f9f9f9;
}

.notification-item.is-read {
  opacity: 0.7;
}

.notification-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.notification-content {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-time {
  font-size: 12px;
  color: #999;
}
</style>
```

### 初始化WebSocket连接

在 `src/main.js` 中添加WebSocket初始化：

```javascript
// src/main.js
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import './assets/css/main.css'
import newsWebSocketService from './utils/websocket'

Vue.config.productionTip = false
Vue.use(ElementUI)

// 创建全局通知函数
Vue.prototype.$message = ElementUI.Message
window.$message = ElementUI.Message

// 初始化WebSocket
store.watch(
  // 当认证状态改变时
  state => state.auth.token,
  // 连接或断开WebSocket
  token => {
    if (token) {
      newsWebSocketService.connect();
    } else {
      newsWebSocketService.disconnect();
    }
  },
  // 立即执行一次
  { immediate: true }
)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
```

## 权限控制

实时推送功能的权限控制完全集成了系统现有的用户权限模型，确保只有合适的用户能接收通知：

### 用户组分类

- **通用组 (news_general)**：所有认证用户接收
- **管理员组 (news_admin)**：仅管理员用户接收
- **学生组 (news_student_{id})**：特定学生用户接收

### 认证机制

- 使用JWT令牌进行WebSocket连接认证
- 遵循系统的两模型认证结构：
  1. User模型 (user_type字段区分用户类型)
  2. Student模型 (与User模型的一对一关系)

### 权限验证流程

1. 客户端连接WebSocket时发送JWT令牌
2. 服务器验证令牌并确定用户身份
3. 根据用户类型和关联关系，将用户加入相应的通知组
4. 只允许特定组的用户接收特定类型的通知

## 部署说明

### 开发环境

在开发环境中运行实时推送功能：

```bash
# 后端
pip install channels daphne
cd fitness_backend
daphne fitness_backend.asgi:application -p 8000

# 前端
cd frontend
npm run serve
```

### 生产环境

生产环境部署推荐使用以下配置：

1. **使用Redis作为Channel Layer**

修改 `settings.py`：

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis-server', 6379)],
        },
    },
}
```

2. **使用专业ASGI服务器**

```bash
# 安装依赖
pip install uvicorn

# 运行
uvicorn fitness_backend.asgi:application --host 0.0.0.0 --port 8000 --workers 4
```

## 使用指南

### 管理员添加/编辑新闻

1. 登录管理员账户
2. 在管理页面创建或编辑新闻
3. 将新闻状态设置为"已发布"
4. 保存新闻，系统会自动将新闻推送给在线用户

### 学生接收新闻通知

1. 学生登录系统后，WebSocket连接自动建立
2. 当有新闻发布时，系统会自动推送通知
3. 新闻通知显示在页面顶部的通知图标上
4. 学生可以点击通知图标查看详细内容
5. 点击通知项目会跳转到相应的新闻详情页

### 通知权限请求

首次使用浏览器通知功能时，系统会请求用户授予通知权限：

1. 用户登录后，系统自动请求通知权限
2. 用户需要在浏览器中允许接收通知
3. 允许后，即使页面不在活动状态也可以接收桌面通知

## 常见问题

### WebSocket连接失败

**问题**：前端无法建立WebSocket连接
**解决方案**：
- 确认ASGI服务器正常运行
- 检查前端WebSocket URL配置是否正确
- 确保认证令牌有效且未过期
- 检查用户是否有权限建立连接

### 推送延迟或没有收到推送

**问题**：用户没有实时收到新闻推送
**解决方案**：
- 检查Channel Layers配置是否正确
- 确认后端信号处理器已正确注册
- 验证用户已加入正确的通知组
- 检查浏览器控制台是否有WebSocket错误

### 通知权限被拒绝

**问题**：用户无法接收浏览器桌面通知
**解决方案**：
- 指导用户在浏览器设置中重新启用通知权限
- 提供明确的通知价值说明，鼓励用户允许通知
- 实现备选通知方式，如应用内通知

### WebSocket断开后自动重连

**问题**：网络波动导致WebSocket连接断开
**解决方案**：
- 使用现有的重连机制（已实现）
- 调整重连参数以适应不同网络环境
- 在重连之间实现应用状态保存
