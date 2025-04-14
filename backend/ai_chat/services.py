import requests
import json
import os
from django.conf import settings

class AIModelService:
    """AI模型服务的基类"""
    def get_response(self, messages):
        """获取AI响应的抽象方法，子类必须实现"""
        raise NotImplementedError("子类必须实现此方法")
        
    def get_streaming_response(self, messages, use_case=None):
        """获取AI流式响应的抽象方法，子类必须实现"""
        raise NotImplementedError("子类必须实现此方法")

class DeepSeekService(AIModelService):
    """与DeepSeek API通信的服务类"""
    def __init__(self):
        # 从环境变量获取API密钥
        self.api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        # DeepSeek API端点URL
        self.base_url = "https://api.deepseek.com"
        self.api_url = f"{self.base_url}/v1/chat/completions"
        # 默认使用的模型
        self.model = "deepseek-chat"  # 使用DeepSeek Chat模型
        # 针对不同用例的温度设置
        self.use_case_temperatures = {
            "coding": 0.0,     # 编程/数学
            "data": 1.0,       # 数据清洗/分析
            "general": 1.3,    # 一般对话
            "translation": 1.3, # 翻译
            "creative": 1.5    # 创意写作/诗歌
        }
        # 默认使用一般对话的温度
        self.temperature = self.use_case_temperatures["general"]
        
    def get_response(self, messages, use_case="general"):
        """向DeepSeek API发送请求并获取响应
        
        Args:
            messages: 消息历史记录
            use_case: 使用场景，可以是"coding", "data", "general", "translation", "creative"
        """
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
            
        # 根据使用场景设置温度
        if use_case in self.use_case_temperatures:
            self.temperature = self.use_case_temperatures[use_case]
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature
        }
        
        try:
            print(f"向DeepSeek API发送请求: URL={self.api_url}, 模型={self.model}, 温度={self.temperature}")
            response = requests.post(self.api_url, headers=headers, json=data)
            
            # 打印详细的响应信息
            print(f"DeepSeek API响应状态码: {response.status_code}")
            print(f"DeepSeek API响应头: {response.headers}")
            
            if response.status_code != 200:
                print(f"DeepSeek API错误响应: {response.text}")
                
            # 检查HTTP错误
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            print(f"DeepSeek API成功响应: {result}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API请求异常: {str(e)}")
            raise ValueError(f"DeepSeek API请求失败: {str(e)}")
        except ValueError as e:
            print(f"DeepSeek API JSON解析错误: {str(e)}")
            raise ValueError(f"无法解析DeepSeek API响应: {str(e)}")
        except Exception as e:
            print(f"DeepSeek API未知错误: {str(e)}")
            raise
        
    def get_streaming_response(self, messages, use_case="general"):
        """向DeepSeek API发送流式请求并获取流式响应
        
        Args:
            messages: 消息历史记录
            use_case: 使用场景，可以是"coding", "data", "general", "translation", "creative"
            
        Returns:
            generator: 生成每个响应块的生成器
        """
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
            
        # 根据使用场景设置温度
        if use_case in self.use_case_temperatures:
            self.temperature = self.use_case_temperatures[use_case]
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True  # 启用流式传输
        }
        
        try:
            print(f"向DeepSeek API发送流式请求: URL={self.api_url}, 模型={self.model}, 温度={self.temperature}")
            response = requests.post(self.api_url, headers=headers, json=data, stream=True)
            
            # 检查HTTP错误
            response.raise_for_status()
            
            # 对每个响应行进行处理
            for line in response.iter_lines():
                if line:
                    # 移除data: 前缀并解析JSON
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        line_text = line_text[6:]  # 移除'data: '前缀
                        
                    if line_text == '[DONE]':
                        break
                        
                    try:
                        chunk = json.loads(line_text)
                        yield chunk
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误: {e}, 原始行: {line_text}")
        
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API流式请求异常: {str(e)}")
            raise ValueError(f"DeepSeek API流式请求失败: {str(e)}")
        except Exception as e:
            print(f"DeepSeek API流式请求未知错误: {str(e)}")
            raise


class OllamaService(AIModelService):
    """与本地Ollama实例通信的服务类"""
    def __init__(self):
        # Ollama API端点URL，默认为本地地址
        self.api_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434') + "/api/chat"
        # 使用DeepSeek-R1 1.5B模型
        self.model = "deepseek-r1:1.5b"  # 按用户要求使用deepseek-r1:1.5b模型
        
    def get_response(self, messages, use_case=None):
        """向Ollama发送请求并获取响应
        
        Args:
            messages: 消息历史记录
            use_case: 使用场景，在Ollama中不使用，保持API一致性
        """
        # 配置请求参数
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            # 根据不同任务设置合适的温度
            # 对于编程和推理任务，使用低温度设置
            "temperature": 0.7  # 默认使用中等温度
        }
        
        try:
            print(f"向Ollama发送请求: URL={self.api_url}, 模型={self.model}")
            response = requests.post(self.api_url, json=data)
            
            # 打印详细的响应信息
            print(f"Ollama响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Ollama错误响应: {response.text}")
                
            # 检查HTTP错误
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            print(f"Ollama成功响应")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Ollama请求异常: {str(e)}")
            raise ValueError(f"Ollama请求失败: {str(e)}")
        except ValueError as e:
            print(f"Ollama JSON解析错误: {str(e)}")
            raise ValueError(f"无法解析Ollama响应: {str(e)}")
        except Exception as e:
            print(f"Ollama未知错误: {str(e)}")
            raise
            
    def get_streaming_response(self, messages, use_case=None):
        """向Ollama发送流式请求并获取流式响应
        
        Args:
            messages: 消息历史记录
            use_case: 使用场景，在Ollama中不使用，保持API一致性
            
        Returns:
            generator: 生成每个响应块的生成器
        """
        # 配置请求参数为流式模式
        data = {
            "model": self.model,
            "messages": messages,
            "stream": True  # 启用流式处理
        }
        
        try:
            print(f"向Ollama发送流式请求: URL={self.api_url}, 模型={self.model}")
            response = requests.post(self.api_url, json=data, stream=True)
            
            # 检查HTTP错误
            response.raise_for_status()
            
            # 对每个响应行进行处理
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        yield chunk
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误: {e}, 原始行: {line.decode('utf-8')}")
                        
        except requests.exceptions.RequestException as e:
            print(f"Ollama API流式请求异常: {str(e)}")
            raise ValueError(f"Ollama API流式请求失败: {str(e)}")
        except Exception as e:
            print(f"Ollama API流式请求未知错误: {str(e)}")
            raise
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            # 根据不同任务设置合适的温度
            # 对于编程和推理任务，使用低温度设置
            "temperature": 0.1  # 推理模型使用低温度以提高准确性
        }
        
        response = requests.post(self.api_url, json=data)
        response.raise_for_status()  # 对HTTP错误抛出异常
        return response.json()

def get_ai_service(service_type="deepseek", use_case="general"):
    """工厂函数，获取适当的AI服务
    
    Args:
        service_type: 服务类型，可以是"deepseek", "ollama"
        use_case: 使用场景，仅对DeepSeek有效
    """
    # 如果未明确指定，从环境变量获取默认服务类型
    if service_type == "auto" or service_type not in ["deepseek", "ollama"]:
        # 检查是否有DeepSeek API密钥
        if os.environ.get('DEEPSEEK_API_KEY'):
            service_type = "deepseek"
        # 没有DeepSeek API密钥，默认使用Ollama
        else:
            service_type = "ollama"
            
    # 根据服务类型返回相应的服务实例
    if service_type == "deepseek":
        # 添加额外检查，确保API密钥真的存在
        if not os.environ.get('DEEPSEEK_API_KEY'):
            print("警告：请求使用DeepSeek但API密钥不存在，自动切换到Ollama")
            return OllamaService()
        return DeepSeekService()
    else:  # 默认为Ollama
        return OllamaService()


class MemoryService:
    """对话记忆服务，生成和维护对话的记忆摘要"""
    def __init__(self):
        # 使用DeepSeek服务来生成记忆摘要
        self.ai_service = DeepSeekService()
        # 记忆生成阈值，当消息数达到该值时生成记忆
        self.memory_threshold = 10
    
    def should_generate_memory(self, message_count):
        """判断是否应该生成记忆摘要
        
        Args:
            message_count: 当前对话的消息数量
            
        Returns:
            bool: 是否应该生成记忆
        """
        # 当消息数是记忆阈值的倍数时生成记忆
        return message_count > 0 and message_count % self.memory_threshold == 0
    
    def generate_memory(self, messages, previous_memory=None):
        """生成对话记忆摘要
        
        Args:
            messages: 对话消息列表
            previous_memory: 之前的记忆摘要，如果有的话
            
        Returns:
            str: 生成的记忆摘要
        """
        # 构建系统提示词
        system_message = {
            "role": "system",
            "content": self._get_memory_system_prompt(previous_memory)
        }
        
        # 收集用户和AI的消息，限制数量以避免上下文过长
        conversation_messages = messages[-self.memory_threshold:]
        
        # 格式化消息
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in conversation_messages]
        
        # 在消息列表开头添加系统提示词
        formatted_messages.insert(0, system_message)
        
        # 添加用户指令，要求AI生成摘要
        formatted_messages.append({
            "role": "user",
            "content": "请根据以上对话内容，生成一个简洁的记忆摘要，捕捉用户的关键信息、偏好和重要上下文。摘要应该以第三人称陈述形式呈现，突出重点。"
        })
        
        try:
            # 获取AI生成的记忆摘要
            response = self.ai_service.get_response(formatted_messages, use_case="general")
            
            # 提取AI响应内容
            memory_summary = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 如果已有之前的记忆，则合并
            if previous_memory and memory_summary:
                return self._merge_memories(previous_memory, memory_summary)
            
            return memory_summary
        
        except Exception as e:
            print(f"生成记忆摘要时出错: {str(e)}")
            return previous_memory or ""
    
    def _get_memory_system_prompt(self, previous_memory=None):
        """获取用于记忆生成的系统提示词
        
        Args:
            previous_memory: 之前的记忆摘要，如果有的话
            
        Returns:
            str: 系统提示词
        """
        base_prompt = "你是一个专门负责总结对话的助手。你的任务是识别对话中的关键信息，并创建一个简洁的记忆摘要，以便在将来的对话中参考。"
        
        if previous_memory:
            base_prompt += f"\n\n以下是之前的记忆摘要，请在生成新摘要时考虑这些信息：\n{previous_memory}"
        
        base_prompt += "\n\n重点关注用户的：\n1. 健身和运动目标\n2. 体测数据和身体状况\n3. 饮食偏好和限制\n4. 健身习惯和频率\n5. 任何健康问题或伤病历史"
        
        return base_prompt
    
    def _merge_memories(self, old_memory, new_memory):
        """合并旧记忆和新记忆
        
        Args:
            old_memory: 旧的记忆摘要
            new_memory: 新生成的记忆摘要
            
        Returns:
            str: 合并后的记忆摘要
        """
        # 使用AI来智能合并记忆
        system_message = {
            "role": "system",
            "content": "你是一个专门负责整合信息的助手。你的任务是将两段记忆摘要合并成一个连贯的、无冗余的新摘要。保留所有重要信息，消除重复内容，并确保结果逻辑连贯。"
        }
        
        formatted_messages = [
            system_message,
            {
                "role": "user",
                "content": f"请将以下两段记忆摘要合并成一个连贯的摘要，避免重复内容：\n\n旧摘要：\n{old_memory}\n\n新摘要：\n{new_memory}"
            }
        ]
        
        try:
            response = self.ai_service.get_response(formatted_messages, use_case="general")
            merged_memory = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            return merged_memory
        except Exception as e:
            print(f"合并记忆摘要时出错: {str(e)}")
            # 如果合并失败，简单地将新旧记忆连接起来
            return f"{old_memory}\n\n{new_memory}"
