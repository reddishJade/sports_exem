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
            <p>您可以询问有关体测相关的问题，获取健身建议，或任何其他问题。</p>
            
            <!-- 主题模板 -->
            <div class="prompt-templates">
              <h4>选择一个主题开始</h4>
              <div class="template-grid">
                <div 
                  v-for="(template, index) in promptTemplates" 
                  :key="index"
                  class="template-item"
                  @click="startTemplateConversation(template)">
                  <i :class="template.icon"></i>
                  <span>{{ template.title }}</span>
                </div>
              </div>
            </div>
            
            <button @click="createNewConversation" class="start-chat-btn">
              <i class="fas fa-comment-dots"></i> 开始新对话
            </button>
          </div>
        </div>
        
        <template v-else>
          <div v-if="messages.length === 0" class="empty-chat">
            <p>这是一个新对话，请开始发送消息。</p>
            <!-- 主题提示 -->
            <div class="prompt-suggestions">
              <h4>可能的话题</h4>
              <div class="suggestion-chips">
                <div 
                  v-for="(suggestion, index) in suggestedPrompts" 
                  :key="index"
                  class="suggestion-chip"
                  @click="applySuggestion(suggestion)">
                  {{ suggestion }}
                </div>
              </div>
            </div>
          </div>
          <AIChatMessage 
            v-for="message in messages" 
            :key="message.id" 
            :message="message"
          />
          <!-- 添加打字指示器，当AI正在回复时显示 -->
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useStore } from 'vuex';
import { useRoute, useRouter } from 'vue-router';
import AIConversationList from '@/components/AIConversationList.vue';
import AIChatMessage from '@/components/AIChatMessage.vue';
import AIChatInput from '@/components/AIChatInput.vue';

export default {
  name: 'AIChatView',
  
  components: {
    AIConversationList,
    AIChatMessage,
    AIChatInput
  },
  
  setup() {
    const store = useStore();
    const route = useRoute();
    const router = useRouter();
    const messagesContainer = ref(null);
    const chatInput = ref(null);
    
    // 获取当前对话ID
    const currentConversationId = computed(() => {
      return route.params.id ? parseInt(route.params.id) : null;
    });
    
    // 获取当前对话
    const currentConversation = computed(() => {
      return store.getters['aiChat/currentConversation'];
    });
    
    // 对话标题
    const currentTitle = computed(() => {
      return currentConversation.value?.title || 'AI助手';
    });
    
    // 获取消息列表
    const messages = computed(() => {
      return store.getters['aiChat/messages'];
    });
    
    // 加载状态
    const isLoading = computed(() => store.getters['aiChat/isLoading']);
    
    // 发送消息状态
    const isSendingMessage = computed(() => store.getters['aiChat/isSendingMessage']);
    
    // 获取错误信息
    const error = computed(() => store.getters['aiChat/error']);
    
    // 预定义提示词模板
    const promptTemplates = [
      { 
        title: '体能训练计划', 
        icon: 'fas fa-dumbbell', 
        prompt: '我想要一个为期4周的体能训练计划，帮助我提高整体体能水平。我的目标是提高耐力和力量。' 
      },
      { 
        title: '饮食营养建议', 
        icon: 'fas fa-apple-alt', 
        prompt: '请根据中国居民膳食指南，为我制定一个健康的一周饮食计划，我希望通过饮食增加肌肉并减少脂肪。' 
      },
      { 
        title: '体测分析', 
        icon: 'fas fa-chart-line', 
        prompt: '我最近参加了体测，我的BMI是23，50米跑成绩是7.5秒，立定跳远成绩是2.3米，坐位体前屈成绩是10厘米。请分析我的体测成绩并给出提高建议。' 
      },
      { 
        title: '运动损伤咨询', 
        icon: 'fas fa-medkit', 
        prompt: '我在跑步后膝盖感到疼痛，尤其是上下楼梯时。这可能是什么原因造成的？我应该如何处理以避免伤势加重？' 
      },
      { 
        title: '健身器材使用', 
        icon: 'fas fa-cog', 
        prompt: '我是健身房新手，请解释一下常见的健身器材如何正确使用，尤其是哑铃、杠铃和卧推架等器材的使用方法和注意事项。' 
      },
      { 
        title: '运动科学问答', 
        icon: 'fas fa-microscope', 
        prompt: '请解释无氧运动和有氧运动的区别，以及它们各自对健康和体能的影响。' 
      }
    ];
    
    // 新对话的提示词建议
    const suggestedPrompts = [
      '如何提高我的长跑成绩？',
      '请给我一些增强核心力量的练习',
      '我想了解更多关于间歇训练的知识',
      '如何正确测量和理解我的体测数据？',
      '请推荐适合学生的健康零食选择'
    ];
    
    // 在组件挂载时加载对话列表
    onMounted(async () => {
      try {
        // 加载对话列表
        await store.dispatch('aiChat/fetchConversations');
        
        // 如果URL中有对话ID，加载该对话
        if (currentConversationId.value) {
          await loadConversation(currentConversationId.value);
        }
      } catch (error) {
        console.error('加载对话数据失败:', error);
      }
    });
    
    // 监听当前对话ID变化，加载相应对话
    watch(currentConversationId, async (newId, oldId) => {
      if (newId && newId !== oldId) {
        await loadConversation(newId);
      }
    });
    
    // 监听消息列表变化，滚动到底部
    watch(messages, () => {
      scrollToBottom();
    });
    
    // 加载特定对话及其消息
    const loadConversation = async (conversationId) => {
      try {
        // 加载对话详情
        await store.dispatch('aiChat/fetchConversation', conversationId);
        
        // 加载对话消息
        await store.dispatch('aiChat/fetchMessages', conversationId);
        
        // 滚动到底部
        await nextTick();
        scrollToBottom();
      } catch (error) {
        console.error('加载对话详情失败:', error);
        router.push({ name: 'ai-chat' });
      }
    };
    
    // 选择对话
    const selectConversation = (conversation) => {
      router.push({ 
        name: 'ai-chat-conversation', 
        params: { id: conversation.id } 
      });
    };
    
    // 创建新对话
    const createNewConversation = async () => {
      try {
        const newConversation = await store.dispatch('aiChat/createConversation', {
          title: '新对话'
        });
        router.push({ 
          name: 'ai-chat-conversation', 
          params: { id: newConversation.id } 
        });
      } catch (error) {
        console.error('创建新对话失败:', error);
      }
    };
    
    // 使用模板创建新对话
    const startTemplateConversation = async (template) => {
      try {
        const newConversation = await store.dispatch('aiChat/createConversation', {
          title: template.title
        });
        
        router.push({ 
          name: 'ai-chat-conversation', 
          params: { id: newConversation.id } 
        });
        
        // 等待路由更新和组件重新渲染
        await nextTick();
        
        // 发送模板提示词
        if (chatInput.value) {
          setTimeout(() => {
            sendMessage(template.prompt);
          }, 300);
        }
      } catch (error) {
        console.error('使用模板创建对话失败:', error);
      }
    };
    
    // 应用提示词建议
    const applySuggestion = (suggestion) => {
      if (chatInput.value) {
        chatInput.value.setMessage(suggestion);
      }
    };
    
    // 发送消息
    const sendMessage = async (messageInput) => {
      if (!currentConversationId.value) return;
      
      try {
        const message = typeof messageInput === 'string' ? messageInput : messageInput.message;
        const serviceType = typeof messageInput === 'string' ? 'auto' : (messageInput.serviceType || 'auto');
        
        if (!message.trim()) return;
        
        await store.dispatch('aiChat/sendMessage', {
          conversationId: currentConversationId.value,
          message: message,
          serviceType: serviceType
        });
        
        // 滚动到底部
        await nextTick();
        scrollToBottom();
      } catch (error) {
        console.error('发送消息失败:', error);
      }
    };
    
    // 滚动到底部
    const scrollToBottom = () => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    };
    
    return {
      currentConversationId,
      currentConversation,
      currentTitle,
      messages,
      isLoading,
      isSendingMessage,
      error,
      messagesContainer,
      chatInput,
      selectConversation,
      createNewConversation,
      sendMessage,
      promptTemplates,
      suggestedPrompts,
      startTemplateConversation,
      applySuggestion
    };
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 150px);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  background-color: #fff;
  margin: 20px;
  overflow: hidden;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 0 12px 12px 0;
}

.chat-header {
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #efefef;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
}

.chat-header h2 {
  margin: 0;
  font-size: 1.3rem;
  color: #2c3e50;
  font-weight: 600;
}

.status-indicator {
  color: #10a37f;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background-color: #f9fafb;
  scroll-behavior: smooth;
}

.welcome-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
}

.welcome-content {
  text-align: center;
  max-width: 600px;
  padding: 3rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.welcome-content:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.welcome-content h3 {
  margin-top: 0;
  color: #10a37f;
  font-size: 1.8rem;
  margin-bottom: 1rem;
}

.welcome-content p {
  color: #4b5563;
  margin: 12px 0;
  line-height: 1.6;
  font-size: 1.05rem;
}

.start-chat-btn {
  margin-top: 28px;
  background-color: #10a37f;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.start-chat-btn:hover {
  background-color: #0d8c6c;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 163, 127, 0.2);
}

.start-chat-btn:active {
  transform: translateY(0);
}

.empty-chat {
  text-align: center;
  color: #6b7280;
  padding: 3rem 0;
  font-size: 1.1rem;
}

.prompt-templates {
  margin: 1.5rem 0;
  text-align: left;
}

.prompt-templates h4 {
  color: #4b5563;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  text-align: center;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.template-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
  height: 80px;
}

.template-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: #f0fdf9;
}

.template-item i {
  font-size: 1.5rem;
  margin-bottom: 8px;
  color: #10a37f;
}

.template-item span {
  font-size: 0.9rem;
  font-weight: 500;
  color: #4b5563;
  text-align: center;
}

.prompt-suggestions {
  margin: 2rem 0;
}

.prompt-suggestions h4 {
  color: #4b5563;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.suggestion-chip {
  background-color: #f0fdf9;
  border: 1px solid #d1fae5;
  color: #047857;
  padding: 8px 16px;
  border-radius: 16px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-chip:hover {
  background-color: #d1fae5;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .chat-container {
    flex-direction: column;
    height: calc(100vh - 100px);
    margin: 10px;
  }
  
  .chat-container > :first-child {
    width: 100%;
    border-radius: 12px 12px 0 0;
    max-height: 250px;
    overflow-y: auto;
  }
  
  .chat-main {
    border-radius: 0 0 12px 12px;
  }
  
  .welcome-content {
    padding: 2rem;
    max-width: 90%;
  }
  
  .template-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .template-item {
    height: 70px;
  }
}

@media (max-width: 480px) {
  .template-grid {
    grid-template-columns: 1fr;
  }
}
</style>
