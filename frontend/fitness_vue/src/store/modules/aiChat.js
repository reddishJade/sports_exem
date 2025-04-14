import aiChatService from '@/services/aiChatService';

// 初始状态
const state = {
  conversations: [],
  currentConversation: null,
  messages: [],
  currentPage: 1,
  totalPages: 0,
  loading: false,
  loadingMore: false,  // 加载更多消息状态
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
  
  // 是否正在加载更多消息
  isLoadingMore: state => state.loadingMore,
  
  // 当前页码
  currentPage: state => state.currentPage,
  
  // 总页数
  totalPages: state => state.totalPages,
  
  // 是否有更多消息可加载
  hasMoreMessages: state => state.currentPage < state.totalPages,
  
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
  
  // 更新对话信息
  UPDATE_CONVERSATION(state, { id, data }) {
    // 更新对话列表中的对话
    state.conversations = state.conversations.map(conversation => {
      if (conversation.id === id) {
        return { ...conversation, ...data };
      }
      return conversation;
    });
    
    // 如果更新的是当前对话，也更新当前对话
    if (state.currentConversation && state.currentConversation.id === id) {
      state.currentConversation = { ...state.currentConversation, ...data };
    }
  },
  
  // 设置消息列表
  SET_MESSAGES(state, messages) {
    state.messages = messages || [];
    state.currentPage = 1;  // 重置当前页
  },
  
  // 添加更多消息到列表头部
  PREPEND_MESSAGES(state, messages) {
    if (!state.messages) {
      state.messages = [];
    }
    state.messages = [...(messages || []), ...state.messages];
  },
  
  // 添加消息到列表尾部
  ADD_MESSAGE(state, message) {
    // 确保messages数组存在
    if (!state.messages) {
      state.messages = [];
    }
    state.messages.push(message);
  },
  
  // 设置分页信息
  SET_PAGINATION(state, { currentPage, totalPages }) {
    state.currentPage = currentPage;
    state.totalPages = totalPages;
  },
  
  // 更新正在流式生成的消息内容
  UPDATE_STREAMING_MESSAGE(state, { id, content, message_id }) {
    if (!state.messages) {
      state.messages = [];
      return;
    }
    
    const messageIndex = state.messages.findIndex(msg => msg.id === id);
    if (messageIndex !== -1) {
      // 更新现有消息
      state.messages[messageIndex].content = content;
      if (message_id) {
        state.messages[messageIndex].server_id = message_id;
      }
    }
  },
  
  // 完成流式消息生成，将临时消息更新为正式消息
  FINALIZE_STREAMING_MESSAGE(state, { streamId, messageId, content, serviceType }) {
    if (!state.messages) {
      state.messages = [];
      return;
    }
    
    const messageIndex = state.messages.findIndex(msg => msg.id === streamId);
    if (messageIndex !== -1) {
      // 更新为正式消息，保持同一个消息实例，只更新必要的字段
      state.messages[messageIndex].id = messageId;
      state.messages[messageIndex].content = content;
      state.messages[messageIndex].streaming = false;
      state.messages[messageIndex].service_type = serviceType;
      state.messages[messageIndex].finalized = true;
    }
  },
  
  // 清除所有流式消息
  CLEAR_STREAMING_MESSAGES(state) {
    if (!state.messages) {
      state.messages = [];
      return;
    }
    
    state.messages = state.messages.filter(msg => !msg.streaming);
  },
  
  // 设置加载更多状态
  SET_LOADING_MORE(state, status) {
    state.loadingMore = status;
  },
  
  // 从列表中移除消息
  REMOVE_MESSAGE(state, messageId) {
    state.messages = state.messages.filter(message => message.id !== messageId);
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
  
  // 更新对话信息
  async updateConversation({ commit }, { id, ...data }) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      const response = await aiChatService.updateConversation(id, data);
      commit('UPDATE_CONVERSATION', { id, data });
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '更新对话失败');
      console.error('更新对话失败:', error);
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
      // 默认加载第一页，每页 20 条消息，最新的消息在前
      const response = await aiChatService.getMessages(conversationId, { page: 1, page_size: 20 });
      const { results, count, next, previous } = response.data;
      
      // 计算总页数 (每页 20 条)
      const totalPages = Math.ceil(count / 20);
      
      // 更新消息列表和分页信息
      commit('SET_MESSAGES', results);
      commit('SET_PAGINATION', { currentPage: 1, totalPages });
      
      return results;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '获取消息失败');
      console.error('获取消息失败:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // 加载更多历史消息
  async loadMoreMessages({ commit, state }, conversationId) {
    // 如果当前已经是最后一页或正在加载，则不再加载
    if (state.currentPage >= state.totalPages || state.loadingMore) {
      return;
    }
    
    commit('SET_LOADING_MORE', true);
    commit('CLEAR_ERROR');
    
    try {
      const nextPage = state.currentPage + 1;
      const response = await aiChatService.getMessages(conversationId, { page: nextPage, page_size: 20 });
      const { results, count, next, previous } = response.data;
      
      // 将返回的消息添加到当前消息列表的前面
      commit('PREPEND_MESSAGES', results);
      commit('SET_PAGINATION', { currentPage: nextPage, totalPages: Math.ceil(count / 20) });
      
      return results;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '加载更多消息失败');
      console.error('加载更多消息失败:', error);
      throw error;
    } finally {
      commit('SET_LOADING_MORE', false);
    }
  },
  
  // 发送消息并获取AI响应 - 使用流式生成展示形式
  async sendMessage({ commit, state }, { conversationId, message, serviceType = 'auto', useCase = 'general' }) {
    if (!conversationId || !message) {
      commit('SET_ERROR', '消息或对话ID不能为空');
      return;
    }
    
    commit('SET_SENDING_MESSAGE', true);
    commit('CLEAR_ERROR');
    
    try {
      // 添加用户消息到对话
      const userMessage = {
        id: 'temp-' + Date.now(),
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      commit('ADD_MESSAGE', userMessage);
      
      // 初始化AI的流式回复消息
      const initialAiMessage = {
        id: 'stream-' + Date.now(),
        role: 'assistant',
        content: '', // 初始空内容，会在流式生成过程中更新
        timestamp: new Date().toISOString(),
        streaming: true // 标记为正在流式生成
      };
      commit('ADD_MESSAGE', initialAiMessage);
      
      // 使用流式响应进行消息生成
      let fullContent = ''; // 最终累积的完整内容
      
      // 定义处理每个响应块的回调函数
      const handleChunk = (chunk, messageId) => {
        fullContent += chunk; // 逐步累积完整内容
        
        // 更新当前消息的内容
        commit('UPDATE_STREAMING_MESSAGE', {
          id: initialAiMessage.id,
          content: fullContent,
          message_id: messageId // 实际消息ID，来自服务器
        });
      };
      
      // 发送消息并开始流式生成
      const response = await aiChatService.sendMessageStream(
        conversationId,
        message,
        handleChunk,
        serviceType,
        useCase
      );
      
      // 生成完成，更新最终消息状态
      if (response && response.message_id) {
        commit('FINALIZE_STREAMING_MESSAGE', {
          streamId: initialAiMessage.id,
          messageId: response.message_id,
          content: fullContent,
          serviceType: serviceType
        });
      }
      
      return { message: fullContent, message_id: response.message_id };
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '发送消息失败');
      console.error('发送消息失败:', error);
      
      // 出错时清理可能存在的流式消息
      commit('CLEAR_STREAMING_MESSAGES');
      
      throw error;
    } finally {
      commit('SET_SENDING_MESSAGE', false);
    }
  },
  
  // 清除当前对话
  clearCurrentConversation({ commit }) {
    commit('SET_CURRENT_CONVERSATION', null);
    commit('SET_MESSAGES', []);
  },
  
  // 清空当前对话的消息历史
  async clearConversationMessages({ commit, state }, conversationId) {
    if (!conversationId || !state.currentConversation) {
      commit('SET_ERROR', '没有选择对话');
      return;
    }
    
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      await aiChatService.clearMessages(conversationId);
      commit('SET_MESSAGES', []);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '清空消息失败');
      console.error('清空消息失败:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // 删除单条消息
  async deleteMessage({ commit, state }, { conversationId, messageId }) {
    if (!conversationId || !state.currentConversation) {
      commit('SET_ERROR', '没有选择对话');
      return;
    }
    
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    try {
      await aiChatService.deleteMessage(conversationId, messageId);
      commit('REMOVE_MESSAGE', messageId);
      return true;
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.error || '删除消息失败');
      console.error('删除消息失败:', error);
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
