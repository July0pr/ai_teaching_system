<template>
    <div class="login-container">
        <div class="login-box">
            <h1>教学系统登录</h1>
            <form @submit.prevent="handleLogin">
                <div class="form-group">
                    <label for="username">用户名</label>
                    <input type="text" id="username" v-model="username" placeholder="请输入用户名" required />
                </div>
                <div class="form-group">
                    <label for="password">密码</label>
                    <input type="password" id="password" v-model="password" placeholder="请输入密码" required />
                </div>
                <div v-if="errorMessage" class="error-message">
                    {{ errorMessage }}
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn-login">登录</button>
                    <div class="extra-links">
                        <router-link to="/register">注册账号</router-link>
                        <a href="#" @click.prevent="forgotPassword">忘记密码</a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const password = ref('');
const errorMessage = ref('');

const handleLogin = async () => {
    try {
        const response = await fetch('http://localhost:8000/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username.value,
                password: password.value
            })
        });

        if (!response.ok) {
            const error = await response.json();
            if (response.status === 403) {
                throw new Error(error.detail || '该账号已被禁用，请联系管理员');
            } else {
                throw new Error(error.detail || '登录失败');
            }
        }

        const data = await response.json();

        // 保存用户信息和token到localStorage
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('userRole', data.role);
        localStorage.setItem('userId', data.id.toString());
        localStorage.setItem('username', data.username);
        localStorage.setItem('token', data.token);

        // 根据角色跳转到不同的页面
        if (data.role === 'teacher') {
            router.push('/teacher/workbench');
        } else if (data.role === 'student') {
            router.push('/student/recommend');
        } else if (data.role === 'admin') {
            router.push('/admin/users');
        }
    } catch (error: any) {
        errorMessage.value = error.message || '登录失败，请检查用户名和密码是否正确';
    }
};

const forgotPassword = () => {
    alert('请联系管理员重置密码');
};
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    height: 100%;
    width: 100%;
    margin: 0;
    padding: 0;
    background-color: #f5f7fa;
}

.login-box {
    width: 400px;
    padding: 2rem;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h1 {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 2rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

label {
    display: block;
    margin-bottom: 0.5rem;
    color: #34495e;
    font-weight: 500;
}

input,
select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

input:focus,
select:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-actions {
    margin-top: 2rem;
}

.btn-login {
    width: 100%;
    padding: 0.75rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s;
}

.btn-login:hover {
    background-color: #2980b9;
}

.extra-links {
    display: flex;
    justify-content: space-between;
    margin-top: 1rem;
}

.extra-links a {
    color: #3498db;
    text-decoration: none;
    font-size: 0.9rem;
}

.extra-links a:hover {
    text-decoration: underline;
}

.error-message {
    color: #e74c3c;
    margin-bottom: 1rem;
    text-align: center;
    font-size: 0.9rem;
}
</style>