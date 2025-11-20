<template>
    <div class="step3-view">
        <div class="main-content">
            <div class="header">
                <h2>资源推荐</h2>
                <button class="download-btn" @click="downloadSelected" :disabled="!hasSelectedResources">
                    下载选中资源
                </button>
            </div>

            <!-- 课件部分 -->
            <div class="resource-section">
                <h3>课件</h3>
                <div class="resource-list">
                    <div v-for="resource in resourcesByType.courseware" :key="resource.id" class="resource-item"
                        :class="{ selected: selectedResources.courseware.includes(resource.id.toString()) }"
                        @click="toggleSelection('courseware', resource.id.toString())">
                        <div class="match-rate">{{ resource.priority }}%</div>
                        <div class="thumbnail">{{ resource.resource_name }}</div>
                        <div v-if="selectedResources.courseware.includes(resource.id.toString())" class="check-icon">✓
                        </div>
                        <button class="preview-btn" @click.stop="previewResource(resource)">预览</button>
                    </div>
                    <div v-if="resourcesByType.courseware.length === 0" class="empty-message">
                        暂无推荐课件
                    </div>
                </div>
            </div>

            <!-- 视频部分 -->
            <div class="resource-section">
                <h3>视频</h3>
                <div class="resource-list">
                    <div v-for="resource in resourcesByType.video" :key="resource.id" class="resource-item"
                        :class="{ selected: selectedResources.video.includes(resource.id.toString()) }"
                        @click="toggleSelection('video', resource.id.toString())">
                        <div class="match-rate">{{ resource.priority }}%</div>
                        <div class="thumbnail">{{ resource.resource_name }}</div>
                        <div v-if="selectedResources.video.includes(resource.id.toString())" class="check-icon">✓</div>
                        <button class="preview-btn" @click.stop="previewResource(resource)">预览</button>
                    </div>
                    <div v-if="resourcesByType.video.length === 0" class="empty-message">
                        暂无推荐视频
                    </div>
                </div>
            </div>

            <!-- 相关图片 -->
            <div class="resource-section">
                <h3>相关图片</h3>
                <div class="resource-list">
                    <div v-for="resource in resourcesByType.image" :key="resource.id" class="resource-item"
                        :class="{ selected: selectedResources.image.includes(resource.id.toString()) }"
                        @click="toggleSelection('image', resource.id.toString())">
                        <div class="match-rate">{{ resource.priority }}%</div>
                        <div class="thumbnail">{{ resource.resource_name }}</div>
                        <div v-if="selectedResources.image.includes(resource.id.toString())" class="check-icon">✓</div>
                        <button class="preview-btn" @click.stop="previewResource(resource)">预览</button>
                    </div>
                    <div v-if="resourcesByType.image.length === 0" class="empty-message">
                        暂无推荐图片
                    </div>
                </div>
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
                    <iframe
                        v-if="getResourceType(currentPreviewResource) === 'courseware' && !isPptx(currentPreviewResource?.file_path)"
                        :src="`http://localhost:8000/resources/${currentPreviewResource?.resource_id}/preview`"
                        frameborder="0"></iframe>
                    <div v-else-if="getResourceType(currentPreviewResource) === 'courseware' && isPptx(currentPreviewResource?.file_path)"
                        class="pptx-preview">
                        <div class="pptx-info">
                            <i class="pptx-icon">📊</i>
                            <h4>PPT文件需要下载后查看</h4>
                            <p>您正在预览的是PowerPoint演示文稿，浏览器无法直接显示此类文件。</p>
                            <button class="download-ppt-btn" @click="downloadResource(currentPreviewResource)">
                                下载PPT文件
                            </button>
                        </div>
                    </div>
                    <video v-else-if="getResourceType(currentPreviewResource) === 'video'"
                        :src="`http://localhost:8000/resources/${currentPreviewResource?.resource_id}/preview`"
                        controls></video>
                    <img v-else-if="getResourceType(currentPreviewResource) === 'image'"
                        :src="`http://localhost:8000/resources/${currentPreviewResource?.resource_id}/preview`"
                        alt="预览图片" />
                    <div v-else class="preview-fallback">
                        无法预览此类型的资源
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { reactive, computed, ref, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';
import { useLoadingStore } from '@/stores/loading';
import { apiWithLoading } from '@/utils/api';

const router = useRouter();
const loadingStore = useLoadingStore();

// 加载的计时相关状态
const waitingStartTime = ref(0);
const waitingInterval = ref<number | null>(null);
const maxWaitTime = 20 * 60 * 1000; // 20分钟，单位为毫秒

interface Resource {
    id: number;
    resource_id: number;
    resource_name: string;
    resource_type: string;
    file_path: string;
    priority: number;
    reason?: string;
}

interface SelectedResources {
    courseware: string[];
    video: string[];
    image: string[];
}

const resources = ref<Resource[]>([]);

// 预览相关状态
const showPreview = ref(false);
const currentPreviewResource = ref<Resource | null>(null);

const selectedResources = reactive<SelectedResources>({
    courseware: [],
    video: [],
    image: []
});

// 按资源类型分组
const resourcesByType = computed(() => {
    const result = {
        courseware: [] as Resource[],
        video: [] as Resource[],
        image: [] as Resource[]
    };

    resources.value.forEach(resource => {
        const type = resource.resource_type.toLowerCase();
        if (type === 'ppt' || type === '课件' || type === 'courseware') {
            result.courseware.push(resource);
        } else if (type === '视频' || type === 'video') {
            result.video.push(resource);
        } else if (type === '图片' || type === 'image') {
            result.image.push(resource);
        } else {
            // 默认归类为课件
            result.courseware.push(resource);
        }
    });

    return result;
});

// 获取资源类型，用于预览
const getResourceType = (resource: Resource | null): string => {
    if (!resource) return '';

    const type = resource.resource_type.toLowerCase();
    if (type === 'ppt' || type === '课件' || type === 'courseware') {
        return 'courseware';
    } else if (type === '视频' || type === 'video') {
        return 'video';
    } else if (type === '图片' || type === 'image') {
        return 'image';
    }
    return '';
};

// 更新等待时间的函数
const updateWaitingTime = () => {
    if (waitingStartTime.value > 0) {
        const waitedTime = Date.now() - waitingStartTime.value;
        const minutes = Math.floor(waitedTime / 60000);
        const seconds = Math.floor((waitedTime % 60000) / 1000);
        
        // 如果等待时间超过最大值，自动停止等待
        if (waitedTime >= maxWaitTime) {
            loadingStore.hideLoading();
            clearInterval(waitingInterval.value!);
            waitingInterval.value = null;
            waitingStartTime.value = 0;
            window.$showToast('操作超时，请稍后重试', 'error');
            return;
        }
        
        // 更新加载提示，显示已等待时间
        loadingStore.showLoading(`正在获取资源，已等待 ${minutes}分${seconds}秒... (最长等待时间: 20分钟)`);
    }
};

// 开始计时
const startWaitingTimer = () => {
    waitingStartTime.value = Date.now();
    // 清除可能存在的旧计时器
    if (waitingInterval.value) {
        clearInterval(waitingInterval.value);
    }
    // 创建新计时器，每秒更新一次
    waitingInterval.value = setInterval(updateWaitingTime, 1000);
};

// 停止计时
const stopWaitingTimer = () => {
    if (waitingInterval.value) {
        clearInterval(waitingInterval.value);
        waitingInterval.value = null;
    }
    waitingStartTime.value = 0;
};

// 获取推荐资源列表
const fetchRecommendations = async () => {
    try {
        loadingStore.showLoading('正在获取推荐资源，这可能需要一些时间...');
        startWaitingTimer();

        const userId = localStorage.getItem('userId');
        const response = await apiWithLoading.get<any[]>(
            `/students/${userId}/recommendations`,
            '',
            { timeout: maxWaitTime }
        );

        // 获取资源详情
        const recommendations = response;
        console.log('API返回的推荐数据:', recommendations);

        // 确保 recommendations 是数组
        if (!Array.isArray(recommendations)) {
            console.error('API返回的推荐数据不是数组格式');
            resources.value = [];
            return;
        }

        if (recommendations.length === 0) {
            console.log('没有推荐资源');
            resources.value = [];
            return;
        }

        const detailedResources = await Promise.all(
            recommendations.map(async (recommendation: any) => {
                try {
                    const resourceResponse = await apiWithLoading.get<any>(
                        `/resources/${recommendation.resource_id}`,
                        ''
                    );

                    return {
                        id: recommendation.id,
                        resource_id: recommendation.resource_id,
                        resource_name: resourceResponse.resource_name,
                        resource_type: resourceResponse.resource_type,
                        file_path: resourceResponse.file_path,
                        priority: recommendation.priority,
                        reason: recommendation.reason
                    };
                } catch (error) {
                    console.error(`获取资源详情失败, ID: ${recommendation.resource_id}`, error);
                    return null;
                }
            })
        );

        resources.value = detailedResources.filter((r: Resource | null) => r !== null) as Resource[];
    } catch (error) {
        console.error('获取推荐资源失败:', error);
        window.$showToast('获取推荐资源失败，请稍后重试', 'error');
        resources.value = [];
    } finally {
        // 清除计时器
        stopWaitingTimer();
        loadingStore.hideLoading();
    }
};

const toggleSelection = (type: keyof SelectedResources, id: string) => {
    const index = selectedResources[type].indexOf(id);
    if (index === -1) {
        selectedResources[type].push(id);
    } else {
        selectedResources[type].splice(index, 1);
    }
};

// 检查是否有选中的资源
const hasSelectedResources = computed(() => {
    return selectedResources.courseware.length > 0 ||
        selectedResources.video.length > 0 ||
        selectedResources.image.length > 0;
});

// 预览资源
const previewResource = (resource: Resource) => {
    currentPreviewResource.value = resource;
    showPreview.value = true;

    // 标记推荐为已查看
    apiWithLoading.put(`/recommendations/${resource.id}/view`, {}, '')
        .catch(error => {
            console.error('标记资源为已查看失败:', error);
        });
};

// 关闭预览
const closePreview = () => {
    showPreview.value = false;
    currentPreviewResource.value = null;
};

// 下载选中的资源
const downloadSelected = async () => {
    try {
        loadingStore.showLoading('正在准备下载资源...');
        // 获取所有选中的资源ID
        const selectedIds = [
            ...selectedResources.courseware,
            ...selectedResources.video,
            ...selectedResources.image
        ];

        // 如果没有选中任何资源，直接返回
        if (selectedIds.length === 0) {
            window.$showToast('请先选择要下载的资源', 'error');
            loadingStore.hideLoading();
            return;
        }

        // 下载每个选中的资源
        for (const id of selectedIds) {
            const resource = resources.value.find(r => r.id.toString() === id);
            if (!resource) continue;

            try {
                // 使用后端API下载资源
                window.open(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/resources/${resource.resource_id}/download`, '_blank');

                // 标记推荐为已查看
                try {
                    await apiWithLoading.put(`/recommendations/${resource.id}/view`, {}, '');
                    console.log(`已将资源 ${resource.id} 标记为已查看`);
                } catch (viewError) {
                    console.error('标记资源为已查看失败:', viewError);
                    // 不因为标记失败而中断下载流程
                }
            } catch (downloadError) {
                console.error(`下载资源${resource.resource_id}失败:`, downloadError);
                window.$showToast(`资源"${resource.resource_name}"下载失败，请稍后重试`, 'error');
            }
        }
        window.$showToast('资源准备完成，请在新窗口中查看', 'success');
    } catch (error) {
        console.error('下载资源错误:', error);
        window.$showToast('下载资源失败，请稍后重试', 'error');
    } finally {
        loadingStore.hideLoading();
    }
};

// 判断是否为pptx文件
const isPptx = (filePath: string | undefined): boolean => {
    if (!filePath) return false;
    return filePath.toLowerCase().endsWith('.pptx') || filePath.toLowerCase().endsWith('.ppt');
};

// 下载资源
const downloadResource = (resource: Resource | null) => {
    if (!resource) return;
    try {
        window.open(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/resources/${resource.resource_id}/download`, '_blank');
    } catch (error) {
        console.error('下载资源错误:', error);
        window.$showToast(`资源"${resource.resource_name}"下载失败，请稍后重试`, 'error');
    }
};

// 初始加载
onMounted(() => {
    fetchRecommendations();
});

// 组件卸载前的清理工作
onBeforeUnmount(() => {
    stopWaitingTimer();
});
</script>

<style scoped>
.step3-view {
    height: 100%;
    display: flex;
    max-width: 1400px;
    margin: 0 auto;
    box-sizing: border-box;
}

.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 16px;
    height: 100%;
    padding: 0;
    box-sizing: border-box;
}

h2 {
    margin: 0;
    font-size: 20px;
    color: #333;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.download-btn {
    padding: 8px 16px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s ease;
}

.download-btn:hover {
    background-color: #2980b9;
}

.download-btn:disabled {
    background-color: #bdc3c7;
    cursor: not-allowed;
}

.resource-section {
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h3 {
    margin: 0 0 16px 0;
    font-size: 16px;
    color: #333;
}

.resource-list {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    padding: 4px;
    min-height: 150px;
}

.resource-item {
    position: relative;
    width: 200px;
    height: 150px;
    background: #f5f7fa;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.resource-item.selected {
    border-color: #3498db;
    background: #f5f7fa;
}

.resource-item:hover {
    border-color: #3498db;
    opacity: 0.9;
}

.match-rate {
    position: absolute;
    top: 8px;
    left: 8px;
    background-color: #3498db;
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 14px;
}

.check-icon {
    position: absolute;
    top: 8px;
    right: 8px;
    color: #3498db;
    font-size: 16px;
    font-weight: bold;
    background: white;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.thumbnail {
    color: #666;
    font-size: 14px;
    text-align: center;
    padding: 0 10px;
    word-break: break-word;
    max-height: 80px;
    overflow: hidden;
}

.preview-btn {
    position: absolute;
    bottom: 8px;
    right: 8px;
    background: #e6e8eb;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
    font-size: 12px;
}

.preview-btn:hover {
    background: #d8d8d8;
}

.empty-message {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 150px;
    color: #999;
    font-size: 14px;
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
        
        .preview-fallback {
            padding: 20px;
            text-align: center;
            color: #666;
        }
        
        /* PPT预览样式 */
        .pptx-preview {
            padding: 40px;
            text-align: center;
            color: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
        }
        
        .pptx-info {
            background: #f5f7fa;
            padding: 30px;
            border-radius: 8px;
            max-width: 500px;
            text-align: center;
        }
        
        .pptx-icon {
            font-size: 48px;
            margin-bottom: 16px;
            display: block;
        }
        
        .pptx-info h4 {
            font-size: 18px;
            margin: 0 0 16px 0;
            color: #333;
        }
        
        .pptx-info p {
            margin: 0 0 24px 0;
            color: #666;
            line-height: 1.5;
        }
        
        .download-ppt-btn {
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
}

.download-ppt-btn:hover {
    background-color: #2980b9;
}
</style>