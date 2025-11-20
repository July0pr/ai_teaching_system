<template>
    <div class="admin-layout">
        <header class="app-header">
            <div class="logo">
                <h1>教学系统 - 管理端</h1>
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
                            <router-link to="/admin/users" :class="{ active: isUsersActive }">
                                用户管理
                            </router-link>
                        </li>
                        <li>
                            <router-link to="/admin/resources" :class="{ active: isResourcesActive }">
                                资源管理
                            </router-link>
                        </li>
                    </ul>
                </nav>
            </aside>

            <main class="main-content">
                <router-view></router-view>
            </main>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const username = ref('管理员');

// 计算当前路由是否属于用户管理模块
const isUsersActive = computed(() => {
    return route.path.startsWith('/admin/users');
});

// 计算当前路由是否属于资源管理模块
const isResourcesActive = computed(() => {
    return route.path === '/admin/resources';
});

const logout = () => {
    // 清除登录状态
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userRole');

    // 跳转到登录页
    router.push('/login');
};
</script>

<style scoped>
.admin-layout {
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
    background-color: #2c3e50;
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
    color: #2c3e50;
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
}

.sidebar nav a:hover,
.sidebar nav a.active {
    background-color: #4c84ff;
    color: white;
}

.main-content {
    flex: 1;
    height: 100%;
    width: 100%;
    padding: 1.5rem;
    overflow-y: auto;
}

.sub-menu {
    padding-left: 1.5rem !important;
}

.sub-menu a {
    padding: 0.5rem 1.5rem !important;
    font-size: 0.9rem;
}
</style>