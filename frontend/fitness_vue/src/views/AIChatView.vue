<!--
  @description AI聊天视图组件 - 提供与AI助手的对话界面
  @roles 所有已认证用户
  @features
    - 支持多轮对话历史记录
    - 实时消息发送和接收
    - 对话列表管理
    - 消息排版和格式化
-->
<template>
  <div class="chat-container">
    <!-- 错误提示条 -->
    <div v-if="error" class="error-banner">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ error }}</span>
      <button @click="dismissError" class="dismiss-error-btn">
        <i class="fas fa-times"></i>
      </button>
    </div>

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
        <div class="header-actions">
          <!-- 操作按钮组 - 仅在有对话时显示 -->
          <div v-if="currentConversation" class="action-buttons">
            <!-- 导出按钮 - 仅在有消息时显示 -->
            <div v-if="messages && messages.length > 0" class="export-dropdown">
              <button class="action-btn export-btn" @click="toggleExportMenu" title="导出对话">
                <i class="fas fa-download"></i> 导出
              </button>
              <div v-if="showExportMenu" class="export-menu">
                <div class="export-menu-item" @click="exportChat('text')">
                  <i class="fas fa-file-alt"></i> 导出为文本 (.txt)
                </div>
                <div class="export-menu-item" @click="exportChat('markdown')">
                  <i class="fas fa-file-code"></i> 导出为Markdown (.md)
                </div>
                <div class="export-menu-item" @click="exportChat('html')">
                  <i class="fas fa-file-code"></i> 导出为HTML (.html)
                </div>
              </div>
            </div>

            <!-- 清空对话历史按钮 - 仅在有消息时显示 -->
            <button
              v-if="messages && messages.length > 0"
              class="action-btn clear-btn"
              @click="confirmClearMessages"
              title="清空对话历史">
              <i class="fas fa-trash-alt"></i> 清空
            </button>
          </div>
          <!-- 状态指示器 -->
          <div v-if="isSendingMessage" class="status-indicator">
            <i class="fas fa-spinner fa-spin"></i> AI正在响应...
          </div>
        </div>
      </div>

      <!-- 消息列表区域 -->
      <div class="chat-messages" ref="messagesContainer" @scroll="handleScroll">
        <!-- 加载更多消息提示 -->
        <div v-if="isLoadingMore" class="loading-more">
          <i class="fas fa-spinner fa-spin"></i> 加载更多消息...
        </div>

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
          <div v-if="messages && messages.length === 0" class="empty-chat">
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
            v-for="message in (messages || [])"
            :key="message.id"
            :message="message"
            :conversationId="currentConversationId"
            :isTyping="message.streaming"
            @message-deleted="handleMessageDeleted"
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

  <!-- 清空对话历史确认模态框 -->
  <div v-if="showClearMessagesModal" class="modal-overlay">
    <div class="modal-content">
      <h4>确认清空历史</h4>
      <p>您确定要清空当前对话的所有历史消息吗？</p>
      <p>此操作不可撤销。</p>
      <div class="modal-actions">
        <button @click="cancelClearMessages" class="cancel-btn">取消</button>
        <button @click="clearMessages" class="confirm-btn">清空</button>
      </div>
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
import { exportChatAsText, exportChatAsMarkdown, exportChatAsHTML } from '@/services/exportService';

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

    // 滚动相关状态
    const scrollThreshold = 100; // px
    const isAtScrollTop = ref(false);
    const initialScrollPosition = ref(null);
    const scrollPositionBeforeLoad = ref(null);

    // 导出和清空功能相关状态
    const showExportMenu = ref(false);
    const showClearMessagesModal = ref(false);

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

    // 获取当前对话的messages
    const messages = computed(() => store.getters['aiChat/messages']);

    // 加载状态
    const isLoading = computed(() => store.getters['aiChat/isLoading']);

    // 是否正在发送消息
    const isSendingMessage = computed(() => store.getters['aiChat/isSendingMessage']);

    // 是否正在加载更多消息
    const isLoadingMore = computed(() => store.getters['aiChat/isLoadingMore']);

    // 是否还有更多消息可加载
    const hasMoreMessages = computed(() => store.getters['aiChat/hasMoreMessages']);

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
        // 检查认证状态
        if (!store.getters.isAuthenticated) {
          // 如果没有认证，尝试从localStorage获取token
          const token = localStorage.getItem('token');
          if (!token) {
            console.warn('用户未登录，无法加载对话数据');
            router.push('/login');
            return;
          }
        }

        // 加载对话列表
        await store.dispatch('aiChat/fetchConversations');

        // 如果URL中有对话ID，加载该对话
        if (currentConversationId.value) {
          await loadConversation(currentConversationId.value);
        }
      } catch (error) {
        console.error('加载对话数据失败:', error);

        // 如果是认证错误，重定向到登录页面
        if (error.response && error.response.status === 401) {
          router.push('/login');
        }
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

        // 显示用户友好的错误提示
        let errorMessage = '发送消息失败';

        if (error.userMessage) {
          // 如果有用户友好的错误信息，使用它
          errorMessage = error.userMessage;
        } else if (error.response) {
          // 处理常见HTTP错误
          const status = error.response.status;
          if (status === 401) {
            errorMessage = '登录已过期，请重新登录';
            // 重定向到登录页面
            router.push('/login');
          } else if (status === 404) {
            errorMessage = '对话不存在，请创建新对话';
          } else if (status === 500) {
            errorMessage = '服务器错误，请稍后再试';
          }
        } else if (!navigator.onLine) {
          // 检查网络连接
          errorMessage = '网络连接已断开，请检查您的网络设置';
        }

        // 使用全局通知显示错误
        if (window.antd && window.antd.message) {
          window.antd.message.error(errorMessage);
        } else {
          alert(errorMessage);
        }

        // 如果是认证错误，重新加载页面
        if (error.response && error.response.status === 401) {
          setTimeout(() => {
            window.location.reload();
          }, 1500);
        }
      }
    };

    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    };

    // 处理滚动事件
    const handleScroll = () => {
      if (!messagesContainer.value || !currentConversation.value) return;

      const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value;

      // 检测是否已经滚动到顶部
      if (scrollTop < 200 && hasMoreMessages.value && !isLoadingMore.value) {
        // 记录当前滚动位置
        scrollPositionBeforeLoad.value = {
          scrollTop,
          scrollHeight,
          clientHeight
        };

        // 加载更多历史消息
        loadMoreMessages();
      }
    };

    // 加载更多消息
    const loadMoreMessages = async () => {
      if (!currentConversation.value || !hasMoreMessages.value || isLoadingMore.value) return;

      try {
        // 加载更多消息
        await store.dispatch('aiChat/loadMoreMessages', currentConversation.value.id);

        // 保持滚动位置，防止加载更多消息后滚动位置跳变
        nextTick(() => {
          if (messagesContainer.value && scrollPositionBeforeLoad.value) {
            // 计算相对滚动位置
            const { scrollHeight: oldScrollHeight } = scrollPositionBeforeLoad.value;
            const newScrollHeight = messagesContainer.value.scrollHeight;
            const heightDiff = newScrollHeight - oldScrollHeight;

            // 调整滚动位置保持相对位置不变
            messagesContainer.value.scrollTop = heightDiff + 10; // 给用户一个小反馈，滚动位置稍微下移
          }
        });
      } catch (error) {
        console.error('加载更多消息失败:', error);
      }
    };
    // 切换导出菜单显示状态
    const toggleExportMenu = () => {
      showExportMenu.value = !showExportMenu.value;

      // 如果打开菜单，添加点击外部关闭的事件
      if (showExportMenu.value) {
        setTimeout(() => {
          document.addEventListener('click', closeExportMenuOnClickOutside);
        }, 100);
      }
    };

    // 点击外部关闭导出菜单
    const closeExportMenuOnClickOutside = (event) => {
      const exportDropdown = document.querySelector('.export-dropdown');
      if (exportDropdown && !exportDropdown.contains(event.target)) {
        showExportMenu.value = false;
        document.removeEventListener('click', closeExportMenuOnClickOutside);
      }
    };

    // 导出对话
    const exportChat = (format) => {
      if (!currentConversation.value || messages.value.length === 0) return;

      const title = currentConversation.value.title || '未命名对话';

      // 根据选择的格式导出
      switch (format) {
        case 'text':
          exportChatAsText(messages.value, title);
          break;
        case 'markdown':
          exportChatAsMarkdown(messages.value, title);
          break;
        case 'html':
          exportChatAsHTML(messages.value, title);
          break;
      }

      // 关闭导出菜单
      showExportMenu.value = false;
      document.removeEventListener('click', closeExportMenuOnClickOutside);
    };

    // 确认清空对话历史
    const confirmClearMessages = () => {
      showClearMessagesModal.value = true;
    };

    // 取消清空对话历史
    const cancelClearMessages = () => {
      showClearMessagesModal.value = false;
    };

    // 清空对话历史
    const clearMessages = async () => {
      if (!currentConversation.value) return;

      try {
        await store.dispatch('aiChat/clearConversationMessages', currentConversation.value.id);
        showClearMessagesModal.value = false;
      } catch (error) {
        console.error('清空对话历史失败:', error);
      }
    };

    // 处理消息删除事件
    const handleMessageDeleted = (messageId) => {
      // 消息已在 AIChatMessage 组件中调用 Vuex 删除，这里只需要处理UI相关逻辑
      // 如果需要，可以在这里添加提示消息或其他反馈
      nextTick(() => {
        // UI更新后的操作，比如滚动调整
        scrollToBottom();
      });
    };

    // 关闭错误提示
    const dismissError = () => {
      store.commit('aiChat/setError', null);
    };

    return {
      currentConversationId,
      currentConversation,
      currentTitle,
      messages,
      isLoading,
      isSendingMessage,
      isLoadingMore,
      hasMoreMessages,
      error,
      messagesContainer,
      chatInput,
      suggestedPrompts,
      promptTemplates,
      showExportMenu,
      showClearMessagesModal,
      loadConversation,
      selectConversation,
      createNewConversation,
      startTemplateConversation,
      applySuggestion,
      sendMessage,
      scrollToBottom,
      handleScroll,
      loadMoreMessages,
      toggleExportMenu,
      exportChat,
      clearMessages,
      confirmClearMessages,
      cancelClearMessages,
      handleMessageDeleted,
      dismissError
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.export-dropdown {
  position: relative;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  background: transparent;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.export-btn {
  color: #10a37f;
  border-color: rgba(16, 163, 127, 0.3);
}

.export-btn:hover {
  background-color: rgba(16, 163, 127, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(16, 163, 127, 0.2);
}

.clear-btn {
  color: #e74c3c;
  border-color: rgba(231, 76, 60, 0.3);
}

.clear-btn:hover {
  background-color: rgba(231, 76, 60, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(231, 76, 60, 0.2);
}

.export-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 240px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  z-index: 100;
  margin-top: 8px;
  overflow: hidden;
  animation: menuFadeIn 0.2s ease-in-out;
  border: 1px solid rgba(16, 163, 127, 0.2);
}

@keyframes menuFadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.export-menu-item {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
  border-bottom: 1px solid rgba(16, 163, 127, 0.1);
}

.export-menu-item:last-child {
  border-bottom: none;
}

.export-menu-item i {
  color: #10a37f;
  font-size: 1.1rem;
}

.export-menu-item:hover {
  background-color: #f0fdf9;
  transform: translateX(3px);
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

/* 错误提示条样式 */
.error-banner {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-width: 80%;
  animation: slideDown 0.3s ease-out;
}

.error-banner i.fa-exclamation-circle {
  color: #ff4d4f;
  font-size: 16px;
  margin-right: 8px;
}

.dismiss-error-btn {
  background: transparent;
  border: none;
  color: rgba(0, 0, 0, 0.45);
  cursor: pointer;
  padding: 4px;
  margin-left: 12px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.dismiss-error-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: rgba(0, 0, 0, 0.65);
}

@keyframes slideDown {
  from {
    transform: translate(-50%, -20px);
    opacity: 0;
  }
  to {
    transform: translate(-50%, 0);
    opacity: 1;
  }
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-content h4 {
  margin-top: 0;
  color: #e74c3c;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn {
  padding: 8px 16px;
  background-color: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background-color: #e6e6e6;
}

.confirm-btn {
  padding: 8px 16px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn:hover {
  background-color: #c0392b;
}
</style>
