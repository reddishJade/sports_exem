<template>
  <div class="conversation-list">
    <div class="conversation-list-header">
      <h3>会话列表</h3>
      <button @click="createNewConversation" class="new-conversation-btn" :disabled="loading">
        <i class="fas fa-plus"></i> 新对话
      </button>
    </div>
    
    <div v-if="loading" class="loading-container">
      <i class="fas fa-spinner fa-spin"></i> 加载中...
    </div>
    
    <div v-else-if="conversations.length === 0" class="empty-state">
      <i class="fas fa-comment-dots empty-icon"></i>
      <p>没有会话</p>
      <p>点击 "新对话" 开始聊天</p>
    </div>
    
    <ul v-else class="conversations">
      <li 
        v-for="conversation in conversations" 
        :key="conversation.id"
        :class="{ 'active': currentConversationId === conversation.id }"
        @click="selectConversation(conversation)">
        <div class="conversation-item">
          <div class="conversation-info">
            <span class="conversation-title">{{ conversation.title }}</span>
            <small class="timestamp">{{ formatDate(conversation.updated_at) }}</small>
          </div>
          <div class="conversation-actions">
            <button 
              @click.stop="editTitle(conversation)" 
              class="edit-btn"
              title="编辑标题">
              <i class="fas fa-edit"></i>
            </button>
            <button 
              @click.stop="confirmDelete(conversation)" 
              class="delete-btn"
              title="删除对话">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </li>
    </ul>
    
    <!-- 确认删除对话的模态框 -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content">
        <h4>确认删除</h4>
        <p>您确定要删除对话 "{{ conversationToDelete?.title }}" 吗？</p>
        <p>此操作不可撤销。</p>
        <div class="modal-actions">
          <button @click="cancelDelete" class="cancel-btn">取消</button>
          <button @click="deleteSelectedConversation" class="confirm-btn">删除</button>
        </div>
      </div>
    </div>
    
    <!-- 编辑标题的模态框 -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-content">
        <h4>编辑对话标题</h4>
        <input 
          v-model="editTitleText" 
          class="title-input" 
          placeholder="输入对话标题" 
          @keydown.enter="saveTitle"
        />
        <div class="modal-actions">
          <button @click="cancelEdit" class="cancel-btn">取消</button>
          <button 
            @click="saveTitle" 
            class="save-btn" 
            :disabled="!editTitleText.trim()"
          >保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'AIConversationList',
  
  props: {
    // 当前选中的对话ID
    currentConversationId: {
      type: [Number, String],
      default: null
    }
  },
  
  emits: ['select-conversation'],
  
  setup(props, { emit }) {
    const store = useStore();
    
    // 从vuex获取对话列表
    const conversations = computed(() => store.getters['aiChat/allConversations']);
    
    // 加载状态
    const loading = computed(() => store.getters['aiChat/isLoading']);
    
    // 删除相关状态
    const showDeleteModal = ref(false);
    const conversationToDelete = ref(null);
    
    // 编辑标题相关状态
    const showEditModal = ref(false);
    const conversationToEdit = ref(null);
    const editTitleText = ref('');
    
    // 选择对话
    const selectConversation = (conversation) => {
      emit('select-conversation', conversation);
    };
    
    // 创建新对话
    const createNewConversation = async () => {
      try {
        const newConversation = await store.dispatch('aiChat/createConversation');
        emit('select-conversation', newConversation);
      } catch (error) {
        console.error('创建新对话失败:', error);
      }
    };
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffMinutes < 60) {
        return `${diffMinutes} 分钟前`;
      } else if (diffHours < 24) {
        return `${diffHours} 小时前`;
      } else if (diffDays < 7) {
        return `${diffDays} 天前`;
      } else {
        return date.toLocaleDateString('zh-CN');
      }
    };
    
    // 确认删除对话
    const confirmDelete = (conversation) => {
      conversationToDelete.value = conversation;
      showDeleteModal.value = true;
    };
    
    // 取消删除
    const cancelDelete = () => {
      showDeleteModal.value = false;
      conversationToDelete.value = null;
    };
    
    // 删除选中的对话
    const deleteSelectedConversation = async () => {
      if (!conversationToDelete.value) return;
      
      try {
        await store.dispatch('aiChat/deleteConversation', conversationToDelete.value.id);
        showDeleteModal.value = false;
        conversationToDelete.value = null;
        
        // 如果刚删除的对话是当前选中的，清除当前对话
        if (conversationToDelete.value?.id === props.currentConversationId) {
          store.dispatch('aiChat/clearCurrentConversation');
          emit('select-conversation', null);
        }
      } catch (error) {
        console.error('删除对话失败:', error);
      }
    };
    
    // 编辑对话标题
    const editTitle = (conversation) => {
      conversationToEdit.value = conversation;
      editTitleText.value = conversation.title;
      showEditModal.value = true;
    };
    
    // 取消编辑
    const cancelEdit = () => {
      showEditModal.value = false;
      conversationToEdit.value = null;
      editTitleText.value = '';
    };
    
    // 保存标题
    const saveTitle = async () => {
      if (!editTitleText.value.trim()) return;
      
      try {
        await store.dispatch('aiChat/updateConversation', {
          id: conversationToEdit.value.id,
          title: editTitleText.value.trim()
        });
        
        showEditModal.value = false;
        conversationToEdit.value = null;
        editTitleText.value = '';
      } catch (error) {
        console.error('更新对话标题失败:', error);
      }
    };
    
    return {
      conversations,
      loading,
      showDeleteModal,
      conversationToDelete,
      showEditModal,
      conversationToEdit,
      editTitleText,
      selectConversation,
      createNewConversation,
      formatDate,
      confirmDelete,
      cancelDelete,
      deleteSelectedConversation,
      editTitle,
      cancelEdit,
      saveTitle
    };
  }
};
</script>

<style scoped>
.conversation-list {
  width: 280px;
  background-color: #f6f8fa;
  border-right: 1px solid #efefef;
  display: flex;
  flex-direction: column;
  border-radius: 12px 0 0 12px;
  overflow: hidden;
}

.conversation-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem;
  border-bottom: 1px solid #efefef;
  background-color: #fff;
}

.conversation-list-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #2c3e50;
  font-weight: 600;
}

.new-conversation-btn {
  background-color: #10a37f;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 0.8rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.new-conversation-btn:hover:not(:disabled) {
  background-color: #0d8c6c;
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(16, 163, 127, 0.15);
}

.new-conversation-btn:active:not(:disabled) {
  transform: translateY(0);
}

.new-conversation-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  color: #888;
  height: 100px;
}

.empty-state {
  padding: 3rem 1.5rem;
  text-align: center;
  color: #666;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #ccc;
}

.conversations {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex: 1;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #efefef;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.2s;
}

.conversations li:hover .conversation-item {
  background-color: #edf2f7;
}

.conversations li.active .conversation-item {
  background-color: #e6f7f3;
  border-left: 3px solid #10a37f;
}

.conversation-info {
  flex: 1;
  overflow: hidden;
}

.conversation-title {
  font-weight: 500;
  color: #333;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

.timestamp {
  font-size: 0.75rem;
  color: #888;
  display: block;
  margin-top: 4px;
}

.conversation-actions {
  display: flex;
  gap: 6px;
}

.edit-btn, .delete-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  opacity: 0.6;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.edit-btn {
  color: #10a37f;
}

.edit-btn:hover {
  color: #0d8c6c;
  background-color: rgba(16, 163, 127, 0.1);
  opacity: 1;
}

.delete-btn {
  color: #888;
}

.delete-btn:hover {
  color: #e74c3c;
  background-color: rgba(231, 76, 60, 0.1);
  opacity: 1;
}

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
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  animation: modalFadeIn 0.3s;
}

@keyframes modalFadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-content h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 1.5rem;
}

.cancel-btn, .confirm-btn {
  padding: 0.6rem 1rem;
  border-radius: 6px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.confirm-btn {
  background-color: #e74c3c;
  color: white;
}

.confirm-btn:hover {
  background-color: #c0392b;
}

.save-btn {
  background-color: #10a37f;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background-color: #0d8c6c;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.title-input {
  width: 100%;
  padding: 0.8rem;
  margin: 1rem 0;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.title-input:focus {
  border-color: #10a37f;
  box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
}

@media (max-width: 768px) {
  .conversation-list {
    width: 100%;
    border-radius: 12px 12px 0 0;
    border-right: none;
    border-bottom: 1px solid #efefef;
  }
  
  .conversation-list-header {
    padding: 1rem;
  }
  
  .conversations {
    max-height: 200px;
  }
}
</style>
