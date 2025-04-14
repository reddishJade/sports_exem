<template>
  <div :class="['message-container', message.role === 'user' ? 'user-message' : 'ai-message']" @mouseover="showControls = true" @mouseleave="showControls = false">
    <div class="message-avatar">
      <i :class="[message.role === 'user' ? 'fas fa-user' : 'fas fa-robot']"></i>
    </div>
    <div class="message-content">
      <div class="message-header">
        <div class="message-sender">{{ message.role === 'user' ? '用户' : 'AI助手' }}</div>
        <div class="message-meta">
          <button 
            v-if="!isTyping && message.id && !isDeleting" 
            class="delete-message-btn" 
            @click="confirmDeleteMessage"
            title="删除消息"
          >
            <i class="fas fa-trash-alt"></i>
          </button>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      <div v-if="isDeleting" class="message-deleting">
        <span>正在删除...</span>
      </div>
      <div v-else-if="message.role === 'assistant' && (isTyping || message.streaming)" class="message-text streaming-text" v-html="formattedContent">
      </div>
      <div v-else class="message-text" v-html="formattedContent"></div>
    </div>
    
    <!-- 确认删除消息模态框 -->
    <div v-if="showDeleteModal" class="delete-confirm-modal">
      <div class="delete-confirm-content">
        <p>确定要删除这条消息吗？</p>
        <div class="delete-confirm-actions">
          <button @click="cancelDelete" class="cancel-btn">取消</button>
          <button @click="deleteMessage" class="confirm-btn">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// 配置marked选项
marked.setOptions({
  breaks: true,  // 将回车转换为<br>
  gfm: true,     // 使用GitHub风格的Markdown
});

export default {
  name: 'AIChatMessage',
  
  props: {
    message: {
      type: Object,
      required: true
    },
    isTyping: {
      type: Boolean,
      default: false
    },
    conversationId: {
      type: [Number, String],
      required: true
    }
  },
  
  emits: ['message-deleted'],
  
  setup(props, { emit }) {
    const store = useStore();
    
    // 状态变量
    const showControls = ref(false);        // 显示控制按钮
    const showDeleteModal = ref(false);     // 显示删除对话模态框
    const isDeleting = ref(false);          // 正在删除消息
    
    // 处理后的消息内容
    const formattedContent = computed(() => {
      if (!props.message.content) return '';
      
      // 将Markdown转换为HTML，并使用DOMPurify进行净化
      const rawHtml = marked(props.message.content || '');
      const sanitizedHtml = DOMPurify.sanitize(rawHtml);
      
      // 如果是流式消息，添加光标效果
      if (props.isTyping || props.message.streaming) {
        return sanitizedHtml + '<span class="typing-cursor"></span>';
      }
      
      return sanitizedHtml;
    });
    
    // 格式化时间戳
    const formatTime = (timestamp) => {
      if (!timestamp) return '';
      
      try {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit'
        });
      } catch (error) {
        console.error('格式化时间戳失败:', error);
        return '';
      }
    };
    
    // 确认删除消息
    const confirmDeleteMessage = () => {
      showDeleteModal.value = true;
    };
    
    // 取消删除
    const cancelDelete = () => {
      showDeleteModal.value = false;
    };
    
    // 删除消息
    const deleteMessage = async () => {
      if (!props.message.id || !props.conversationId) return;
      
      try {
        isDeleting.value = true;
        await store.dispatch('aiChat/deleteMessage', {
          conversationId: props.conversationId,
          messageId: props.message.id
        });
        
        // 通知父组件消息已删除
        emit('message-deleted', props.message.id);
        
        // 隐藏删除模态框
        showDeleteModal.value = false;
      } catch (error) {
        console.error('删除消息失败:', error);
      } finally {
        isDeleting.value = false;
      }
    };
    
    return {
      formattedContent,
      formatTime,
      showControls,
      showDeleteModal,
      isDeleting,
      confirmDeleteMessage,
      cancelDelete,
      deleteMessage
    };
  }
};
</script>

<style scoped>
.message-container {
  display: flex;
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.message-container:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.user-message {
  margin-left: 2rem;
}

.ai-message {
  margin-right: 2rem;
  background-color: rgba(16, 163, 127, 0.05);
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.user-message .message-avatar {
  background-color: #4d7cfe;
  color: white;
}

.ai-message .message-avatar {
  background-color: #10a37f;
  color: white;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.message-sender {
  font-weight: 600;
  font-size: 0.95rem;
}

.user-message .message-sender {
  color: #4d7cfe;
}

.ai-message .message-sender {
  color: #10a37f;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-time {
  font-size: 0.8rem;
  color: #888;
}

.delete-message-btn {
  background: rgba(231, 76, 60, 0.1);
  border: 1px solid rgba(231, 76, 60, 0.3);
  color: #e74c3c;
  padding: 4px 8px;
  font-size: 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.9;
  transition: all 0.2s;
  margin-right: 5px;
}

.delete-message-btn:hover {
  opacity: 1;
  background-color: rgba(231, 76, 60, 0.2);
  transform: scale(1.05);
}

.message-deleting {
  font-style: italic;
  color: #888;
  padding: 0.5rem 0;
}

.message-text {
  white-space: pre-wrap;
  line-height: 1.5;
  overflow-wrap: break-word;
  font-size: 0.95rem;
}

/* 为Markdown内容添加样式 */
.message-text :deep(p) {
  margin: 0.5rem 0;
}

.message-text :deep(pre) {
  padding: 0.75rem;
  background-color: #f6f8fa;
  border-radius: 6px;
  border: 1px solid #e1e4e8;
  overflow-x: auto;
  margin: 0.5rem 0;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
}

.message-text :deep(code) {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  background-color: rgba(27, 31, 35, 0.05);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.message-text :deep(pre code) {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

.message-text :deep(ul), .message-text :deep(ol) {
  padding-left: 1.5rem;
  margin: 0.5rem 0;
}

.message-text :deep(blockquote) {
  margin: 0.5rem 0;
  padding-left: 1rem;
  border-left: 3px solid #e1e4e8;
  color: #6a737d;
}

.message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5rem 0;
}

.message-text :deep(th), .message-text :deep(td) {
  border: 1px solid #e1e4e8;
  padding: 6px 13px;
}

.message-text :deep(th) {
  background-color: #f6f8fa;
}

/* 打字动画效果 */
.message-typing {
  display: flex;
  align-items: center;
  height: 24px;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #10a37f;
  margin-right: 4px;
  animation: wave 1.5s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

/* 删除确认模态框 */
.delete-confirm-modal {
  position: absolute;
  bottom: calc(100% + 10px);
  right: 0;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  z-index: 10;
  min-width: 200px;
  animation: fadeIn 0.2s ease-in-out;
}

.delete-confirm-content {
  padding: 12px;
}

.delete-confirm-content p {
  margin: 0 0 10px 0;
  font-size: 0.9rem;
}

.delete-confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.cancel-btn, .confirm-btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background-color: #e5e5e5;
}

.confirm-btn {
  background-color: #e74c3c;
  color: white;
}

.confirm-btn:hover {
  background-color: #c0392b;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes wave {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}

/* 流式生成的光标动画 */
.streaming-text {
  position: relative;
}

.typing-cursor {
  display: inline-block;
  width: 8px;
  height: 15px;
  background-color: #10a37f;
  margin-left: 2px;
  animation: cursor-blink 0.8s infinite;
  vertical-align: middle;
}

@keyframes cursor-blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .user-message {
    margin-left: 0.5rem;
  }
  
  .ai-message {
    margin-right: 0.5rem;
  }
}
</style>
