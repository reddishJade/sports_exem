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
import { ref, computed, onMounted } from 'vue';
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
    }
  },
  
  setup(props) {
    // 处理后的消息内容
    const formattedContent = computed(() => {
      if (!props.message.content) return '';
      
      // 将Markdown转换为HTML，并使用DOMPurify进行净化
      const rawHtml = marked(props.message.content || '');
      return DOMPurify.sanitize(rawHtml);
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
    
    return {
      formattedContent,
      formatTime
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

.message-time {
  font-size: 0.8rem;
  color: #888;
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

@keyframes wave {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
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
