import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .services import get_ai_service
from .models import Conversation, Message
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """实时AI聊天的WebSocket消费者"""
    
    async def connect(self):
        """处理连接 - 加入对话组"""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # 接受连接
        await self.accept()
        
        # 发送连接建立消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'已连接到对话 {self.conversation_id}'
        }))

    async def disconnect(self, close_code):
        """处理断开连接 - 离开对话组"""
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """从WebSocket接收消息并使用AI响应"""
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            # 获取AI服务类型和使用场景
            service_type = data.get('service_type', 'auto')
            use_case = data.get('use_case', 'general')
            
            if not message.strip():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': '消息不能为空'
                }))
                return
                
            # 告知用户我们正在处理
            await self.send(text_data=json.dumps({
                'type': 'status',
                'status': 'processing',
                'message': 'AI思考中...'
            }))
            
            # 保存用户消息
            user_message = await self.save_message('user', message)
            
            # 广播用户消息到组
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'role': 'user',
                    'message_id': user_message.id,
                    'timestamp': user_message.timestamp.isoformat()
                }
            )
            
            # 获取对话历史
            formatted_messages = await self.get_conversation_history()
            
            # 获取AI服务和响应
            ai_service = await sync_to_async(get_ai_service)(service_type=service_type, use_case=use_case)
            response = await sync_to_async(ai_service.get_response)(formatted_messages, use_case=use_case)
            
            # 根据服务类型提取AI响应
            if service_type == 'ollama':
                ai_message = response.get('message', {}).get('content', '')
            else:  # DeepSeek使用类似OpenAI的响应格式
                ai_message = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if not ai_message:
                raise ValueError("无法从AI响应中提取消息内容")
            
            # 保存AI响应
            ai_response = await self.save_message('assistant', ai_message)
            
            # 广播AI消息到组
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': ai_message,
                    'role': 'assistant',
                    'message_id': ai_response.id,
                    'timestamp': ai_response.timestamp.isoformat(),
                    'service_type': service_type
                }
            )
            
        except Exception as e:
            logger.error(f"ChatConsumer.receive中出错: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'错误: {str(e)}'
            }))

    async def chat_message(self, event):
        """向WebSocket发送消息"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'role': event['role'],
            'message_id': event.get('message_id'),
            'timestamp': event.get('timestamp'),
            'service_type': event.get('service_type', 'auto')
        }))
    
    @database_sync_to_async
    def save_message(self, role, content):
        """将消息保存到数据库"""
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            role=role,
            content=content
        )
        # 更新对话的updated_at时间戳
        conversation.save()
        return message
    
    @database_sync_to_async
    def get_conversation_history(self):
        """获取AI上下文的对话历史"""
        conversation = Conversation.objects.get(id=self.conversation_id)
        # 限制为最后20条消息，避免上下文问题
        messages = Message.objects.filter(conversation=conversation).order_by('timestamp')[:20]
        return [{"role": msg.role, "content": msg.content} for msg in messages]
