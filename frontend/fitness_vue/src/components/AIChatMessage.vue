<template>
  <div :class="['message-container', message.role === 'user' ? 'user-message' : 'ai-message']" @mouseover="showControls = true" @mouseleave="showControls = false">
    <div class="message-avatar">
      <i :class="[message.role === 'user' ? 'fas fa-user' : 'fas fa-robot']"></i>
    </div>
    <div class="message-content">
      <div class="message-header">
        <div class="message-sender">{{ message.role === 'user' ? '用户' : 'AI助手' }}</div>
        <div class="message-meta">
          <div v-if="showControls && !isTyping && !isDeleting" class="message-actions">
            <button
              class="copy-message-btn"
              @click="copyMessageContent"
              title="复制消息"
            >
              <i :class="[copySuccess ? 'fas fa-check' : 'fas fa-copy']"></i>
            </button>
            <button
              v-if="message.id"
              class="delete-message-btn"
              @click="confirmDeleteMessage"
              title="删除消息"
            >
              <i class="fas fa-trash-alt"></i>
            </button>
          </div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      <div v-if="isDeleting" class="message-deleting">
        <span>正在删除...</span>
      </div>
      <div v-else-if="message.role === 'assistant' && (isTyping || message.streaming)" class="message-text streaming-text" v-html="formattedContent">
      </div>
      <div v-else class="message-text" v-html="formattedContent"></div>

      <!-- 消息反馈按钮 - 仅对AI消息显示 -->
      <div v-if="message.role === 'assistant' && !isTyping && !message.streaming && showControls" class="message-reactions">
        <button
          class="reaction-btn"
          :class="{ 'active': reaction === 'like' }"
          @click="setReaction('like')"
          title="有用"
        >
          <i class="fas fa-thumbs-up"></i>
        </button>
        <button
          class="reaction-btn"
          :class="{ 'active': reaction === 'dislike' }"
          @click="setReaction('dislike')"
          title="没用"
        >
          <i class="fas fa-thumbs-down"></i>
        </button>
      </div>
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
    const copySuccess = ref(false);         // 复制成功状态
    const reaction = ref(null);             // 消息反馈状态

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

        // 打印调试信息
        console.log('尝试删除消息:', {
          conversationId: props.conversationId,
          messageId: props.message.id
        });

        // 检查是否为临时ID（以temp-开头）
        if (typeof props.message.id === 'string' && props.message.id.startsWith('temp-')) {
          // 如果是临时ID，直接从列表中移除，不调用API
          console.log('检测到临时ID，直接从列表中移除');
          store.commit('aiChat/REMOVE_MESSAGE', props.message.id);
        } else {
          // 如果是真实ID，调用API删除
          const aiChatService = await import('@/services/aiChatService').then(module => module.default);
          await aiChatService.deleteMessage(props.conversationId, props.message.id);

          // 删除成功后，从列表中移除消息
          store.commit('aiChat/REMOVE_MESSAGE', props.message.id);
        }

        // 通知父组件消息已删除
        emit('message-deleted', props.message.id);

        // 隐藏删除模态框
        showDeleteModal.value = false;
      } catch (error) {
        console.error('删除消息失败:', error);
        // 不显示警告，因为可能是临时ID导致的错误
      } finally {
        isDeleting.value = false;
      }
    };

    // 复制消息内容
    const copyMessageContent = () => {
      if (!props.message.content) return;

      try {
        // 创建一个临时文本区域元素
        const textArea = document.createElement('textarea');
        textArea.value = props.message.content;

        // 将文本区域添加到文档中
        document.body.appendChild(textArea);

        // 选中文本区域的内容
        textArea.select();

        // 执行复制命令
        const successful = document.execCommand('copy');

        // 从文档中移除文本区域
        document.body.removeChild(textArea);

        if (successful) {
          // 显示复制成功状态
          copySuccess.value = true;
          setTimeout(() => {
            copySuccess.value = false;
          }, 2000);
        } else {
          console.error('复制命令失败');
        }
      } catch (error) {
        console.error('复制消息失败:', error);

        // 尝试使用现代API
        try {
          navigator.clipboard.writeText(props.message.content)
            .then(() => {
              copySuccess.value = true;
              setTimeout(() => {
                copySuccess.value = false;
              }, 2000);
            })
            .catch(err => {
              console.error('使用Clipboard API复制失败:', err);
              alert('复制失败，请手动复制消息内容');
            });
        } catch (clipboardError) {
          console.error('不支持Clipboard API:', clipboardError);
          alert('复制失败，请手动复制消息内容');
        }
      }
    };



    // 设置消息反馈
    const setReaction = (type) => {
      // 如果已经选中了这个反馈，则取消选中
      if (reaction.value === type) {
        reaction.value = null;
      } else {
        reaction.value = type;
      }

      // 这里可以添加将反馈发送到服务器的逻辑
      // 例如：
      // store.dispatch('aiChat/sendMessageFeedback', {
      //   messageId: props.message.id,
      //   feedback: reaction.value
      // });
    };

    return {
      formattedContent,
      formatTime,
      showControls,
      showDeleteModal,
      isDeleting,
      copySuccess,
      reaction,
      confirmDeleteMessage,
      cancelDelete,
      deleteMessage,
      copyMessageContent,
      setReaction
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

.message-actions {
  display: flex;
  align-items: center;
  gap: 5px;
}

.message-time {
  font-size: 0.8rem;
  color: #888;
}

.copy-message-btn,
.delete-message-btn {
  padding: 4px;
  font-size: 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.9;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid;
}

.copy-message-btn {
  background: rgba(52, 152, 219, 0.1);
  border-color: rgba(52, 152, 219, 0.3);
  color: #3498db;
}

.copy-message-btn:hover {
  opacity: 1;
  background-color: rgba(52, 152, 219, 0.2);
  transform: scale(1.05);
  box-shadow: 0 2px 5px rgba(52, 152, 219, 0.2);
}

.delete-message-btn {
  background: rgba(231, 76, 60, 0.1);
  border-color: rgba(231, 76, 60, 0.3);
  color: #e74c3c;
}



.delete-message-btn:hover {
  opacity: 1;
  background-color: rgba(231, 76, 60, 0.2);
  transform: scale(1.05);
  box-shadow: 0 2px 5px rgba(231, 76, 60, 0.2);
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
}s

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



.message-reactions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  justify-content: flex-end;
}

.reaction-btn {
  background: transparent;
  border: 1px solid #e0e0e0;
  color: #888;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.reaction-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.reaction-btn.active.like {
  background-color: rgba(46, 204, 113, 0.2);
  border-color: rgba(46, 204, 113, 0.5);
  color: #27ae60;
}

.reaction-btn.active.dislike {
  background-color: rgba(231, 76, 60, 0.2);
  border-color: rgba(231, 76, 60, 0.5);
  color: #e74c3c;
}

/* 删除消息确认模态框 */
.delete-confirm-modal {
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

.delete-confirm-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 300px;
  text-align: center;
}

.delete-confirm-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
}

.delete-confirm-actions .cancel-btn {
  padding: 6px 12px;
  background-color: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
}

.delete-confirm-actions .confirm-btn {
  padding: 6px 12px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .user-message {
    margin-left: 0.5rem;
  }

  .ai-message {
    margin-right: 0.5rem;
  }

  .message-actions {
    flex-direction: column;
    gap: 3px;
  }

  .message-reactions {
    justify-content: flex-start;
  }

  .delete-confirm-content {
    width: 90%;
    max-width: 300px;
  }
}
/* 删除消息确认模态框 */
.delete-confirm-modal {
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

.delete-confirm-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 300px;
  text-align: center;
}

.delete-confirm-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
}

.delete-confirm-actions .cancel-btn {
  padding: 6px 12px;
  background-color: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
}

.delete-confirm-actions .confirm-btn {
  padding: 6px 12px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
