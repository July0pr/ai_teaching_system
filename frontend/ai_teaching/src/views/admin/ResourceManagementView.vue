<template>
    <div class="resource-management">
        <h2>资源管理</h2>

        <!-- 顶部搜索和操作区 -->
        <div class="top-actions">
            <div class="search-area">
                <input type="text" v-model="searchQuery" placeholder="搜索..." class="search-input"
                    @input="handleSearch" />
                <button class="search-btn" @click="handleSearch">搜索</button>
            </div>
            <button class="upload-resource-btn" @click="triggerFileInput">上传资源</button>
            <input type="file" ref="fileInput" style="display: none" @change="handleUpload" />
        </div>

        <!-- 资源类型筛选 -->
        <div class="filter-tabs">
            <button v-for="type in resourceTypes" :key="type.value"
                :class="['filter-tab', { active: selectedType === type.value }]" @click="selectedType = type.value">
                {{ type.label }}
            </button>
        </div>

        <!-- 资源列表 -->
        <div class="resource-table">
            <table>
                <thead>
                    <tr>
                        <th>名称</th>
                        <th>类型</th>
                        <th>上传时间</th>
                        <th>上传者</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="resource in filteredResources" :key="resource.id">
                        <td>
                            <div class="resource-name">
                                <div class="resource-tag" :class="getTagClass(resource.resource_type)">
                                    {{ getTagText(resource.resource_type) }}
                                </div>
                                {{ resource.resource_name }}
                            </div>
                        </td>
                        <td>{{ resource.resource_type }}</td>
                        <td>{{ formatDate(resource.created_at) }}</td>
                        <td>{{ resource.uploader }}</td>
                        <td class="actions">
                            <button class="action-btn preview" @click="previewResource(resource)">
                                预览
                            </button>
                            <button class="action-btn delete" @click="deleteResource(resource.id)">
                                删除
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <!-- 加载中状态 -->
            <div v-if="isLoading" class="loading">加载中...</div>

            <!-- 查看更多按钮 -->
            <div v-if="!isLoading && filteredResources.length > 0" class="load-more">
                <button class="more-btn" @click="loadMore">查看更多</button>
            </div>

            <!-- 无数据提示 -->
            <div v-if="!isLoading && filteredResources.length === 0" class="empty-message">
                没有找到符合条件的资源
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

        <!-- 操作提示 -->
        <div v-if="showToast" class="toast" :class="toastType">
            {{ toastMessage }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { debounce } from 'lodash';

interface Resource {
    id: number;
    resource_name: string;
    resource_type: string;
    file_path: string;
    uploader: string;
    uploader_id: number;
    created_at: string;
}

const searchQuery = ref('');
const selectedType = ref('');
const resources = ref<Resource[]>([]);
const isLoading = ref(false);
const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref<'success' | 'error'>('success');
const fileInput = ref<HTMLInputElement | null>(null);

// 预览相关状态
const showPreview = ref(false);
const currentPreviewResource = ref<Resource | null>(null);

// 资源类型选项
const resourceTypes = [
    { label: '全部', value: '' },
    { label: '教材', value: '教材' },
    { label: '教案', value: '教案' },
    { label: '习题', value: '习题' },
    { label: '图片', value: '图片' },
    { label: '视频', value: '视频' },
    { label: 'PPT', value: 'PPT' }
];

// 根据筛选条件过滤资源
const filteredResources = computed(() => {
    return resources.value;
});

// 获取资源列表
const fetchResources = async () => {
    try {
        isLoading.value = true;

        // 构建查询参数
        const params = new URLSearchParams();
        if (searchQuery.value) {
            params.append('search_query', searchQuery.value);
        }
        if (selectedType.value) {
            params.append('resource_type', selectedType.value);
        }

        const response = await fetch(`http://localhost:8000/share-resources/?${params.toString()}`, {
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
        showToastMessage('获取资源列表失败', 'error');
    } finally {
        isLoading.value = false;
    }
};

// 处理搜索
const handleSearch = debounce(() => {
    fetchResources();
}, 500);

// 监听资源类型变化
watch([selectedType], () => {
    fetchResources();
});

// 处理上传
const handleUpload = async (event: Event) => {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) return;

    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        isLoading.value = true;
        const response = await fetch('http://localhost:8000/share-resources/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('上传资源失败');
        }

        showToastMessage('资源上传成功', 'success');
        // 刷新资源列表
        fetchResources();
    } catch (error) {
        console.error('上传资源错误:', error);
        showToastMessage('上传资源失败', 'error');
    } finally {
        isLoading.value = false;
        // 清空文件输入框
        input.value = '';
    }
};

// 删除资源
const deleteResource = async (resourceId: number) => {
    if (!confirm('确定要删除此资源吗？此操作不可恢复')) {
        return;
    }

    try {
        isLoading.value = true;
        const response = await fetch(`http://localhost:8000/share-resources/${resourceId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('删除资源失败');
        }

        showToastMessage('资源删除成功', 'success');
        // 刷新资源列表
        fetchResources();
    } catch (error) {
        console.error('删除资源错误:', error);
        showToastMessage('删除资源失败', 'error');
    } finally {
        isLoading.value = false;
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

// Toast消息提示
const showToastMessage = (message: string, type: 'success' | 'error' = 'success') => {
    toastMessage.value = message;
    toastType.value = type;
    showToast.value = true;
    setTimeout(() => {
        showToast.value = false;
    }, 3000);
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
    if (type === '教材') return 'book-tag';
    if (type === '教案') return 'plan-tag';
    if (type === '习题') return 'exercise-tag';
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
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// 加载更多
const loadMore = () => {
    // 实现加载更多逻辑，这里暂未实现分页
    showToastMessage('已加载全部资源', 'success');
};

// 触发文件输入
const triggerFileInput = () => {
    if (fileInput.value) {
        fileInput.value.click();
    }
};

onMounted(() => {
    fetchResources();
});
</script>

<style scoped>
.resource-management {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
}

h2 {
    margin-bottom: 20px;
    color: #333;
}

.top-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
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

.upload-resource-btn {
    padding: 8px 20px;
    background-color: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.upload-resource-btn:hover {
    background-color: #3a70e3;
}

.filter-tabs {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
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

.resource-table {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow-y: auto;
    flex: 1;
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

.resource-name {
    display: flex;
    align-items: center;
    gap: 8px;
}

.resource-tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: white;
}

.ppt-tag {
    background-color: #4c84ff;
}

.video-tag {
    background-color: #27ae60;
}

.image-tag {
    background-color: #f1c40f;
}

.book-tag {
    background-color: #e67e22;
}

.plan-tag {
    background-color: #9b59b6;
}

.exercise-tag {
    background-color: #e74c3c;
}

.other-tag {
    background-color: #95a5a6;
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
    transition: all 0.3s;
}

.action-btn.preview {
    background-color: #27ae60;
}

.action-btn.delete {
    background-color: #e74c3c;
}

.action-btn:hover {
    opacity: 0.9;
}

.loading {
    text-align: center;
    padding: 20px;
    color: #666;
}

.load-more {
    text-align: center;
    margin-top: 20px;
}

.more-btn {
    padding: 8px 20px;
    background-color: #f5f7fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    color: #666;
    transition: all 0.3s;
}

.more-btn:hover {
    background-color: #eee;
}

.empty-message {
    text-align: center;
    padding: 40px 0;
    color: #999;
    font-style: italic;
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
    color: #333;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #666;
    cursor: pointer;
}

.preview-body {
    flex: 1;
    padding: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: auto;
}

.preview-body iframe,
.preview-body video,
.preview-body img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.document-preview {
    text-align: center;
    padding: 40px;
    background: #f5f7fa;
    border-radius: 8px;
}

.document-preview a {
    color: #4c84ff;
    text-decoration: none;
}

.document-preview a:hover {
    text-decoration: underline;
}

/* Toast提示样式 */
.toast {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 24px;
    border-radius: 4px;
    font-size: 14px;
    z-index: 1000;
    animation: fadeInOut 3s ease-in-out;
}

.toast.success {
    background-color: #2ecc71;
    color: white;
}

.toast.error {
    background-color: #e74c3c;
    color: white;
}

@keyframes fadeInOut {
    0% {
        opacity: 0;
        transform: translate(-50%, 20px);
    }

    15% {
        opacity: 1;
        transform: translate(-50%, 0);
    }

    85% {
        opacity: 1;
        transform: translate(-50%, 0);
    }

    100% {
        opacity: 0;
        transform: translate(-50%, -20px);
    }
}
</style>