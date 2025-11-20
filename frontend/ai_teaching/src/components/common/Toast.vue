<template>
    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-toast">
        {{ errorMessage }}
    </div>

    <!-- 成功提示 -->
    <div v-if="showSuccess" class="success-toast">
        {{ successMessage }}
    </div>
</template>

<script setup lang="ts">
import { ref, defineExpose } from 'vue';

const errorMessage = ref('');
const showSuccess = ref(false);
const successMessage = ref('');

// 显示成功提示
const showToastMessage = (message: string, type: 'success' | 'error' = 'success') => {
    if (type === 'success') {
        successMessage.value = message;
        showSuccess.value = true;
        setTimeout(() => {
            showSuccess.value = false;
        }, 2000);
    } else {
        errorMessage.value = message;
        setTimeout(() => {
            errorMessage.value = '';
        }, 2000);
    }
};

// 暴露方法给父组件使用
defineExpose({
    showToastMessage
});
</script>

<style scoped>
/* 提示样式 */
.success-toast,
.error-toast {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 24px;
    border-radius: 4px;
    font-size: 14px;
    z-index: 1000;
    animation: fadeInOut 2s ease-in-out;
}

.success-toast {
    background-color: #2ecc71;
    color: white;
}

.error-toast {
    background-color: #e74c3c;
    color: white;
}

@keyframes fadeInOut {
    0% {
        opacity: 0;
        transform: translate(-50%, 20px);
    }

    15% {
        opacity: 1;
        transform: translate(-50%, 0);
    }

    85% {
        opacity: 1;
        transform: translate(-50%, 0);
    }

    100% {
        opacity: 0;
        transform: translate(-50%, -20px);
    }
}
</style>