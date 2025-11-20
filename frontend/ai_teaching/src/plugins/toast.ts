import { type App, createApp } from 'vue';
import Toast from '@/components/common/Toast.vue';

const toast = {
    install(app: App) {
        // 创建一个Toast实例的容器
        const container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);

        // 创建Toast实例
        const toastInstance = createApp(Toast).mount(container);

        // 全局方法
        app.config.globalProperties.$showToast = (message: string, type: 'success' | 'error' = 'success') => {
            (toastInstance as any).showToastMessage(message, type);
        };

        // 也可以通过window全局访问
        window.$showToast = (message: string, type: 'success' | 'error' = 'success') => {
            (toastInstance as any).showToastMessage(message, type);
        };
    }
};

export default toast;

// 扩展Window接口，添加$showToast方法的类型定义
declare global {
    interface Window {
        $showToast: (message: string, type?: 'success' | 'error') => void;
    }
} 