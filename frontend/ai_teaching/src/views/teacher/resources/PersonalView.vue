<template>
    <div class="personal-view">
        <!-- 顶部操作区 -->
        <div class="top-actions">
            <div class="search-bar">
                <input type="text" v-model="searchQuery" placeholder="单击输入关键词或标题" @input="handleSearch" />
                <button class="search-btn" @click="handleSearch">搜索</button>
            </div>
            <label class="upload-btn">
                + 上传资源
                <input type="file" style="display: none" @change="handleUpload" />
            </label>
        </div>

        <!-- 资源类型标签 -->
        <div class="resource-types">
            <button v-for="type in resourceTypes" :key="type.value"
                :class="['type-btn', { active: type.value === activeType }]" @click="activeType = type.value">
                {{ type.label }}
            </button>
        </div>

        <!-- 资源列表 -->
        <div class="resource-list">
            <table>
                <thead>
                    <tr>
                        <th class="name-col">名称</th>
                        <th class="type-col">类型</th>
                        <th class="date-col">生成时间</th>
                        <th class="actions-col">操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in resources" :key="item.id">
                        <td class="name-col">
                            <div class="resource-name">
                                <div class="resource-tag" :class="getTagClass(item.resource_type)">{{
                                    getTagText(item.resource_type) }}</div>
                                {{ item.resource_name }}
                            </div>
                        </td>
                        <td class="type-col">{{ item.resource_type }}</td>
                        <td class="date-col">{{ formatDate(item.created_at) }}</td>
                        <td class="actions-col">
                            <button class="action-btn preview" @click="previewResource(item)">预览</button>
                            <button class="action-btn publish" @click="showPublishDialog(item)">发布</button>
                            <button class="action-btn delete" @click="deleteResource(item.id)">删除</button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <!-- 加载中状态 -->
            <div v-if="isLoading" class="loading">加载中...</div>

            <!-- 查看更多按钮 -->
            <div v-if="!isLoading && resources.length > 0" class="load-more">
                <button class="more-btn" @click="loadMore">查看更多</button>
            </div>
        </div>

        <!-- 发布资源对话框 -->
        <div v-if="showPublishModal" class="modal">
            <div class="modal-content">
                <h3>发布资源到班级</h3>
                <form @submit.prevent="publishResource">
                    <div class="form-group">
                        <label for="classSelect">选择班级</label>
                        <select id="classSelect" v-model="publishForm.classId" required>
                            <option value="">请选择班级</option>
                            <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                                {{ cls.class_name }}
                            </option>
                        </select>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="cancel-btn" @click="closePublishDialog">取消</button>
                        <button type="submit" class="submit-btn">确定</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 预览对话框 -->
        <div v-if="showPreview" class="preview-dialog">
            <div class="preview-content">
                <div class="preview-header">
                    <h3>{{ currentPreviewResource?.resource_name }}</h3>
                    <button class="close-btn" @click="closePreview">×</button>
                </div>
                <div class="preview-body">
                    <iframe v-if="isPPT(currentPreviewResource?.resource_type)" :src="currentPreviewResource?.file_path"
                        frameborder="0"></iframe>
                    <video v-else-if="isVideo(currentPreviewResource?.resource_type)"
                        :src="currentPreviewResource?.file_path" controls></video>
                    <img v-else-if="isImage(currentPreviewResource?.resource_type)"
                        :src="currentPreviewResource?.file_path" alt="预览图片" />
                    <div v-else class="document-preview">
                        <p>当前资源类型不支持预览，请<a :href="currentPreviewResource?.file_path" target="_blank">点击下载</a>后查看</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { debounce } from 'lodash';

interface Resource {
    id: number;
    resource_name: string;
    resource_type: string;
    file_path: string;
    created_at: string;
}

const searchQuery = ref('');
const activeType = ref('all');
const resources = ref<Resource[]>([]);
const isLoading = ref(false);

// 预览相关状态
const showPreview = ref(false);
const currentPreviewResource = ref<Resource | null>(null);

// 资源类型
const resourceTypes = [
    { label: '全部', value: 'all' },
    { label: '教材', value: '教材' },
    { label: '教案', value: '教案' },
    { label: '习题', value: '习题' },
    { label: '图片', value: '图片' },
    { label: '视频', value: '视频' },
    { label: '课件', value: 'PPT' }
];

// 班级列表
const classes = ref<{ id: number; class_name: string }[]>([]);
const showPublishModal = ref(false);
const selectedResource = ref<Resource | null>(null);
const publishForm = ref({
    classId: ''
});

// 获取资源列表
const fetchResources = async () => {
    try {
        isLoading.value = true;
        const userId = localStorage.getItem('userId');

        // 构建查询参数
        const params = new URLSearchParams();
        if (searchQuery.value) {
            params.append('search_query', searchQuery.value);
        }
        if (activeType.value !== 'all') {
            params.append('resource_type', activeType.value);
        }

        const response = await fetch(`http://localhost:8000/resources/user/${userId}?${params.toString()}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取资源列表失败');
        }

        const data = await response.json();
        resources.value = data;
    } catch (error) {
        console.error('获取资源列表错误:', error);
    } finally {
        isLoading.value = false;
    }
};

// 处理搜索
const handleSearch = () => {
    fetchResources();
};

// 监听资源类型变化
watch(activeType, () => {
    fetchResources();
});

// 监听搜索关键词变化（实现实时搜索）
watch(searchQuery, debounce(() => {
    fetchResources();
}, 500));

// 处理上传
const handleUpload = async (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://localhost:8000/resources/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('上传资源失败');
        }

        // 刷新资源列表
        fetchResources();
    } catch (error) {
        console.error('上传资源错误:', error);
    }
};

// 删除资源
const deleteResource = async (resourceId: number) => {
    try {
        const response = await fetch(`http://localhost:8000/resources/${resourceId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('删除资源失败');
        }

        // 刷新资源列表
        fetchResources();
    } catch (error) {
        console.error('删除资源错误:', error);
    }
};

// 预览资源
const previewResource = (resource: Resource) => {
    currentPreviewResource.value = resource;
    showPreview.value = true;
};

// 关闭预览
const closePreview = () => {
    showPreview.value = false;
    currentPreviewResource.value = null;
};

// 判断资源类型
const isPPT = (type: string | undefined) => {
    return type === 'PPT' || type?.includes('ppt');
};

const isVideo = (type: string | undefined) => {
    return type === '视频' || type?.includes('video') || type?.includes('mp4');
};

const isImage = (type: string | undefined) => {
    return type === '图片' || type?.includes('image') || type?.includes('jpg') || type?.includes('png');
};

// 获取资源标签样式类
const getTagClass = (type: string) => {
    if (isPPT(type)) return 'ppt-tag';
    if (isVideo(type)) return 'video-tag';
    if (isImage(type)) return 'image-tag';
    return 'other-tag';
};

// 获取资源标签文本
const getTagText = (type: string) => {
    if (isPPT(type)) return 'PPT';
    if (isVideo(type)) return '视频';
    if (isImage(type)) return '图片';
    if (type === '教材') return '教材';
    if (type === '教案') return '教案';
    if (type === '习题') return '习题';
    return '其他';
};

// 格式化日期
const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
};

// 加载更多
const loadMore = () => {
    // 实现加载更多逻辑
};

// 获取教师的班级列表
const fetchTeacherClasses = async () => {
    try {
        const teacherId = localStorage.getItem('userId');
        const response = await fetch(`http://localhost:8000/teachers/${teacherId}/classes`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取班级列表失败');
        }

        classes.value = await response.json();
    } catch (error: any) {
        console.error('获取班级列表错误:', error);
        window.$showToast('获取班级列表失败', 'error');
    }
};

// 显示发布对话框
const showPublishDialog = (resource: Resource) => {
    selectedResource.value = resource;
    showPublishModal.value = true;
};

// 关闭发布对话框
const closePublishDialog = () => {
    showPublishModal.value = false;
    selectedResource.value = null;
    publishForm.value.classId = '';
};

// 发布资源
const publishResource = async () => {
    try {
        if (!selectedResource.value) {
            throw new Error('未选择资源');
        }

        const response = await fetch('http://localhost:8000/classes/resources/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                class_id: parseInt(publishForm.value.classId),
                resource_type: selectedResource.value.resource_type,
                resource_name: selectedResource.value.resource_name,
                file_path: selectedResource.value.file_path,
                uploaded_by: parseInt(localStorage.getItem('userId') || '0')
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '发布资源失败');
        }

        // 显示成功提示
        window.$showToast('发布成功！', 'success');
        closePublishDialog();
    } catch (error: any) {
        console.error('发布资源错误:', error);
        window.$showToast(error.message || '发布资源失败，请稍后重试', 'error');
    }
};

onMounted(() => {
    fetchResources();
    fetchTeacherClasses();
});
</script>

<style scoped>
.personal-view {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.top-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}

.search-bar {
    display: flex;
    gap: 10px;
    flex: 1;
    max-width: 500px;
}

.search-bar input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
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

.upload-btn {
    padding: 8px 20px;
    background-color: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.resource-types {
    display: flex;
    gap: 10px;
    padding: 10px 0;
}

.type-btn {
    padding: 6px 16px;
    border: none;
    border-radius: 4px;
    background-color: #f5f7fa;
    color: #666;
    cursor: pointer;
    transition: all 0.3s;
}

.type-btn.active {
    background-color: #4c84ff;
    color: white;
}

.resource-list {
    flex: 1;
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow-y: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}

th {
    text-align: left;
    padding: 12px;
    color: #666;
    font-weight: normal;
    border-bottom: 1px solid #eee;
}

td {
    padding: 12px;
    border-bottom: 1px solid #eee;
    vertical-align: middle;
}

.name-col {
    width: 40%;
}

.type-col {
    width: 15%;
}

.date-col {
    width: 20%;
}

.actions-col {
    width: 25%;
}

.resource-name {
    display: flex;
    align-items: center;
    gap: 8px;
}

.resource-tag {
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 12px;
    color: white;
    min-width: 40px;
    text-align: center;
}

.ppt-tag {
    background-color: #4c84ff;
}

.video-tag {
    background-color: #2ecc71;
}

.image-tag {
    background-color: #9b59b6;
}

.other-tag {
    background-color: #7f8c8d;
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
    font-size: 14px;
    margin-right: 8px;
}

.action-btn.preview {
    background-color: #4c84ff;
    color: white;
}

.action-btn.publish {
    background-color: #4c84ff;
    color: white;
}

.action-btn.delete {
    background-color: #ff4c4c;
    color: white;
}

.load-more {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}

.more-btn {
    padding: 8px 24px;
    background-color: #f5f7fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
}

.more-btn:hover {
    background-color: #e6e8eb;
}

.loading {
    text-align: center;
    padding: 20px;
    color: #666;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}

.modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    width: 500px;
    max-width: 100%;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
}

.form-group select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    background-color: white;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.cancel-btn {
    padding: 8px 20px;
    background-color: #ff4c4c;
    color: white;
    border: none;
    border-radius: 4px;
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

select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    background-color: white;
}

/* 预览对话框样式 */
.preview-dialog {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.preview-content {
    background: white;
    border-radius: 8px;
    width: 80%;
    height: 80%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.preview-header {
    padding: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
}

.preview-header h3 {
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #666;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
}

.close-btn:hover {
    background: #f5f5f5;
}

.preview-body {
    flex: 1;
    padding: 16px;
    overflow: auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

.preview-body iframe,
.preview-body video,
.preview-body img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.document-preview {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
}

.document-preview a {
    color: #4c84ff;
    text-decoration: none;
    margin-left: 5px;
}

.document-preview a:hover {
    text-decoration: underline;
}
</style>