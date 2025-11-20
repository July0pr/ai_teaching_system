<template>
    <div class="step4-view">
        <div class="main-content">
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

                    <button class="generate-btn" @click="generateQuestions" :disabled="loadingStore.isLoading">
                        {{ loadingStore.isLoading ? '生成中...' : '一键生成' }}
                    </button>
                </div>
            </div>

            <div class="questions-list">
                <h3>题目列表：</h3>
                <div class="questions-container">
                    <div v-for="(question, index) in (questions || [])" :key="index" class="question-item"
                        :class="{ selected: (selectedQuestions || []).includes(index) }"
                        @click="toggleQuestionSelection(index)">
                        <div class="question-header">
                            <span class="question-number">题目 {{ index + 1 }}</span>
                            <div class="question-actions">
                                <button class="edit-btn" @click.stop="editQuestion(index)">编辑</button>
                                <button class="delete-btn" @click.stop="deleteQuestion(index)">删除</button>
                            </div>
                        </div>
                        <div class="question-content">
                            <div class="question-title">{{ question.title }}</div>
                            <div class="question-text">{{ question.content }}</div>
                            <div v-if="question.options" class="question-options">
                                <div v-for="(option, optIndex) in JSON.parse(question.options || '[]')" :key="optIndex">
                                    {{ String.fromCharCode(65 + optIndex) }}. {{ option }}
                                </div>
                            </div>
                            <div class="question-answer">答案：{{ question.answers }}</div>
                        </div>
                        <div class="question-type">{{ question.type }}</div>
                    </div>
                </div>
                <button class="add-question-btn" @click="showAddQuestionDialog">添加题目</button>
            </div>

            <div class="actions">
                <button class="action-btn back-btn" @click="goBack" :disabled="loadingStore.isLoading">上一步</button>
                <button class="action-btn save-btn" @click="saveContent" :disabled="loadingStore.isLoading">保存</button>
                <button class="action-btn next-btn" @click="nextStep" :disabled="loadingStore.isLoading">
                    {{ isLastStep ? '完成' : '下一步' }}
                </button>
            </div>
        </div>

        <div class="side-panel">
            <div class="suggestion-input">
                <h3>修改建议：</h3>
                <textarea v-model="suggestion" placeholder="请输入修改建议..." maxlength="200" 
                    :disabled="loadingStore.isLoading"></textarea>
                <div class="word-count">{{ (suggestion || '').length }}/200字</div>
                <button class="regenerate-btn" @click="regenerateQuestions" :disabled="loadingStore.isLoading">
                    {{ loadingStore.isLoading ? '生成中...' : '重新生成' }}
                </button>
            </div>
        </div>

        <!-- 编辑题目对话框 -->
        <div v-if="showDialog" class="dialog-overlay" @click="closeDialog">
            <div class="dialog-content" @click.stop>
                <div class="dialog-header">
                    <h3>{{ editingIndex === -1 ? '添加题目' : '编辑题目' }}</h3>
                    <button class="close-btn" @click="closeDialog">&times;</button>
                </div>
                <div class="dialog-body">
                    <div class="form-group">
                        <label>题目类型：</label>
                        <select v-model="editingQuestion.type">
                            <option value="单选">单选题</option>
                            <option value="多选">多选题</option>
                            <option value="判断">判断题</option>
                            <option value="填空">填空题</option>
                            <option value="简答">简答题</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>标题：</label>
                        <input type="text" v-model="editingQuestion.title" placeholder="请输入题目标题">
                    </div>
                    <div class="form-group">
                        <label>内容：</label>
                        <textarea v-model="editingQuestion.content" placeholder="请输入题目内容"></textarea>
                    </div>
                    <div class="form-group" v-if="['单选', '多选', '判断'].includes(editingQuestion.type || '')">
                        <label>选项：</label>
                        <div v-if="editingQuestion.type === '判断'" class="options-list">
                            <div class="option-item">
                                <span>1. 正确</span>
                            </div>
                            <div class="option-item">
                                <span>2. 错误</span>
                            </div>
                        </div>
                        <div v-else class="options-list">
                            <div v-for="(option, index) in (parsedOptions || [])" :key="index" class="option-item">
                                <span>{{ String.fromCharCode(65 + index) }}.</span>
                                <input type="text" v-model="parsedOptions[index]"
                                    :placeholder="'选项' + String.fromCharCode(65 + index)">
                                <button v-if="index > 1" @click="removeOption(index)"
                                    class="remove-option-btn">&times;</button>
                            </div>
                            <button v-if="(parsedOptions || []).length < 6" @click="addOption"
                                class="add-option-btn">添加选项</button>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>答案：</label>
                        <div v-if="editingQuestion.type === '单选'" class="answer-options">
                            <label v-for="(option, index) in (parsedOptions || [])" :key="index">
                                <input type="radio" :value="String.fromCharCode(65 + index)"
                                    v-model="editingQuestion.answers">
                                {{ String.fromCharCode(65 + index) }}
                            </label>
                        </div>
                        <div v-else-if="editingQuestion.type === '多选'" class="answer-options">
                            <label v-for="(option, index) in (parsedOptions || [])" :key="index">
                                <input type="checkbox" :value="String.fromCharCode(65 + index)"
                                    v-model="selectedAnswers">
                                {{ String.fromCharCode(65 + index) }}
                            </label>
                        </div>
                        <div v-else-if="editingQuestion.type === '判断'" class="answer-options">
                            <label>
                                <input type="radio" value="正确" v-model="editingQuestion.answers">
                                正确
                            </label>
                            <label>
                                <input type="radio" value="错误" v-model="editingQuestion.answers">
                                错误
                            </label>
                        </div>
                        <textarea v-else v-model="editingQuestion.answers" placeholder="请输入答案"></textarea>
                    </div>
                </div>
                <div class="dialog-footer">
                    <button class="cancel-btn" @click="closeDialog">取消</button>
                    <button class="save-btn" @click="saveQuestion">保存</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useLoadingStore } from '@/stores/loading';
import { apiWithLoading } from '@/utils/api';

const router = useRouter();

// 添加loadingStore
const loadingStore = useLoadingStore();

// 设置面板折叠状态
const isSettingsCollapsed = ref(false);

// 选中的题型
const selectedTypes = ref<string[]>([]);

// 题目数量统计
const questionCounts = reactive({
    choice: 0,
    judgment: 0,
    blank: 0,
    short: 0
});

// 难度设置
const difficulty = ref(3);

// 难度等级映射
const difficultyLevels: Record<string, string> = {
    '1': '易',
    '2': '较易',
    '3': '中',
    '4': '较难',
    '5': '难'
};

interface Question {
    id?: number;
    type: string;
    title: string;
    content: string;
    options?: string | null;
    answers: string;
}

// 题目列表
const questions = ref<Question[]>([]);

// 选中的题目
const selectedQuestions = ref<number[]>([]);

// 修改建议
const suggestion = ref('');

// 加载状态
const isLoading = ref(false);

// 编辑相关的状态
const showDialog = ref(false);
const editingIndex = ref(-1);
const editingQuestion = ref<Question>({
    type: '单选',
    title: '',
    content: '',
    options: JSON.stringify(['选项A', '选项B', '选项C', '选项D']),
    answers: ''
});
const selectedAnswers = ref<string[]>([]);
const parsedOptions = ref<string[]>(['选项A', '选项B', '选项C', '选项D']);

// 保存数据到 localStorage
const saveToLocalStorage = () => {
    const step4Data = {
        selectedTypes: selectedTypes.value,
        questionCounts,
        difficulty: difficulty.value,
        questions: questions.value,
        selectedQuestions: selectedQuestions.value,
        suggestion: suggestion.value,
        isSettingsCollapsed: isSettingsCollapsed.value
    };

    // 获取当前课程信息
    const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
    courseInfo.step4Data = step4Data;
    localStorage.setItem('currentCourseInfo', JSON.stringify(courseInfo));
};

// 从 localStorage 恢复数据
const restoreFromLocalStorage = () => {
    try {
        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        const step4Data = courseInfo.step4Data || {};

        // 确保所有必要的属性都存在，使用默认值
        selectedTypes.value = Array.isArray(step4Data.selectedTypes) ? step4Data.selectedTypes : [];
        
        if (step4Data.questionCounts) {
            Object.assign(questionCounts, step4Data.questionCounts);
        }
        
        difficulty.value = step4Data.difficulty || 3;
        questions.value = Array.isArray(step4Data.questions) ? step4Data.questions : [];
        selectedQuestions.value = Array.isArray(step4Data.selectedQuestions) ? step4Data.selectedQuestions : [];
        suggestion.value = step4Data.suggestion || '';
        isSettingsCollapsed.value = !!step4Data.isSettingsCollapsed;
    } catch (error) {
        console.error('从localStorage恢复数据失败:', error);
        // 重置为默认值
        selectedTypes.value = [];
        questions.value = [];
        selectedQuestions.value = [];
        suggestion.value = '';
        isSettingsCollapsed.value = false;
    }
};

// 监听数据变化，自动保存
watch([selectedTypes, questionCounts, difficulty, questions, selectedQuestions, suggestion, isSettingsCollapsed],
    () => {
        saveToLocalStorage();
    },
    { deep: true }
);

// 组件挂载时恢复数据
onMounted(() => {
    restoreFromLocalStorage();
});

// 验证题目数量
const validateCount = (type: keyof typeof questionCounts) => {
    let value = questionCounts[type];
    if (value < 0) questionCounts[type] = 0;
    if (value > 99) questionCounts[type] = 99;
};

// 获取难度文字说明
const getDifficultyText = (value: number) => {
    if (value <= 20) return '易';
    if (value <= 40) return '较易';
    if (value <= 60) return '中';
    if (value <= 80) return '较难';
    return '难';
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
    
    // 确保状态更新后保存到localStorage
    saveToLocalStorage();
};

// 切换题目选中状态
const toggleQuestionSelection = (index: number) => {
    // 确保数组初始化
    if (!Array.isArray(selectedQuestions.value)) {
        selectedQuestions.value = [];
    }
    if (!Array.isArray(questions.value)) {
        questions.value = [];
        return; // 如果没有题目，直接返回
    }
    
    // 确保questions数组有元素且索引有效
    if (questions.value.length === 0 || index < 0 || index >= questions.value.length) return;
    
    const selectedIndex = selectedQuestions.value.indexOf(index);
    if (selectedIndex === -1) {
        selectedQuestions.value.push(index);
    } else {
        selectedQuestions.value.splice(selectedIndex, 1);
    }
    
    // 确保状态更新后保存到localStorage
    saveToLocalStorage();
};

// 删除题目
const deleteQuestion = (index: number) => {
    // 如果题目在选中列表中，也要从选中列表中移除
    const selectedIndex = selectedQuestions.value.indexOf(index);
    if (selectedIndex !== -1) {
        selectedQuestions.value.splice(selectedIndex, 1);
    }
    // 更新其他选中题目的索引
    selectedQuestions.value = selectedQuestions.value.map(i => i > index ? i - 1 : i);
    questions.value.splice(index, 1);
};

// 显示添加题目对话框
const showAddQuestionDialog = () => {
    editingIndex.value = -1;
    editingQuestion.value = {
        type: '单选',
        title: '',
        content: '',
        options: JSON.stringify(['选项A', '选项B', '选项C', '选项D']),
        answers: ''
    };
    selectedAnswers.value = [];
    parsedOptions.value = ['选项A', '选项B', '选项C', '选项D'];
    showDialog.value = true;
};

// 编辑题目
const editQuestion = (index: number) => {
    editingIndex.value = index;
    const question = questions.value[index];
    editingQuestion.value = { ...question };
    if (question.options) {
        parsedOptions.value = JSON.parse(question.options);
    }
    if (question.type === '多选') {
        selectedAnswers.value = question.answers.split(',');
    }
    showDialog.value = true;
};

// 关闭对话框
const closeDialog = () => {
    showDialog.value = false;
    editingIndex.value = -1;
    editingQuestion.value = {
        type: '单选',
        title: '',
        content: '',
        options: JSON.stringify(['选项A', '选项B', '选项C', '选项D']),
        answers: ''
    };
    selectedAnswers.value = [];
};

// 添加选项
const addOption = () => {
    if (parsedOptions.value.length < 6) {
        parsedOptions.value.push('新选项');
    }
};

// 删除选项
const removeOption = (index: number) => {
    parsedOptions.value.splice(index, 1);
};

// 保存题目
const saveQuestion = () => {
    // 验证必填字段
    if (!editingQuestion.value.title.trim()) {
        window.$showToast('请输入题目标题', 'error');
        return;
    }
    if (!editingQuestion.value.content.trim()) {
        window.$showToast('请输入题目内容', 'error');
        return;
    }

    // 处理选项和答案
    if (['单选', '多选', '判断'].includes(editingQuestion.value.type)) {
        if (editingQuestion.value.type === '判断') {
            editingQuestion.value.options = JSON.stringify(['正确', '错误']);
        } else {
            editingQuestion.value.options = JSON.stringify(parsedOptions.value);
        }

        if (editingQuestion.value.type === '多选') {
            editingQuestion.value.answers = selectedAnswers.value.sort().join(',');
        }
    } else {
        editingQuestion.value.options = null;
    }

    if (editingIndex.value === -1) {
        // 添加新题目
        questions.value.push({ ...editingQuestion.value });
    } else {
        // 更新现有题目
        questions.value[editingIndex.value] = { ...editingQuestion.value };
    }

    closeDialog();
};

// 监听题目类型变化
watch(() => editingQuestion.value.type, (newType) => {
    if (newType === '判断') {
        editingQuestion.value.options = JSON.stringify(['正确', '错误']);
        editingQuestion.value.answers = '正确';
    } else if (newType === '单选' || newType === '多选') {
        parsedOptions.value = ['选项A', '选项B', '选项C', '选项D'];
        editingQuestion.value.options = JSON.stringify(parsedOptions.value);
        editingQuestion.value.answers = '';
        selectedAnswers.value = [];
    } else {
        editingQuestion.value.options = null;
        editingQuestion.value.answers = '';
        selectedAnswers.value = [];
    }
});

// 计算是否是最后一步
const isLastStep = computed(() => {
    const features = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}').features || {};
    // 如果没有选择资源推荐，那么这就是最后一步
    return !features.resourceRecommend;
});

// 返回上一步
const goBack = () => {
    saveToLocalStorage(); // 保存当前数据
    router.push('/teacher/workbench/step2');
};

// 保存内容
const saveContent = async () => {
    try {
        loadingStore.showLoading('正在保存习题...');

        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            throw new Error('未找到课程信息');
        }

        // 使用apiWithLoading替换原来的fetch
        const response = await apiWithLoading.post<Question[]>('/exercises/save/', {
            course_id: courseInfo.id,
            exercises: questions.value
        }, ''); // 空消息，因为已经显示了自定义消息

        // 重要：用服务器返回的数据（包含ID）更新questions状态
        if (Array.isArray(response)) {
            console.log('服务器返回的习题数据:', response);
            questions.value = response;
        } else {
            console.error('服务器返回的数据格式不正确:', response);
        }

        // 更新localStorage中的习题数据
        courseInfo.step4Data = {
            ...courseInfo.step4Data,
            questions: questions.value,  // 使用更新后的questions
            selectedTypes: selectedTypes.value,
            questionCounts,
            difficulty: difficulty.value,
            selectedQuestions: selectedQuestions.value,
            suggestion: suggestion.value,
            isSettingsCollapsed: isSettingsCollapsed.value
        };
        localStorage.setItem('currentCourseInfo', JSON.stringify(courseInfo));

        window.$showToast('保存成功！', 'success');
    } catch (error: any) {
        console.error('保存习题错误:', error);
        console.error('错误详情:', error.response?.data); // 添加详细错误信息日志
        window.$showToast(`保存习题失败: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
        loadingStore.hideLoading();
    }
};

// 下一步
const nextStep = async () => {
    // 先保存习题
    await saveContent();

    // 获取功能选择
    const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
    const features = courseInfo.features || {};

    try {
        loadingStore.showLoading('正在进入下一步...');
        
        if (features.resourceRecommend) {
            // 如果选择了资源推荐，去 step3
            router.push('/teacher/workbench/step3');
        } else {
            // 如果没选资源推荐，则当前是最后一步
            // 提交最终备课数据
            console.log('课程信息:', courseInfo); // 添加调试日志
            console.log('选中资源:', courseInfo.step3Data?.selectedResources); // 添加资源数据日志
            
            // 确保questions.value有值且每个问题都有id
            if (!questions.value || questions.value.length === 0) {
                window.$showToast('请先生成习题', 'error');
                loadingStore.hideLoading();
                return;
            }
            
            // 检查习题是否都有ID
            const validQuestions = questions.value.filter(q => q.id);
            if (validQuestions.length === 0) {
                window.$showToast('生成的习题未保存，请先点击保存按钮', 'error');
                loadingStore.hideLoading();
                return;
            }
            
            const exerciseIds = validQuestions.map(q => q.id).filter(id => id) as number[];
            console.log('习题ID列表:', exerciseIds); // 添加习题ID日志
            
            const requestData = {
                course_id: courseInfo.id,
                teacher_id: parseInt(localStorage.getItem('userId') || '0'),
                lesson_plan_id: courseInfo.lessonPlanId,
                exercises: {
                    selected_ids: exerciseIds
                },
                selected_resources: courseInfo.step3Data?.selectedResources || {} // 从courseInfo中获取资源数据
            };

            console.log('发送请求数据:', requestData); // 添加请求数据日志

            const response = await apiWithLoading.post(
                'http://localhost:8000/lesson-preparation/complete/',
                requestData,
                '正在完成备课...'
            );

            window.$showToast('备课完成！', 'success');
            
            // 清理localStorage中的课程信息
            localStorage.removeItem('currentCourseInfo');
            
            // 返回工作台
            router.push('/teacher/workbench');
        }
    } catch (error: any) {
        console.error('完成备课错误:', error);
        console.error('错误详情:', error.response?.data); // 添加详细错误信息日志
        window.$showToast(`完成备课失败: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
        loadingStore.hideLoading();
    }
};

// 更新难度文字说明
const updateDifficultyText = () => {
    return difficultyLevels[difficulty.value.toString()];
};

const toggleSettings = () => {
    isSettingsCollapsed.value = !isSettingsCollapsed.value;
    // 确保状态更新后保存到localStorage
    saveToLocalStorage();
};

// 生成题目
const generateQuestions = async () => {
    // 确保selectedTypes是数组
    if (!Array.isArray(selectedTypes.value)) {
        selectedTypes.value = [];
    }
    
    // 验证是否选择了题型并设置了数量
    if (selectedTypes.value.length === 0) {
        window.$showToast('请至少选择一种题型', 'error');
        return;
    }

    const totalCount = Object.values(questionCounts).reduce((sum, count) => sum + (count || 0), 0);
    if (totalCount === 0) {
        window.$showToast('请设置题目数量', 'error');
        return;
    }

    try {
        // 显示加载状态
        loadingStore.showLoading('正在生成习题，请稍候...');

        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            throw new Error('未找到课程信息');
        }

        // 构建types对象，符合后端期望的格式
        const typesObj: Record<string, number> = {};
        selectedTypes.value.forEach(type => {
            typesObj[type] = questionCounts[type as keyof typeof questionCounts] || 0;
        });

        console.log('Sending request with types:', typesObj);
        
        // 使用apiWithLoading替换原来的fetch，修改请求数据结构
        const data = await apiWithLoading.post('/exercises/generate/', {
            course_id: courseInfo.id,
            types: typesObj,  // 改为字典格式 {"choice": 2, "judgment": 3, ...}
            difficulty: difficulty.value,
            suggestions: suggestion.value
        }, ''); // 空消息，因为已经显示了自定义消息

        console.log('Received response:', data);
        
        // 处理响应
        if (data && typeof data === 'object' && 'exercises' in data && Array.isArray(data.exercises)) {
            questions.value = data.exercises;
            window.$showToast('习题生成成功！', 'success');
            
            // 保存数据到localStorage
            saveToLocalStorage();
        } else {
            throw new Error('生成习题失败');
        }
    } catch (error: any) {
        console.error('生成习题错误:', error);
        console.error('错误详情:', error.response?.data); // 添加详细错误信息日志
        window.$showToast(`生成习题失败: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
        // 隐藏加载状态
        loadingStore.hideLoading();
    }
};

// 重新生成题目
const regenerateQuestions = async () => {
    // 确保数组初始化
    if (!Array.isArray(selectedQuestions.value)) {
        selectedQuestions.value = [];
    }
    if (!Array.isArray(selectedTypes.value)) {
        selectedTypes.value = [];
    }
    if (!Array.isArray(questions.value)) {
        questions.value = [];
    }
    
    if (selectedQuestions.value.length === 0) {
        window.$showToast('请先选择需要重新生成的题目', 'error');
        return;
    }
    if (!suggestion.value.trim()) {
        window.$showToast('请输入修改建议', 'error');
        return;
    }
    
    try {
        // 显示加载状态
        loadingStore.showLoading('正在重新生成习题，请稍候...');

        const courseInfo = JSON.parse(localStorage.getItem('currentCourseInfo') || '{}');
        if (!courseInfo.id) {
            throw new Error('未找到课程信息');
        }

        // 获取选中题目的ID列表
        const selectedIds = selectedQuestions.value
            .filter(index => index >= 0 && index < questions.value.length)
            .map(index => questions.value[index].id)
            .filter(id => id !== undefined);

        // 构建types对象，符合后端期望的格式
        const typesObj: Record<string, number> = {};
        selectedTypes.value.forEach(type => {
            typesObj[type] = questionCounts[type as keyof typeof questionCounts] || 0;
        });

        console.log('Regenerating questions with IDs:', selectedIds);

        // 使用apiWithLoading替换原来的fetch
        const data = await apiWithLoading.post('/exercises/generate/', {
            course_id: courseInfo.id,
            types: typesObj,
            difficulty: difficulty.value,
            suggestions: suggestion.value,
            selected_ids: selectedIds
        }, ''); // 空消息，因为已经显示了自定义消息

        console.log('Received regenerated questions:', data);

        // 处理响应
        if (data && typeof data === 'object' && 'exercises' in data && Array.isArray(data.exercises)) {
            // 更新选中的题目
            data.exercises.forEach((newQuestion, i) => {
                if (i < selectedQuestions.value.length) {
                    const index = selectedQuestions.value[i];
                    if (index >= 0 && index < questions.value.length) {
                        questions.value[index] = newQuestion;
                    }
                }
            });
            
            window.$showToast('习题重新生成成功！', 'success');
            // 清空选中状态
            selectedQuestions.value = [];
            
            // 保存到localStorage
            saveToLocalStorage();
        } else {
            throw new Error('重新生成习题失败');
        }
    } catch (error: any) {
        console.error('重新生成习题错误:', error);
        console.error('错误详情:', error.response?.data); // 添加详细错误信息日志
        window.$showToast(`重新生成习题失败: ${error.response?.data?.detail || error.message}`, 'error');
    } finally {
        // 隐藏加载状态
        loadingStore.hideLoading();
    }
};
</script>

<style scoped>
.step4-view {
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
    height: 100%;
    position: relative;
    padding-bottom: 64px;
    /* 为底部按钮预留空间 */
}

.side-panel {
    width: 300px;
    height: 100%;
}

.question-settings {
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    margin-bottom: 16px;
}

.question-settings.collapsed {
    padding: 12px 16px;
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
    border: 1px solid #ddd;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s;
}

.collapse-btn:hover {
    background: #e6e8eb;
}

.settings-content {
    transition: all 0.3s ease;
}

h3 {
    margin: 0 0 12px 0;
    font-size: 16px;
    color: #333;
}

.type-buttons,
.difficulty-buttons {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.type-button,
.difficulty-button {
    padding: 8px 16px;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
    background: white;
    color: #666;
}

.type-button .count {
    color: #999;
    font-size: 14px;
}

.type-button.active,
.difficulty-button.active {
    background: #4c84ff;
    color: white;
    border-color: #4c84ff;
}

.type-button.active .count {
    color: rgba(255, 255, 255, 0.8);
}

.difficulty-setting {
    margin-top: 16px;
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

.questions-container {
    flex: 1;
    overflow-y: auto;
    margin-bottom: 16px;
}

.question-item {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.3s;
}

.question-item.selected {
    border-color: #4c84ff;
    background: rgba(76, 132, 255, 0.05);
}

.question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
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

.question-type {
    font-size: 12px;
    color: #666;
    margin-top: 8px;
}

.add-question-btn {
    width: 100%;
    padding: 12px;
    background: #f5f7fa;
    border: 1px dashed #ddd;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
    transition: all 0.3s;
}

.add-question-btn:hover {
    background: #e6e8eb;
}

.actions {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    gap: 16px;
    height: 48px;
    background: transparent;
}

.action-btn {
    flex: 1;
    height: 100%;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
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

.type-button {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
    background: white;
    color: #666;
    min-width: 160px;
}

.count-input {
    display: flex;
    align-items: center;
    margin-left: 8px;
    background: rgba(0, 0, 0, 0.05);
    padding: 2px 4px;
    border-radius: 4px;
}

.count-input input {
    width: 40px;
    padding: 2px 4px;
    border: 1px solid #ddd;
    border-radius: 2px;
    text-align: center;
    font-size: 14px;
}

.count-input .unit {
    margin-left: 2px;
    font-size: 12px;
    color: inherit;
}

.type-button.active .count-input {
    background: rgba(255, 255, 255, 0.2);
}

.type-button.active .count-input input {
    border-color: rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

.difficulty-slider-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 0 16px;
}

.difficulty-labels {
    display: flex;
    justify-content: space-between;
    padding: 0 8px;
    color: #666;
    font-size: 14px;
}

.slider-wrapper {
    position: relative;
    padding: 10px 0;
}

.difficulty-slider {
    width: 100%;
    height: 4px;
    background: #e6e8eb;
    border-radius: 2px;
    outline: none;
    -webkit-appearance: none;
    margin: 0;
    cursor: pointer;
}

.difficulty-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    background: #4c84ff;
    border: 2px solid #fff;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    position: relative;
    z-index: 2;
}

.difficulty-slider::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 2px 6px rgba(76, 132, 255, 0.4);
}

.suggestion-input {
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    height: 100%;
    display: flex;
    flex-direction: column;
}

.suggestion-input textarea {
    flex: 1;
    min-height: 200px;
    margin-bottom: 12px;
}

.word-count {
    text-align: right;
    color: #666;
    font-size: 12px;
    margin-bottom: 12px;
}

.regenerate-btn {
    width: 100%;
    padding: 12px;
    background: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.regenerate-btn:hover {
    background: #3a70e3;
}

.generate-btn {
    width: 100%;
    padding: 12px;
    margin-top: 16px;
    background: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
}

.generate-btn:hover {
    background: #3a70e3;
}
/* 对话框样式 */
.dialog-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.dialog-content {
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
}

.dialog-header {
    padding: 16px;
    border-bottom: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dialog-body {
    padding: 16px;
    overflow-y: auto;
}

.dialog-footer {
    padding: 16px;
    border-top: 1px solid #ddd;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
}

.form-group {
    margin-bottom: 16px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #333;
}

.form-group input[type="text"],
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.form-group textarea {
    min-height: 100px;
    resize: vertical;
}

.options-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.option-item {
    display: flex;
    align-items: center;
    gap: 8px;
}

.option-item input {
    flex: 1;
}

.remove-option-btn {
    padding: 4px 8px;
    background: #f5f7fa;
    border: none;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
}

.add-option-btn {
    padding: 8px;
    background: #f5f7fa;
    border: 1px dashed #ddd;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
    width: 100%;
    margin-top: 8px;
}

.answer-options {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

.answer-options label {
    display: flex;
    align-items: center;
    gap: 4px;
}

.question-content {
    margin: 8px 0;
}

.question-title {
    font-weight: bold;
    margin-bottom: 8px;
}

.question-text {
    margin-bottom: 8px;
}

.question-options {
    margin-left: 16px;
    margin-bottom: 8px;
}

.question-answer {
    color: #666;
    font-size: 14px;
}

.question-actions {
    display: flex;
    gap: 8px;
}

.edit-btn {
    padding: 4px 8px;
    background: #f5f7fa;
    border: none;
    border-radius: 4px;
    color: #666;
    cursor: pointer;
}

.edit-btn:hover {
    background: #e6e8eb;
}
</style>