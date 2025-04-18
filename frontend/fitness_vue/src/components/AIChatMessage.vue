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
              class="action-btn copy-message-btn"
              @click="copyMessageContent"
              title="复制消息"
            >
              <i :class="[copySuccess ? 'fas fa-check' : 'fas fa-copy']"></i>
            </button>
            <button
              v-if="message.id"
              class="action-btn delete-message-btn"
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
        <div class="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
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
        <div class="delete-modal-header">
          <i class="fas fa-exclamation-triangle warning-icon"></i>
          <h3>删除确认</h3>
        </div>
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
  margin-bottom: 1.5rem;
  padding: 1rem;
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message-container:hover {
  background-color: rgba(0, 0, 0, 0.03);
  transform: translateY(-1px);
}

.user-message {
  margin-left: 2rem;
  border-left: 3px solid #4d7cfe;
}

.ai-message {
  margin-right: 2rem;
  background-color: rgba(16, 163, 127, 0.05);
  border-left: 3px solid #10a37f;
}

.message-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.message-avatar:hover {
  transform: scale(1.05);
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #4d7cfe, #5a8eff);
  color: white;
}

.ai-message .message-avatar {
  background: linear-gradient(135deg, #10a37f, #12b48a);
  color: white;
}

.message-avatar i {
  font-size: 1.2rem;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  align-items: center;
}

.message-sender {
  font-weight: 600;
  font-size: 1rem;
  letter-spacing: 0.5px;
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
  gap: 10px;
}

.message-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-time {
  font-size: 0.8rem;
  color: #888;
  background-color: rgba(0, 0, 0, 0.03);
  padding: 2px 8px;
  border-radius: 12px;
}

.action-btn {
  padding: 6px;
  font-size: 0.85rem;
  border-radius: 6px;
  cursor: pointer;
  opacity: 0.9;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
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
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(52, 152, 219, 0.2);
}

.delete-message-btn {
  background: rgba(231, 76, 60, 0.1);
  border-color: rgba(231, 76, 60, 0.3);
  color: #e74c3c;
}

.delete-message-btn:hover {
  opacity: 1;
  background-color: rgba(231, 76, 60, 0.2);
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(231, 76, 60, 0.2);
}

.message-deleting {
  font-style: italic;
  color: #888;
  padding: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-dots {
  display: flex;
  align-items: center;
  gap: 3px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background-color: #888;
  border-radius: 50%;
  display: inline-block;
  animation: loadingDots 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loadingDots {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}

.message-text {
  white-space: pre-wrap;
  line-height: 1.6;
  overflow-wrap: break-word;
  font-size: 1rem;
  color: #333;
}

/* 为Markdown内容添加样式 */
.message-text :deep(p) {
  margin: 0.8rem 0;
}

.message-text :deep(pre) {
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e8eaed;
  overflow-x: auto;
  margin: 1rem 0;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.05);
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
  padding-left: 1.8rem;
  margin: 1rem 0;
}

.message-text :deep(li) {
  margin-bottom: 0.5rem;
}

.message-text :deep(blockquote) {
  margin: 1rem 0;
  padding: 0.8rem 1rem;
  border-left: 4px solid #10a37f;
  background-color: rgba(16, 163, 127, 0.05);
  color: #494949;
  border-radius: 0 6px 6px 0;
}

.message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.message-text :deep(th), .message-text :deep(td) {
  border: 1px solid #e8eaed;
  padding: 10px 16px;
}

.message-text :deep(th) {
  background-color: #f8f9fa;
  font-weight: 600;
}

.message-text :deep(tr:nth-child(even)) {
  background-color: #f8f9fa;
}

/* 打字动画效果 */
.typing-cursor {
  display: inline-block;
  width: 3px;
  height: 18px;
  background-color: #10a37f;
  margin-left: 4px;
  animation: cursor-blink 1s infinite;
  vertical-align: middle;
  border-radius: 1px;
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
  gap: 10px;
  margin-top: 12px;
  justify-content: flex-end;
}

.reaction-btn {
  background: transparent;
  border: 1px solid #e0e0e0;
  color: #888;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reaction-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  transform: translateY(-3px);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
}

.reaction-btn.active.like {
  background-color: rgba(46, 204, 113, 0.2);
  border-color: rgba(46, 204, 113, 0.5);
  color: #27ae60;
  box-shadow: 0 3px 8px rgba(46, 204, 113, 0.3);
}

.reaction-btn.active.dislike {
  background-color: rgba(231, 76, 60, 0.2);
  border-color: rgba(231, 76, 60, 0.5);
  color: #e74c3c;
  box-shadow: 0 3px 8px rgba(231, 76, 60, 0.3);
}

/* 删除消息确认模态框 */
.delete-confirm-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
  backdrop-filter: blur(3px);
}

.delete-confirm-content {
  background-color: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  width: 360px;
  text-align: center;
  animation: modalEnter 0.4s ease;
}

.delete-modal-header {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.warning-icon {
  font-size: 2rem;
  color: #e74c3c;
}

.delete-modal-header h3 {
  margin: 0;
  color: #333;
  font-weight: 600;
}

.delete-confirm-content p {
  margin: 0 0 20px 0;
  font-size: 1rem;
  color: #666;
}

.delete-confirm-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.cancel-btn, .confirm-btn {
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  min-width: 100px;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
}

.cancel-btn:hover {
  background-color: #e5e5e5;
  transform: translateY(-2px);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
}

.confirm-btn {
  background-color: #e74c3c;
  color: white;
}

.confirm-btn:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
  box-shadow: 0 3px 6px rgba(231, 76, 60, 0.3);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalEnter {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .user-message {
    margin-left: 0.5rem;
  }

  .ai-message {
    margin-right: 0.5rem;
  }

  .message-container {
    padding: 0.8rem;
  }

  .message-actions {
    flex-direction: row;
    gap: 6px;
  }

  .action-btn {
    width: 28px;
    height: 28px;
    font-size: 0.8rem;
  }

  .message-reactions {
    justify-content: flex-end;
  }

  .delete-confirm-content {
    width: 90%;
    max-width: 320px;
    padding: 20px;
  }
}
</style>