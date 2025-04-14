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
   * 获取对话的消息
   * @param {Number} conversationId 对话ID
   * @param {Object} params 分页参数，包括 page 和 page_size
   * @returns {Promise} 包含消息列表的Promise
   */
  getMessages(conversationId, params = { page: 1, page_size: 20 }) {
    return api.get(`/ai/conversations/${conversationId}/messages/`, { params });
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
  },
  
  /**
   * 发送消息到AI并获取流式响应 - 支持查看生成过程
   * @param {Number} conversationId 对话ID
   * @param {String} message 用户消息内容
   * @param {Function} onChunk 处理每个响应块的回调函数
   * @param {String} serviceType AI服务类型
   * @param {String} useCase 使用场景
   * @returns {Promise} 包含完整AI响应的Promise
   */
  sendMessageStream(conversationId, message, onChunk, serviceType = 'auto', useCase = 'general') {
    return new Promise((resolve, reject) => {
      // 创建请求对象
      const xhr = new XMLHttpRequest();
      xhr.open('POST', `${api.defaults.baseURL}/ai/conversations/${conversationId}/send_message_stream/`);
      
      // 设置请求头
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.setRequestHeader('Authorization', `Bearer ${localStorage.getItem('token')}`);
      
      // 设置为流式响应
      xhr.responseType = 'text';
      
      // 处理正在传输的数据
      let receivedText = '';
      let messageId = null;
      
      xhr.onprogress = function() {
        // 获取新接收的文本部分
        const newText = xhr.responseText.substring(receivedText.length);
        receivedText = xhr.responseText;
        
        try {
          // 尝试解析为JSON - 有可能收到部分数据
          const lines = newText.split('\n');
          
          for (const line of lines) {
            if (!line.trim()) continue;
            
            try {
              const chunk = JSON.parse(line);
              
              // 获取消息ID（仅第一个块）
              if (chunk.message_id && !messageId) {
                messageId = chunk.message_id;
              }
              
              // 调用回调处理块
              if (chunk.chunk) {
                onChunk(chunk.chunk, messageId);
              }
            } catch (e) {
              console.warn('解析流式响应块失败:', e, line);
            }
          }
        } catch (e) {
          console.error('处理流式响应失败:', e);
        }
      };
      
      xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
          // 成功完成，返回最后的完整响应
          resolve({
            status: 'success',
            message_id: messageId,
            completed: true
          });
        } else {
          reject(new Error(`请求失败 ${xhr.status}: ${xhr.statusText}`));
        }
      };
      
      xhr.onerror = function() {
        reject(new Error('网络请求失败'));
      };
      
      // 发送请求
      xhr.send(JSON.stringify({
        message,
        service_type: serviceType,
        use_case: useCase
      }));
    });
  },
  
  /**
   * 更新对话信息
   * @param {Number} id 对话ID
   * @param {Object} data 要更新的数据（如标题）
   * @returns {Promise}
   */
  updateConversation(id, data) {
    return api.patch(`/ai/conversations/${id}/`, data);
  },
  
  /**
   * 清空对话历史记录
   * @param {Number} conversationId 对话ID
   * @returns {Promise}
   */
  clearMessages(conversationId) {
    return api.post(`/ai/conversations/${conversationId}/clear_messages/`);
  },
  
  /**
   * 删除单条消息
   * @param {Number} conversationId 对话ID
   * @param {Number} messageId 消息ID
   * @returns {Promise}
   */
  deleteMessage(conversationId, messageId) {
    return api.delete(`/ai/conversations/${conversationId}/messages/${messageId}/`);
  }
};

export default aiChatService;
