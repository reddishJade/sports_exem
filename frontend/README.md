# 体测管理系统前端

## 项目简介

本项目是一个基于Vue.js开发的大学生体测管理系统前端，提供了友好的用户界面，支持学生体测数据的展示、成绩查询、健康报告查看以及体育新闻浏览等功能。

## 技术栈

- Vue 3.0+
- Vue Router
- Vuex
- Axios
- Element Plus
- TypeScript (部分使用)

## 功能特性

- 响应式布局设计，适配各种设备
- 用户登录与认证
- 学生信息管理界面
- 体测计划查看
- 体测成绩查询与展示
- 健康报告查看
- 体育新闻浏览与评论
- 权限控制

## 环境要求

- Node.js 14.0+
- npm 6.0+ 或 yarn 1.22+

## 快速开始

### 安装依赖

```bash
# 使用npm
npm install

# 或使用yarn
yarn install
```

### 开发模式

```bash
# 使用npm
npm run dev

# 或使用yarn
yarn dev
```

应用将运行在 http://localhost:5173

### 构建生产版本

```bash
# 使用npm
npm run build

# 或使用yarn
yarn build
```

## 目录结构

```
frontend/fitness_vue/
├── public/                # 静态资源
├── src/                   # 源代码
│   ├── assets/            # 资源文件（图片、样式等）
│   ├── components/        # 通用组件
│   ├── router/            # 路由配置
│   ├── store/             # Vuex状态管理
│   ├── utils/             # 工具函数
│   ├── views/             # 页面组件
│   ├── App.vue            # 根组件
│   └── main.js            # 应用入口
├── .editorconfig          # 编辑器配置
├── .gitignore             # Git忽略文件
├── index.html             # HTML模板
├── package.json           # 项目依赖与脚本
├── tsconfig.json          # TypeScript配置
└── vite.config.ts         # Vite配置
```

## 主要页面

- 登录页 (`/login`)
- 首页 (`/`)
- 学生列表 (`/students`) - 仅管理员可见
- 体测计划 (`/test-plans`)
- 体测成绩 (`/test-results`)
- 体测标准 (`/physical-standards`)
- 健康报告 (`/health-reports`)
- 体育新闻列表 (`/news`)
- 新闻详情 (`/news/:id`)

## 与后端通信

前端使用Axios库与后端API进行通信，API基本URL配置在环境变量中。所有API请求都会自动附带身份验证token。

## 用户认证

用户登录后，JWT token存储在localStorage中，并在每次请求时通过请求拦截器添加到请求头中。

## 部署说明

1. 构建生产版本
2. 将`dist`目录下的文件部署到Web服务器
3. 配置Web服务器以支持SPA路由（所有路由都指向index.html）

## 许可证

[MIT License](LICENSE)
