<template>
    <div class="register-container">
        <div class="register-box">
            <h1>教学系统注册</h1>
            <form @submit.prevent="handleRegister">
                <div class="form-group">
                    <label for="username">用户名</label>
                    <input type="text" id="username" v-model="username" placeholder="请输入用户名" required />
                </div>
                <div class="form-group">
                    <label for="password">密码</label>
                    <input type="password" id="password" v-model="password" placeholder="请输入密码" required />
                </div>
                <div class="form-group">
                    <label for="confirmPassword">确认密码</label>
                    <input type="password" id="confirmPassword" v-model="confirmPassword" placeholder="请再次输入密码"
                        required />
                </div>
                <div class="form-group">
                    <label for="role">角色</label>
                    <select id="role" v-model="role" required>
                        <option value="">请选择角色</option>
                        <option value="teacher">教师</option>
                        <option value="student">学生</option>
                        <option value="admin">管理员</option>
                    </select>
                </div>
                <div v-if="errorMessage" class="error-message">
                    {{ errorMessage }}
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn-register" :disabled="isRegistering">
                        {{ isRegistering ? '注册中...' : '注册' }}
                    </button>
                    <div class="login-link">
                        已有账号？<router-link to="/login">登录</router-link>
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
const confirmPassword = ref('');
const role = ref('');
const errorMessage = ref('');
const isRegistering = ref(false);

const handleRegister = async () => {
    try {
        // 清除之前的错误信息
        errorMessage.value = '';

        // 表单验证
        if (password.value !== confirmPassword.value) {
            errorMessage.value = '两次输入的密码不一致';
            return;
        }

        if (password.value.length < 3) {
            errorMessage.value = '密码长度不能少于3位';
            return;
        }

        isRegistering.value = true;

        const response = await fetch('http://localhost:8000/users/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username.value,
                password: password.value,
                role: role.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || '注册失败');
        }

        // 注册成功
        alert('注册成功，请登录');
        router.push('/login');
    } catch (error: any) {
        errorMessage.value = error.message || '注册失败，请稍后重试';
    } finally {
        isRegistering.value = false;
    }
};
</script>

<style scoped>
.register-container {
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

.register-box {
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

.btn-register {
    width: 100%;
    padding: 0.75rem;
    background-color: #2ecc71;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s;
}

.btn-register:hover:not(:disabled) {
    background-color: #27ae60;
}

.btn-register:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
}

.login-link {
    text-align: center;
    margin-top: 1rem;
    color: #7f8c8d;
}

.login-link a {
    color: #3498db;
    text-decoration: none;
}

.login-link a:hover {
    text-decoration: underline;
}

.error-message {
    color: #e74c3c;
    margin-bottom: 1rem;
    text-align: center;
    font-size: 0.9rem;
}
</style>