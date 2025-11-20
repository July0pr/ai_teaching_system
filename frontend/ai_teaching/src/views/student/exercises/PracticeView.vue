<template>
    <div class="practice-view">
        <div class="header">
            <h2>习题自主作答</h2>
            <div class="exercise-info" v-if="exerciseData">
                <span class="title">{{ exerciseData.assignment_name }}</span>
                <span class="sequence">#{{ exerciseData.sequence_number }}</span>
            </div>
            <button class="back-btn" @click="goBack">返回</button>
        </div>

        <div v-if="loading" class="loading">
            正在加载习题...
        </div>

        <div v-else-if="error" class="error">
            {{ error }}
        </div>

        <div v-else-if="!exerciseData" class="error">
            未找到习题数据
        </div>

        <div v-else class="content">
            <!-- 未提交状态 -->
            <div v-if="!submitted" class="questions-container">
                <div v-for="(question, index) in exerciseData.exercises" :key="index" class="question-card">
                    <div class="question-header">
                        <span class="question-number">题目 {{ index + 1 }}</span>
                        <span class="question-type">{{ question.type }}</span>
                    </div>
                    <div class="question-content">{{ question.content }}</div>

                    <!-- 选择题 -->
                    <div v-if="question.type === '单选'" class="options">
                        <label v-for="(option, optIndex) in parseOptions(question.options)" :key="optIndex"
                            class="option">
                            <input type="radio" :name="'question-' + index" :value="option.value"
                                v-model="userAnswers[index]">
                            <span>{{ option.label }}</span>
                        </label>
                    </div>

                    <!-- 多选题 -->
                    <div v-else-if="question.type === '多选'" class="options">
                        <label v-for="(option, optIndex) in parseOptions(question.options)" :key="optIndex"
                            class="option">
                            <input type="checkbox" :value="option.value" v-model="userAnswers[index]">
                            <span>{{ option.label }}</span>
                        </label>
                    </div>

                    <!-- 判断题 -->
                    <div v-else-if="question.type === '判断'" class="options">
                        <label class="option">
                            <input type="radio" :name="'question-' + index" value="true" v-model="userAnswers[index]">
                            <span>正确</span>
                        </label>
                        <label class="option">
                            <input type="radio" :name="'question-' + index" value="false" v-model="userAnswers[index]">
                            <span>错误</span>
                        </label>
                    </div>

                    <!-- 填空题 -->
                    <div v-else-if="question.type === '填空'" class="fill-blank">
                        <input type="text" v-model="userAnswers[index]" placeholder="请输入答案" class="text-input">
                    </div>

                    <!-- 简答题 -->
                    <div v-else-if="question.type === '简答'" class="short-answer">
                        <textarea v-model="userAnswers[index]" placeholder="请输入答案" class="text-area"
                            rows="4"></textarea>
                    </div>
                </div>

                <div class="actions">
                    <button class="submit-btn" @click="submitAnswers">提交答案</button>
                </div>
            </div>

            <!-- 已提交状态，显示结果 -->
            <div v-else class="results-container">
                <div class="summary">
                    <h3>答题结果</h3>
                    <div class="score">得分: {{ score }}/{{ exerciseData.exercises.length * 10 }}</div>
                </div>

                <div v-for="(question, index) in exerciseData.exercises" :key="index" class="result-card">
                    <div class="question-header">
                        <span class="question-number">题目 {{ index + 1 }}</span>
                        <span class="question-type">{{ question.type }}</span>
                        <span class="result-badge" :class="correctness[index] ? 'correct' : 'wrong'">
                            {{ correctness[index] ? '正确' : '错误' }}
                        </span>
                    </div>
                    <div class="question-content">{{ question.content }}</div>

                    <!-- 答案部分 -->
                    <div class="answer-section">
                        <div class="user-answer">
                            <strong>你的答案:</strong>
                            <span v-if="Array.isArray(userAnswers[index])">{{ userAnswers[index].join(', ') }}</span>
                            <span v-else>{{ userAnswers[index] }}</span>
                        </div>
                        <div class="correct-answer">
                            <strong>正确答案:</strong>
                            <span>{{ question.answers }}</span>
                        </div>
                    </div>
                </div>

                <div class="actions">
                    <button class="retry-btn" @click="resetAnswers">重新作答</button>
                    <button class="back-btn" @click="goBack">返回列表</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

interface ExerciseQuestion {
    type: string;
    title: string;
    content: string;
    options?: string;
    answers: string;
    difficulty: number;
}

interface ExerciseData {
    id: number;
    assignment_id: number;
    assignment_name: string;
    student_id: number;
    sequence_number: number;
    exercises: ExerciseQuestion[];
    created_at: string;
    updated_at: string;
}

const route = useRoute();
const router = useRouter();
const exerciseId = route.params.id;
const loading = ref(true);
const error = ref<string | null>(null);
const exerciseData = ref<ExerciseData | null>(null);
const userAnswers = reactive<(string | string[])[]>([]);
const submitted = ref(false);
const correctness = ref<boolean[]>([]);
const score = ref(0);

// 获取习题数据
const fetchExerciseData = async () => {
    try {
        loading.value = true;
        error.value = null;

        const response = await axios.get(`http://localhost:8000/student/exercises/${exerciseId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        exerciseData.value = response.data;

        // 初始化用户答案数组
        if (exerciseData.value && exerciseData.value.exercises) {
            exerciseData.value.exercises.forEach((question) => {
                if (question.type === '多选') {
                    userAnswers.push([]);
                } else {
                    userAnswers.push('');
                }
            });
        }
    } catch (error: any) {
        console.error('获取习题数据失败:', error);
        error.value = `获取习题数据失败: ${error.message || '未知错误'}`;
    } finally {
        loading.value = false;
    }
};

// 解析选项
const parseOptions = (optionsString?: string) => {
    if (!optionsString) return [];
    try {
        let options = JSON.parse(optionsString);
        if (Array.isArray(options) && typeof options[0] === 'string') {
            return options.map((text, index) => ({
                value: String.fromCharCode(65 + index),
                label: `${String.fromCharCode(65 + index)}. ${text}`
            }));
        }
        return options;
    } catch (error) {
        return [];
    }
};

// 提交答案
const submitAnswers = () => {
    if (!exerciseData.value) return;

    correctness.value = [];
    let totalScore = 0;

    // 检查每个答案是否正确
    exerciseData.value.exercises.forEach((question, index) => {
        let isCorrect = false;

        if (question.type === '多选') {
            // 多选题比较数组
            const userAnsArray = userAnswers[index] as string[];
            const correctAnsArray = question.answers.split(',').map(a => a.trim());
            isCorrect = userAnsArray.length === correctAnsArray.length &&
                userAnsArray.every(ans => correctAnsArray.includes(ans));
        } else {
            // 其他题型直接比较字符串
            const userAns = userAnswers[index] as string;
            const correctAns = question.answers;
            isCorrect = userAns === correctAns;
        }

        correctness.value.push(isCorrect);
        if (isCorrect) totalScore += 10;
    });

    score.value = totalScore;
    submitted.value = true;
};

// 重置答案，重新作答
const resetAnswers = () => {
    userAnswers.length = 0;
    if (exerciseData.value) {
        exerciseData.value.exercises.forEach((question) => {
            if (question.type === '多选') {
                userAnswers.push([]);
            } else {
                userAnswers.push('');
            }
        });
    }
    submitted.value = false;
    correctness.value = [];
    score.value = 0;
};

// 返回上一页
const goBack = () => {
    router.push('/student/resources/history');
};

// 在组件挂载时获取习题数据
onMounted(() => {
    fetchExerciseData();
});
</script>

<style scoped>
.practice-view {
    height: 100%;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: white;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header h2 {
    margin: 0;
    color: #333;
}

.exercise-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.exercise-info .title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
}

.exercise-info .sequence {
    font-weight: bold;
    color: #3498db;
}

.back-btn {
    padding: 8px 16px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.back-btn:hover {
    background-color: #2980b9;
}

.loading,
.error {
    text-align: center;
    padding: 40px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error {
    color: #e74c3c;
}

.content {
    flex: 1;
    overflow-y: auto;
}

.questions-container,
.results-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.question-card,
.result-card {
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.question-header {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
}

.question-number {
    font-weight: bold;
    margin-right: 12px;
}

.question-type {
    padding: 4px 8px;
    background: #3498db;
    color: white;
    border-radius: 4px;
    font-size: 12px;
}

.result-badge {
    margin-left: auto;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: white;
}

.result-badge.correct {
    background: #27ae60;
}

.result-badge.wrong {
    background: #e74c3c;
}

.question-content {
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
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.option:hover {
    background: #edf1f7;
}

.fill-blank .text-input,
.short-answer .text-area {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    resize: vertical;
}

.actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 20px;
}

.submit-btn,
.retry-btn {
    padding: 10px 24px;
    border: none;
    border-radius: 4px;
    color: white;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
}

.submit-btn {
    background-color: #27ae60;
}

.submit-btn:hover {
    background-color: #219653;
}

.retry-btn {
    background-color: #e67e22;
}

.retry-btn:hover {
    background-color: #d35400;
}

.summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary h3 {
    margin: 0;
}

.score {
    font-size: 18px;
    font-weight: bold;
    color: #27ae60;
}

.answer-section {
    margin-top: 16px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.user-answer,
.correct-answer {
    display: flex;
    gap: 8px;
}

.user-answer strong,
.correct-answer strong {
    min-width: 100px;
}
</style>