<template>
    <div class="resources-index">
        <div class="welcome-container">
            <div class="welcome-content">
                <div class="icon-container">
                    <i class="icon">📚</i>
                </div>
                <h1>资源展示</h1>
                <p class="subtitle">在这里管理和查看您的教学资源</p>
                <div class="resource-entries">
                    <div class="entry-card" @click="goToHistory">
                        <div class="entry-icon">📋</div>
                        <div class="entry-content">
                            <h3>历史记录</h3>
                            <p>查看您的历史资源记录</p>
                        </div>
                        <div class="entry-arrow">→</div>
                    </div>
                    <div class="entry-card" @click="goToPersonal">
                        <div class="entry-icon">📁</div>
                        <div class="entry-content">
                            <h3>个人资源</h3>
                            <p>管理您的个人教学资源</p>
                        </div>
                        <div class="entry-arrow">→</div>
                    </div>
                </div>
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

const goToHistory = () => {
    router.push('/teacher/resources/history');
};

const goToPersonal = () => {
    router.push('/teacher/resources/personal');
};
</script>

<style scoped>
.resources-index {
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

.resource-entries {
    display: flex;
    gap: 24px;
    justify-content: center;
    margin-top: 40px;
}

.entry-card {
    flex: 1;
    max-width: 300px;
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    display: flex;
    align-items: center;
    gap: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: left;
}

.entry-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 20px rgba(76, 132, 255, 0.15);
}

.entry-icon {
    font-size: 32px;
    color: #4c84ff;
}

.entry-content {
    flex: 1;
}

.entry-content h3 {
    font-size: 18px;
    color: #2c3e50;
    margin: 0 0 8px 0;
}

.entry-content p {
    font-size: 14px;
    color: #666;
    margin: 0;
}

.entry-arrow {
    font-size: 24px;
    color: #4c84ff;
    transition: transform 0.3s ease;
}

.entry-card:hover .entry-arrow {
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