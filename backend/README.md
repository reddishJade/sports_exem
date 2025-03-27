# 体测管理系统后端

## 项目简介

本项目是一个基于Django REST framework开发的大学生体测管理系统后端，提供了完整的API接口，支持学生体测数据的管理、成绩查询、体测标准维护、健康报告生成以及体育新闻发布等功能。

## 技术栈

- Python 3.8+
- Django 3.2+
- Django REST framework
- SQLite (开发环境) / MySQL (可选生产环境)
- JWT 认证

## 功能特性

- 用户认证与授权（学生、家长、管理员）
- 学生信息管理
- 体测计划管理
- 体测成绩记录与查询
- 体测标准设置与维护
- 健康报告生成
- 体育新闻发布与管理
- 评论管理
- 补考通知

## 环境配置

### 安装依赖

```bash
# 创建并激活虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 数据库配置

```bash
# 创建数据库
python create_database.py

# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 导入测试数据（可选）
python create_test_data.py
```

## 启动服务

```bash
python manage.py runserver
```

服务默认运行在 http://localhost:8000

## API文档

API文档可通过访问 http://localhost:8000/api/ 获取

## 目录结构

```
backend/
├── fitness/                  # 主应用
│   ├── migrations/           # 数据库迁移文件
│   ├── __init__.py           
│   ├── admin.py              # 管理后台配置
│   ├── apps.py               # 应用配置
│   ├── auth.py               # 认证相关
│   ├── models.py             # 数据模型
│   ├── serializers.py        # 序列化器
│   ├── urls.py               # URL配置
│   ├── views.py              # 视图和API接口
│   └── tests.py              # 测试
├── fitness_backend/          # 项目配置
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # 项目设置
│   ├── urls.py               # 主URL配置
│   └── wsgi.py
├── manage.py                 # Django命令行工具
├── requirements.txt          # 依赖列表
├── create_database.py        # 数据库创建脚本
└── create_test_data.py       # 测试数据生成脚本
```

## 部署说明

1. 在生产环境中，请修改 `settings.py` 中的 `DEBUG = False`
2. 配置正确的数据库连接
3. 设置安全的 `SECRET_KEY`
4. 配置允许的主机 `ALLOWED_HOSTS`
5. 考虑使用 Gunicorn 或 uWSGI 作为 WSGI 服务器
6. 使用 Nginx 作为反向代理

## 许可证

[MIT License](LICENSE)
