# 大学生体测管理系统

一个现代化的大学生体测管理系统，使用 Django + Vue.js 构建。

## 功能特点

### 用户管理
- 多角色支持：学生、家长、管理员
- JWT 认证
- 个人信息管理

### 体测管理
- 体测计划管理
- 成绩录入与查询
- 补考通知自动生成
- 成绩趋势分析
- 数据可视化展示

### 健康管理
- 健康报告生成
- BMI 指数计算
- 体能评估
- 健康建议

### 系统功能
- 响应式界面设计
- 数据导出功能
- 评论与反馈
- 实时通知

## 技术栈

### 后端
- Python 3.11
- Django 5.1.5
- Django REST framework
- Simple JWT
- MySQL 8.0

### 前端
- Vue.js 3
- Ant Design Vue
- ECharts
- Axios
- Vue Router
- Vuex

## 安装说明

### 环境要求
- Python 3.11+
- Node.js 16+
- MySQL 8.0+

### 数据库配置
1. 创建数据库：
```sql
CREATE DATABASE fitness_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 配置数据库连接：
编辑 `backend/fitness_backend/settings.py` 中的数据库配置：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fitness_db',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 后端设置
1. 创建并激活虚拟环境：
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

2. 安装依赖：
```bash
cd backend
pip install -r requirements.txt
```

3. 初始化数据库：
```bash
python manage.py makemigrations
python manage.py migrate
```

4. 创建超级用户：
```bash
python manage.py createsuperuser
```

5. 填充测试数据：
```bash
python manage.py populate_test_data
```

6. 启动开发服务器：
```bash
python manage.py runserver
```

### 前端设置
1. 安装依赖：
```bash
cd frontend/fitness_vue
npm install
```

2. 启动开发服务器：
```bash
npm run serve
```

3. 构建生产版本：
```bash
npm run build
```

## 访问系统

1. 后端管理界面：
   - URL: http://localhost:8000/admin/
   - 使用创建的超级用户账号登录

2. 前端应用：
   - URL: http://localhost:8080/
   - 默认测试账号：
     - 管理员：admin / admin
     - 学生：student1 / 123456
     - 家长：parent1 / 123456

## 项目结构
```
fitness_system/
├── backend/                 # Django 后端
│   ├── fitness/            # 主应用
│   │   ├── models.py      # 数据模型
│   │   ├── views.py       # 视图
│   │   ├── serializers.py # 序列化器
│   │   └── urls.py        # URL 配置
│   ├── fitness_backend/    # 项目设置
│   └── requirements.txt    # 后端依赖
├── frontend/               # Vue.js 前端
│   └── fitness_vue/
│       ├── src/
│       │   ├── components/# Vue 组件
│       │   ├── views/     # 页面视图
│       │   ├── router/    # 路由配置
│       │   └── store/     # Vuex 存储
└── docs/                  # 文档
```

## API 文档

### 认证 API
- POST /api/auth/login/ - 用户登录
- POST /api/auth/refresh/ - 刷新 Token
- POST /api/auth/logout/ - 用户登出

### 用户 API
- GET /api/users/me/ - 获取当前用户信息
- PUT /api/users/me/ - 更新用户信息

### 体测 API
- GET /api/test-plans/ - 获取体测计划列表
- GET /api/test-results/ - 获取体测成绩
- POST /api/test-results/ - 提交体测成绩

### 健康报告 API
- GET /api/health-reports/ - 获取健康报告
- POST /api/health-reports/ - 创建健康报告

## 开发指南

### 代码规范
- Python: 遵循 PEP 8 规范
- JavaScript: 使用 ESLint + Prettier
- Vue: 遵循 Vue.js 风格指南

### Git 工作流
1. 创建功能分支
2. 提交代码
3. 创建 Pull Request
4. 代码审查
5. 合并到主分支

## 部署指南

### 后端部署
1. 配置 gunicorn：
```bash
pip install gunicorn
gunicorn fitness_backend.wsgi:application
```

2. 配置 Nginx：
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 前端部署
1. 构建生产版本：
```bash
npm run build
```

2. 配置 Nginx：
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

## 测试

### 后端测试
```bash
python manage.py test
```

### 前端测试
```bash
npm run test:unit
```

## 常见问题

1. 数据库连接错误
   - 检查 MySQL 服务是否启动
   - 验证数据库凭据是否正确
   - 确认数据库字符集为 utf8mb4

2. 前端编译错误
   - 确保 Node.js 版本兼容
   - 清除 node_modules 并重新安装依赖

3. 跨域问题
   - 检查 CORS 配置是否正确
   - 验证 API 请求地址是否正确

## 维护者

- [维护者姓名]
- [联系方式]

## 许可证

MIT License
