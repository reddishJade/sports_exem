import { AxiosInstance } from 'axios';

/**
 * 配置好的 Axios 实例，用于与后端 API 通信
 * - 已配置 baseURL (http://127.0.0.1:8000/api)
 * - 自动处理认证令牌
 * - 配置了拦截器来处理错误和令牌刷新
 */
declare const api: AxiosInstance;
export default api;
