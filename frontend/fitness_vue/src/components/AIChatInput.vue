<template>
  <div class="chat-input-container">
    <div class="model-selector">
      <select v-model="selectedModel" class="model-select">
        <option value="auto">DeepSeek (自动)</option>
        <option value="deepseek">DeepSeek (指定)</option>
        <option value="ollama">Ollama (本地)</option>
      </select>
    </div>
    <textarea
      v-model="messageText"
      class="message-input"
      placeholder="在此输入消息..."
      :disabled="disabled"
      @keydown.enter.exact.prevent="sendMessage"
      @keydown.enter.shift.exact="newLine"
    ></textarea>
    <div class="actions">
      <div class="hints">
        <small>按 Enter 发送. Shift+Enter 换行.</small>
      </div>
      <div class="controls">
        <button
          @click="clearMessage"
          class="clear-btn"
          :disabled="disabled || !messageText"
          title="清空输入框">
          <i class="fas fa-eraser"></i> 清空
        </button>
        <button
          @click="sendMessage"
          class="send-btn"
          :disabled="disabled || !messageText.trim()">
          <i class="fas fa-paper-plane"></i> 发送
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'AIChatInput',

  props: {
    // 是否禁用输入
    disabled: {
      type: Boolean,
      default: false
    }
  },

  emits: ['send-message'],

  setup(props, { emit }) {
    // 消息文本
    const messageText = ref('');
    // 选中的模型
    const selectedModel = ref('auto');

    // 发送消息
    const sendMessage = () => {
      if (props.disabled || !messageText.value.trim()) return;

      emit('send-message', {
        message: messageText.value,
        serviceType: selectedModel.value
      });

      // 清空输入
      messageText.value = '';
    };

    // 清空消息
    const clearMessage = () => {
      messageText.value = '';
    };

    // 在按下Shift+Enter时添加换行
    const newLine = (e) => {
      messageText.value += '\n';
    };

    // 设置消息文本 - 用于提示词建议
    const setMessage = (text) => {
      messageText.value = text;

      // 自动聚焦输入框
      setTimeout(() => {
        const textarea = document.querySelector('.message-input');
        if (textarea) {
          textarea.focus();
        }
      }, 100);
    };

    return {
      messageText,
      selectedModel,
      sendMessage,
      clearMessage,
      newLine,
      setMessage
    };
  }
};
</script>

<style scoped>
.chat-input-container {
  border-top: 1px solid #efefef;
  padding: 1rem;
  background-color: #fff;
}

.message-input {
  width: 100%;
  min-height: 60px;
  max-height: 200px;
  padding: 0.8rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  resize: vertical;
  font-family: inherit;
  font-size: 1rem;
  background-color: #f9fafb;
  color: #333;
  transition: border-color 0.2s, box-shadow 0.2s;
  margin-bottom: 0.8rem;
}

.message-input:focus {
  outline: none;
  border-color: #10a37f;
  box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
}

.message-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.7;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hints {
  font-size: 0.8rem;
  color: #888;
}

.controls {
  display: flex;
  gap: 10px;
}

.clear-btn, .send-btn {
  border-radius: 8px;
  padding: 0.6rem 1rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 90px;
  justify-content: center;
}

.clear-btn {
  background-color: #f5f5f5;
  color: #666;
  border: 1px solid #e0e0e0;
}

.clear-btn:hover:not(:disabled) {
  background-color: #e5e5e5;
  border-color: #d0d0d0;
}

.send-btn {
  background-color: #10a37f;
  color: white;
  border: 1px solid #10a37f;
}

.send-btn:hover:not(:disabled) {
  background-color: #0d8c6c;
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(16, 163, 127, 0.15);
  border-color: #0d8c6c;
}

.send-btn:active:not(:disabled) {
  transform: translateY(0);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.model-selector {
  margin-bottom: 0.8rem;
}

.model-select {
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  background-color: #f9fafb;
  color: #333;
  font-size: 0.9rem;
  width: 180px;
  cursor: pointer;
}

.model-select:focus {
  outline: none;
  border-color: #10a37f;
}

@media (max-width: 768px) {
  .actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .hints {
    margin-bottom: 8px;
  }

  .controls {
    width: 100%;
  }

  .send-btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
