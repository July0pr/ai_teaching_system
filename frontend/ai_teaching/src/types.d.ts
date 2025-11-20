// 全局类型定义

// 为window对象扩展$showToast方法
declare global {
  interface Window {
    $showToast: (message: string, type?: 'success' | 'error') => void;
  }
}

export {}; 