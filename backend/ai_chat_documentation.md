# AI 聊天功能技术文档

## 1. 功能概述

AI 聊天系统是健身管理平台的核心功能之一，为用户提供智能对话服务。系统使用 DeepSeek AI 模型，支持多种应用场景（如健身指导、营养建议等），并根据用户类型提供个性化响应。

主要功能包括：
- 对话管理（创建、列表、删除）
- 消息交互
- 支持 Markdown 格式的响应
- 根据用户角色的个性化系统提示词
- 对话长期记忆

## 2. 系统架构

### 2.1 技术栈

- **后端**：
  - Django REST Framework
  - Python 3.8+
  
- **前端**：
  - Vue.js
  - Vuex 状态管理
  - Vue Router
  - Axios

- **AI 服务**：
  - DeepSeek API
  - 可选：Ollama（本地部署模型）

### 2.2 架构图

```
┌───────────────────┐      ┌────────────────────┐      ┌───────────────────┐
│                   │      │                    │      │                   │
│  前端 Vue 组件    │◄────►│  Django REST API   │◄────►│  DeepSeek AI API  │
│  (AIChatView 等)  │      │  (ConversationViewSet)    │                   │
│                   │      │                    │      │                   │
└───────────────────┘      └────────────────────┘      └───────────────────┘
         ▲                          ▲
         │                          │
         │                          │
         ▼                          ▼
┌───────────────────┐      ┌────────────────────┐
│                   │      │                    │
│  Vuex 状态管理    │      │  PostgreSQL 数据库 │
│  (aiChat 模块)    │      │  (用户、对话、消息)│
│                   │      │                    │
└───────────────────┘      └────────────────────┘
```

## 3. 后端实现

### 3.1 数据模型

两个核心模型：`Conversation` 和 `Message`，用于管理对话和消息内容。

#### 3.1.1 Conversation 模型

```python
class Conversation(models.Model):
    """用户和AI之间的对话"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=255, default='新对话')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    use_memory = models.BooleanField(default=True)  # 是否启用对话记忆
    memory_summary = models.TextField(blank=True, null=True)  # 对话记忆摘要
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    def update_memory_summary(self, new_summary):
        """更新记忆摘要"""
        self.memory_summary = new_summary
        self.save(update_fields=['memory_summary'])
    
    class Meta:
        ordering = ['-updated_at']  # 默认按更新时间降序
```

#### 3.1.2 Message 模型

```python
class Message(models.Model):
    """对话中的单条消息"""
    ROLE_CHOICES = (
        ('user', '用户'),
        ('assistant', '助手'),
        ('system', '系统')
    )
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
    
    class Meta:
        ordering = ['timestamp']  # 按时间升序排序
```

### 3.2 序列化器

用于将模型转换为 JSON 格式，提供 API 接口。

```python
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'user', 'title', 'created_at', 'updated_at', 'use_memory', 'memory_summary', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'memory_summary']
```

### 3.3 视图集（ViewSets）

处理 API 请求、鉴权和业务逻辑。

```python
class ConversationViewSet(viewsets.ModelViewSet):
    """对话管理API接口"""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """只返回当前用户的对话记录，按更新时间降序排序"""
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')
    
    def perform_create(self, serializer):
        """创建新对话时设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """发送消息给AI并获取响应"""
        conversation = self.get_object()
        user_message = request.data.get('message', '')
        
        # 验证消息不为空
        if not user_message.strip():
            return Response({'error': '消息不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存用户消息
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # 更新对话时间戳
        conversation.save()
        
        # 获取用户类型，用于个性化响应
        user_type = request.user.user_type if hasattr(request.user, 'user_type') else 'unknown'
        
        # 构建系统提示词，根据用户类型定制
        system_prompt = self._get_system_prompt_for_user_type(user_type, request.user)
        
        # 将对话记忆添加到系统提示中（如果启用记忆功能）
        if conversation.use_memory and conversation.memory_summary:
            system_prompt += f"\n\n用户的历史记忆摘要：\n{conversation.memory_summary}"
            
        system_message = {
            "role": "system", 
            "content": system_prompt
        }
        
        # 获取对话历史（最后10条消息，避免上下文过长）
        messages = Message.objects.filter(conversation=conversation).order_by('timestamp')[:10]
        
        # 格式化消息用于AI服务
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        # 将系统提示词添加到消息列表的开头
        formatted_messages.insert(0, system_message)
        
        # 从请求中获取服务类型和使用场景
        service_type = request.data.get('service_type', 'auto')
        use_case = request.data.get('use_case', 'general')
        
        # [细节请求处理逻辑略]...
        
        # 处理AI响应...
        
        # 检查是否需要更新对话记忆
        message_count = Message.objects.filter(conversation=conversation).count()
        memory_service = MemoryService()
        
        if conversation.use_memory and memory_service.should_generate_memory(message_count):
            all_messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
            new_memory = memory_service.generate_memory(
                all_messages, 
                previous_memory=conversation.memory_summary
            )
            
            if new_memory:
                conversation.update_memory_summary(new_memory)
        
        # 返回响应...
    
    def _get_system_prompt_for_user_type(self, user_type, user):
        """根据用户类型生成系统提示词"""
        base_prompt = "你是一位专业的体育健身AI助手，为健身运动提供专业指导和建议。"
        
        if user_type == 'student':
            # 尝试获取学生资料
            try:
                student_profile = user.student_profile
                prompt = f"{base_prompt}你正在与一名学生交流，请提供适合学生的健身和体测指导。"
                
                # 如果有身高体重数据，可以计算BMI并添加到提示中
                if hasattr(student_profile, 'height') and hasattr(student_profile, 'weight'):
                    if student_profile.height and student_profile.weight:
                        height_m = student_profile.height / 100  # 转换为米
                        bmi = student_profile.weight / (height_m * height_m)
                        prompt += f" 该学生的BMI约为{bmi:.1f}。"
                
                return prompt
            except:
                return f"{base_prompt}你正在与一名学生交流，请提供适合学生的健身和体测指导。"
                
        elif user_type == 'parent':
            return f"{base_prompt}你正在与一位家长交流，请提供适合指导孩子体育锻炼的建议..."
            
        elif user_type == 'admin':
            return f"{base_prompt}你正在与一位管理员交流，请提供关于体育教育、健身项目管理..."
            
        else:
            return f"{base_prompt}请提供关于健身、营养和体育锻炼的专业建议。"
```

### 3.4 AI 服务

负责与 AI 模型进行交互的服务层。

```python
class DeepSeekService(AIModelService):
    """与DeepSeek API通信的服务类"""
    def __init__(self):
        # 从环境变量获取API密钥
        self.api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        # DeepSeek API端点URL
        self.base_url = "https://api.deepseek.com"
        self.api_url = f"{self.base_url}/v1/chat/completions"
        # 默认使用的模型
        self.model = "deepseek-chat"
        # 针对不同用例的温度设置
        self.use_case_temperatures = {
            "coding": 0.0,     # 编程/数学
            "data": 1.0,       # 数据清洗/分析
            "general": 1.3,    # 一般对话
            "translation": 1.3, # 翻译
            "creative": 1.5    # 创意写作/诗歌
        }
        # 默认使用一般对话的温度
        self.temperature = self.use_case_temperatures["general"]
        
    def get_response(self, messages, use_case="general"):
        """向DeepSeek API发送请求并获取响应"""
        # 实现逻辑...
```

### 3.5 记忆服务

负责生成和维护对话记忆的服务。

```python
class MemoryService:
    """对话记忆服务，生成和维护对话的记忆摘要"""
    def __init__(self):
        # 使用DeepSeek服务来生成记忆摘要
        self.ai_service = DeepSeekService()
        # 记忆生成阈值，当消息数达到该值时生成记忆
        self.memory_threshold = 10
    
    def should_generate_memory(self, message_count):
        """判断是否应该生成记忆摘要"""
        return message_count > 0 and message_count % self.memory_threshold == 0
    
    def generate_memory(self, messages, previous_memory=None):
        """生成对话记忆摘要"""
        # 实现逻辑...
        
    def _merge_memories(self, old_memory, new_memory):
        """合并旧记忆和新记忆"""
        # 实现逻辑...
```

### 3.6 URL 路由配置

```python
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## 4. 前端实现

### 4.1 Vuex 状态管理

为 AI 聊天功能提供统一的状态管理。

```javascript
// aiChat.js

// 初始状态
const state = {
  conversations: [],
  currentConversation: null,
  messages: [],
  loading: false,
  sendingMessage: false,
  error: null
};

// Getters
const getters = {
  allConversations: state => state.conversations,
  currentConversation: state => state.currentConversation,
  messages: state => state.messages,
  isLoading: state => state.loading,
  isSendingMessage: state => state.sendingMessage,
  error: state => state.error
};

// Mutations
const mutations = {
  SET_CONVERSATIONS(state, conversations) {
    state.conversations = conversations;
  },
  SET_CURRENT_CONVERSATION(state, conversation) {
    state.currentConversation = conversation;
  },
  // 其他 mutations...
};

// Actions
const actions = {
  async fetchConversations({ commit }) {
    // 逻辑...
  },
  
  async createConversation({ commit }, payload = {}) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      // 默认值
      const data = {
        title: payload.title || '新对话',
        use_memory: payload.use_memory !== undefined ? payload.use_memory : true
      };
      
      const response = await aiChatService.createConversation(data);
      const newConversation = response.data;
      commit('ADD_CONVERSATION', newConversation);
      commit('SET_CURRENT_CONVERSATION', newConversation);
      commit('SET_MESSAGES', []);
      return newConversation;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '创建对话失败');
      console.error('创建对话失败:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  async sendMessage({ commit, state }, { conversationId, message, serviceType = 'auto', useCase = 'general' }) {
    // 逻辑...
  },
  
  // 其他 actions...
};
```

### 4.2 API 服务

封装与后端 API 的通信。

```javascript
// aiChatService.js
import api from './api';

const aiChatService = {
  getConversations() {
    return api.get('/ai/conversations/');
  },
  
  createConversation(data) {
    return api.post('/ai/conversations/', data);
  },
  
  getConversation(id) {
    return api.get(`/ai/conversations/${id}/`);
  },
  
  deleteConversation(id) {
    return api.delete(`/ai/conversations/${id}/`);
  },
  
  getMessages(conversationId) {
    return api.get(`/ai/conversations/${conversationId}/messages/`);
  },
  
  sendMessage(conversationId, message, serviceType = 'auto', useCase = 'general') {
    return api.post(`/ai/conversations/${conversationId}/send_message/`, {
      message,
      service_type: serviceType,
      use_case: useCase
    });
  }
};

export default aiChatService;
```

### 4.3 Vue 组件

#### 4.3.1 主聊天视图 (AIChatView.vue)

负责整体布局和协调其他组件。

```vue
<template>
  <div class="chat-container">
    <!-- 对话列表侧边栏 -->
    <AIConversationList 
      :currentConversationId="currentConversationId" 
      @select-conversation="selectConversation" 
    />
    
    <!-- 聊天主要区域 -->
    <div class="chat-main">
      <!-- 当前聊天顶部 -->
      <div class="chat-header">
        <h2>{{ currentTitle }}</h2>
        <div v-if="isSendingMessage" class="status-indicator">
          <i class="fas fa-spinner fa-spin"></i> AI正在响应...
        </div>
      </div>
      
      <!-- 消息列表区域 -->
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="!currentConversation" class="welcome-container">
          <div class="welcome-content">
            <h3>欢迎使用AI助手</h3>
            <p>使用DeepSeek AI模型提供智能对话支持</p>
            
            <!-- 主题模板 -->
            <div class="prompt-templates">
              <h4>选择一个主题开始</h4>
              <div class="template-grid"><!-- 模板项 --></div>
            </div>
            
            <button @click="createNewConversation" class="start-chat-btn">
              <i class="fas fa-comment-dots"></i> 开始新对话
            </button>
          </div>
        </div>
        
        <!-- 消息列表 -->
        <template v-else>
          <!-- ... -->
          <AIChatMessage 
            v-for="message in messages" 
            :key="message.id" 
            :message="message"
          />
          <!-- 打字动画 -->
          <AIChatMessage
            v-if="isSendingMessage"
            :message="{role: 'assistant', content: '', timestamp: new Date().toISOString()}"
            :isTyping="true"
          />
        </template>
      </div>
      
      <!-- 消息输入区域 -->
      <AIChatInput 
        v-if="currentConversation" 
        @send-message="sendMessage"
        :disabled="isSendingMessage"
        ref="chatInput"
      />
    </div>
  </div>
</template>

<script>
export default {
  setup() {
    // 组件逻辑...
    
    // 预定义提示词模板
    const promptTemplates = [
      { 
        title: '体能训练计划', 
        icon: 'fas fa-dumbbell', 
        prompt: '我想要一个为期4周的体能训练计划，帮助我提高整体体能水平...' 
      },
      // 其他模板...
    ];
    
    // 发送消息方法
    const sendMessage = async (messageInput) => {
      // 实现逻辑...
    };
    
    return {
      // 返回数据和方法...
    };
  }
};
</script>
```

#### 4.3.2 聊天消息组件 (AIChatMessage.vue)

负责显示单个聊天消息，支持 Markdown 渲染和打字动画。

```vue
<template>
  <div :class="['message-container', message.role === 'user' ? 'user-message' : 'ai-message']">
    <div class="message-avatar">
      <i :class="[message.role === 'user' ? 'fas fa-user' : 'fas fa-robot']"></i>
    </div>
    <div class="message-content">
      <div class="message-header">
        <div class="message-sender">{{ message.role === 'user' ? '用户' : 'AI助手' }}</div>
        <div class="message-time">{{ formatTime(message.timestamp) }}</div>
      </div>
      <div v-if="message.role === 'assistant' && isTyping" class="message-typing">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
      <div v-else class="message-text" v-html="formattedContent"></div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked';
import DOMPurify from 'dompurify';

export default {
  props: {
    message: {
      type: Object,
      required: true
    },
    isTyping: {
      type: Boolean,
      default: false
    }
  },
  
  setup(props) {
    // Markdown 渲染逻辑...
    
    return {
      // 返回数据和方法...
    };
  }
};
</script>
```

#### 4.3.3 其他组件

- **AIChatInput.vue**: 消息输入组件
- **AIConversationList.vue**: 对话列表组件

## 5. 鉴权和权限控制

系统使用两模型认证结构：
1. **User 模型**：扩展 AbstractUser，包含 user_type 字段（'student', 'parent', 'admin'）
2. **Student 模型**：通过 OneToOneField 关联到 User（related_name='student_profile'）

AI 聊天功能根据用户类型提供个性化体验：
- 学生：获取健身和体测指导，可能包含基于其身体数据的个性化建议
- 家长：获取关于指导孩子体育锻炼的建议
- 管理员：获取关于体育教育、健身项目管理和学生体测数据分析的专业建议

## 6. 关键业务流程

### 6.1 创建新对话

1. 用户点击"开始新对话"或选择主题模板
2. 前端调用 `createConversation` action，创建对话并保存标题和记忆设置
3. 后端创建新的 Conversation 记录，关联到当前用户
4. 如果选择了模板，系统自动发送预设提示词作为第一条消息

### 6.2 发送消息流程

1. 用户输入消息，点击发送
2. 前端调用 `sendMessage` action，将消息发送到后端
3. 后端处理：
   - 保存用户消息
   - 根据用户类型构建系统提示词
   - 获取历史消息（最近10条）
   - 添加对话记忆（如果启用）
   - 调用 AI 服务获取回复
   - 保存 AI 回复
   - 检查是否需要更新对话记忆
4. 前端显示 AI 响应，并在等待响应时显示打字动画

### 6.3 记忆生成流程

1. 系统检查当前消息数量是否达到阈值（每10条消息）
2. 如果达到阈值且开启了记忆功能：
   - 收集所有历史消息
   - 使用 MemoryService 生成记忆摘要
   - 如果已有记忆，则合并新旧记忆
   - 更新对话的记忆摘要字段
3. 在后续对话中，系统会将记忆摘要添加到系统提示中，帮助 AI 保持上下文连贯性

## 7. 部署和配置

### 7.1 必要环境变量

- `DEEPSEEK_API_KEY`: DeepSeek API 密钥（必需）
- `OLLAMA_BASE_URL`: Ollama 本地部署地址（可选，默认为 http://localhost:11434）

### 7.2 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

## 8. 扩展和定制

### 8.1 添加新的 AI 服务提供商

1. 创建新的服务类，继承 `AIModelService` 基类
2. 实现 `get_response` 方法
3. 在 `get_ai_service` 工厂函数中添加新的类型处理

### 8.2 自定义提示词模板

编辑 `AIChatView.vue` 中的 `promptTemplates` 数组，添加新的模板：

```javascript
const promptTemplates = [
  { 
    title: '新模板名称', 
    icon: 'fas fa-icon-name', 
    prompt: '模板提示词内容' 
  },
  // ...
];
```

## 9. 调试和故障排除

### 9.1 常见问题

1. **400 Bad Request**: 检查序列化器和模型字段是否匹配
2. **API 密钥错误**: 确认环境变量 `DEEPSEEK_API_KEY` 已正确设置
3. **消息不显示**: 检查前端组件数据绑定和 Vuex 状态

### 9.2 调试工具

- Django Debug Toolbar
- Vue.js DevTools
- 浏览器开发者工具
- API 端点测试工具（如 Postman）

## 10. 结论

AI 聊天功能提供了丰富的用户交互体验，并根据不同用户类型提供个性化服务。系统设计模块化，便于扩展和维护。

通过对话记忆功能，AI 能够记住用户的关键信息和偏好，提供更连贯、更个性化的响应，大大提升了用户体验。
