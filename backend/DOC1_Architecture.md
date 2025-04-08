# 体测管理系统后端架构文档

## 技术架构概述

本系统采用Django REST framework构建RESTful API，为前端提供数据服务。主要技术组件包括：

- **Django**: Python Web框架，提供ORM、中间件、认证等基础功能
- **Django REST framework**: 用于构建RESTful API的强大工具集
- **SQLite/MySQL**: 数据存储
- **JWT**: JSON Web Token用于用户认证

### 系统架构图

```
前端应用 <---> Django REST API <---> 数据库
                   |
                   v
               业务逻辑层
```

## 项目结构

后端项目采用标准的Django项目结构，主要目录和文件包括：

```
backend/
├── fitness/                  # 主应用
│   ├── migrations/           # 数据库迁移文件
│   ├── admin.py              # 管理后台配置
│   ├── apps.py               # 应用配置
│   ├── auth.py               # 认证相关
│   ├── models.py             # 数据模型
│   ├── serializers.py        # 序列化器
│   ├── urls.py               # URL配置
│   ├── views.py              # 视图和API接口
├── fitness_backend/          # 项目配置
│   ├── settings.py           # 项目设置
│   ├── urls.py               # 主URL配置
├── manage.py                 # Django命令行工具
├── requirements.txt          # 依赖列表
```

## 技术栈详解

### Django REST framework

Django REST framework是一个强大的工具集，用于构建Web API。在本项目中，我们利用它实现了以下功能：

1. **序列化**: 将复杂的数据类型（如Django模型实例）转换为Python原生数据类型，再序列化为JSON
2. **视图集(ViewSets)**: 将相关视图组合在一起，自动处理常见HTTP方法
3. **路由器(Routers)**: 自动为ViewSets生成URL配置
4. **权限控制**: 实现基于角色的访问控制
5. **认证**: 支持多种认证方式，本项目使用JWT

### 数据库设计原则

系统使用Django的ORM（对象关系映射）进行数据库操作，遵循以下设计原则：

1. **规范化**: 减少数据冗余，避免异常
2. **合理的关系**: 使用外键、一对一、多对多关系表达数据之间的联系
3. **索引优化**: 为经常查询的字段添加索引
4. **命名约定**: 使用清晰一致的命名约定

### API设计原则

系统API设计遵循RESTful原则：

1. **资源导向**: API围绕资源（如学生、测试计划、成绩等）设计
2. **HTTP方法**: 使用GET、POST、PUT、DELETE方法表示不同操作
3. **无状态**: 不依赖服务器状态，每个请求包含所有信息
4. **一致性**: 保持API格式和错误处理的一致性

### 认证与安全

系统采用以下安全措施：

1. **JWT认证**: 使用JSON Web Token进行身份验证
2. **CSRF保护**: 防止跨站请求伪造
3. **权限控制**: 基于用户角色（学生、家长、管理员）的访问控制
4. **输入验证**: 验证客户端输入，防止注入攻击

## 技术实现挑战与解决方案

### 挑战1: 复杂的用户角色权限控制

**解决方案**:
- 使用自定义User模型扩展AbstractUser
- 在视图集中重写get_queryset方法，根据用户角色过滤数据
- 使用DRF的权限类控制API访问

### 挑战2: 根据性别区分体测标准

**解决方案**:
- 设计PhysicalStandard模型，按性别存储不同标准
- 在测试结果计算时动态查询适用标准
- 使用属性方法（@property）计算是否合格

### 挑战3: 自动补考通知生成

**解决方案**:
- 利用Django信号机制(signals)监听测试结果保存事件
- 根据成绩自动创建补考通知
- 使用关联查询查找合适的补考计划
