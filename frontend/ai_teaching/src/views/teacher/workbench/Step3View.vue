<template>
    <div class="step3-view">
        <div class="main-content">
            <h2>资源推荐</h2>

            <!-- 课件部分 -->
            <div class="resource-section">
                <h3>课件</h3>
                <div class="resource-list">
                    <div v-for="(resource, index) in resources.courseware" :key="index" class="resource-item"
                        :class="{ selected: selectedResources.courseware.includes(resource.id) }"
                        @click="toggleSelection('courseware', resource.id)">
                        <div class="match-rate">{{ resource.matchRate }}%</div>
                        <div class="thumbnail">
                            <img src="/icons/ppt-icon.svg" alt="PPT图标" class="resource-icon" />
                            <div class="resource-name">{{ resource.name }}</div>
                        </div>
                        <div v-if="selectedResources.courseware.includes(resource.id)" class="check-icon">✓</div>
                        <button class="preview-btn" @click.stop="previewResource(resource)">预览</button>
                    </div>
                </div>
            </div>

            <!-- 视频部分 -->
            <div class="resource-section">
                <h3>视频</h3>
                <div class="resource-list">
                    <div v-for="(resource, index) in resources.video" :key="index" class="resource-item"
                        :class="{ selected: selectedResources.video.includes(resource.id) }"
                        @click="toggleSelection('video', resource.id)">
                        <div class="match-rate">{{ resource.matchRate }}%</div>
                        <div class="thumbnail">
                            <img src="/icons/video-icon.svg" alt="视频图标" class="resource-icon" />
                            <div class="resource-name">{{ resource.name }}</div>
                        </div>
                        <div v-if="selectedResources.video.includes(resource.id)" class="check-icon">✓</div>
                        <button class="preview-btn" @click.stop="previewResource(resource)">预览</button>
                    </div>
                </div>
            </div>

            <!-- 相关图片 -->
            <div class="resource-section">
                <h3>相关图片</h3>
                <div class="resource-list">
                    <div v-for="(resource, index) in resources.image" :key="index" class="resource-item"
                        :class="{ selected: selectedResources.image.includes(resource.id) }"
                        @click="toggleSelection('image', resource.id)">
                        <div class="match-rate">{{ resource.matchRate }}%</div>
                        <div class="thumbnail">
                            <img src="/icons/image-icon.svg" alt="图片图标" class="resource-icon" />
                            <div class="resource-name">{{ resource.name }}</div>
                        </div>
                        <div v-if="selectedResources.image.includes(resource.id)" class="check-icon">✓</div>
                        <button class="preview-btn" @click.stop="previewResource(resource)">预览</button>
                    </div>
                </div>
            </div>

            <!-- 底部按钮 -->
            <div class="actions">
                <button class="action-btn back-btn" @click="goBack" :disabled="loadingStore.isLoading">上一步</button>
                <button class="action-btn save-btn" @click="saveContent" :disabled="loadingStore.isLoading">保存</button>
                <button class="action-btn next-btn" @click="nextStep" :disabled="loadingStore.isLoading">
                    {{ isLastStep ? '完成' : '下一步' }}
                </button>
            </div>
        </div>

        <!-- 预览对话框 -->
        <div v-if="showPreview" class="preview-dialog">
            <div class="preview-content">
                <div class="preview-header">
                    <h3>{{ currentPreviewResource?.name }}</h3>
                    <button class="close-btn" @click="closePreview">×</button>
                </div>
                <div class="preview-body">
                    <iframe v-if="currentPreviewResource?.type === 'courseware'" :src="currentPreviewResource?.path"
                        frameborder="0"></iframe>
                    <video v-else-if="currentPreviewResource?.type === 'video'" :src="currentPreviewResource?.path"
                        controls></video>
                    <img v-else-if="currentPreviewResource?.type === 'image'" :src="currentPreviewResource?.path"
                        alt="预览图片" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { reactive, computed, onMounted, watch, ref, onBeforeUnmount } from 'vue';
import axios from 'axios';
import { useLoadingStore } from '@/stores/loading';
import { apiWithLoading } from '@/utils/api';

const router = useRouter();
const loadingStore = useLoadingStore();

// 定义消息提示API
const messageApi = window.$showToast || ((msg: string, type: string) => console.log(`${type}: ${msg}`));

// 加载的计时相关状态
const waitingStartTime = ref(0);
const waitingInterval = ref<number | null>(null);
const maxWaitTime = 20 * 60 * 1000; // 20分钟，单位为毫秒

// 预览相关状态
const showPreview = ref(false);
const currentPreviewResource = ref<Resource | null>(null);

interface Resource {
    id: string;
    name: string;
    path: string;
    type: 'courseware' | 'video' | 'image';
    matchRate: number;
}

interface Resources {
    courseware: Resource[];
    video: Resource[];
    image: Resource[];
}

interface SelectedResources {
    courseware: string[];
    video: string[];
    image: string[];
}

const resources = reactive<Resources>({
    courseware: [],
    video: [],
    image: []
});

const selectedResources = reactive<SelectedResources>({
    courseware: [],
    video: [],
    image: []
});

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
            messageApi('操作超时，请稍后重试', 'error');
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

// 在组件销毁前清理计时器
onBeforeUnmount(() => {
    stopWaitingTimer();
});

// 获取推荐资源
const fetchResources = async () => {
    try {
        // 开始显示加载状态和计时
        loadingStore.showLoading('正在获取资源，请稍候...');
        startWaitingTimer();

        // 从localStorage获取课程信息
        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            throw new Error('未找到课程信息');
        }

        const data = await apiWithLoading.get<Resources>(
            `http://localhost:8000/resources/recommend/${courseInfo.id}`,
            '' // 空消息，因为我们已经使用自定义消息
        );

        // 更新资源列表
        resources.courseware = data.courseware || [];
        resources.video = data.video || [];
        resources.image = data.image || [];

        messageApi('获取资源成功！', 'success');
    } catch (error: any) {
        console.error('获取资源错误:', error);
        messageApi(error.message || '获取资源失败，请稍后重试', 'error');

        // 使用测试数据
        resources.courseware = [
            { id: '1', name: 'test1.pptx', path: '/backend/data/PPT/test1.pptx', type: 'courseware', matchRate: 95 },
            { id: '2', name: 'test2.pptx', path: '/backend/data/PPT/test2.pptx', type: 'courseware', matchRate: 90 }
        ];
        resources.video = [
            { id: '3', name: 'test1.mp4', path: '/backend/data/视频/test1.mp4', type: 'video', matchRate: 85 },
            { id: '4', name: 'test2.mp4', path: '/backend/data/视频/test2.mp4', type: 'video', matchRate: 80 }
        ];
        resources.image = [
            { id: '5', name: 'test1.jpg', path: '/backend/data/图片/test1.jpg', type: 'image', matchRate: 75 },
            { id: '6', name: 'test2.jpg', path: '/backend/data/图片/test2.jpg', type: 'image', matchRate: 70 }
        ];
    } finally {
        // 停止计时和加载状态
        stopWaitingTimer();
        loadingStore.hideLoading();
    }
};

// 保存数据到 localStorage
const saveToLocalStorage = () => {
    const step3Data = {
        selectedResources
    };

    // 获取当前课程信息
    const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
    courseInfo.step3Data = step3Data;
    localStorage.setItem('currentCourseInfo', JSON.stringify(courseInfo));
};

// 从 localStorage 恢复数据
const restoreFromLocalStorage = () => {
    const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
    const step3Data = courseInfo.step3Data;

    if (step3Data) {
        Object.assign(selectedResources, step3Data.selectedResources);
    }
};

// 监听数据变化，自动保存
watch(selectedResources, () => {
    saveToLocalStorage();
}, { deep: true });

// 组件挂载时获取资源并恢复数据
onMounted(async () => {
    loadingStore.showLoading('正在加载资源列表...');
    try {
        // 加载课程信息
        const courseInfoStr = localStorage.getItem('currentCourseInfo');
        if (!courseInfoStr) {
            throw new Error('未找到课程信息');
        }
        const courseInfo = JSON.parse(courseInfoStr);
        const courseId = ref(courseInfo.id);
        
        // 加载PPT资源
        loadPPTResources().then(() => {
            // 处理之前选择的资源
            if (courseInfo.step3Data && courseInfo.step3Data.selectedResourceIds) {
                // 恢复选中状态
                const selectedIds = courseInfo.step3Data.selectedResourceIds;
                
                // 确保每个ID都被正确处理
                if (selectedIds.PPT && Array.isArray(selectedIds.PPT)) {
                    selectedIds.PPT.forEach((id: string | number) => {
                        // 将字符串ID转换为数字，除非是AI资源
                        const processedId = typeof id === 'string' && !id.startsWith('ai_') 
                            ? parseInt(id, 10) 
                            : id;
                        addSelectedResource('courseware', processedId);
                    });
                }
                
                if (selectedIds.video && Array.isArray(selectedIds.video)) {
                    selectedIds.video.forEach((id: string | number) => {
                        const processedId = typeof id === 'string' && !id.startsWith('ai_') 
                            ? parseInt(id, 10) 
                            : id;
                        addSelectedResource('video', processedId);
                    });
                }
                
                if (selectedIds.image && Array.isArray(selectedIds.image)) {
                    selectedIds.image.forEach((id: string | number) => {
                        const processedId = typeof id === 'string' && !id.startsWith('ai_') 
                            ? parseInt(id, 10) 
                            : id;
                        addSelectedResource('image', processedId);
                    });
                }
            }
        });
        
        // 加载视频资源
        loadVideoResources();
        
        // 加载图片资源
        loadImageResources();
        
    } catch (error) {
        console.error('加载资源失败:', error);
        messageApi('加载资源失败: ' + ((error as Error).message || '未知错误'), 'error');
    } finally {
        loadingStore.hideLoading();
    }
});

const toggleSelection = (type: keyof SelectedResources, id: string) => {
    const index = selectedResources[type].indexOf(id);
    if (index === -1) {
        selectedResources[type].push(id);
    } else {
        selectedResources[type].splice(index, 1);
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

// 计算是否是最后一步
const isLastStep = computed(() => {
    return true; // Step3 现在总是最后一步
});

const goBack = () => {
    saveToLocalStorage(); // 保存当前数据
    // 获取功能选择
    const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
    const features = courseInfo.features || {};

    if (features.exerciseGeneration) {
        // 如果选择了练习题生成，返回到 step4
        router.push('/teacher/workbench/step4');
    } else {
        // 否则返回到 step2
        router.push('/teacher/workbench/step2');
    }
};

const saveContent = async () => {
    try {
        loadingStore.showLoading('正在保存资源...');
        
        if (!selectedResources.courseware.length && !selectedResources.video.length && !selectedResources.image.length) {
            messageApi('请至少选择一项资源', 'error');
            return;
        }
        
        // 获取课程ID和教师ID
        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            throw new Error('未找到课程信息');
        }
        
        // 将资源ID转换为正确的数据类型
        const processedResourceIds = {
            PPT: selectedResources.courseware.map(id => {
                // AI资源保持字符串格式
                if (typeof id === 'string' && id.startsWith('ai_')) {
                    return id;
                }
                // 数字ID确保是整数类型
                return parseInt(id, 10);
            }),
            video: selectedResources.video.map(id => {
                if (typeof id === 'string' && id.startsWith('ai_')) {
                    return id;
                }
                return parseInt(id, 10);
            }),
            image: selectedResources.image.map(id => {
                if (typeof id === 'string' && id.startsWith('ai_')) {
                    return id;
                }
                return parseInt(id, 10);
            })
        };
        
        console.log('处理后要保存的资源ID:', processedResourceIds);
        
        const response = await apiWithLoading.post('/resources/save/', {
            course_id: courseInfo.id,
            selected_resources: processedResourceIds
        }, '');
        
        // 更新课程信息中的资源选择
        courseInfo.step3Data = {
            selectedResourceIds: processedResourceIds
        };
        localStorage.setItem('currentCourseInfo', JSON.stringify(courseInfo));
        
        messageApi('保存成功！', 'success');
        return true;
    } catch (error) {
        console.error('保存资源失败:', error);
        messageApi('保存资源失败: ' + ((error as Error).message || '未知错误'), 'error');
        return false;
    } finally {
        loadingStore.hideLoading();
    }
};

interface Question {
    id: number;
    user_id: number;
    type: string;
    title: string;
    content: string;
    options: string | null;
    answers: string;
    created_at: string;
    updated_at: string;
}

interface CourseInfo {
    id: number;
    lessonPlanId: number;
    step3Data: {
        selectedResourceIds: {
            PPT: number[];
            video: number[];
            image: number[];
        };
    };
    step4Data?: {
        questions?: Question[];
    };
    features?: {
        exerciseGeneration?: boolean;
    };
}

const nextStep = async () => {
    try {
        loadingStore.showLoading('正在完成备课...');

        // 保存选中的资源
        await saveContent();

        // 从localStorage获取课程信息
        const courseInfoStr = localStorage.getItem('currentCourseInfo');
        if (!courseInfoStr) {
            throw new Error('未找到课程信息');
        }
        const courseInfo: CourseInfo = JSON.parse(courseInfoStr);
        console.log('课程信息：', courseInfo); // 调试日志
        
        // 处理习题ID
        let exerciseIds: number[] = [];
        if (courseInfo.step4Data && courseInfo.step4Data.questions) {
            // 过滤出有效的习题ID
            exerciseIds = courseInfo.step4Data.questions
                .filter((q: any) => q && q.id)
                .map((q: any) => q.id)
                .filter((id: any) => id);
        }
        
        // 如果没有有效习题ID但是需要习题，显示提示
        const features = courseInfo.features || {};
        if (features.exerciseGeneration && exerciseIds.length === 0) {
            messageApi('习题未生成或未保存，请先在习题步骤中生成并保存习题', 'error');
            loadingStore.hideLoading();
            // 导航到习题步骤
            router.push('/teacher/workbench/step4');
            return;
        }
        
        console.log('习题ID列表:', exerciseIds); // 调试日志

        // 构建请求数据
        const requestData = {
            course_id: courseInfo.id,
            teacher_id: parseInt(localStorage.getItem('userId') || '0'),
            lesson_plan_id: courseInfo.lessonPlanId,
            selected_resources: courseInfo.step3Data.selectedResourceIds,
            exercises: {
                selected_ids: exerciseIds
            }
        };

        console.log('请求数据：', requestData); // 调试日志

        // 发送完成备课请求
        const response = await axios.post('http://localhost:8000/lesson-preparation/complete/', requestData);

        if (response.data) {
            messageApi('备课完成！', 'success');
            // 清理localStorage中的课程信息
            localStorage.removeItem('currentCourseInfo');
            // 返回工作台
            router.push('/teacher/workbench');
        }
    } catch (error: any) {
        console.error('完成备课错误:', error);
        console.error('错误详情:', error.response?.data); // 添加详细错误信息日志
        messageApi(`完成备课错误: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
        loadingStore.hideLoading();
    }
};

// 添加选中的资源
const addSelectedResource = (type: keyof SelectedResources, id: string | number) => {
    const stringId = id.toString();
    if (!selectedResources[type].includes(stringId)) {
        selectedResources[type].push(stringId);
    }
};

// 加载PPT资源
const loadPPTResources = async () => {
    try {
        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            throw new Error('未找到课程信息');
        }
        
        const response = await axios.get(`http://localhost:8000/resources/ppt/${courseInfo.id}`);
        resources.courseware = response.data.map((item: any) => ({
            id: item.id.toString(),
            name: item.name,
            path: item.path,
            type: 'courseware',
            matchRate: item.match_rate || 90
        }));
        
        return resources.courseware;
    } catch (error) {
        console.error('加载PPT资源失败:', error);
        // 使用测试数据
        resources.courseware = [
            { id: '1', name: 'test1.pptx', path: '/backend/data/PPT/test1.pptx', type: 'courseware', matchRate: 95 },
            { id: '2', name: 'test2.pptx', path: '/backend/data/PPT/test2.pptx', type: 'courseware', matchRate: 90 }
        ];
        return resources.courseware;
    }
};

// 加载视频资源
const loadVideoResources = async () => {
    try {
        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            throw new Error('未找到课程信息');
        }
        
        const response = await axios.get(`http://localhost:8000/resources/video/${courseInfo.id}`);
        resources.video = response.data.map((item: any) => ({
            id: item.id.toString(),
            name: item.name,
            path: item.path,
            type: 'video',
            matchRate: item.match_rate || 85
        }));
        
        return resources.video;
    } catch (error) {
        console.error('加载视频资源失败:', error);
        // 使用测试数据
        resources.video = [
            { id: '3', name: 'test1.mp4', path: '/backend/data/视频/test1.mp4', type: 'video', matchRate: 85 },
            { id: '4', name: 'test2.mp4', path: '/backend/data/视频/test2.mp4', type: 'video', matchRate: 80 }
        ];
        return resources.video;
    }
};

// 加载图片资源
const loadImageResources = async () => {
    try {
        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            throw new Error('未找到课程信息');
        }
        
        const response = await axios.get(`http://localhost:8000/resources/image/${courseInfo.id}`);
        resources.image = response.data.map((item: any) => ({
            id: item.id.toString(),
            name: item.name,
            path: item.path,
            type: 'image',
            matchRate: item.match_rate || 75
        }));
        
        return resources.image;
    } catch (error) {
        console.error('加载图片资源失败:', error);
        // 使用测试数据
        resources.image = [
            { id: '5', name: 'test1.jpg', path: '/backend/data/图片/test1.jpg', type: 'image', matchRate: 75 },
            { id: '6', name: 'test2.jpg', path: '/backend/data/图片/test2.jpg', type: 'image', matchRate: 70 }
        ];
        return resources.image;
    }
};
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
        padding: 12px;
    }
    
    .resource-item.selected {
        border-color: #4c84ff;
        background: #f5f7fa;
    }
    
    .resource-item:hover {
        border-color: #4c84ff;
        opacity: 0.9;
    }
    
    .match-rate {
        position: absolute;
        top: 8px;
        left: 8px;
        background: rgba(76, 132, 255, 0.9);
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    .check-icon {
        position: absolute;
        top: 8px;
        right: 8px;
        color: #4c84ff;
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
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
    }
    
    .resource-icon {
        width: 48px;
        height: 48px;
        object-fit: contain;
    }
    
    .resource-name {
        color: #666;
        font-size: 14px;
        text-align: center;
        word-break: break-all;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
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
    
    /* 按钮样式 */
    .actions {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        height: 48px;
        margin-top: auto;
        padding: 0;
        width: 100%;
        box-sizing: border-box;
    }
    
    .action-btn {
        flex: 1;
        height: 48px;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s;
        padding: 0;
        box-sizing: border-box;
    }
    
    .back-btn {
        background-color: #f5f7fa;
        color: #666;
        border: 1px solid #ddd;
    }
    
    .back-btn:hover {
        background-color: #e6e8eb;
    }
    
    .save-btn {
        background-color: #f5f7fa;
        color: #666;
        border: 1px solid #ddd;
    }
    
    .save-btn:hover {
        background-color: #e6e8eb;
    }
    
    .next-btn {
        background-color: #4c84ff;
        color: white;
    }
    
    .next-btn:hover {
        background-color: #3a70e3;
    }
    
                /* 禁用状态样式 */
                .action-btn:disabled {
                    cursor: not-allowed;
                    opacity: 0.7;
                }
</style>