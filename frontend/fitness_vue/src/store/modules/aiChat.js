import aiChatService from '@/services/aiChatService';

// 初始状态
const state = {
  conversations: [],
  currentConversation: null,
  messages: [],
  loading: false,
  sendingMessage: false,
  error: null
};

// getter方法
const getters = {
  // 获取所有对话
  allConversations: state => state.conversations,
  
  // 获取当前对话
  currentConversation: state => state.currentConversation,
  
  // 获取当前对话的消息
  messages: state => state.messages,
  
  // 是否正在加载对话
  isLoading: state => state.loading,
  
  // 是否正在发送消息
  isSendingMessage: state => state.sendingMessage,
  
  // 获取错误信息
  error: state => state.error
};

// 修改状态的mutation方法
const mutations = {
  // 设置对话列表
  SET_CONVERSATIONS(state, conversations) {
    state.conversations = conversations;
  },
  
  // 设置当前对话
  SET_CURRENT_CONVERSATION(state, conversation) {
    state.currentConversation = conversation;
  },
  
  // 添加新对话到列表
  ADD_CONVERSATION(state, conversation) {
    state.conversations.unshift(conversation); // 添加到列表最前面
  },
  
  // 从列表中移除对话
  REMOVE_CONVERSATION(state, conversationId) {
    state.conversations = state.conversations.filter(c => c.id !== conversationId);
    if (state.currentConversation && state.currentConversation.id === conversationId) {
      state.currentConversation = null;
      state.messages = [];
    }
  },
  
  // 设置消息列表
  SET_MESSAGES(state, messages) {
    state.messages = messages;
  },
  
  // 添加消息到列表
  ADD_MESSAGE(state, message) {
    state.messages.push(message);
  },
  
  // 设置加载状态
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  
  // 设置发送消息状态
  SET_SENDING_MESSAGE(state, status) {
    state.sendingMessage = status;
  },
  
  // 设置错误信息
  SET_ERROR(state, error) {
    state.error = error;
  },
  
  // 清除错误信息
  CLEAR_ERROR(state) {
    state.error = null;
  }
};

// 异步actions
const actions = {
  // 获取所有对话
  async fetchConversations({ commit }) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await aiChatService.getConversations();
      commit('SET_CONVERSATIONS', response.data);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '获取对话失败');
      console.error('获取对话失败:', error);
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // 创建新对话
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
  
  // 获取特定对话
  async fetchConversation({ commit }, conversationId) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await aiChatService.getConversation(conversationId);
      commit('SET_CURRENT_CONVERSATION', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '获取对话详情失败');
      console.error('获取对话详情失败:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // 删除对话
  async deleteConversation({ commit }, conversationId) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      await aiChatService.deleteConversation(conversationId);
      commit('REMOVE_CONVERSATION', conversationId);
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '删除对话失败');
      console.error('删除对话失败:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // 获取对话消息
  async fetchMessages({ commit }, conversationId) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await aiChatService.getMessages(conversationId);
      commit('SET_MESSAGES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '获取消息失败');
      console.error('获取消息失败:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // 发送消息
  async sendMessage({ commit, state }, { conversationId, message, serviceType = 'auto', useCase = 'general' }) {
    if (!conversationId || !state.currentConversation) {
      commit('SET_ERROR', '没有选择对话');
      return;
    }
    
    commit('SET_SENDING_MESSAGE', true);
    commit('CLEAR_ERROR');
    
    try {
      // 先添加用户消息到本地（乐观更新）
      const userMessage = {
        id: 'temp-' + Date.now(),
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      commit('ADD_MESSAGE', userMessage);
      
      // 发送消息到服务器
      const response = await aiChatService.sendMessage(
        conversationId, 
        message, 
        serviceType,
        useCase
      );
      
      // 添加AI响应到消息列表
      if (response.data && response.data.message) {
        const aiMessage = {
          id: response.data.message_id,
          role: 'assistant',
          content: response.data.message,
          timestamp: response.data.timestamp,
          service_type: response.data.service_type
        };
        commit('ADD_MESSAGE', aiMessage);
      }
      
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '发送消息失败');
      console.error('发送消息失败:', error);
      throw error;
    } finally {
      commit('SET_SENDING_MESSAGE', false);
    }
  },
  
  // 清除当前对话
  clearCurrentConversation({ commit }) {
    commit('SET_CURRENT_CONVERSATION', null);
    commit('SET_MESSAGES', []);
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
