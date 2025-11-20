<template>
    <div class="assignment-submissions">
        <div class="header">
            <div class="header-top">
                <button class="back-btn" @click="goBack">返回</button>
                <h2>{{ assignment.title }}</h2>
            </div>
            <div class="assignment-info">
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

        <div class="submissions-container">
            <!-- 已提交学生列表 -->
            <div class="section">
                <h3>已提交学生</h3>
                <div class="students-list">
                    <div v-for="submission in submittedStudents" :key="submission.student_id" class="student-item">
                        <span class="student-name">{{ submission.student_name }}</span>
                        <span class="submission-time">{{ formatDate(submission.submission_date) }}</span>
                        <div class="actions">
                            <button class="review-btn" @click="reviewSubmission(submission)">批阅</button>
                        </div>
                    </div>
                    <div v-if="submittedStudents.length === 0" class="empty-message">
                        暂无学生提交作业
                    </div>
                </div>
            </div>

            <!-- 未提交学生列表 -->
            <div class="section">
                <h3>未提交学生</h3>
                <div class="students-list">
                    <div v-for="student in unsubmittedStudents" :key="student.id" class="student-item">
                        <span class="student-name">{{ student.name }}</span>
                    </div>
                    <div v-if="unsubmittedStudents.length === 0" class="empty-message">
                        所有学生都已提交作业
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

interface Assignment {
    id: number;
    title: string;
    description: string;
    due_date: string;
    status: string;
    completion_count: number;
    total_students: number;
}

interface Submission {
    id: number;
    student_id: number;
    student_name: string;
    submission_date: string;
    grade: number | null;
}

interface Student {
    id: number;
    name: string;
}

const assignment = ref<Assignment>({
    id: 0,
    title: '',
    description: '',
    due_date: '',
    status: '',
    completion_count: 0,
    total_students: 0
});

const submittedStudents = ref<Submission[]>([]);
const unsubmittedStudents = ref<Student[]>([]);

// 获取作业信息
const fetchAssignment = async () => {
    try {
        const response = await fetch(`http://localhost:8000/assignments/${route.params.id}`, {
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
    } catch (error) {
        console.error('获取作业信息错误:', error);
    }
};

// 获取提交情况
const fetchSubmissions = async () => {
    try {
        const response = await fetch(`http://localhost:8000/assignments/${route.params.id}/submissions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取提交情况失败');
        }

        const data = await response.json();
        submittedStudents.value = data;
    } catch (error) {
        console.error('获取提交情况错误:', error);
    }
};

// 获取未提交学生列表
const fetchUnsubmittedStudents = async () => {
    try {
        const response = await fetch(`http://localhost:8000/assignments/${route.params.id}/unsubmitted`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取未提交学生列表失败');
        }

        const data = await response.json();
        unsubmittedStudents.value = data;
    } catch (error) {
        console.error('获取未提交学生列表错误:', error);
    }
};

// 格式化日期
const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 批阅作业
const reviewSubmission = (submission: Submission) => {
    router.push(`/teacher/assignments/${route.params.id}/submissions/${submission.id}/review`);
};

const goBack = () => {
    router.back();
};

onMounted(() => {
    fetchAssignment();
    fetchSubmissions();
    fetchUnsubmittedStudents();
});
</script>

<style scoped>
.assignment-submissions {
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

.header-top {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;
}

.header-top h2 {
    margin: 0;
    font-size: 22px;
    color: #333;
}

.back-btn {
    padding: 8px 24px;
    background: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s;
}

.back-btn:hover {
    background: #3a70e3;
}

.assignment-info h2 {
    margin: 0 0 16px 0;
    font-size: 22px;
    color: #333;
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
    background-color: #4c84ff;
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

.submissions-container {
    display: flex;
    gap: 20px;
    flex: 1;
}

.section {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    flex: 1;
}

.section h3 {
    margin: 0 0 16px 0;
    font-size: 18px;
    color: #333;
}

.students-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.student-item {
    display: flex;
    align-items: center;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 4px;
    gap: 16px;
}

.student-name {
    flex: 1;
    font-size: 14px;
    color: #333;
}

.submission-time {
    color: #666;
    font-size: 14px;
}

.actions {
    display: flex;
    gap: 8px;
}

.review-btn {
    padding: 4px 12px;
    background: #4c84ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.empty-message {
    text-align: center;
    color: #999;
    padding: 20px;
}
</style>