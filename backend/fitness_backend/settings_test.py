"""
测试环境配置 - 使用独立的测试数据库
"""
import os
from dotenv import load_dotenv

# 确保加载环境变量，即使在测试环境中
load_dotenv()

from .settings import *

# 使用测试数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

# 确保时区设置正确
USE_TZ = True
