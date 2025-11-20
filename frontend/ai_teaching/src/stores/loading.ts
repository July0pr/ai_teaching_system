// 使用Pinia管理加载状态
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLoadingStore = defineStore('loading', () => {
  // 加载状态
  const isLoading = ref(false)
  // 加载提示消息
  const loadingMessage = ref('正在加载中...')
  
  // 显示加载
  function showLoading(message = '正在加载中...') {
    loadingMessage.value = message
    isLoading.value = true
  }
  
  // 隐藏加载
  function hideLoading() {
    isLoading.value = false
  }
  
  // 包装异步请求，自动处理加载状态
  async function withLoading<T>(promise: Promise<T>, message = '正在加载中...'): Promise<T> {
    try {
      showLoading(message)
      return await promise
    } finally {
      hideLoading()
    }
  }
  
  return {
    isLoading,
    loadingMessage,
    showLoading,
    hideLoading,
    withLoading
  }
}) 