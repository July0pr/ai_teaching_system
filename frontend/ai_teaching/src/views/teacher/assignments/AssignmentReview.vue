<template>
    <div class="assignment-review">
        <!-- 作业信息头部 -->
        <div class="header">
            <div class="assignment-info">
                <h2>{{ assignment.title }}</h2>
                <div class="info-row">
                    <span class="label">学生姓名：</span>
                    <span class="value">{{ submission.student_name }}</span>
                </div>
                <div class="info-row">
                    <span class="label">提交时间：</span>
                    <span class="value">{{ formatDate(submission.submission_date) }}</span>
                </div>
            </div>
        </div>

        <!-- 作业内容区域 -->
        <div class="content">
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
                                    v-model="studentAnswers[exercise.id]" disabled>
                                <span class="option-text">{{ option.label }}</span>
                            </label>
                        </div>

                        <!-- 判断题选项 -->
                        <div v-else-if="exercise.type === '判断'" class="options">
                            <label class="option">
                                <input type="radio" :name="'exercise-' + exercise.id" value="true"
                                    v-model="studentAnswers[exercise.id]" disabled>
                                正确
                            </label>
                            <label class="option">
                                <input type="radio" :name="'exercise-' + exercise.id" value="false"
                                    v-model="studentAnswers[exercise.id]" disabled>
                                错误
                            </label>
                        </div>

                        <!-- 填空题答案 -->
                        <div v-else-if="exercise.type === '填空'" class="fill-blank">
                            <div class="student-answer">{{ studentAnswers[exercise.id] }}</div>
                        </div>

                        <!-- 简答题答案 -->
                        <div v-else-if="exercise.type === '简答'" class="short-answer">
                            <div class="student-answer">{{ studentAnswers[exercise.id] }}</div>
                        </div>

                        <!-- 批改区域 -->
                        <div class="review-area">
                            <div class="correct-answer">
                                <span class="label">正确答案：</span>
                                <span class="value">{{ exercise.answers }}</span>
                            </div>
                            <div class="grading">
                                <span class="label">得分：</span>
                                <input type="number" v-model="grades[exercise.id]" min="0" max="100" step="1">
                            </div>
                            <div class="feedback">
                                <span class="label">评语：</span>
                                <textarea v-model="feedbacks[exercise.id]" placeholder="请输入评语"></textarea>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 底部操作栏 -->
        <div class="footer">
            <div class="total-score">
                总分：{{ calculateTotalScore() }}
            </div>
            <div class="buttons">
                <button class="submit-btn" @click="submitReview">提交评分</button>
                <button class="back-btn" @click="goBack">返回</button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

interface Assignment {
    id: number;
    title: string;
    description: string;
    due_date: string;
}

interface Exercise {
    id: number;
    type: string;
    content: string;
    options?: string;
    answers: string;
}

interface Submission {
    id: number;
    student_id: number;
    student_name: string;
    submission_date: string;
    answers: string;
    grade: number | null;
    feedback: string | null;
}

const assignment = ref<Assignment>({
    id: 0,
    title: '',
    description: '',
    due_date: ''
});

const submission = ref<Submission>({
    id: 0,
    student_id: 0,
    student_name: '',
    submission_date: '',
    answers: '{}',
    grade: null,
    feedback: null
});

const exercises = ref<Exercise[]>([]);
const studentAnswers = ref<Record<number, any>>({});
const grades = ref<Record<number, number>>({});
const feedbacks = ref<Record<number, string>>({});

// 获取作业信息
const fetchAssignment = async () => {
    try {
        const response = await fetch(`http://localhost:8000/assignments/${route.params.assignmentId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取作业信息失败');
        }

        assignment.value = await response.json();
    } catch (error) {
        console.error('获取作业信息错误:', error);
    }
};

// 获取提交信息
const fetchSubmission = async () => {
    try {
        const response = await fetch(`http://localhost:8000/assignments/submissions/${route.params.submissionId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取提交信息失败');
        }

        const data = await response.json();
        submission.value = data;
        studentAnswers.value = JSON.parse(data.answers);
    } catch (error) {
        console.error('获取提交信息错误:', error);
    }
};

// 获取作业题目
const fetchExercises = async () => {
    try {
        const response = await fetch(`http://localhost:8000/assignments/${route.params.assignmentId}/exercises`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取作业题目失败');
        }

        exercises.value = await response.json();

        // 初始化每道题的分数和评语
        exercises.value.forEach(exercise => {
            grades.value[exercise.id] = 0;
            feedbacks.value[exercise.id] = '';
        });
    } catch (error) {
        console.error('获取作业题目错误:', error);
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

// 检查选项是否被选中
const isOptionSelected = (exerciseId: number, optionValue: string) => {
    const answer = studentAnswers.value[exerciseId];
    if (!answer) return false;
    if (Array.isArray(answer)) {
        return answer.includes(optionValue);
    }
    return answer === optionValue;
};

// 计算总分
const calculateTotalScore = () => {
    return Object.values(grades.value).reduce((sum, score) => sum + score, 0);
};

// 提交评分
const submitReview = async () => {
    try {
        const response = await fetch(`http://localhost:8000/assignments/submissions/${route.params.submissionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                grade: calculateTotalScore(),
                feedback: JSON.stringify(feedbacks.value)
            })
        });

        if (!response.ok) {
            throw new Error('提交评分失败');
        }

        alert('评分提交成功！');
        router.push(`/teacher/assignments/${route.params.assignmentId}/submissions`);
    } catch (error) {
        console.error('提交评分错误:', error);
        alert('提交评分失败，请稍后重试');
    }
};

// 格式化日期
const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 返回上一页
const goBack = () => {
    router.back();
};

onMounted(() => {
    fetchAssignment();
    fetchSubmission();
    fetchExercises();
});
</script>

<style scoped>
.assignment-review {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.header {
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

.content {
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
}

.option.selected {
    background: #e6f7ff;
    border: 1px solid #4c84ff;
}

.student-answer {
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 4px;
    margin-top: 8px;
    white-space: pre-wrap;
}

.review-area {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.correct-answer {
    margin-bottom: 16px;
}

.grading {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}

.grading input {
    width: 80px;
    padding: 4px 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.feedback {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.feedback textarea {
    width: 100%;
    height: 80px;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
}

.footer {
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.total-score {
    font-size: 18px;
    font-weight: bold;
    color: #333;
}

.buttons {
    display: flex;
    gap: 12px;
}

.submit-btn,
.back-btn {
    padding: 8px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s;
}

.submit-btn {
    background: #4c84ff;
    color: white;
}

.submit-btn:hover {
    background: #3a70e3;
}

.back-btn {
    background: #4c84ff;
    color: white;
}

.back-btn:hover {
    background: #3a70e3;
}
</style>