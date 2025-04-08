from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services import get_ai_service, MemoryService
# Create your views here.

class ConversationViewSet(viewsets.ModelViewSet):
    """对话管理API接口"""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """只返回当前用户的对话记录，按更新时间降序排序"""
        return Conversation.objects.filter(user=self.request.user).order_by('-updated_at')
    
    def perform_create(self, serializer):
        """创建新对话时设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """发送消息给AI并获取响应
        
        参数:
            request: 包含消息内容的请求对象
            pk: 对话ID
            
        查询参数:
            service_type: AI服务类型 (openai, deepseek, ollama, auto)
            use_case: 使用场景 (coding, data, general, translation, creative)
        """
        conversation = self.get_object()
        user_message = request.data.get('message', '')
        
        # 验证消息不为空
        if not user_message.strip():
            return Response(
                {'error': '消息不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 保存用户消息
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # 更新对话时间戳
        conversation.save()  # 这将更新updated_at字段
        
        # 获取用户类型，用于个性化响应
        user_type = request.user.user_type if hasattr(request.user, 'user_type') else 'unknown'
        
        # 构建系统提示词，根据用户类型定制
        system_prompt = self._get_system_prompt_for_user_type(user_type, request.user)
        
        # 将对话记忆添加到系统提示中（如果启用记忆功能）
        if conversation.use_memory and conversation.memory_summary:
            system_prompt += f"\n\n用户的历史记忆摘要：\n{conversation.memory_summary}"
            
        system_message = {
            "role": "system", 
            "content": system_prompt
        }
        
        # 获取对话历史（最后10条消息，避免上下文过长）
        messages = Message.objects.filter(conversation=conversation).order_by('timestamp')[:10]
        
        # 格式化消息用于AI服务
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        # 将系统提示词添加到消息列表的开头
        formatted_messages.insert(0, system_message)
        
        # 从请求中获取服务类型和使用场景
        service_type = request.data.get('service_type', 'auto')
        use_case = request.data.get('use_case', 'general')
        
        try:
            # 根据配置获取AI服务
            ai_service = get_ai_service(service_type=service_type, use_case=use_case)
            
            # 获取AI响应
            response = ai_service.get_response(formatted_messages, use_case=use_case if hasattr(ai_service, 'use_case_temperatures') else None)
            
            # 根据服务类型提取AI响应内容
            if service_type == 'ollama':
                ai_message = response.get('message', {}).get('content', '')
            else:  # OpenAI和DeepSeek使用相同的响应格式
                ai_message = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if not ai_message:
                raise ValueError("无法从AI响应中提取消息内容")
            
            # 保存AI响应
            ai_response = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=ai_message
            )
            
            # 检查是否需要更新对话记忆
            # 获取当前对话的总消息数
            message_count = Message.objects.filter(conversation=conversation).count()
            
            # 初始化记忆服务
            memory_service = MemoryService()
            
            # 当消息数达到阈值时，更新记忆
            if conversation.use_memory and memory_service.should_generate_memory(message_count):
                # 获取所有消息进行记忆生成
                all_messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
                
                # 生成或更新记忆摘要
                new_memory = memory_service.generate_memory(
                    all_messages, 
                    previous_memory=conversation.memory_summary
                )
                
                # 更新对话的记忆摘要
                if new_memory:
                    conversation.update_memory_summary(new_memory)
            
            # 返回响应
            return Response({
                'message': ai_message,
                'message_id': ai_response.id,
                'timestamp': ai_response.timestamp,
                'service_type': service_type
            })
            
        except Exception as e:
            import traceback
            print(f"发送消息时出错: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_system_prompt_for_user_type(self, user_type, user):
        """根据用户类型生成系统提示词
        
        参数:
            user_type: 用户类型 ('student', 'parent', 'admin', 'unknown')
            user: 用户对象
            
        返回:
            适合用户类型的系统提示词
        """
        base_prompt = "你是一位专业的体育健身AI助手，为健身运动提供专业指导和建议。"
        
        if user_type == 'student':
            # 尝试获取学生资料
            try:
                student_profile = user.student_profile
                prompt = f"{base_prompt}你正在与一名学生交流，请提供适合学生的健身和体测指导。"
                
                # 如果有身高体重数据，可以计算BMI并添加到提示中
                if hasattr(student_profile, 'height') and hasattr(student_profile, 'weight'):
                    if student_profile.height and student_profile.weight:
                        height_m = student_profile.height / 100  # 转换为米
                        bmi = student_profile.weight / (height_m * height_m)
                        prompt += f" 该学生的BMI约为{bmi:.1f}。"
                
                return prompt
            except:
                return f"{base_prompt}你正在与一名学生交流，请提供适合学生的健身和体测指导。"
                
        elif user_type == 'parent':
            return f"{base_prompt}你正在与一位家长交流，请提供适合指导孩子体育锻炼的建议，并考虑如何帮助家长更好地关注孩子的身体健康发展。"
            
        elif user_type == 'admin':
            return f"{base_prompt}你正在与一位管理员交流，请提供关于体育教育、健身项目管理和学生体测数据分析的专业建议。"
            
        else:
            return f"{base_prompt}请提供关于健身、营养和体育锻炼的专业建议。"
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取对话的所有消息"""
        conversation = self.get_object()
        messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
