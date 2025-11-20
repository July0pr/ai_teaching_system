<template>
    <div class="student-layout">
        <header class="app-header">
            <div class="logo">
                <h1>教学系统 - 学生端</h1>
            </div>
            <div class="user-info">
                <span>{{ username }}</span>
                <button @click="logout" class="logout-btn">退出登录</button>
            </div>
        </header>

        <div class="layout-content">
            <aside class="sidebar">
                <nav>
                    <ul>
                        <li>
                            <router-link to="/student/recommend" :class="{ active: isRecommendActive }">
                                自学中心
                            </router-link>
                            <ul class="sub-menu" :class="{ show: isRecommendActive }">
                                <li>
                                    <router-link to="/student/recommend/resources" active-class="active">
                                        资源推荐
                                    </router-link>
                                </li>
                                <li>
                                    <router-link to="/student/recommend/exercises" active-class="active">
                                        练习题生成
                                    </router-link>
                                </li>
                            </ul>
                        </li>
                        <li>
                            <router-link to="/student/resources/history" active-class="active">
                                历史记录
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/student/classes" :class="{ active: isClassesActive }">
                                班级中心
                            </router-link>
                        </li>
                    </ul>
                </nav>
            </aside>

            <main class="main-content">
                <router-view></router-view>
            </main>
        </div>

        <!-- 全局Toast组件 -->
        <Toast ref="toastRef" />
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import Toast from '../../components/common/Toast.vue';

const router = useRouter();
const route = useRoute();
const username = ref('学生用户');

// 为Toast组件定义类型
interface ToastInstance {
    showToastMessage: (message: string, type: 'success' | 'error') => void;
}

const toastRef = ref<ToastInstance | null>(null);

// 计算当前路由是否属于自学中心模块
const isRecommendActive = computed(() => {
    return route.path.startsWith('/student/recommend');
});

// 计算当前路由是否属于班级中心模块
const isClassesActive = computed(() => {
    return route.path.startsWith('/student/classes');
});

const logout = () => {
    // 清除登录状态
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userRole');

    // 跳转到登录页
    router.push('/login');
};

// 在全局对象上添加显示Toast的方法
onMounted(() => {
    window.$showToast = (message: string, type: 'success' | 'error' = 'success') => {
        if (toastRef.value) {
            toastRef.value.showToastMessage(message, type);
        }
    };
});
</script>

<style scoped>
.student-layout {
    height: 100%;
    width: 100%;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
}

.app-header {
    background-color: #3498db;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}

.logo h1 {
    margin: 0;
    font-size: 1.5rem;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.logout-btn {
    background-color: transparent;
    color: white;
    border: 1px solid white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.logout-btn:hover {
    background-color: white;
    color: #3498db;
}

.layout-content {
    display: flex;
    flex: 1;
    height: calc(100% - 60px);
    /* 减去header高度 */
    width: 100%;
    overflow: hidden;
}

.sidebar {
    width: 250px;
    height: 100%;
    background-color: #f5f7fa;
    padding: 1rem 0;
    border-right: 1px solid #ddd;
    overflow-y: auto;
}

.sidebar nav ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.sidebar nav ul li {
    margin-bottom: 0.5rem;
}

.sidebar nav a {
    display: block;
    padding: 0.75rem 1.5rem;
    color: #2c3e50;
    text-decoration: none;
    transition: all 0.3s;
    position: relative;
}

.sidebar nav a:hover,
.sidebar nav a.active {
    background-color: #3498db;
    color: white;
}

.sub-menu {
    padding-left: 1.5rem !important;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease-out;
}

.sub-menu.show {
    max-height: 200px;
}

.sub-menu a {
    padding: 0.5rem 1.5rem !important;
    font-size: 0.9rem;
    opacity: 0.9;
}

.sub-menu a:hover {
    opacity: 1;
}

.main-content {
    flex: 1;
    height: 100%;
    width: 100%;
    padding: 1.5rem;
    overflow-y: auto;
}
</style>