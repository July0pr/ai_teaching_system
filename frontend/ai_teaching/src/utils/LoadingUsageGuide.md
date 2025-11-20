# 加载组件使用指南

## 简介

本项目提供了一个全局的加载状态管理系统，用于在等待后端API响应或其他异步操作期间显示加载提示。加载组件可以显示半透明的遮罩层和一个加载动画，以及自定义提示文字。

## 组件结构

加载状态系统包含以下几个部分：

1. **Loading.vue** - 加载状态的视觉组件
2. **loading.ts** - Pinia store，用于管理加载状态
3. **api.ts** - 封装了自动处理加载状态的API请求工具

## 基本用法

### 1. 直接使用加载状态Store

```vue
<script setup>
import { useLoadingStore } from '@/stores/loading';

const loadingStore = useLoadingStore();

// 显示加载状态
const handleAction = async () => {
  loadingStore.showLoading('加载中...');
  
  try {
    // 执行异步操作
    await someAsyncOperation();
  } finally {
    // 隐藏加载状态
    loadingStore.hideLoading();
  }
};
</script>
```

### 2. 使用apiWithLoading工具

```vue
<script setup>
import { apiWithLoading } from '@/utils/api';

// 获取数据并自动处理加载状态
const fetchData = async () => {
  try {
    const data = await apiWithLoading.get('/api/resources', '正在获取资源...');
    // 处理数据
  } catch (error) {
    // 处理错误
  }
};

// 提交数据并自动处理加载状态
const submitData = async (formData) => {
  try {
    const result = await apiWithLoading.post('/api/resources', formData, '正在提交数据...');
    // 处理结果
  } catch (error) {
    // 处理错误
  }
};
</script>
```

### 3. 使用withLoading辅助函数

```vue
<script setup>
import { useLoadingStore } from '@/stores/loading';

const loadingStore = useLoadingStore();

const fetchData = async () => {
  try {
    const data = await loadingStore.withLoading(
      fetch('/api/data').then(res => res.json()),
      '正在获取数据...'
    );
    // 处理数据
  } catch (error) {
    // 处理错误
  }
};
</script>
```

## 高级用法

### 自定义加载提示信息

```vue
<script setup>
import { useLoadingStore } from '@/stores/loading';

const loadingStore = useLoadingStore();

// AI生成资源时显示特定消息
const generateAIResource = async () => {
  loadingStore.showLoading('AI正在为您生成教学资源，这可能需要一点时间...');
  
  try {
    // 执行AI生成操作
    await generateResource();
  } finally {
    loadingStore.hideLoading();
  }
};
</script>
```

### 处理多个并发请求

当有多个并发的请求时，我们的加载组件会智能处理：只有当所有请求都完成后，才会隐藏加载状态。

```vue
<script setup>
import { apiWithLoading } from '@/utils/api';

const fetchMultipleResources = async () => {
  // 同时发起多个请求
  const [userData, resourceData, classData] = await Promise.all([
    apiWithLoading.get('/api/user'),
    apiWithLoading.get('/api/resources'),
    apiWithLoading.get('/api/classes')
  ]);
  
  // 当所有请求完成后，加载状态会自动隐藏
};
</script>
```

## 注意事项

1. 确保在异步操作结束后始终调用 `hideLoading()`，最好使用 try-finally 语句块确保即使出错也能隐藏加载状态。
2. 对于长时间运行的操作，建议提供明确的提示信息，让用户知道正在进行什么操作。
3. 使用 `apiWithLoading` 工具可以自动处理加载状态，推荐用于所有API请求。
4. 默认的加载提示为"正在加载中..."，可以根据具体操作自定义消息。
