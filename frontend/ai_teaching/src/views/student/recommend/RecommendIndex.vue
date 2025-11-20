<template>
    <div class="recommend-index">
        <div class="welcome-container">
            <div class="welcome-content">
                <div class="icon-container">
                    <i class="icon">📚</i>
                </div>
                <h1>欢迎使用自学中心</h1>
                <p class="subtitle">让AI助手帮您提升学习效率</p>
                <div class="entry-cards">
                    <div class="entry-card" @click="goToResources">
                        <div class="entry-icon">📖</div>
                        <div class="entry-content">
                            <h3>资源推荐</h3>
                            <p>智能推荐适合您的学习资源</p>
                        </div>
                        <div class="entry-arrow">→</div>
                    </div>
                    <div class="entry-card" @click="goToExercises">
                        <div class="entry-icon">✏️</div>
                        <div class="entry-content">
                            <h3>练习题生成</h3>
                            <p>个性化练习题推荐</p>
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

const goToResources = () => {
    router.push('/student/recommend/resources');
};

const goToExercises = () => {
    router.push('/student/recommend/exercises');
};
</script>

<style scoped>
.recommend-index {
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
    background: linear-gradient(135deg, #3498db 0%, #2b5ff3 100%);
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

.entry-cards {
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
    color: #3498db;
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
    color: #3498db;
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
    background: #3498db;
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
    background: #3498db;
    top: 50%;
    right: 50px;
    transform: translateY(-50%);
}
</style>