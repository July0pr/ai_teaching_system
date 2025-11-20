<template>
    <div class="step4-view">
        <div class="main-content">
            <!-- 添加作业选择下拉栏 -->
            <div class="homework-selection">
                <h3>选择目标作业：</h3>
                <select v-model="selectedHomework" class="homework-select" @change="handleHomeworkChange">
                    <option :value="null">请选择作业</option>
                    <option v-for="homework in homeworkList" :key="homework.id" :value="homework.id">
                        {{ homework.title }} - {{ homework.class_name }} (得分：{{ homework.score }})
                    </option>
                </select>
            </div>

            <div class="question-settings" :class="{ collapsed: isSettingsCollapsed }">
                <div class="settings-header">
                    <h3>题目设置</h3>
                    <button class="collapse-btn" @click="toggleSettings">
                        {{ isSettingsCollapsed ? '展开' : '收起' }}
                    </button>
                </div>
                <div class="settings-content" v-show="!isSettingsCollapsed">
                    <div class="question-types">
                        <h3>题型选择：</h3>
                        <div class="type-buttons">
                            <div class="type-button" :class="{ active: (selectedTypes || []).includes('choice') }"
                                @click="toggleType('choice')">
                                选择题
                                <div class="count-input" @click.stop>
                                    <input type="number" v-model="questionCounts.choice" min="0" max="99"
                                        @input="validateCount('choice')">
                                    <span class="unit">道</span>
                                </div>
                            </div>
                            <div class="type-button" :class="{ active: (selectedTypes || []).includes('judgment') }"
                                @click="toggleType('judgment')">
                                判断题
                                <div class="count-input" @click.stop>
                                    <input type="number" v-model="questionCounts.judgment" min="0" max="99"
                                        @input="validateCount('judgment')">
                                    <span class="unit">道</span>
                                </div>
                            </div>
                            <div class="type-button" :class="{ active: (selectedTypes || []).includes('blank') }"
                                @click="toggleType('blank')">
                                填空题
                                <div class="count-input" @click.stop>
                                    <input type="number" v-model="questionCounts.blank" min="0" max="99"
                                        @input="validateCount('blank')">
                                    <span class="unit">道</span>
                                </div>
                            </div>
                            <div class="type-button" :class="{ active: (selectedTypes || []).includes('short') }"
                                @click="toggleType('short')">
                                简答题
                                <div class="count-input" @click.stop>
                                    <input type="number" v-model="questionCounts.short" min="0" max="99"
                                        @input="validateCount('short')">
                                    <span class="unit">道</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="difficulty-setting">
                        <h3>难度设置：</h3>
                        <div class="difficulty-slider-container">
                            <div class="difficulty-labels">
                                <span>易</span>
                                <span>较易</span>
                                <span>中</span>
                                <span>较难</span>
                                <span>难</span>
                            </div>
                            <div class="slider-wrapper">
                                <input type="range" v-model="difficulty" :min="1" :max="5" :step="1"
                                    class="difficulty-slider">
                            </div>
                        </div>
                    </div>

                    <button class="generate-btn" @click="generateQuestions"
                        :disabled="!selectedHomework || loadingStore.isLoading">
                        {{ loadingStore.isLoading ? '生成中...' : '一键生成' }}
                    </button>
                </div>
            </div>

            <div class="questions-list">
                <div class="list-header">
                    <h3>题目列表：</h3>
                </div>
                <div class="questions-container">
                    <div v-for="(question, index) in questions" :key="index" class="question-item"
                        :class="{ selected: selectedQuestions.includes(index) }"
                        @click="toggleQuestionSelection(index)">
                        <div class="question-header">
                            <span class="question-number">题目 {{ index + 1 }}</span>
                            <button class="delete-btn" @click.stop="deleteQuestion(index)">删除</button>
                        </div>
                        <div class="question-content">{{ question.content }}</div>
                        <div class="question-footer">
                            <span class="question-type">{{ question.type }}</span>
                            <span class="difficulty-badge">难度: {{ question.difficulty }}</span>
                        </div>
                    </div>
                    <div v-if="questions.length === 0" class="empty-message">
                        暂无题目，请先选择作业并生成题目
                    </div>
                </div>
                <button class="save-btn" @click="saveQuestions" :disabled="questions.length === 0 || loadingStore.isLoading">
                    {{ loadingStore.isLoading ? '保存中...' : '保存题目' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { useLoadingStore } from '@/stores/loading';
import { apiWithLoading } from '@/utils/api';

interface Homework {
    id: number;
    title: string;
    class_name: string;
    score: number;
}

interface ExerciseQuestion {
    type: string;
    title: string;
    content: string;
    options?: string;
    answers: string;
    difficulty: number;
}

const router = useRouter();
const loadingStore = useLoadingStore();

// 作业列表数据
const homeworkList = ref<Homework[]>([]);
const selectedHomework = ref<number | null>(null);

// 创建一个会话ID
const currentSessionId = ref<string>(uuidv4());
const currentSequence = ref<number>(0);

// 选中的题型
const selectedTypes = ref<string[]>(['choice']);

// 题目数量统计
const questionCounts = reactive({
    choice: 3,
    judgment: 2,
    blank: 1,
    short: 0
});

// 难度设置
const difficulty = ref(3);

// 题目列表
const questions = ref<ExerciseQuestion[]>([]);

// 选中的题目
const selectedQuestions = ref<number[]>([]);

// 获取已完成的作业列表
const fetchHomeworkList = async () => {
    try {
        loadingStore.showLoading('正在获取作业列表...');
        const userId = localStorage.getItem('userId');

        // 获取学生所有提交的作业
        const response = await apiWithLoading.get<any[]>(`/students/${userId}/submissions`, '');

        // 将作业数据转换为需要的格式
        const submissions = response;
        const homeworks = await Promise.all(submissions.map(async (submission: any) => {
            try {
                // 获取作业信息
                const assignmentResponse = await apiWithLoading.get<any>(`/assignments/${submission.assignment_id}`, '');

                // 获取班级信息
                const classResponse = await apiWithLoading.get<any>(`/classes/${assignmentResponse.class_id}`, '');

                return {
                    id: submission.assignment_id,
                    title: assignmentResponse.title,
                    class_name: classResponse.class_name,
                    score: submission.grade || 0
                };
            } catch (error) {
                console.error('获取作业详情失败:', error);
                return null;
            }
        }));

        homeworkList.value = homeworks.filter((h): h is Homework => h !== null);
    } catch (error) {
        console.error('获取作业列表失败:', error);
        window.$showToast('获取作业列表失败', 'error');
    } finally {
        loadingStore.hideLoading();
    }
};

// 选择作业
const handleHomeworkChange = () => {
    if (selectedHomework.value) {
        // 选择新作业时，可以设置一个新的会话ID
        currentSessionId.value = uuidv4();
        currentSequence.value = 0;
    }
};

// 验证题目数量
const validateCount = (type: keyof typeof questionCounts) => {
    let value = questionCounts[type];
    if (value < 0) questionCounts[type] = 0;
    if (value > 99) questionCounts[type] = 99;
};

// 切换题型选择
const toggleType = (type: string) => {
    // 确保selectedTypes是数组
    if (!Array.isArray(selectedTypes.value)) {
        selectedTypes.value = [];
    }
    
    const index = selectedTypes.value.indexOf(type);
    if (index === -1) {
        selectedTypes.value.push(type);
    } else {
        selectedTypes.value.splice(index, 1);
    }
};

// 切换题目选中状态
const toggleQuestionSelection = (index: number) => {
    const selectedIndex = selectedQuestions.value.indexOf(index);
    if (selectedIndex === -1) {
        selectedQuestions.value.push(index);
    } else {
        selectedQuestions.value.splice(selectedIndex, 1);
    }
};

// 删除题目
const deleteQuestion = (index: number) => {
    questions.value.splice(index, 1);
};

// 设置显示/隐藏
const isSettingsCollapsed = ref(false);
const toggleSettings = () => {
    isSettingsCollapsed.value = !isSettingsCollapsed.value;
};

// 生成题目
const generateQuestions = async () => {
    if (!selectedHomework.value) {
        window.$showToast('请先选择目标作业', 'error');
        return;
    }

    if (selectedTypes.value.length === 0) {
        window.$showToast('请至少选择一种题型', 'error');
        return;
    }

    try {
        loadingStore.showLoading('正在生成练习题，请稍候...');

        // 将选择的题型转换为API需要的格式
        const typesPayload: Record<string, number> = {};
        selectedTypes.value.forEach(type => {
            typesPayload[type] = questionCounts[type as keyof typeof questionCounts];
        });

        const userId = localStorage.getItem('userId');
        
        // 确保数据格式与后端API的GenerateStudentExercisesRequest匹配
        const requestData = {
            student_id: parseInt(userId || '0'),
            assignment_id: selectedHomework.value,
            types: typesPayload,
            difficulty: difficulty.value,
            session_id: currentSessionId.value
        };
        
        console.log('发送的请求数据:', requestData);
        
        // 获取选中作业的信息，用于调试
        const selectedHomeworkInfo = homeworkList.value.find(h => h.id === selectedHomework.value);
        console.log('选中的作业信息:', selectedHomeworkInfo);

        try {
            const response = await apiWithLoading.post<any[]>(
                '/student/exercises/generate', 
                requestData,
                ''
            );

            console.log('接收到的响应:', response);
            
            // API直接返回题目数组，不是嵌套在exercises属性中
            if (Array.isArray(response)) {
                if (response.length === 0) {
                    window.$showToast('后端未生成任何习题，请尝试其他作业或联系管理员', 'error');
                    return;
                }
                
                questions.value = response;
                
                // 检查返回的习题是否和选择的作业类型相关
                console.log('生成的习题与作业的相关性分析:', {
                    '作业标题': selectedHomeworkInfo?.title,
                    '作业成绩': selectedHomeworkInfo?.score,
                    '生成题目数量': response.length,
                    '生成题目示例': response.slice(0, 2)
                });
                
                window.$showToast('习题生成成功！', 'success');
            } else {
                throw new Error('返回的数据格式不正确');
            }
        } catch (error: any) {
            console.error('API调用失败:', error);
            throw error;
        }
    } catch (error: any) {
        console.error('生成题目失败:', error);
        
        // 增强错误日志，帮助诊断问题
        if (error.response) {
            console.error('错误状态码:', error.response.status);
            console.error('错误数据:', error.response.data);
        }
        
        // 显示更具体的错误信息
        let errorMessage = '生成题目失败，请稍后重试';
        if (error.response?.data?.detail) {
            errorMessage = `错误: ${error.response.data.detail}`;
        } else if (error.message) {
            errorMessage = `错误: ${error.message}`;
        }
        
        window.$showToast(errorMessage, 'error');
    } finally {
        loadingStore.hideLoading();
    }
};

// 保存题目
const saveQuestions = async () => {
    if (!selectedHomework.value) {
        window.$showToast('请先选择目标作业', 'error');
        return;
    }

    if (questions.value.length === 0) {
        window.$showToast('请先生成题目', 'error');
        return;
    }

    try {
        loadingStore.showLoading('正在保存练习题...');
        const userId = localStorage.getItem('userId');

        // 确保请求格式与后端API的SaveStudentExercisesRequest模型匹配
        const requestData = {
            student_id: parseInt(userId || '0'),
            assignment_id: selectedHomework.value,
            exercises: questions.value,
            session_id: currentSessionId.value
        };
        
        console.log('保存题目请求数据:', requestData);

        const response = await apiWithLoading.post<any>(
            '/student/exercises/save', 
            requestData,
            ''
        );
        
        console.log('保存题目响应:', response);

        if (response && response.success) {
            window.$showToast('题目保存成功！', 'success');
            if (response.sequence_number !== undefined) {
                currentSequence.value = response.sequence_number;
            }
        } else {
            window.$showToast('保存成功，但未返回预期的响应数据', 'success');
        }
    } catch (error: any) {
        console.error('保存题目失败:', error);
        window.$showToast(error.response?.data?.detail || '保存题目失败，请稍后重试', 'error');
    } finally {
        loadingStore.hideLoading();
    }
};

// 在组件挂载时获取作业列表
onMounted(() => {
    fetchHomeworkList();
});
</script>

<style scoped>
.step4-view {
    height: 100%;
    display: flex;
    max-width: 1400px;
    margin: 0 auto;
    box-sizing: border-box;
    position: relative;
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
    
    h2,
    h3 {
        margin: 0;
        color: #333;
    }
    
        .homework-selection {
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
    
        .homework-selection h3 {
            margin-bottom: 12px;
            font-size: 16px;
        }
    
        .homework-select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
    
        .question-settings {
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
        }
    
        .settings-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
    
        .collapse-btn {
            padding: 4px 12px;
            background: #f5f7fa;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
    
        .question-types {
            margin-bottom: 20px;
        }
    
        .type-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 12px;
        }
    
        .type-button {
            padding: 8px 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
            background: white;
            color: #666;
            display: flex;
            align-items: center;
            gap: 12px;
        }
    
        .type-button.active {
            background: #4c84ff;
            color: white;
            border-color: #4c84ff;
        }
    
        .type-button.active .count-input {
            background: rgba(255, 255, 255, 0.2);
        }
    
        .type-button.active .count-input input {
            border-color: rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
    
        .count-input {
            display: flex;
            align-items: center;
        }
    
        .count-input input {
            width: 40px;
            padding: 4px;
            border: 1px solid #ddd;
            border-radius: 4px;
            text-align: center;
        }
    
        .unit {
            font-size: 12px;
            color: #666;
            margin-left: 4px;
        }
    
        .difficulty-setting {
            margin-bottom: 20px;
        }
    
        .difficulty-slider-container {
            margin-top: 12px;
        }
    
        .difficulty-labels {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
            color: #666;
        }
    
        .slider-wrapper {
            padding: 0 10px;
        }
    
        .difficulty-slider {
            width: 100%;
        }
    
        .generate-btn {
            padding: 12px 24px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
            width: 100%;
        }
    
        .generate-btn:hover {
            background: #2980b9;
        }
    
        .generate-btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
    
        .questions-list {
            flex: 1;
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
    
        .list-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
    
        .questions-container {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 16px;
        }
    
        .question-item {
            padding: 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.3s;
        }
    
        .question-item.selected {
            border-color: #3498db;
            background: rgba(52, 152, 219, 0.05);
        }
    
        .question-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
    
        .question-number {
            font-weight: bold;
            color: #333;
        }
    
        .delete-btn {
            padding: 4px 8px;
            background: #f5f7fa;
            border: none;
            border-radius: 4px;
            color: #666;
            cursor: pointer;
        }
    
        .delete-btn:hover {
            background: #e6e8eb;
        }
    
        .question-content {
            margin-bottom: 12px;
            line-height: 1.5;
            color: #333;
        }
    
        .question-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
        }
    
        .question-type {
            color: #666;
            background: #f5f7fa;
            padding: 4px 8px;
            border-radius: 4px;
        }
    
        .difficulty-badge {
            color: #666;
        }
    
        .save-btn {
            padding: 12px 24px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
    
        .save-btn:hover {
            background: #2980b9;
        }
    
        .save-btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
    .empty-message {
        padding: 40px;
        text-align: center;
        color: #999;
        font-size: 14px;
    }
</style>