import api from './api';

/**
 * AI聊天服务 - 处理与AI聊天相关的API请求
 */
const aiChatService = {
  /**
   * 获取用户的所有对话
   * @returns {Promise} 包含对话列表的Promise
   */
  getConversations() {
    return api.get('/ai/conversations/');
  },
  
  /**
   * 创建新的对话
   * @param {Object} data 对话数据，如标题
   * @returns {Promise} 包含新创建对话的Promise
   */
  createConversation(data) {
    return api.post('/ai/conversations/', data);
  },
  
  /**
   * 获取特定对话
   * @param {Number} id 对话ID
   * @returns {Promise} 包含对话详情的Promise
   */
  getConversation(id) {
    return api.get(`/ai/conversations/${id}/`);
  },
  
  /**
   * 删除对话
   * @param {Number} id 对话ID
   * @returns {Promise}
   */
  deleteConversation(id) {
    return api.delete(`/ai/conversations/${id}/`);
  },
  
  /**
   * 获取对话的所有消息
   * @param {Number} conversationId 对话ID
   * @returns {Promise} 包含消息列表的Promise
   */
  getMessages(conversationId) {
    return api.get(`/ai/conversations/${conversationId}/messages/`);
  },
  
  /**
   * 发送消息到AI并获取响应
   * @param {Number} conversationId 对话ID
   * @param {String} message 用户消息内容
   * @param {String} serviceType AI服务类型，'deepseek'或'ollama'
   * @param {String} useCase 使用场景，用于DeepSeek
   * @returns {Promise} 包含AI响应的Promise
   */
  sendMessage(conversationId, message, serviceType = 'auto', useCase = 'general') {
    return api.post(`/ai/conversations/${conversationId}/send_message/`, {
      message,
      service_type: serviceType,
      use_case: useCase
    });
  }
};

export default aiChatService;
