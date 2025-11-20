<template>
    <div class="not-found">
        <div class="content">
            <div class="icon-container">
                <i class="icon">🔍</i>
            </div>
            <h1>404</h1>
            <p class="message">抱歉，您访问的页面不存在</p>
            <router-link class="back-btn" to="/">
                <span class="btn-text">返回首页</span>
                <span class="btn-icon">→</span>
            </router-link>
        </div>
        <div class="decoration">
            <div class="circle circle-1"></div>
            <div class="circle circle-2"></div>
            <div class="circle circle-3"></div>
        </div>
    </div>
</template>

<script setup lang="ts">
// 404页面组件
</script>

<style scoped>
.not-found {
    position: relative;
    height: 100vh;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f7fa;
    overflow: hidden;
}

.content {
    position: relative;
    z-index: 2;
    text-align: center;
    padding: 40px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    max-width: 400px;
    width: 90%;
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
    font-size: 64px;
    background: linear-gradient(135deg, #4c84ff 0%, #2b5ff3 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
    font-weight: 600;
}

.message {
    font-size: 18px;
    color: #666;
    margin-bottom: 32px;
}

.back-btn {
    display: inline-flex;
    align-items: center;
    padding: 12px 32px;
    background: linear-gradient(135deg, #4c84ff 0%, #2b5ff3 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
    box-shadow: 0 4px 15px rgba(76, 132, 255, 0.3);
}

.back-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(76, 132, 255, 0.4);
}

.btn-text {
    margin-right: 8px;
}

.btn-icon {
    font-size: 18px;
    transition: transform 0.3s ease;
}

.back-btn:hover .btn-icon {
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
}

.circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
}

.circle-1 {
    width: 300px;
    height: 300px;
    background: #4c84ff;
    top: -150px;
    left: -150px;
}

.circle-2 {
    width: 400px;
    height: 400px;
    background: #2b5ff3;
    bottom: -200px;
    right: -200px;
}

.circle-3 {
    width: 200px;
    height: 200px;
    background: #4c84ff;
    top: 50%;
    right: 100px;
    transform: translateY(-50%);
}
</style>