import axios from 'axios';
import { useLoadingStore } from '@/stores/loading';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 20 * 60 * 1000, // 20min超时
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器 - 添加token等
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误等
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 这里可以添加全局错误处理，如401跳转到登录页等
    const status = error.response ? error.response.status : null;
    
    if (status === 401) {
      // 未授权，清除token并跳转到登录页
      localStorage.removeItem('token');
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('userRole');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// 带加载状态的API调用
const apiWithLoading = {
  async get<T>(url: string, message = '正在加载数据...', config = {}) {
    const loadingStore = useLoadingStore();
    return loadingStore.withLoading<T>(api.get(url, config).then(res => res.data), message);
  },
  
  async post<T>(url: string, data = {}, message = '正在提交数据...', config = {}) {
    const loadingStore = useLoadingStore();
    return loadingStore.withLoading<T>(api.post(url, data, config).then(res => res.data), message);
  },
  
  async put<T>(url: string, data = {}, message = '正在更新数据...', config = {}) {
    const loadingStore = useLoadingStore();
    return loadingStore.withLoading<T>(api.put(url, data, config).then(res => res.data), message);
  },
  
  async delete<T>(url: string, message = '正在删除数据...', config = {}) {
    const loadingStore = useLoadingStore();
    return loadingStore.withLoading<T>(api.delete(url, config).then(res => res.data), message);
  },
};

// 导出
export default api;
export { api, apiWithLoading }; 