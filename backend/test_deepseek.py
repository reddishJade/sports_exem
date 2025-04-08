import requests
import json
from django.conf import settings
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

# 导入服务
from ai_chat.services import DeepSeekService

# 测试DeepSeek服务
def test_deepseek_integration():
    print("开始测试DeepSeek集成...")
    
    # 初始化DeepSeek服务
    service = DeepSeekService()
    
    # 打印配置信息
    print(f"API密钥存在: {bool(service.api_key)}")
    print(f"API URL: {service.api_url}")
    print(f"模型: {service.model}")
    
    # 测试简单消息
    try:
        messages = [
            {"role": "system", "content": "你是一个健身助手，帮助用户解答健身相关问题。"},
            {"role": "user", "content": "请给我一个简单的胸肌训练计划"}
        ]
        
        print("发送测试消息到DeepSeek API...")
        response = service.get_response(messages)
        
        print("API响应:")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        
        # 提取实际的AI回复内容
        ai_message = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        print("\n实际的AI回复内容:")
        print(ai_message)
        
        return True
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_deepseek_integration()
    print(f"\n测试结果: {'成功' if success else '失败'}")
