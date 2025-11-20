<template>
    <div class="step2-view">
        <div class="main-content">
            <div class="content-section">
                <h3>请编辑教案内容：</h3>
                <div class="editor-container">
                    <textarea v-model="lessonContent" placeholder="请在此输入教案内容..."
                        :disabled="loadingStore.isLoading"></textarea>
                </div>
            </div>

            <div class="actions">
                <button class="action-btn back-btn" @click="goBack" :disabled="loadingStore.isLoading">上一步</button>
                <button class="action-btn save-btn" @click="saveContent" :disabled="loadingStore.isLoading">保存</button>
                <button class="action-btn next-btn" @click="nextStep" :disabled="loadingStore.isLoading">
                    <!--{{ isLastStep ? '完成' : '下一步' }}-->
                    完成
                </button>
            </div>
        </div>

        <!-- 右侧修改建议面板 -->
        <div class="side-panel">
            <div class="suggestions-panel">
                <h3>请输入修改建议：</h3>
                <textarea v-model="modificationSuggestions" placeholder="单击输入文字" :maxlength="200"
                    :disabled="loadingStore.isLoading"></textarea>
                <div class="word-count">{{ modificationSuggestions.length }}/200字</div>
                <button class="regenerate-btn" @click="regenerateContent" :disabled="loadingStore.isLoading">
                    {{ loadingStore.isLoading ? '生成中...' : '再次生成' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useLoadingStore } from '@/stores/loading';
import { apiWithLoading } from '@/utils/api';

const router = useRouter();
const lessonContent = ref('');
const modificationSuggestions = ref('');
const loadingStore = useLoadingStore();

// 计算是否是最后一步
const isLastStep = computed(() => {
    const features = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}').features || {};
    // 只有当两个功能都没选时，才是最后一步
    return !features.resourceRecommend && !features.exerciseGeneration;
});

// 生成教案
const generateLessonPlan = async () => {
    try {
        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            window.$showToast('未找到课程信息', 'error');
            return;
        }

        loadingStore.showLoading('正在生成教案，请稍候...');

        const data = await apiWithLoading.post<{content: string}>(
            'http://localhost:8000/lesson-plans/generate/',
            {
                course_id: courseInfo.id,
                suggestions: modificationSuggestions.value
            },
            ''  // 空消息，因为已经显示了自定义消息
        );
        
        lessonContent.value = data.content;

        window.$showToast('生成教案成功！', 'success');
    } catch (error: any) {
        console.error('生成教案错误:', error);
        window.$showToast(error.message || '生成教案失败，请稍后重试', 'error');
    } finally {
        loadingStore.hideLoading();
    }
};

// 页面加载时自动生成教案
onMounted(() => {
    generateLessonPlan();
});

// 返回上一步
const goBack = () => {
    router.push('/teacher/workbench/step1');
};

// 保存内容
const saveContent = async () => {
    try {
        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            window.$showToast('未找到课程信息', 'error');
            return;
        }

        loadingStore.showLoading('正在保存教案...');

        const data = await apiWithLoading.post<{id: number}>(
            'http://localhost:8000/lesson-plans/save/',
            {
                course_id: courseInfo.id,
                content: lessonContent.value
            },
            ''  // 空消息，因为已经显示了自定义消息
        );

        courseInfo.lessonPlanId = data.id;
        localStorage.setItem('currentCourseInfo', JSON.stringify(courseInfo));

        window.$showToast('保存成功！', 'success');
    } catch (error: any) {
        console.error('保存教案错误:', error);
        window.$showToast(error.message || '保存教案失败，请稍后重试', 'error');
    } finally {
        loadingStore.hideLoading();
    }
};

// 下一步
const nextStep = () => {
    saveContent();
    // 获取功能选择
    const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
    const features = courseInfo.features || {};
    router.push('/teacher/workbench');
    /*if (features.exerciseGeneration) {
        // 如果选择了练习题生成，无论是否选择了资源推荐，都先去 step4
        router.push('/teacher/workbench/step4');
    } else if (features.resourceRecommend) {
        // 如果只选了资源推荐，去 step3
        router.push('/teacher/workbench/step3');
    } else {
        // 如果都没选，完成
        router.push('/teacher/workbench');
    }*/
};

// 重新生成内容
const regenerateContent = () => {
    if (!modificationSuggestions.value.trim()) {
        window.$showToast('请先输入修改建议', 'error');
        return;
    }
    generateLessonPlan();
};
</script>

<style scoped>
.step2-view {
    height: 100%;
    display: flex;
    gap: 20px;
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
}

.content-section {
    flex: 1;
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    margin-bottom: 16px;
}

.editor-container {
    flex: 1;
    display: flex;
    margin-top: 12px;
}

.editor-container textarea {
    width: 100%;
    height: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: none;
    font-size: 14px;
    line-height: 1.6;
}

.side-panel {
    width: 300px;
    flex-shrink: 0;
    height: 100%;
}

h3 {
    color: #333;
    margin: 0;
    font-size: 16px;
}

/* 按钮样式 */
.actions {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    height: 48px;
}

.action-btn {
    flex: 1;
    height: 100%;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
    padding: 0;
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

/* 右侧修改建议面板样式 */
.suggestions-panel {
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    height: 100%;
    display: flex;
    flex-direction: column;
}

.suggestions-panel textarea {
    flex: 1;
    margin: 12px 0 8px;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: none;
    font-size: 14px;
}

.word-count {
    text-align: right;
    color: #666;
    font-size: 12px;
    margin-bottom: 12px;
}

.regenerate-btn {
    width: 100%;
    height: 48px;
    background-color: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
    padding: 0;
}

.regenerate-btn:hover {
    background-color: #3a70e3;
}

/* 禁用状态样式 */
button:disabled {
    background-color: #ccc !important;
    cursor: not-allowed;
}

textarea:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
}
</style>