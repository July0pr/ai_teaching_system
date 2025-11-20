<template>
    <div class="history-view">
        <!-- 顶部搜索和操作区 -->
        <div class="top-actions">
            <div class="search-bar">
                <input type="text" v-model="searchQuery" placeholder="搜索课程名称或教案内容" @input="handleSearch" />
                <button class="search-btn" @click="handleSearch">搜索</button>
            </div>
            <div class="batch-actions" v-if="!showDetail && !currentRecord">
                <button class="delete-btn" :disabled="selectedRecords.length === 0" @click="batchDelete">
                    删除选中 ({{ selectedRecords.length }})
                </button>
            </div>
        </div>

        <!-- 备课记录列表 -->
        <div class="preparation-list" v-if="!showDetail && !currentRecord">
            <div v-for="record in filteredRecords" :key="record.id" class="preparation-card"
                :class="{ selected: selectedRecords.includes(record.id) }">
                <div class="card-checkbox">
                    <input type="checkbox" :checked="selectedRecords.includes(record.id)"
                        @click.stop="toggleRecordSelection(record.id)" />
                </div>
                <div class="card-content" @click="viewDetail(record)">
                    <div class="info-section">
                        <h3>{{ record.course_name }}</h3>
                        <p class="time">{{ formatDate(record.preparation_date) }}</p>
                    </div>
                    <div class="class-info">
                        <span class="info-item">
                            <i class="el-icon-school"></i>
                            目标班级：{{ record.target_class }}
                        </span>
                        <span class="info-item">
                            <i class="el-icon-time"></i>
                            课时长度：{{ record.duration }}
                        </span>
                    </div>
                    <div class="resources-summary">
                        <div v-if="record.selected_resources" class="resource-tags">
                            <span v-if="record.selected_resources.courseware?.length" class="resource-tag courseware">
                                课件 ({{ record.selected_resources.courseware.length }})
                            </span>
                            <span v-if="record.selected_resources.video?.length" class="resource-tag video">
                                视频 ({{ record.selected_resources.video.length }})
                            </span>
                            <span v-if="record.selected_resources.image?.length" class="resource-tag image">
                                图片 ({{ record.selected_resources.image.length }})
                            </span>
                            <span v-if="record.exercises?.length" class="resource-tag exercise">
                                习题 ({{ record.exercises.length }})
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 备课详情 -->
        <div v-if="currentRecord" class="preparation-detail">
            <div class="detail-header">
                <button class="back-btn" @click="backToList">返回列表</button>
                <h2>{{ currentRecord.course_name }}</h2>
                <span class="date">{{ formatDate(currentRecord.preparation_date) }}</span>
            </div>

            <!-- 教案内容 -->
            <div class="detail-section">
                <div class="section-header">
                    <h3>教案内容</h3>
                    <div class="action-buttons">
                        <button class="edit-btn" v-if="!isEditingLessonPlan" @click="startEditLessonPlan">
                            <i class="el-icon-edit"></i>
                            编辑教案
                        </button>
                        <template v-else>
                            <button class="save-btn" @click="saveLessonPlan">
                                <i class="el-icon-check"></i>
                                保存
                            </button>
                            <button class="cancel-btn" @click="cancelEditLessonPlan">
                                <i class="el-icon-close"></i>
                                取消
                            </button>
                        </template>
                        <button class="download-btn" @click="downloadLessonPlan(currentRecord.lesson_plan_content)">
                            <i class="el-icon-download"></i>
                            下载教案
                        </button>
                    </div>
                </div>
                <div class="lesson-plan-content">
                    <div v-if="!currentRecord.lesson_plan_content" class="no-content">
                        暂无教案内容
                    </div>
                    <template v-else>
                        <textarea v-if="isEditingLessonPlan" v-model="editingLessonPlanContent"
                            class="lesson-plan-editor" placeholder="请输入教案内容..."></textarea>
                        <div v-else class="content-text">
                            {{ currentRecord.lesson_plan_content }}
                        </div>
                    </template>
                </div>
            </div>

            <!-- 资源列表 -->
            <div class="detail-section" v-if="hasResources">
                <div class="section-header">
                    <h3>相关资源</h3>
                </div>
                <div class="resources-grid">
                    <!-- 课件 -->
                    <div v-if="currentRecord.resources_details?.courseware?.length" class="resource-group">
                        <h4>课件</h4>
                        <div class="resource-items">
                            <div v-for="resource in currentRecord.resources_details.courseware" :key="resource.id"
                                class="resource-item">
                                <img :src="getResourceTypeIcon(resource.type)" alt="PPT" />
                                <span>{{ resource.name }}</span>
                                <div class="resource-actions">
                                    <button class="preview-action" @click="openPreview(resource)">
                                        <i class="el-icon-view"></i>
                                        预览
                                    </button>
                                    <button class="download-action" @click="downloadResource(resource)">
                                        <i class="el-icon-download"></i>
                                        下载
                                    </button>
                                    <button class="publish-action" @click="() => showPublishModal(resource)">
                                        <i class="el-icon-upload"></i>
                                        发布
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 视频 -->
                    <div v-if="currentRecord.resources_details?.video?.length" class="resource-group">
                        <h4>视频</h4>
                        <div class="resource-items">
                            <div v-for="resource in currentRecord.resources_details.video" :key="resource.id"
                                class="resource-item">
                                <img :src="getResourceTypeIcon(resource.type)" alt="视频" />
                                <span>{{ resource.name }}</span>
                                <div class="resource-actions">
                                    <button class="preview-action" @click="openPreview(resource)">
                                        <i class="el-icon-view"></i>
                                        预览
                                    </button>
                                    <button class="download-action" @click="downloadResource(resource)">
                                        <i class="el-icon-download"></i>
                                        下载
                                    </button>
                                    <button class="publish-action" @click="() => showPublishModal(resource)">
                                        <i class="el-icon-upload"></i>
                                        发布
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 图片 -->
                    <div v-if="currentRecord.resources_details?.image?.length" class="resource-group">
                        <h4>图片</h4>
                        <div class="resource-items">
                            <div v-for="resource in currentRecord.resources_details.image" :key="resource.id"
                                class="resource-item">
                                <img :src="getResourceTypeIcon(resource.type)" alt="图片" />
                                <span>{{ resource.name }}</span>
                                <div class="resource-actions">
                                    <button class="preview-action" @click="openPreview(resource)">
                                        <i class="el-icon-view"></i>
                                        预览
                                    </button>
                                    <button class="download-action" @click="downloadResource(resource)">
                                        <i class="el-icon-download"></i>
                                        下载
                                    </button>
                                    <button class="publish-action" @click="() => showPublishModal(resource)">
                                        <i class="el-icon-upload"></i>
                                        发布
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 习题列表 -->
            <div class="detail-section" v-if="currentRecord.exercises?.length || isEditingExercises">
                <div class="section-header">
                    <h3>练习题</h3>
                    <div class="action-buttons">
                        <template v-if="!isEditingExercises">
                            <button class="action-btn preview" @click="startEditExercises">
                                <i class="el-icon-edit"></i>
                                编辑习题
                            </button>
                            <button class="action-btn preview" @click="handlePublish">
                                <i class="el-icon-s-promotion"></i>
                                发布
                            </button>
                        </template>
                        <template v-else>
                            <button class="action-btn save" @click="saveExercises">
                                <i class="el-icon-check"></i>
                                保存
                            </button>
                            <button class="action-btn cancel" @click="cancelEditExercises">
                                <i class="el-icon-close"></i>
                                取消
                            </button>
                        </template>
                    </div>
                </div>
                <div class="exercises-list" ref="exercisesList" @scroll="handleExercisesScroll">
                    <div v-for="(exercise, index) in (isEditingExercises ? editingExercises : currentRecord.exercises)"
                        :key="'exercise-' + index" class="exercise-item">
                        <div class="exercise-header">
                            <div class="exercise-type-selector" v-if="isEditingExercises">
                                <select v-model="exercise.type">
                                    <option value="单选">单选题</option>
                                    <option value="多选">多选题</option>
                                    <option value="判断">判断题</option>
                                    <option value="填空">填空题</option>
                                    <option value="简答">简答题</option>
                                </select>
                            </div>
                            <div v-else class="exercise-type-tag">{{ exercise.type }}</div>
                            <input v-if="isEditingExercises" v-model="exercise.title" class="exercise-title-input"
                                placeholder="请输入题目标题" />
                            <div v-else class="exercise-title">{{ exercise.title }}</div>
                            <button v-if="isEditingExercises" class="delete-exercise-btn"
                                @click="deleteExercise(index)">
                                <i class="el-icon-delete"></i>
                                删除
                            </button>
                        </div>
                        <div class="exercise-content">
                            <textarea v-if="isEditingExercises" v-model="exercise.content"
                                placeholder="请输入题目内容"></textarea>
                            <div v-else class="content-text">{{ exercise.content }}</div>
                        </div>
                        <div v-if="exercise.type !== '填空' && exercise.type !== '简答'" class="exercise-options">
                            <template v-if="isEditingExercises">
                                <div v-if="exercise.type === '判断'" class="options-list">
                                    <div class="option-item">
                                        <span>1. 正确</span>
                                    </div>
                                    <div class="option-item">
                                        <span>2. 错误</span>
                                    </div>
                                </div>
                                <div v-else class="options-list">
                                    <div v-for="(option, optIndex) in getExerciseOptions(exercise)" :key="optIndex"
                                        class="option-item">
                                        <span>{{ String.fromCharCode(65 + optIndex) }}.</span>
                                        <input type="text" v-model="option.text"
                                            :placeholder="'选项' + String.fromCharCode(65 + optIndex)" />
                                        <button v-if="optIndex > 1" @click="removeOption(exercise, optIndex)"
                                            class="remove-option-btn">×</button>
                                    </div>
                                    <button v-if="getExerciseOptions(exercise).length < 6" @click="addOption(exercise)"
                                        class="add-option-btn">添加选项</button>
                                </div>
                            </template>
                            <template v-else>
                                <div class="options-grid">
                                    <div v-for="(option, optIndex) in (exercise.options ? JSON.parse(exercise.options) : [])"
                                        :key="optIndex" class="option-item-display">
                                        <span class="option-label">{{ String.fromCharCode(65 + optIndex) }}.</span>
                                        <span class="option-text">{{ option }}</span>
                                    </div>
                                </div>
                            </template>
                        </div>
                        <div class="exercise-answer">
                            <strong>答案：</strong>
                            <template v-if="isEditingExercises">
                                <div v-if="exercise.type === '单选'" class="answer-options">
                                    <label v-for="(option, index) in getExerciseOptions(exercise)" :key="index">
                                        <input type="radio" :value="String.fromCharCode(65 + index)"
                                            v-model="exercise.answers" />
                                        {{ String.fromCharCode(65 + index) }}
                                    </label>
                                </div>
                                <div v-else-if="exercise.type === '多选'" class="answer-options">
                                    <label v-for="(option, index) in getExerciseOptions(exercise)" :key="index">
                                        <input type="checkbox" :value="String.fromCharCode(65 + index)"
                                            v-model="exercise.selectedAnswers"
                                            @change="updateMultipleChoiceAnswers(exercise)" />
                                        {{ String.fromCharCode(65 + index) }}
                                    </label>
                                </div>
                                <div v-else-if="exercise.type === '判断'" class="answer-options">
                                    <label>
                                        <input type="radio" value="正确" v-model="exercise.answers" />
                                        正确
                                    </label>
                                    <label>
                                        <input type="radio" value="错误" v-model="exercise.answers" />
                                        错误
                                    </label>
                                </div>
                                <textarea v-else v-model="exercise.answers" placeholder="请输入答案"></textarea>
                            </template>
                            <span v-else class="answer-text">{{ exercise.answers }}</span>
                        </div>
                    </div>
                </div>
                <div v-if="isEditingExercises" class="add-exercise-section">
                    <button class="add-exercise-btn" @click="addNewExercise">
                        <i class="el-icon-plus"></i>
                        添加新习题
                    </button>
                </div>
            </div>
        </div>

        <!-- 资源预览对话框 -->
        <div v-if="showPreview" class="preview-dialog">
            <div class="preview-content">
                <div class="preview-header">
                    <h3>{{ previewingResource?.name }}</h3>
                    <button class="close-btn" @click="closePreview">×</button>
                </div>
                <div class="preview-body">
                    <iframe v-if="previewingResource?.type === 'PPT'" :src="previewingResource?.path"
                        frameborder="0"></iframe>
                    <video v-else-if="previewingResource?.type === '视频'" :src="previewingResource?.path"
                        controls></video>
                    <img v-else-if="previewingResource?.type === '图片'" :src="previewingResource?.path" alt="预览图片" />
                </div>
            </div>
        </div>

        <!-- 发布资源对话框 -->
        <div v-if="showPublishDialog" class="modal">
            <div class="modal-content">
                <h3>{{ selectedResource ? '发布资源到班级' : '发布习题到班级' }}</h3>
                <form @submit.prevent="handlePublishSubmit">
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

        <!-- 提示框 -->
        <div v-if="showToast" class="toast" :class="toastType">
            {{ toastMessage }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

interface DisplayResource {
    id: number | string;
    name: string;
    path: string;
    type: 'PPT' | '视频' | '图片';
}

interface BackendResource {
    id: number;
    resource_name: string;
    resource_type: string;
    file_path: string;
}

interface Exercise {
    id?: number;
    type: string;
    title: string;
    content: string;
    options?: string;
    answers: string;
    selectedAnswers?: string[];
}

interface PreparationRecord {
    id: number;
    course_id: number;
    course_name: string;
    target_class: string;
    duration: string;
    preparation_date: string;
    lesson_plan_id: number | null;
    lesson_plan_title: string;
    lesson_plan_content: string;
    selected_resources: {
        courseware: number[];
        video: number[];
        image: number[];
    };
    resources_details?: {
        courseware: DisplayResource[];
        video: DisplayResource[];
        image: DisplayResource[];
    };
    exercises?: Exercise[];
}

interface Option {
    text: string;
}

const searchQuery = ref('');
const records = ref<PreparationRecord[]>([]);
const showDetail = ref(false);
const currentRecord = ref<PreparationRecord | null>(null);
const showPreview = ref(false);
const previewingResource = ref<DisplayResource | null>(null);
const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref<'success' | 'error'>('success');
const errorMessage = ref('');

// 获取备课历史记录
const fetchHistory = async () => {
    try {
        const teacherId = localStorage.getItem('userId');
        const response = await fetch(`http://localhost:8000/lesson-preparation/history/${teacherId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取历史记录失败');
        }

        const data = await response.json();
        console.log('获取到的历史记录数据:', data);
        records.value = data.map((record: any) => ({
            ...record,
            lesson_plan_content: record.lesson_plan_content || record.content || record.lesson_content || '',
            lesson_plan_id: record.lesson_plan_id || record.id, // 使用备课记录ID作为教案ID的备选
            course_id: record.course_id // 确保 course_id 被正确映射
        }));
    } catch (error) {
        console.error('获取历史记录错误:', error);
    }
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

// 搜索过滤
const filteredRecords = computed(() => {
    if (!searchQuery.value) return records.value;

    const query = searchQuery.value.toLowerCase();
    return records.value.filter(record =>
        record.course_name.toLowerCase().includes(query) ||
        record.lesson_plan_content.toLowerCase().includes(query)
    );
});

// 获取教案内容
const fetchLessonPlanContent = async (lessonPlanTitle: string) => {
    try {
        const response = await fetch(`http://localhost:8000/lesson-plans/content/${encodeURIComponent(lessonPlanTitle)}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '获取教案内容失败' }));
            throw new Error(typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail));
        }

        const data = await response.json();
        return data.content || '';
    } catch (error: any) {
        console.error('获取教案内容错误:', error);
        throw error; // 向上传播错误，让调用者处理
    }
};

// 获取资源详细信息
const fetchResourceDetails = async (resourceIds: number[]): Promise<BackendResource[]> => {
    try {
        const resources = await Promise.all(
            resourceIds.map(async (id) => {
                const response = await fetch(`http://localhost:8000/resources/${id}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                if (!response.ok) {
                    throw new Error(`获取资源${id}失败`);
                }
                return response.json();
            })
        );
        return resources;
    } catch (error) {
        console.error('获取资源详情错误:', error);
        return [];
    }
};

// 查看详情
const viewDetail = async (record: PreparationRecord) => {
    console.log('查看详情的记录:', record);
    try {
        let content = '';
        if (record.lesson_plan_title) {
            try {
                content = await fetchLessonPlanContent(record.lesson_plan_title);
            } catch (error) {
                console.error('获取教案内容失败:', error);
                window.$showToast('获取教案内容失败，将显示空内容', 'error');
            }
        }

        // 获取所有资源的详细信息
        const pptResources = await fetchResourceDetails(record.selected_resources.courseware || []);
        const videoResources = await fetchResourceDetails(record.selected_resources.video || []);
        const imageResources = await fetchResourceDetails(record.selected_resources.image || []);

        // 转换资源格式
        const resourceDetails = {
            courseware: pptResources.map(r => ({
                id: r.id,
                name: r.resource_name,
                path: r.file_path,
                type: 'PPT' as const
            })),
            video: videoResources.map(r => ({
                id: r.id,
                name: r.resource_name,
                path: r.file_path,
                type: '视频' as const
            })),
            image: imageResources.map(r => ({
                id: r.id,
                name: r.resource_name,
                path: r.file_path,
                type: '图片' as const
            }))
        };

        // 确保 course_id 被正确设置
        currentRecord.value = {
            ...record,
            lesson_plan_content: content,
            resources_details: resourceDetails,
            lesson_plan_id: record.lesson_plan_id || record.id,
            course_id: record.id // 使用记录的 id 作为 course_id
        };
        console.log('设置的当前记录:', currentRecord.value);
        showDetail.value = true;
    } catch (error: any) {
        console.error('获取详情错误:', error);
        window.$showToast(error.message || '获取详情失败', 'error');
    }
};

// 预览资源
const openPreview = (resource: DisplayResource) => {
    previewingResource.value = resource;
    showPreview.value = true;
};

// 关闭预览
const closePreview = () => {
    showPreview.value = false;
    previewingResource.value = null;
};

// 下载教案
const downloadLessonPlan = async (filePath: string) => {
    try {
        const response = await fetch(filePath);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentRecord.value?.course_name}-教案.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        window.$showToast('教案下载成功', 'success');
    } catch (error: any) {
        console.error('下载教案错误:', error);
        window.$showToast('下载教案失败', 'error');
    }
};

// 下载资源
const downloadResource = async (resource: DisplayResource) => {
    try {
        // 从资源ID中移除'ai_'前缀（如果存在）
        const resourceId = typeof resource.id === 'string' 
            ? resource.id.startsWith('ai_') ? resource.id.substring(3) : resource.id
            : resource.id;
            
        // 通过后端API下载资源
        const response = await fetch(`http://localhost:8000/resources/${resourceId}/download`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '下载资源失败' }));
            throw new Error(typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail));
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = resource.name;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        window.$showToast('资源下载成功', 'success');
    } catch (error: any) {
        console.error('下载资源错误:', error);
        window.$showToast(error.message || '下载资源失败', 'error');
    }
};

// 检查是否有资源
const hasResources = computed(() => {
    if (!currentRecord.value?.resources_details) return false;
    const resources = currentRecord.value.resources_details;
    return (resources.courseware?.length || 0) +
        (resources.video?.length || 0) +
        (resources.image?.length || 0) > 0;
});

// 搜索处理
const handleSearch = () => {
    // 已通过计算属性实现
};

// 返回列表
const backToList = () => {
    showDetail.value = false;
    currentRecord.value = null;
};

// 修改资源类型检查函数
const getResourceTypeIcon = (type: 'PPT' | '视频' | '图片') => {
    switch (type) {
        case 'PPT':
            return '/icons/ppt-icon.svg';
        case '视频':
            return '/icons/video-icon.svg';
        case '图片':
            return '/icons/image-icon.svg';
        default:
            return '';
    }
};

const getResourceTypeName = (type: 'PPT' | '视频' | '图片') => {
    switch (type) {
        case 'PPT':
            return '课件';
        case '视频':
            return '视频';
        case '图片':
            return '图片';
        default:
            return '';
    }
};

// 教案编辑相关状态
const isEditingLessonPlan = ref(false);
const editingLessonPlanContent = ref('');

// 习题编辑相关状态
const isEditingExercises = ref(false);
const editingExercises = ref<Exercise[]>([]);
const exercisesList = ref<HTMLElement | null>(null);
const showPublishDialog = ref(false);
const selectedResource = ref<DisplayResource | null>(null);
const publishForm = ref({
    classId: ''
});

// 班级列表
const classes = ref<{ id: number; class_name: string }[]>([]);

// 获取教师的班级列表
const fetchTeacherClasses = async () => {
    try {
        const teacherId = localStorage.getItem('userId');
        if (!teacherId) {
            // errorMessage.value = '获取班级列表失败';
            window.$showToast('获取班级列表失败', 'error');
            return;
        }
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

// 开始编辑教案
const startEditLessonPlan = () => {
    editingLessonPlanContent.value = currentRecord.value?.lesson_plan_content || '';
    isEditingLessonPlan.value = true;
};

// 保存教案
const saveLessonPlan = async () => {
    try {
        if (!currentRecord.value) {
            throw new Error('当前记录不存在');
        }

        console.log('当前记录:', currentRecord.value);

        // 验证必要的数据
        if (!currentRecord.value.lesson_plan_id && !currentRecord.value.id) {
            console.error('缺少教案ID，当前记录:', currentRecord.value);
            throw new Error('教案ID不存在，请刷新页面重试');
        }

        // 验证课程ID
        const courseId = currentRecord.value.id; // 使用记录的 id 作为 course_id
        if (!courseId) {
            console.error('缺少课程ID，当前记录:', currentRecord.value);
            throw new Error('课程ID不存在，请刷新页面重试');
        }

        const requestData = {
            lesson_plan_id: currentRecord.value.lesson_plan_id || currentRecord.value.id,
            title: currentRecord.value.lesson_plan_title || currentRecord.value.course_name,
            content: editingLessonPlanContent.value,
            course_id: courseId
        };

        console.log('发送的请求数据:', requestData);

        const response = await fetch(`http://localhost:8000/lesson-plans/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (!response.ok) {
            const errorMessage = Array.isArray(data.detail)
                ? data.detail.map((err: any) => err.msg || err.message || String(err)).join('; ')
                : data.detail || '保存教案失败';
            throw new Error(errorMessage);
        }

        // 更新当前记录的教案内容
        currentRecord.value.lesson_plan_content = editingLessonPlanContent.value;
        isEditingLessonPlan.value = false;
        window.$showToast('教案保存成功', 'success');
    } catch (error: any) {
        console.error('保存教案错误:', error);
        window.$showToast(error.message || '保存教案失败', 'error');
    }
};

// 取消编辑教案
const cancelEditLessonPlan = () => {
    isEditingLessonPlan.value = false;
    editingLessonPlanContent.value = '';
};

// 开始编辑习题
const startEditExercises = () => {
    editingExercises.value = JSON.parse(JSON.stringify(currentRecord.value?.exercises || []));
    editingExercises.value.forEach(exercise => {
        if (exercise.type === '多选') {
            exercise.selectedAnswers = exercise.answers.split(',');
        }
    });
    isEditingExercises.value = true;
};

// 保存习题
const saveExercises = async () => {
    try {
        if (!currentRecord.value) {
            // showToastMessage('当前记录不存在', 'error');
            window.$showToast('当前记录不存在', 'error');
            return;
        }

        console.log('编辑的习题数据:', editingExercises.value);

        // 处理习题数据
        const processedExercises = [];

        for (const exercise of editingExercises.value) {
            // 创建一个新对象，避免修改原始对象
            const processedExercise = { ...exercise };

            // 确保id是数字类型（如果存在）
            if (processedExercise.id !== undefined) {
                if (typeof processedExercise.id === 'string') {
                    const numId = parseInt(processedExercise.id);
                    if (!isNaN(numId)) {
                        processedExercise.id = numId; // 只在能成功转换时设置
                    } else {
                        // 如果无法解析为数字且是字符串，删除id字段
                        delete processedExercise.id;
                    }
                }
            }

            // 处理多选题答案
            if (exercise.type === '多选' && Array.isArray(exercise.selectedAnswers)) {
                processedExercise.answers = exercise.selectedAnswers.sort().join(',');
            }

            // 处理选项 - 简化处理以避免类型错误
            if (processedExercise.options) {
                // 简单地转换为字符串数组并JSON化
                try {
                    if (typeof processedExercise.options === 'string') {
                        // 尝试解析现有的JSON字符串
                        try {
                            JSON.parse(processedExercise.options);
                            // 如果能解析，保持原样
                        } catch (e) {
                            // 如果不是有效的JSON，转换为JSON字符串数组
                            processedExercise.options = JSON.stringify([processedExercise.options]);
                        }
                    } else {
                        // 非字符串类型，转换为JSON字符串
                        processedExercise.options = JSON.stringify([String(processedExercise.options)]);
                    }
                } catch (e) {
                    // 任何错误，使用默认空数组
                    processedExercise.options = JSON.stringify([]);
                    console.error('处理选项时出错:', e);
                }
            } else {
                // 如果选项为空，设置为空数组
                processedExercise.options = JSON.stringify([]);
            }

            // 确保必填字段不为空
            if (!processedExercise.title) processedExercise.title = "未命名题目";
            if (!processedExercise.content) processedExercise.content = "题目内容";
            if (!processedExercise.answers) processedExercise.answers = "";

            // 删除不需要的字段
            if ('selectedAnswers' in processedExercise) {
                delete processedExercise.selectedAnswers;
            }

            // 添加到处理后的习题列表
            processedExercises.push(processedExercise);
        }

        // 确保course_id是数字
        let courseId = currentRecord.value.course_id;
        if (typeof courseId === 'string') {
            courseId = parseInt(courseId);
            if (isNaN(courseId)) {
                throw new Error('课程ID格式无效');
            }
        }

        // 确保lesson_plan_id是数字
        let lessonPlanId = currentRecord.value.lesson_plan_id;
        if (typeof lessonPlanId === 'string') {
            lessonPlanId = parseInt(lessonPlanId);
            if (isNaN(lessonPlanId)) {
                throw new Error('教案ID格式无效');
            }
        } else if (lessonPlanId === null || lessonPlanId === undefined) {
            // 如果没有lesson_plan_id，使用记录ID
            lessonPlanId = currentRecord.value.id;
            if (typeof lessonPlanId === 'string') {
                lessonPlanId = parseInt(lessonPlanId);
            }
        }

        // 构建请求数据
        const requestData = {
            course_id: courseId,
            exercises: processedExercises,
            lesson_plan_id: lessonPlanId
        };

        console.log('发送的请求数据结构:', {
            'course_id': typeof requestData.course_id,
            'exercises': Array.isArray(requestData.exercises) ? 'Array' : typeof requestData.exercises,
            'lesson_plan_id': typeof requestData.lesson_plan_id
        });
        console.log('实际发送的JSON字符串:', JSON.stringify(requestData));

        // 发送请求
        const response = await fetch(`http://localhost:8000/exercises/save/`, {
            method: 'POST',  // 注意：端点是POST而不是PUT
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'X-Debug-Frontend': 'true'
            },
            body: JSON.stringify(requestData)
        });

        console.log('请求URL:', response.url);
        console.log('响应状态:', response.status, response.statusText);

        // 解析响应
        const responseText = await response.text();
        console.log('原始响应体:', responseText);

        let data;
        try {
            data = JSON.parse(responseText);
            console.log('解析后的响应数据:', data);
        } catch (e) {
            console.error('响应不是有效的JSON:', e);
            data = { detail: responseText };
        }

        // 处理错误
        if (!response.ok) {
            console.error('保存习题返回的错误数据:', data);
            console.error('错误状态码:', response.status);
            console.error('错误响应头:', Object.fromEntries([...response.headers.entries()]));

            // 提取错误信息
            let errorMessage = '保存习题失败';
            if (data.detail) {
                if (typeof data.detail === 'object') {
                    errorMessage = JSON.stringify(data.detail);
                } else {
                    errorMessage = String(data.detail);
                }
            }

            throw new Error(errorMessage);
        }

        // 更新lesson_preparations表中的习题记录
        try {
            // 创建用于更新lesson_preparations的请求数据
            const updatePreparationData = {
                preparation_id: currentRecord.value.id,
                course_id: courseId,
                teacher_id: parseInt(localStorage.getItem('userId') || '0'),
                lesson_plan_id: lessonPlanId,
                selected_resources: currentRecord.value.selected_resources,
                exercises: {
                    selected_ids: data.map((ex: any) => ex.id)
                }
            };

            console.log('更新备课记录请求数据:', updatePreparationData);

            // 发送更新请求
            const updateResponse = await fetch('http://localhost:8000/lesson-preparation/update/', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(updatePreparationData)
            });

            if (!updateResponse.ok) {
                const updateErrorData = await updateResponse.json();
                console.warn('更新备课记录失败:', updateErrorData);
                throw new Error(updateErrorData.detail || '更新备课记录失败');
            }

            const updateResult = await updateResponse.json();
            console.log('备课记录更新成功:', updateResult);

            // 更新当前记录的习题和课程名称
            currentRecord.value.exercises = updateResult.exercises;
            currentRecord.value.course_name = updateResult.course_name;
            isEditingExercises.value = false;
            window.$showToast('习题保存成功', 'success');
        } catch (updateError: any) {
            console.error('更新备课记录出错:', updateError);
            window.$showToast(updateError.message || '更新备课记录失败', 'error');
        }
    } catch (error: any) {
        console.error('保存习题错误:', error);
        window.$showToast(error.message || '保存习题失败', 'error');
    }
};

// 取消编辑习题
const cancelEditExercises = () => {
    isEditingExercises.value = false;
    editingExercises.value = [];
};

// 添加新习题
const addNewExercise = () => {
    const newExercise: Exercise = {
        id: Date.now(), // 使用临时ID
        type: '单选',
        title: '',
        content: '',
        options: JSON.stringify(['选项A', '选项B', '选项C', '选项D']),
        answers: '',
        selectedAnswers: []
    };
    editingExercises.value.push(newExercise);
};

// 删除习题
const deleteExercise = (index: number) => {
    editingExercises.value.splice(index, 1);
};

// 获取习题选项
const getExerciseOptions = (exercise: Exercise) => {
    if (!exercise.options) return [];
    try {
        return JSON.parse(exercise.options).map((text: string) => ({ text }));
    } catch {
        return [];
    }
};

// 添加选项
const addOption = (exercise: Exercise) => {
    const options = getExerciseOptions(exercise);
    if (options.length < 6) {
        options.push({ text: `选项${String.fromCharCode(65 + options.length)}` });
        exercise.options = JSON.stringify(options.map((opt: { text: string }) => opt.text));
    }
};

// 删除选项
const removeOption = (exercise: Exercise, index: number) => {
    const options = getExerciseOptions(exercise);
    options.splice(index, 1);
    exercise.options = JSON.stringify(options.map((opt: { text: string }) => opt.text));
};

// 更新多选题答案
const updateMultipleChoiceAnswers = (exercise: Exercise) => {
    if (Array.isArray(exercise.selectedAnswers)) {
        exercise.answers = exercise.selectedAnswers.sort().join(',');
    }
};

// 处理习题列表滚动
const handleExercisesScroll = () => {
    if (!exercisesList.value) return;

    const { scrollTop, scrollHeight, clientHeight } = exercisesList.value;
    if (scrollTop + clientHeight >= scrollHeight - 50) {
        // 滚动到底部时自动添加新习题
        if (isEditingExercises.value) {
            addNewExercise();
        }
    }
};

// 显示发布对话框
const showPublishModal = (resource: DisplayResource) => {
    selectedResource.value = resource;
    showPublishDialog.value = true;
};

// 关闭发布对话框
const closePublishDialog = () => {
    showPublishDialog.value = false;
    selectedResource.value = null;
    publishForm.value.classId = '';
};

// 发布资源
const publishResources = async () => {
    try {
        if (!selectedResource.value) {
            throw new Error('未选择资源');
        }

        if (!publishForm.value.classId) {
            throw new Error('请选择班级');
        }

        // 确保class_id是整数
        const classId = parseInt(publishForm.value.classId);
        if (isNaN(classId)) {
            throw new Error('班级ID无效');
        }

        const userId = parseInt(localStorage.getItem('userId') || '0');

        // 资源类型已经是中文，直接使用
        const requestData = {
            class_id: classId,
            resource_type: selectedResource.value.type,
            resource_name: selectedResource.value.name,
            file_path: selectedResource.value.path,
            uploaded_by: userId
        };

        console.log('发布资源请求数据:', requestData);

        const response = await fetch('http://localhost:8000/classes/resources/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(requestData)
        });

        console.log('发布资源响应状态:', response.status, response.statusText);

        // 尝试解析响应内容
        let responseData;
        try {
            const responseText = await response.text();
            console.log('原始响应内容:', responseText);
            responseData = responseText ? JSON.parse(responseText) : {};
        } catch (parseError) {
            console.error('解析响应时出错:', parseError);
            responseData = { detail: '无法解析响应' };
        }

        if (!response.ok) {
            console.error('发布资源失败，响应:', responseData);
            throw new Error(responseData.detail || '发布资源失败');
        }

        // 显示成功提示
        window.$showToast('资源发布成功！', 'success');
        closePublishDialog();
    } catch (error: any) {
        console.error('发布资源错误:', error);
        window.$showToast(error.message || '发布资源失败，请稍后重试', 'error');
    }
};

// 发布习题
const publishExercises = async () => {
    try {
        console.log('开始发布习题，当前记录:', currentRecord.value);

        if (!currentRecord.value?.exercises || currentRecord.value.exercises.length === 0) {
            throw new Error('没有可发布的习题');
        }

        if (!publishForm.value.classId) {
            throw new Error('请选择班级');
        }

        const requestData = {
            class_id: parseInt(publishForm.value.classId),
            teacher_id: parseInt(localStorage.getItem('userId') || '0'),
            title: `${currentRecord.value.course_name}习题`,
            description: `来自《${currentRecord.value.course_name}》的练习题`,
            exercises: currentRecord.value.exercises.map(ex => ex.id),
            due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().substring(0, 10), // 默认7天后截止
            course_id: currentRecord.value.course_id // 添加课程ID
        };

        console.log('发布习题请求数据:', requestData);

        const response = await fetch('http://localhost:8000/assignments/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(requestData)
        });

        console.log('发布习题响应状态:', response.status, response.statusText);

        // 尝试解析响应内容
        let responseData;
        try {
            const responseText = await response.text();
            console.log('原始响应内容:', responseText);
            responseData = responseText ? JSON.parse(responseText) : {};
        } catch (parseError) {
            console.error('解析响应时出错:', parseError);
            responseData = { detail: '无法解析响应' };
        }

        if (!response.ok) {
            console.error('发布习题失败，响应:', responseData);
            throw new Error(responseData.detail || '发布习题失败');
        }

        // 显示成功提示
        window.$showToast('习题发布成功！', 'success');
        closePublishDialog();
    } catch (error: any) {
        console.error('发布习题错误:', error);
        window.$showToast(error.message || '发布习题失败，请稍后重试', 'error');
    }
};

// 批量选择相关状态
const selectedRecords = ref<number[]>([]);

// 切换记录选中状态
const toggleRecordSelection = (recordId: number) => {
    const index = selectedRecords.value.indexOf(recordId);
    if (index === -1) {
        selectedRecords.value.push(recordId);
    } else {
        selectedRecords.value.splice(index, 1);
    }
};

// 批量删除
const batchDelete = async () => {
    try {
        // 显示自定义确认对话框
        if (confirm(`确定要删除选中的${selectedRecords.value.length}条记录吗？此操作不可撤销。`)) {
            const response = await fetch('http://localhost:8000/lesson-preparation/batch-delete/', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    preparation_ids: selectedRecords.value
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '删除失败');
            }

            // 从列表中移除已删除的记录
            records.value = records.value.filter(record => !selectedRecords.value.includes(record.id));
            selectedRecords.value = []; // 清空选中列表
            window.$showToast('删除成功', 'success');
        }
    } catch (error: any) {
        window.$showToast(error.message || '删除失败', 'error');
    }
};

// 处理发布按钮点击
const handlePublish = () => {
    console.log('点击习题区域的发布按钮');
    selectedResource.value = null; // 清空资源选择，表示要发布习题
    showPublishDialog.value = true;
};

// 页面加载时获取历史记录
fetchHistory();

// 组件挂载时获取班级列表
onMounted(() => {
    fetchTeacherClasses();
});

// 处理发布表单提交
const handlePublishSubmit = () => {
    console.log('表单提交，selectedResource:', selectedResource.value);
    if (selectedResource.value) {
        publishResources();
    } else {
        publishExercises();
    }
};
</script>

<style scoped>
.history-view {
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
    margin-bottom: 16px;
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

.batch-actions {
    display: flex;
    gap: 12px;
}

.delete-btn {
    padding: 8px 16px;
    background-color: #e74c3c;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.delete-btn:hover {
    background-color: #c0392b;
}

.delete-btn:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
}

.preparation-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow-y: auto;
    padding: 4px;
}

.preparation-card {
    width: 100%;
    background: white;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.3s;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.preparation-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.preparation-card.selected {
    background-color: #f0f7ff;
    border-color: #4c84ff;
}

.card-checkbox {
    padding-top: 4px;
}

.card-checkbox input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
}

.card-content {
    flex: 1;
    cursor: pointer;
}

.info-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.info-section h3 {
    margin: 0;
    color: #333;
    font-size: 16px;
}

.time {
    color: #999;
    font-size: 14px;
}

.class-info {
    display: flex;
    gap: 20px;
    margin: 10px 0;
}

.info-item {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #666;
    font-size: 14px;
}

.info-item i {
    font-size: 16px;
    color: #4c84ff;
}

.resources-summary {
    flex: 1;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0;
}

.resource-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.resource-tag {
    background: #f0f2f5;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 13px;
    color: #666;
    display: flex;
    align-items: center;
    gap: 4px;
}

.resource-tag::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #4c84ff;
}

.resource-tag:nth-child(2)::before {
    background-color: #2ecc71;
}

.resource-tag:nth-child(3)::before {
    background-color: #f1c40f;
}

.resource-tag:nth-child(4)::before {
    background-color: #e74c3c;
}

.preparation-detail {
    background: white;
    border-radius: 8px;
    padding: 20px;
    height: 100%;
    overflow-y: auto;
}

.detail-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
}

.back-btn {
    padding: 8px 16px;
    background: #f5f7fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
}

.detail-section {
    margin-bottom: 24px;
}

.detail-section h3 {
    margin-bottom: 16px;
    color: #333;
}

.lesson-plan-content {
    white-space: pre-wrap;
    line-height: 1.6;
    color: #333;
}

.resources-grid {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.resource-group {
    background: #f8f9fa;
    padding: 16px;
    border-radius: 8px;
    width: 100%;
}

.resource-items {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.resource-item {
    display: grid;
    grid-template-columns: 40px 1fr auto;
    align-items: center;
    gap: 16px;
    padding: 12px 16px;
    background: white;
    border: 1px solid #eee;
    border-radius: 8px;
    transition: all 0.3s;
    width: 100%;
}

.resource-item img {
    width: 24px;
    height: 24px;
}

.resource-item span {
    font-size: 14px;
    color: #2c3e50;
}

.resource-item .resource-actions {
    display: flex;
    gap: 8px;
    justify-self: end;
}

.preview-action,
.download-action,
.publish-action {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.3s;
    white-space: nowrap;
}

.preview-action {
    background-color: #4c84ff;
    color: white;
}

.preview-action:hover {
    background-color: #3a70e3;
}

.download-action {
    background-color: #f5f7fa;
    color: #666;
}

.download-action:hover {
    background-color: #e6e8eb;
    }
    
    .publish-action {
        background-color: #4c84ff;
        color: white;
    }
    
    .publish-action:hover {
        background-color: #3a70e3;
    }
    
    .resource-group h4 {
        color: #2c3e50;
        font-size: 16px;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #4c84ff;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .resource-group h4::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 16px;
        background-color: #4c84ff;
        border-radius: 2px;
    }
    
    .exercises-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .exercise-item {
        background: white;
        border-radius: 8px;
        padding: 16px;
    }
    
    .exercise-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #eee;
    }
    
    .exercise-type-tag {
        background: #4c84ff;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
    }
    
    .exercise-title {
        font-weight: 500;
    }
    
    .exercise-content {
        margin-bottom: 12px;
        line-height: 1.6;
    }
    
    .exercise-options {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 12px;
    }
    
    .option {
        padding: 8px;
        background: white;
        border-radius: 4px;
    }
    
    .exercise-answer {
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid #eee;
        display: flex;
        align-items: flex-start;
        gap: 8px;
    }
    
    .exercise-answer strong {
        white-space: nowrap;
        color: #2ecc71;
        padding: 8px 0;
    }
    
    .exercise-answer textarea {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        line-height: 1.6;
        background: #f8f9fa;
        resize: vertical;
        min-height: 38px;
    }
    
    .answer-options {
        flex: 1;
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-top: 0;
    }
    
    .answer-options label {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: #f8f9fa;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .answer-options label:hover {
        background: #edf2ff;
    }
    
    .answer-options input[type="radio"],
    .answer-options input[type="checkbox"] {
        margin: 0;
        width: 16px;
        height: 16px;
    }
    
    .answer-text {
        color: #2ecc71;
        font-weight: 500;
        padding: 8px 12px;
        background: #f0fff4;
        border-radius: 4px;
        flex: 1;
    }
    
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
    }
    
    .preview-header {
        padding: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #eee;
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
    
    .no-content {
        color: #999;
        font-style: italic;
        text-align: center;
        padding: 20px;
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .download-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        background: #4c84ff;
        color: white;
        border: none;
    }
    
    .publish-action {
        background-color: #4c84ff;
        color: white;
    }
    
    .publish-action:hover {
        background-color: #3a70e3;
    }
    
    .resource-group h4 {
        color: #2c3e50;
        font-size: 16px;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #4c84ff;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .resource-group h4::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 16px;
        background-color: #4c84ff;
        border-radius: 2px;
    }
    
    .exercises-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .exercise-item {
        background: white;
        border-radius: 8px;
        padding: 16px;
    }
    
    .exercise-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #eee;
    }
    
    .exercise-type-tag {
        background: #4c84ff;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
    }
    
    .exercise-title {
        font-weight: 500;
    }
    
    .exercise-content {
        margin-bottom: 12px;
        line-height: 1.6;
    }
    
    .exercise-options {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 12px;
    }
    
    .option {
        padding: 8px;
        background: white;
        border-radius: 4px;
    }
    
    .exercise-answer {
        margin-top: 20px;
        padding-top: 16px;
        border-top: 1px solid #eee;
        display: flex;
        align-items: flex-start;
        gap: 8px;
    }
    
    .exercise-answer strong {
        white-space: nowrap;
        color: #2ecc71;
        padding: 8px 0;
    }
    
    .exercise-answer textarea {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        line-height: 1.6;
        background: #f8f9fa;
        resize: vertical;
        min-height: 38px;
    }
    
    .answer-options {
        flex: 1;
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-top: 0;
    }
    
    .answer-options label {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: #f8f9fa;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .answer-options label:hover {
        background: #edf2ff;
    }
    
    .answer-options input[type="radio"],
    .answer-options input[type="checkbox"] {
        margin: 0;
        width: 16px;
        height: 16px;
    }
    
    .answer-text {
        color: #2ecc71;
        font-weight: 500;
        padding: 8px 12px;
        background: #f0fff4;
        border-radius: 4px;
        flex: 1;
    }
    
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
    }
    
    .preview-header {
        padding: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #eee;
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
    
    .no-content {
        color: #999;
        font-style: italic;
        text-align: center;
        padding: 20px;
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .download-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        background: #4c84ff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .download-btn:hover {
        background: #3a70e3;
    }
    
    .content-text {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        line-height: 1.8;
        font-size: 15px;
        color: #2c3e50;
    }
    
    .toast {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 24px;
        border-radius: 4px;
        font-size: 14px;
        z-index: 1000;
        animation: fadeInOut 2s ease-in-out;
        color: white;
    }
    
    .toast.success {
        background-color: #2ecc71;
    }
    
    .toast.error {
        background-color: #e74c3c;
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
    
    .action-buttons {
        display: flex;
        gap: 8px;
    }
    
    .edit-btn,
    .save-btn,
    .cancel-btn,
    .publish-btn {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 6px 12px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 13px;
        transition: all 0.3s;
    }
    
    .edit-btn {
        background: #f5f7fa;
        color: #666;
    }
    
    .save-btn {
        background: #2ecc71;
        color: white;
    }
    
    .cancel-btn {
        background: #e74c3c;
        color: white;
    }
    
    .publish-btn {
        background: #4c84ff;
        color: white;
    }
    
    .lesson-plan-editor {
        width: 100%;
        min-height: 300px;
        padding: 16px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        line-height: 1.6;
        resize: vertical;
    }
    
    .exercise-item {
        background: white;
        border: 1px solid #eee;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s;
    }
    
    .exercise-item:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .exercise-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #eee;
    }
    
    .exercise-type-selector {
        display: flex;
        gap: 12px;
        align-items: center;
        min-width: 200px;
    }
    
    .exercise-type-selector select {
        width: 100%;
        padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            color: #2c3e50;
            background-color: white;
            }
            
            .exercise-title-input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                background: #f8f9fa;
                height: 38px;
            }
            
            .delete-exercise-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 4px;
                padding: 0 16px;
                background: #f5f7fa;
                color: #e74c3c;
                border: 1px solid #e74c3c;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
                height: 38px;
                white-space: nowrap;
                margin-left: auto;
            }
            
            .delete-exercise-btn:hover {
                background: #e74c3c;
                color: white;
            }
            
            .delete-exercise-btn i {
                font-size: 14px;
            }
            
            .exercise-content {
                margin: 16px 0;
            }
            
            .exercise-content textarea {
                width: 100%;
                min-height: 100px;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                line-height: 1.6;
                background: #f8f9fa;
                resize: vertical;
            }
            
            .options-list {
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin: 16px 0;
            }
            
            .option-item {
                display: flex;
                align-items: center;
                gap: 12px;
                background: #f8f9fa;
                padding: 8px 12px;
                border-radius: 4px;
            }
            
            .option-item input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                }
                
                .remove-option-btn {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                    padding: 6px 12px;
                    background: #f5f7fa;
                    color: #e74c3c;
                    border: 1px solid #e74c3c;
                    border-radius: 4px;
                    cursor: pointer;
                }
                
                .remove-option-btn:hover {
                    background: #e74c3c;
                    color: white;
                }
                
                .add-option-btn {
                    width: 100%;
                    padding: 8px 16px;
                    background: #f5f7fa;
                    border: 1px dashed #4c84ff;
                    border-radius: 4px;
                    color: #4c84ff;
                    cursor: pointer;
                    font-size: 14px;
                    transition: all 0.3s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }
                
                .add-option-btn:hover {
                    background: #edf2ff;
                }
                
                .add-option-btn i {
                    font-size: 14px;
                }
                
                .add-exercise-section {
                    margin-top: 24px;
                    text-align: center;
                }
                
                .add-exercise-btn {
                    padding: 12px 24px;
                    background: #4c84ff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.3s;
                }
                
                .add-exercise-btn:hover {
                    background: #3a70e3;
                    transform: translateY(-1px);
                }
                
                .add-exercise-btn i {
                    font-size: 16px;
                }
                
                .dialog-overlay {
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
                
                .dialog-content {
                    background: white;
                    border-radius: 8px;
                    width: 500px;
                    max-width: 90%;
                }
                
                .dialog-header {
                    padding: 16px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .dialog-body {
                    padding: 16px;
                }
                
                .dialog-footer {
                    padding: 16px;
                    border-top: 1px solid #eee;
                    display: flex;
                    justify-content: flex-end;
                    gap: 8px;
                }
                
                .form-group {
                    margin-bottom: 16px;
                }
                
                .form-group label {
                    display: block;
                    margin-bottom: 8px;
                    color: #333;
                }
                
                .form-group input,
                .form-group select,
                .form-group textarea {
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                
                .form-group textarea {
                    height: 100px;
                    resize: vertical;
                }
                
                .confirm-btn {
                    padding: 8px 16px;
                    background: #4c84ff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                
                .publish-action {
                    display: flex;
                        align-items: center;
                        gap: 4px;
                        padding: 6px 12px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 13px;
                        transition: all 0.3s;
                        background-color: #4c84ff;
    color: white;
}

.publish-action:hover {
    background-color: #3a70e3;
}

.action-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.3s;
}

.action-btn.preview {
    background-color: #4c84ff;
    color: white;
}

.action-btn.preview:hover {
    background-color: #3a70e3;
}

.action-btn.save {
    background-color: #67c23a;
    color: white;
}

.action-btn.cancel {
    background-color: #909399;
    color: white;
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
    font-size: 18px;
    color: #333;
}

.form-group {
    margin-bottom: 16px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #666;
    font-size: 14px;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 8px;
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

.submit-btn:hover {
    background-color: #3a70e3;
}
</style>