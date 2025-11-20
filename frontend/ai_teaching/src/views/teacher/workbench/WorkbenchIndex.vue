<template>
    <div class="workbench-index">
        <div class="welcome-container">
            <div class="welcome-content">
                <div class="icon-container">
                    <i class="icon">📚</i>
                </div>
                <h1>欢迎使用备课工作台</h1>
                <p class="subtitle">让AI助手帮您轻松完成备课</p>
                <button class="start-btn" @click="startPreparation">
                    <span class="btn-text">开始备课</span>
                    <span class="btn-icon">→</span>
                </button>
            </div>
            <div class="decoration">
                <div class="circle circle-1"></div>
                <div class="circle circle-2"></div>
                <div class="circle circle-3"></div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const startPreparation = () => {
    router.push('/teacher/workbench/step1');
};
</script>

<style scoped>
.workbench-index {
    height: 100%;
    width: 100%;
    display: flex;
    padding: 0;
    background-color: #f5f7fa;
}

.welcome-container {
    position: relative;
    width: 100%;
    height: 100%;
    text-align: center;
    padding: 60px 40px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.welcome-content {
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
}

.icon-container {
    margin-bottom: 24px;
}

.icon {
    font-size: 48px;
    background: linear-gradient(135deg, #4c84ff 0%, #2b5ff3 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

h1 {
    font-size: 32px;
    color: #2c3e50;
    margin-bottom: 16px;
    font-weight: 600;
}

.subtitle {
    font-size: 16px;
    color: #666;
    margin-bottom: 40px;
}

.start-btn {
    display: inline-flex;
    align-items: center;
    padding: 16px 40px;
    background: linear-gradient(135deg, #4c84ff 0%, #2b5ff3 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(76, 132, 255, 0.3);
}

.start-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(76, 132, 255, 0.4);
}

.btn-text {
    margin-right: 12px;
}

.btn-icon {
    font-size: 20px;
    transition: transform 0.3s ease;
}

.start-btn:hover .btn-icon {
    transform: translateX(4px);
}

/* 装饰元素 */
.decoration {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1;
    overflow: hidden;
}

.circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
}

.circle-1 {
    width: 200px;
    height: 200px;
    background: #4c84ff;
    top: -100px;
    left: -100px;
}

.circle-2 {
    width: 300px;
    height: 300px;
    background: #2b5ff3;
    bottom: -150px;
    right: -150px;
}

.circle-3 {
    width: 150px;
    height: 150px;
    background: #4c84ff;
    top: 50%;
    right: 50px;
    transform: translateY(-50%);
}
</style>