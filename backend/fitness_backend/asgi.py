"""
ASGI config for fitness_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import fitness.routing
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')

# 创建合并的WebSocket路由
from channels.routing import ChannelNameRouter

# 尝试导入ai_chat的路由配置
try:
    import ai_chat.routing
    websocket_urlpatterns = fitness.routing.websocket_urlpatterns + ai_chat.routing.websocket_urlpatterns
except (ImportError, AttributeError):
    # 如果ai_chat没有routing.py或没有websocket_urlpatterns，只使用fitness的路由
    websocket_urlpatterns = fitness.routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
