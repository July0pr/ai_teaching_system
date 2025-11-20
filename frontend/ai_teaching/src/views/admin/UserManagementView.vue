<template>
    <div class="user-management">
        <h2>用户管理</h2>

        <!-- 搜索和操作区 -->
        <div class="top-actions">
            <div class="search-area">
                <input type="text" v-model="searchQuery" placeholder="搜索..." class="search-input" />
                <button class="search-btn" @click="searchUsers">搜索</button>
            </div>
            <button class="add-user-btn" @click="showAddUserModal = true">添加用户</button>
        </div>

        <!-- 用户类型筛选 -->
        <div class="filter-tabs">
            <button v-for="type in userTypes" :key="type.value"
                :class="['filter-tab', { active: selectedType === type.value }]" @click="filterUsersByType(type.value)">
                {{ type.label }}
            </button>
        </div>

        <!-- 用户列表 -->
        <div class="user-table">
            <table>
                <thead>
                    <tr>
                        <th>用户名</th>
                        <th>类别</th>
                        <th>用户状态</th>
                        <th>学工号</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in filteredUsers" :key="user.id">
                        <td>{{ user.username }}</td>
                        <td>{{ user.role === 'teacher' ? '教师' :
                            user.role === 'student' ? '学生' : user.role }}</td>
                        <td>
                            <span :class="['status-tag', user.status]">
                                {{ user.status }}
                            </span>
                        </td>
                        <td>{{ user.id }}</td>
                        <td class="actions">
                            <button class="action-btn" :class="user.status === '已禁用' ? 'restore' : 'ban'"
                                @click="toggleUserStatus(user.id)">
                                {{ user.status === '已禁用' ? '恢复' : '禁用' }}
                            </button>
                            <button class="action-btn reset" @click="resetPassword(user.id)">重置密码</button>
                            <button class="action-btn delete" @click="deleteUser(user.id)">注销</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 添加用户对话框 -->
        <div v-if="showAddUserModal" class="modal">
            <div class="modal-content">
                <h3>添加用户</h3>
                <form @submit.prevent="addUser">
                    <div class="form-group">
                        <label>用户名</label>
                        <input type="text" v-model="newUser.username" required />
                    </div>
                    <div class="form-group">
                        <label>类别</label>
                        <select v-model="newUser.role" required>
                            <option value="">请选择类别</option>
                            <option value="teacher">教师</option>
                            <option value="student">学生</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>初始密码</label>
                        <input type="password" v-model="newUser.password" required />
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="cancel-btn" @click="showAddUserModal = false">取消</button>
                        <button type="submit" class="submit-btn">确定</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

// 定义用户类型接口
interface User {
    id: number;
    username: string;
    role: string;
    status: string;
    number?: string;
    created_at: string;
    updated_at: string;
}

const API_BASE_URL = 'http://localhost:8000'; // 后端API基础URL
const searchQuery = ref('');
const selectedType = ref('all');
const showAddUserModal = ref(false);

// 用户类型选项
const userTypes = [
    { label: '全部', value: 'all' },
    { label: '教师', value: 'teacher' },
    { label: '学生', value: 'student' }
];

// 新用户表单数据
const newUser = ref({
    username: '',
    role: '',
    password: ''
});

// 用户数据
const users = ref<User[]>([]);
const loading = ref(false);
const error = ref('');

// 加载用户列表
const loadUsers = async (role: string | null = null) => {
    loading.value = true;
    error.value = '';
    try {
        let url = `${API_BASE_URL}/users/`;
        if (role && role !== 'all') {
            url += `?role=${role}`;
        }
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('获取用户列表失败');
        }
        const data = await response.json();
        users.value = data;
    } catch (err: any) {
        console.error('加载用户列表出错:', err);
        error.value = err.message;
    } finally {
        loading.value = false;
    }
};

// 根据筛选条件过滤用户
const filteredUsers = computed(() => {
    return users.value.filter(user => {
        const matchesSearch = user.username.includes(searchQuery.value) ||
            (user.number && user.number.includes(searchQuery.value));
        const matchesType = selectedType.value === 'all' || user.role === selectedType.value;
        return matchesSearch && matchesType;
    });
});

// 按类型筛选用户
const filterUsersByType = (type: string) => {
    selectedType.value = type;
    if (type !== 'all') {
        loadUsers(type);
    } else {
        loadUsers();
    }
};

// 搜索用户
const searchUsers = () => {
    // 客户端搜索，因为后端没有提供搜索接口
    // 如果后端提供了搜索接口，可以调用后端API
    console.log('搜索:', searchQuery.value);
};

// 切换用户状态（禁用/启用）
const toggleUserStatus = async (userId: number) => {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/toggle-status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error('操作失败');
        }

        const updatedUser = await response.json();
        // 更新本地用户数据
        users.value = users.value.map(user =>
            user.id === userId ? updatedUser : user
        );
    } catch (err: any) {
        console.error('切换用户状态失败:', err);
        alert('操作失败: ' + err.message);
    }
};

// 添加用户
const addUser = async () => {
    try {
        const userData = {
            username: newUser.value.username,
            password: newUser.value.password,
            role: newUser.value.role
        };

        const response = await fetch(`${API_BASE_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            throw new Error('添加用户失败');
        }

        const newUserData = await response.json();
        // 添加到本地用户列表
        users.value.push(newUserData as User);

        // 关闭模态框并重置表单
        showAddUserModal.value = false;
        newUser.value = { username: '', role: '', password: '' };

        // 重新加载用户列表
        loadUsers(selectedType.value !== 'all' ? selectedType.value : null);
    } catch (err: any) {
        console.error('添加用户失败:', err);
        alert('添加用户失败: ' + err.message);
    }
};

// 重置密码
const resetPassword = async (userId: number) => {
    if (!confirm('确定要重置该用户的密码吗？默认密码为：123456')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId
            })
        });

        if (!response.ok) {
            throw new Error('重置密码失败');
        }

        alert('密码已重置为：123456');
    } catch (err: any) {
        console.error('重置密码失败:', err);
        alert('重置密码失败: ' + err.message);
    }
};

// 删除用户
const deleteUser = async (userId: number) => {
    if (!confirm('确定要注销该用户吗？此操作不可恢复。')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('删除用户失败');
        }

        // 从本地列表中移除
        users.value = users.value.filter(user => user.id !== userId);
        alert('用户已成功注销');
    } catch (err: any) {
        console.error('删除用户失败:', err);
        alert('删除用户失败: ' + err.message);
    }
};

// 组件挂载时加载用户列表
onMounted(() => {
    loadUsers();
});
</script>

<style scoped>
.user-management {
    padding: 20px;
}

h2 {
    margin-bottom: 20px;
    color: #333;
}

.top-actions {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
}

.search-area {
    display: flex;
    gap: 10px;
}

.search-input {
    width: 300px;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.search-btn {
    padding: 8px 20px;
    background-color: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
    }
    
    .search-btn:hover {
        background-color: #3a70e3;
}

.add-user-btn {
    padding: 8px 20px;
    background-color: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.filter-tabs {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
}

.filter-tab {
    padding: 8px 20px;
    background-color: #f5f7fa;
    border: none;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
    transition: all 0.3s;
}

.filter-tab.active {
    background-color: #4c84ff;
    color: white;
}

.user-table {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    color: #666;
    font-weight: normal;
}

.status-tag {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.status-tag.正常 {
    background-color: #e3f2fd;
    color: #4c84ff;
}

.status-tag.已禁用 {
    background-color: #ffebee;
    color: #dc3545;
}

.actions {
    display: flex;
    gap: 8px;
}

.action-btn {
    padding: 4px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    color: white;
}

.action-btn.ban {
    background-color: #4c84ff;
}

.action-btn.restore {
    background-color: #28a745;
}

.action-btn.reset {
    background-color: #ffc107;
}

.action-btn.delete {
    background-color: #dc3545;
}

/* 模态框样式 */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 24px;
    border-radius: 8px;
    width: 90%;
    max-width: 400px;
}

.modal-content h3 {
    margin: 0 0 20px 0;
    color: #333;
}

.form-group {
    margin-bottom: 16px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #666;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
}

.cancel-btn {
    padding: 8px 20px;
    background-color: #f5f7fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
}

.submit-btn {
    padding: 8px 20px;
    background-color: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
</style>