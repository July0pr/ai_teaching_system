<template>
    <div class="assignment-detail">
        <!-- 作业信息头部 -->
        <div class="assignment-header">
            <div class="assignment-info">
                <h2>{{ assignment.title }}</h2>
                <div class="info-row">
                    <span class="label">截止时间：</span>
                    <span class="value">{{ formatDate(assignment.due_date) }}</span>
                    <span class="status" :class="assignment.status">{{ assignment.status }}</span>
                </div>
                <div class="info-row">
                    <span class="label">完成情况：</span>
                    <span class="value">{{ assignment.completion_count }}/{{ assignment.total_students }}</span>
                </div>
                <div class="description">
                    {{ assignment.description }}
                </div>
            </div>
        </div>

        <!-- 作业内容区域 -->
        <div class="assignment-content">
            <div class="exercises-list">
                <div v-for="(exercise, index) in exercises" :key="exercise.id" class="exercise-item">
                    <div class="exercise-header">
                        <h3>第{{ index + 1 }}题</h3>
                        <span class="exercise-type">{{ exercise.type }}</span>
                    </div>
                    <div class="exercise-content">
                        <div class="question">{{ exercise.content }}</div>

                        <!-- 选择题选项 -->
                        <div v-if="exercise.type === '单选' || exercise.type === '多选'" class="options">
                            <label v-for="option in parseOptions(exercise.options)" :key="option.value" class="option"
                                :class="{ selected: isOptionSelected(exercise.id, option.value) }">
                                <input :type="exercise.type === '单选' ? 'radio' : 'checkbox'"
                                    :name="'exercise-' + exercise.id" :value="option.value"
                                    v-model="answers[exercise.id]" :disabled="isSubmitted || isExpired">
                                <span class="option-text">{{ option.label }}</span>
                            </label>
                        </div>

                        <!-- 判断题选项 -->
                        <div v-else-if="exercise.type === '判断'" class="options">
                            <label class="option">
                                <input type="radio" :name="'exercise-' + exercise.id" value="true"
                                    v-model="answers[exercise.id]" :disabled="isSubmitted || isExpired">
                                正确
                            </label>
                            <label class="option">
                                <input type="radio" :name="'exercise-' + exercise.id" value="false"
                                    v-model="answers[exercise.id]" :disabled="isSubmitted || isExpired">
                                错误
                            </label>
                        </div>

                        <!-- 填空题输入框 -->
                        <div v-else-if="exercise.type === '填空'" class="fill-blank">
                            <input type="text" v-model="answers[exercise.id]" placeholder="请输入答案"
                                :disabled="isSubmitted || isExpired">
                        </div>

                        <!-- 简答题文本框 -->
                        <div v-else-if="exercise.type === '简答'" class="short-answer">
                            <textarea v-model="answers[exercise.id]" placeholder="请输入答案"
                                :disabled="isSubmitted || isExpired"></textarea>
                        </div>

                        <!-- 已提交时显示正确答案和解析 -->
                        <div v-if="isSubmitted" class="answer-analysis">
                            <div class="correct-answer">
                                <span class="label">正确答案：</span>
                                <span class="value">{{ exercise.answers }}</span>
                            </div>
                            <div v-if="exercise.explanation" class="explanation">
                                <span class="label">解析：</span>
                                <span class="value">{{ exercise.explanation }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 底部操作栏 -->
        <div class="assignment-footer">
            <div class="buttons">
                <button class="submit-btn" @click="submitAssignment"
                    :disabled="isSubmitted || isExpired || !hasAnswered">
                    {{ isSubmitted ? '已提交' : '提交作业' }}
                </button>
                <button class="cancel-btn" @click="goBack">返回</button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

interface Exercise {
    id: number;
    type: string;
    content: string;
    options?: string;
    answers: string;
    explanation?: string;
}

interface Assignment {
    id: number;
    title: string;
    description: string;
    due_date: string;
    status: string;
    completion_count: number;
    total_students: number;
}

const route = useRoute();
const router = useRouter();
const assignmentId = computed(() => Number(route.params.id));

const assignment = ref<Assignment>({
    id: 0,
    title: '',
    description: '',
    due_date: '',
    status: '',
    completion_count: 0,
    total_students: 0
});

const exercises = ref<Exercise[]>([]);
const answers = ref<Record<number, any>>({});
const isSubmitted = ref(false);

// 计算属性：是否已过期
const isExpired = computed(() => {
    return new Date(assignment.value.due_date) < new Date();
});

// 计算属性：是否已答题
const hasAnswered = computed(() => {
    return Object.keys(answers.value).length > 0;
});

// 格式化日期
const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 解析选项
const parseOptions = (optionsString?: string) => {
    if (!optionsString) return [];

    try {
        let options = JSON.parse(optionsString);

        // 如果是字符串数组，转换为对象数组
        if (Array.isArray(options) && typeof options[0] === 'string') {
            return options.map((text, index) => ({
                value: String.fromCharCode(65 + index), // A, B, C, D...
                label: `${String.fromCharCode(65 + index)}. ${text}` // A. 选项1, B. 选项2...
            }));
        }

        return options;
    } catch (error) {
        return [];
    }
};

// 检查选项是否被选中
const isOptionSelected = (exerciseId: number, optionValue: string) => {
    const answer = answers.value[exerciseId];
    if (!answer) return false;

    if (Array.isArray(answer)) {
        return answer.includes(optionValue);
    }
    return answer === optionValue;
};

// 初始化答案
const initAnswers = () => {
    exercises.value.forEach(exercise => {
        if (exercise.type === '多选') {
            answers.value[exercise.id] = [];
        } else {
            answers.value[exercise.id] = '';
        }
    });
};

// 获取作业信息
const fetchAssignment = async () => {
    try {
        const response = await fetch(`http://localhost:8000/assignments/${assignmentId.value}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取作业信息失败');
        }

        const data = await response.json();
        assignment.value = {
            ...data,
            status: new Date(data.due_date) < new Date() ? '已结束' : '进行中'
        };

        // 获取作业完成情况
        const submissionsResponse = await fetch(`http://localhost:8000/assignments/${assignmentId.value}/submissions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (submissionsResponse.ok) {
            const submissionsData = await submissionsResponse.json();
            assignment.value.completion_count = submissionsData.length;
        }
    } catch (error) {
        console.error('获取作业信息错误:', error);
        // 使用默认数据
        assignment.value = {
            id: assignmentId.value,
            title: '第一学期第五次测试',
            description: '覆盖第五章内容',
            due_date: new Date(Date.now() + 86400000 * 5).toISOString(),
            status: '进行中',
            completion_count: 30,
            total_students: 45
        };
    }
};

// 获取作业题目
const fetchExercises = async () => {
    try {
        const response = await fetch(`http://localhost:8000/assignments/${assignmentId.value}/exercises`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取作业题目失败');
        }

        const data = await response.json();
        console.log('获取到的题目:', data);
        exercises.value = data;
        initAnswers();
    } catch (error) {
        console.error('获取作业题目错误:', error);
        exercises.value = [
            {
                id: 1,
                type: '单选',
                content: '下列关于数据结构的说法，正确的是：',
                options: JSON.stringify([
                    { value: 'A', label: 'A. 栈是一种先进先出的数据结构' },
                    { value: 'B', label: 'B. 队列是一种后进先出的数据结构' },
                    { value: 'C', label: 'C. 链表必须是连续存储的' },
                    { value: 'D', label: 'D. 二叉树的每个节点最多有两个子节点' }
                ]),
                answers: 'D',
                explanation: '二叉树的定义就是每个节点最多有两个子节点的树形结构。'
            }
        ];
        initAnswers();
    }
};

// 检查是否已提交
const checkSubmissionStatus = async () => {
    try {
        const userId = localStorage.getItem('userId');
        const response = await fetch(`http://localhost:8000/students/${userId}/assignments/${assignmentId.value}/status`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取提交状态失败');
        }

        const data = await response.json();
        isSubmitted.value = data.submitted;

        // 如果已提交，获取之前的答案
        if (isSubmitted.value) {
            const submissionResponse = await fetch(`http://localhost:8000/assignments/submissions/${data.submission_id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (submissionResponse.ok) {
                const submissionData = await submissionResponse.json();
                answers.value = JSON.parse(submissionData.answers);
            }
        }
    } catch (error) {
        console.error('检查提交状态错误:', error);
        isSubmitted.value = false;
    }
};

// 提交作业
const submitAssignment = async () => {
    if (!confirm('确定要提交作业吗？提交后将无法修改。')) {
        return;
    }

    try {
        const userId = localStorage.getItem('userId');
        const response = await fetch('http://localhost:8000/assignments/submissions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                assignment_id: assignmentId.value,
                student_id: userId,
                answers: JSON.stringify(answers.value)
            })
        });

        if (!response.ok) {
            throw new Error('提交作业失败');
        }

        isSubmitted.value = true;
        alert('作业提交成功！');
    } catch (error) {
        console.error('提交作业错误:', error);
        alert('提交作业失败，请稍后重试');
    }
};

// 返回上一页
const goBack = () => {
    router.back();
};

// 页面加载时初始化数据
onMounted(async () => {
    await Promise.all([
        fetchAssignment(),
        fetchExercises(),
        checkSubmissionStatus()
    ]);
});
</script>

<style scoped>
.assignment-detail {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.assignment-header {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.info-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 8px;
}

.label {
    color: #666;
    font-weight: bold;
}

.status {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.status.进行中 {
    background-color: #3498db;
    color: white;
}

.status.已结束 {
    background-color: #999;
    color: white;
}

.description {
    margin-top: 16px;
    color: #666;
    line-height: 1.5;
}

.assignment-content {
    flex: 1;
    overflow-y: auto;
}

.exercises-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.exercise-item {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.exercise-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.exercise-type {
    padding: 4px 8px;
    background: #f0f2f5;
    border-radius: 4px;
    font-size: 14px;
    color: #666;
}

.question {
    margin-bottom: 16px;
    line-height: 1.5;
}

.options {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.option {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.option:hover {
    background: #e6f7ff;
}

.option.selected {
    background: #e6f7ff;
    border: 1px solid #3498db;
}

.option input[type="radio"],
.option input[type="checkbox"] {
    width: 16px;
    height: 16px;
    margin: 0;
}

.option-text {
    font-size: 14px;
    color: #333;
    flex: 1;
}

.option:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.fill-blank input,
.short-answer textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-top: 8px;
}

.short-answer textarea {
    height: 120px;
    resize: vertical;
}

.answer-analysis {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #eee;
}

.correct-answer,
.explanation {
    margin-top: 8px;
    color: #666;
}

.assignment-footer {
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

.submit-btn,
.cancel-btn {
    padding: 8px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.submit-btn {
    background: #3498db;
    color: white;
}

.submit-btn:disabled {
    background: #999;
    cursor: not-allowed;
}

.cancel-btn {
    background: #f5f7fa;
    color: #666;
}

.cancel-btn:hover {
    background: #e6e8ea;
}
</style>