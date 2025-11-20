<template>
    <div class="class-detail">
        <!-- 顶部班级信息 - 固定位置 -->
        <div class="class-header">
            <div class="class-info">
                <h2>{{ classInfo.name }}</h2>
                <span class="info-item">学生人数：{{ classInfo.studentCount }}</span>
                <span class="info-item">教授科目：{{ classInfo.subjects }}</span>
            </div>
            <button class="end-class-btn" @click="endClass" v-if="!classInfo.isEnded">结束授课</button>
        </div>

        <!-- 主要内容区域 -->
        <div class="main-content">
            <div class="left-content">
                <!-- 课程资源 -->
                <div class="section resource-section">
                    <h3>课程资源</h3>
                    <div class="resource-tabs">
                        <button class="tab-btn" :class="{ active: activeResourceType === 'all' }"
                            @click="filterResourcesByType('all')">全部</button>
                        <button class="tab-btn" :class="{ active: activeResourceType === '图片' }"
                            @click="filterResourcesByType('图片')">图片</button>
                        <button class="tab-btn" :class="{ active: activeResourceType === '视频' }"
                            @click="filterResourcesByType('视频')">视频</button>
                        <button class="tab-btn" :class="{ active: activeResourceType === '课件' }"
                            @click="filterResourcesByType('课件')">课件</button>
                    </div>
                    <div class="resource-list">
                        <div v-for="resource in filteredResources" :key="resource.id" class="resource-item">
                            <span class="resource-name">{{ resource.resource_name }}</span>
                            <span class="resource-date">{{ formatUploadDate(resource.created_at) }}上传</span>
                            <div class="resource-actions">
                                <button class="delete-btn" @click="deleteResource(resource)">删除</button>
                                <button class="action-btn" @click="previewResource(resource)">查看</button>
                                <button class="action-btn" @click="downloadResource(resource)">保存</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 作业管理 -->
                <div class="section homework-section">
                    <h3>作业管理</h3>
                    <div class="homework-list">
                        <div v-for="homework in homeworkList" :key="homework.id" class="homework-item">
                            <div class="homework-info">
                                <span class="homework-name">{{ homework.title }}</span>
                                <span class="status" :class="getHomeworkStatus(homework)">
                                    {{ getHomeworkStatus(homework) }}
                                </span>
                            </div>
                            <span class="completion-rate">{{ getCompletionRate(homework) }}完成</span>
                            <div class="homework-actions">
                                <button class="action-btn" @click="viewHomework(homework)">查看</button>
                                <button class="delete-btn" @click="openDeleteHomeworkDialog(homework)">删除</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 学情分析 -->
                <div class="section analysis-section">
                    <h3>学情分析</h3>
                    <div class="analysis-content">
                        <div class="class-stats">
                            <div class="stat-item">
                                <span class="stat-label">班级平均分：</span>
                                <span class="stat-value">85分</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">合格率：</span>
                                <span class="stat-value">95%</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">优秀率：</span>
                                <span class="stat-value">60%</span>
                            </div>
                        </div>
                        <div class="analysis-charts">
                            <div class="chart grade-distribution">
                                <!-- 成绩分布图表 -->
                            </div>
                            <div class="chart performance-trend">
                                <!-- 表现趋势图表 -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 右侧学生管理列表 -->
            <div class="member-list">
                <div class="member-header">
                    <div class="header-top">
                        <h3>学生管理</h3>
                    </div>
                    <div class="search-box">
                        <input type="text" placeholder="搜索" v-model="searchQuery" />
                        <button class="search-btn" @click="searchStudents">搜索</button>
                    </div>
                </div>

                <div class="column-header">
                    <span class="column-title name-col"></span>
                    <span class="column-title action-col"></span>
                </div>

                <div class="member-items">
                    <div v-for="student in filteredStudents" :key="student.id" class="member-item">
                        <span class="member-name">{{ student.name }}</span>
                        <div class="member-actions">
                            <button class="view-stats-btn" @click="viewStudentStats(student)">学情</button>
                            <button class="remove-btn" @click="removeStudent(student.id)">移除</button>
                        </div>
                    </div>
                </div>

                <button class="add-btn" @click="showAddStudentModal = true">添加学生</button>
            </div>
        </div>

        <!-- 预览资源对话框 -->
        <div v-if="showPreview" class="preview-dialog">
            <div class="preview-content">
                <div class="preview-header">
                    <h3>{{ previewingResource?.resource_name }}</h3>
                    <button class="close-btn" @click="closePreview">×</button>
                </div>
                <div class="preview-body">
                    <iframe v-if="previewingResource?.resource_type === 'PPT' ||
                        previewingResource?.resource_type === '教材' ||
                        previewingResource?.resource_type === '教案' ||
                        previewingResource?.resource_type === '习题'" :src="previewingResource?.file_path"
                        frameborder="0"></iframe>
                    <video v-else-if="previewingResource?.resource_type === '视频'" :src="previewingResource?.file_path"
                        controls></video>
                    <img v-else-if="previewingResource?.resource_type === '图片'" :src="previewingResource?.file_path"
                        alt="预览图片" />
                </div>
            </div>
        </div>

        <!-- 添加学生对话框 -->
        <div v-if="showAddStudentModal" class="modal">
            <div class="modal-content">
                <h3>添加学生</h3>
                <form @submit.prevent="addStudent">
                    <div class="form-group">
                        <label for="studentName">姓名</label>
                        <input type="text" id="studentName" v-model="newStudent.name" required />
                    </div>
                    <div class="form-group">
                        <label for="studentId">学号</label>
                        <input type="text" id="studentId" v-model="newStudent.studentId" required />
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="cancel-btn" @click="showAddStudentModal = false">取消</button>
                        <button type="submit" class="submit-btn">添加</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 学生学情分析对话框 -->
        <div v-if="showStudentStats" class="modal">
            <div class="modal-content student-stats-modal">
                <div class="modal-header">
                    <h3>学生学情分析</h3>
                    <button class="close-btn" @click="closeStudentStats">×</button>
                </div>
                <div class="student-stats">
                    <div class="stat-item">
                        <span class="stat-label">姓名：</span>
                        <span class="stat-value">{{ selectedStudent?.name }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">学号：</span>
                        <span class="stat-value">{{ selectedStudent?.studentId }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">平均分：</span>
                        <span class="stat-value">{{ getStudentAverage() }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">完成作业数：</span>
                        <span class="stat-value">{{ getStudentCompletionCount() }}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">参与度：</span>
                        <span class="stat-value">{{ getStudentParticipationRate() }}</span>
                    </div>
                </div>
                <div class="analysis-charts">
                    <div class="chart">
                        <h4>成绩趋势</h4>
                        <div class="chart-placeholder">成绩趋势图表</div>
                    </div>
                    <div class="chart">
                        <h4>知识点掌握情况</h4>
                        <div class="chart-placeholder">知识点掌握情况图表</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 确认删除作业对话框 -->
        <div v-if="showDeleteHomeworkDialog" class="modal">
            <div class="modal-content">
                <h3>确认删除作业</h3>
                <p>您确定要删除作业 "{{ homeworkToDelete?.title }}" 吗？此操作不可撤销。</p>
                <div class="modal-actions">
                    <button type="button" class="cancel-btn" @click="showDeleteHomeworkDialog = false">取消</button>
                    <button type="button" class="confirm-btn" @click="confirmDeleteHomework">确认删除</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

interface Homework {
    id: number;
    title: string;
    description: string;
    due_date: string;
    created_at: string;
    updated_at: string;
    completion_count: number;
    total_students: number;
}

interface HomeworkSubmission {
    id: number;
    student_id: number;
    answers: string;
    grade: number | null;
    feedback: string | null;
    submission_date: string;
}

interface CourseResource {
    id: number;
    resource_name: string;
    resource_type: string;
    file_path: string;
    match_rate: number;
    is_selected: number;
    created_at: string;
    updated_at: string;
}

const route = useRoute();
const router = useRouter();
const showAddStudentModal = ref(false);
const showDeleteHomeworkDialog = ref(false);
const homeworkToDelete = ref<Homework | null>(null);

// 班级基本信息
const classInfo = ref({
    id: route.params.id,
    name: '',
    studentCount: 0,
    subjects: '',
    isEnded: false
});

// 学生数据
const students = ref<{ id: number; name: string; studentId: string; }[]>([]);
const searchQuery = ref('');
const filteredStudents = computed(() => {
    if (!searchQuery.value) return students.value;
    const query = searchQuery.value.toLowerCase();
    return students.value.filter(student =>
        student.name.toLowerCase().includes(query) ||
        student.studentId.toLowerCase().includes(query)
    );
});

// 将学生数据转换为两列显示
const studentRows = computed(() => {
    const rows = [];
    for (let i = 0; i < students.value.length; i += 2) {
        rows.push(students.value.slice(i, i + 2));
    }
    return rows;
});

// 作业相关的状态
const homeworkList = ref<Homework[]>([]);
const newHomework = ref({
    title: '',
    description: '',
    dueDate: ''
});

// 新学生表单数据
const newStudent = ref({
    name: '',
    studentId: ''
});

// 课程资源
const courseResources = ref<Record<string, CourseResource[]>>({
    'PPT': [],
    '视频': [],
    '图片': [],
    '教材': [],
    '教案': [],
    '习题': []
});
const resourceList = ref<CourseResource[]>([]);
const activeResourceType = ref('all');
const filteredResources = computed(() => {
    if (activeResourceType.value === 'all') {
        return resourceList.value;
    } else if (activeResourceType.value === '课件') {
        // 处理课件和PPT的对应关系
        return resourceList.value.filter(resource => resource.resource_type === 'PPT');
    } else {
        return resourceList.value.filter(resource => resource.resource_type === activeResourceType.value);
    }
});

const showPreview = ref(false);
const previewingResource = ref<CourseResource | null>(null);

// 结束授课
const endClass = () => {
    if (confirm('确定要结束授课吗？')) {
        classInfo.value.isEnded = true;
    }
};

// 获取班级信息
const fetchClassInfo = async () => {
    try {
        const response = await fetch(`http://localhost:8000/classes/${route.params.id}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取班级信息失败');
        }

        const data = await response.json();
        classInfo.value = {
            id: data.id,
            name: data.class_name,
            subjects: data.subjects || '暂无',
            studentCount: 0,  // 将在获取学生列表时更新
            isEnded: false
        };
    } catch (error: any) {
        console.error('获取班级信息错误:', error);
    }
};

// 获取学生列表
const fetchStudents = async () => {
    try {
        const response = await fetch(`http://localhost:8000/classes/${route.params.id}/students`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取学生列表失败');
        }

        const data = await response.json();
        students.value = data.map((student: any) => ({
            id: student.id,
            name: student.username,
            studentId: student.id.toString()  // 临时使用id作为学号
        }));

        // 更新学生人数
        classInfo.value.studentCount = students.value.length;
    } catch (error: any) {
        console.error('获取学生列表错误:', error);
    }
};

// 添加学生
const addStudent = async () => {
    try {
        // 先检查学生是否存在
        const checkResponse = await fetch(`http://localhost:8000/users/${newStudent.value.studentId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!checkResponse.ok) {
            throw new Error('该学生不存在，请检查学号是否正确');
        }

        const studentData = await checkResponse.json();

        // 验证用户角色
        if (studentData.role !== 'student') {
            throw new Error('该用户不是学生，无法添加到班级');
        }

        const response = await fetch('http://localhost:8000/classes/students/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                class_id: parseInt(route.params.id as string),
                student_id: parseInt(newStudent.value.studentId)
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '添加学生失败');
        }

        // 重新获取学生列表
        await fetchStudents();

        // 显示成功提示
        window.$showToast('添加学生成功！', 'success');

        // 重置表单并关闭对话框
        newStudent.value = { name: '', studentId: '' };
        showAddStudentModal.value = false;
    } catch (error: any) {
        console.error('添加学生错误:', error);
        window.$showToast(error.message || '添加学生失败，请稍后重试', 'error');
    }
};

// 移除学生
const removeStudent = async (studentId: number) => {
    try {
        const response = await fetch(`http://localhost:8000/classes/${route.params.id}/students/${studentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('移除学生失败');
        }

        // 重新获取学生列表
        await fetchStudents();
    } catch (error: any) {
        console.error('移除学生错误:', error);
    }
};

// 获取作业列表
const fetchHomeworks = async () => {
    try {
        const response = await fetch(`http://localhost:8000/classes/${route.params.id}/assignments`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取班级作业失败');
        }

        const data = await response.json();
        homeworkList.value = await Promise.all(data.map(async (homework: any) => {
            try {
                // 获取作业提交情况
                const submissionsResponse = await fetch(`http://localhost:8000/assignments/${homework.id}/submissions`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (!submissionsResponse.ok) {
                    throw new Error(`获取作业提交情况失败: ${homework.id}`);
                }

                const submissionsData = await submissionsResponse.json();

                return {
                    ...homework,
                    completion_count: submissionsData.length,
                    total_students: classInfo.value.studentCount,
                    status: new Date(homework.due_date) < new Date() ? '已结束' : '进行中'
                };
            } catch (error) {
                console.error('获取作业信息错误:', error);
                return {
                    ...homework,
                    completion_count: 0,
                    total_students: classInfo.value.studentCount || 0,
                    status: new Date(homework.due_date) < new Date() ? '已结束' : '进行中'
                };
            }
        }));
    } catch (error) {
        console.error('获取班级作业错误:', error);
        homeworkList.value = [];
    }
};

// 获取作业状态
const getHomeworkStatus = (homework: Homework) => {
    const now = new Date();
    const dueDate = new Date(homework.due_date);
    return now > dueDate ? '已结束' : '进行中';
};

// 判断作业是否已结束
const isHomeworkEnded = (homework: Homework) => {
    return getHomeworkStatus(homework) === '已结束';
};

// 获取作业完成率
const getCompletionRate = (homework: Homework) => {
    if (!homework || typeof homework.completion_count === 'undefined' || typeof homework.total_students === 'undefined') {
        return '0/0';
    }
    return `${homework.completion_count}/${homework.total_students}`;
};

// 处理作业
const handleHomework = (homework: Homework) => {
    // 跳转到作业详情页面
    router.push(`/teacher/assignments/${homework.id}/submissions`);
};

// 查看作业
const viewHomework = (homework: Homework) => {
    router.push(`/teacher/assignments/${homework.id}/submissions`);
};

// 格式化日期
const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// 获取课程资源
const fetchCourseResources = async () => {
    try {
        const response = await fetch(`http://localhost:8000/classes/${route.params.id}/resources`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取课程资源失败');
        }

        const data = await response.json();

        // 按资源类型分类
        const resourcesByType: Record<string, CourseResource[]> = {
            'PPT': [],
            '视频': [],
            '图片': [],
            '教材': [],
            '教案': [],
            '习题': []
        };

        data.forEach((resource: CourseResource) => {
            if (resourcesByType[resource.resource_type]) {
                resourcesByType[resource.resource_type].push(resource);
            }
        });

        courseResources.value = resourcesByType;
        // 获取所有资源列表
        resourceList.value = data;
    } catch (error: any) {
        console.error('获取课程资源错误:', error);
        window.$showToast(error.message || '获取课程资源失败', 'error');
    }
};

// 预览资源
const previewResource = (resource: CourseResource) => {
    previewingResource.value = resource;
    showPreview.value = true;
};

// 关闭预览
const closePreview = () => {
    showPreview.value = false;
    previewingResource.value = null;
};

// 下载资源
const downloadResource = async (resource: CourseResource) => {
    try {
        // 通过后端API下载资源
        const response = await fetch(`http://localhost:8000/classes/resources/${resource.id}/download`, {
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
        // 使用资源的原始名称
        a.download = resource.resource_name;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        window.$showToast('资源下载成功', 'success');
    } catch (error: any) {
        console.error('下载资源错误:', error);
        window.$showToast(error.message || '下载资源失败，请稍后重试', 'error');
    }
};

// 格式化上传日期
const formatUploadDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
};

// 搜索学生
const searchStudents = () => {
    // 过滤由 computed 属性 filteredStudents 处理
};

// 查看学生学情分析
const viewStudentStats = (student: any) => {
    selectedStudent.value = student;
    showStudentStats.value = true;
};

// 关闭学生学情分析
const closeStudentStats = () => {
    showStudentStats.value = false;
    selectedStudent.value = null;
};

// 删除资源
const deleteResource = async (resource: CourseResource) => {
    if (confirm(`确定要删除资源"${resource.resource_name}"吗？`)) {
        try {
            // 删除班级资源关联
            const response = await fetch(`http://localhost:8000/classes/resources/${resource.id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('从班级移除资源失败');
            }

            // 从列表中移除已删除的资源
            resourceList.value = resourceList.value.filter(item => item.id !== resource.id);

            // 也从分类的资源中移除
            if (resource.resource_type && courseResources.value[resource.resource_type]) {
                courseResources.value[resource.resource_type] = courseResources.value[resource.resource_type].filter(
                    item => item.id !== resource.id
                );
            }

            // 显示成功提示
            window.$showToast('课程资源移除成功！', 'success');
        } catch (error: any) {
            console.error('移除课程资源错误:', error);
            window.$showToast(error.message || '移除课程资源失败，请稍后重试', 'error');
        }
    }
};

// 筛选资源类型
const filterResourcesByType = (type: string) => {
    activeResourceType.value = type;
};

// 在响应式变量定义部分添加新的变量
const showStudentStats = ref(false);
const selectedStudent = ref<any>(null);

// 获取学生平均分
const getStudentAverage = () => {
    // 实际应从后端获取数据
    return '85.5分';
};

// 获取学生完成作业数
const getStudentCompletionCount = () => {
    // 实际应从后端获取数据
    return '8/10';
};

// 获取学生参与度
const getStudentParticipationRate = () => {
    // 实际应从后端获取数据
    return '90%';
};

// 打开删除作业对话框
const openDeleteHomeworkDialog = (homework: Homework) => {
    homeworkToDelete.value = homework;
    showDeleteHomeworkDialog.value = true;
};

// 确认删除作业
const confirmDeleteHomework = async () => {
    if (!homeworkToDelete.value) return;

    try {
        const response = await fetch(`http://localhost:8000/assignments/${homeworkToDelete.value.id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('删除作业失败');
        }

        // 显示成功信息
        window.$showToast('作业删除成功', 'success');

        // 关闭对话框
        showDeleteHomeworkDialog.value = false;
        homeworkToDelete.value = null;

        // 重新获取作业列表
        await fetchHomeworks();
    } catch (error: any) {
        console.error('删除作业错误:', error);
        window.$showToast(error.message || '删除作业失败，请稍后重试', 'error');
    }
};

// 页面加载时获取数据
onMounted(() => {
    fetchClassInfo();
    fetchStudents();
    fetchHomeworks();
    fetchCourseResources();
});
</script>

<style scoped>
.class-detail {
    padding: 20px;
    height: 100%;
    
        .class-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
    
        .class-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
    
        .class-info h2 {
            margin: 0;
            font-size: 22px;
            color: #333;
        }
    
        .info-item {
            color: #666;
            font-size: 14px;
        }
    
        .end-class-btn {
            padding: 6px 16px;
            background-color: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
    
        .main-content {
            display: flex;
            gap: 20px;
            height: calc(100% - 60px);
        }
    
        .left-content {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
    
        .section {
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
    
        .section h3 {
            margin: 0 0 16px 0;
            font-size: 18px;
            color: #333;
        }
    
        /* 资源展示模块样式 */
        .resource-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 16px;
        }
    
        .tab-btn {
            padding: 6px 16px;
            border: none;
            border-radius: 4px;
            background: #f5f7fa;
            cursor: pointer;
        }
    
        .tab-btn.active {
            background: #4c84ff;
            color: white;
        }
    
        .resource-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
    
        .resource-item {
            display: grid;
            grid-template-columns: 1fr auto auto;
            align-items: center;
            padding: 12px;
            background: #f5f7fa;
            border-radius: 4px;
            gap: 16px;
        }
    
        .resource-name {
            font-size: 14px;
            color: #333;
        }
    
        .resource-date {
            color: #666;
            font-size: 14px;
            text-align: right;
        }
    
        .resource-actions {
            display: flex;
            gap: 8px;
            min-width: 200px;
            justify-content: flex-end;
        }
    
        .action-btn {
            padding: 4px 12px;
            border: none;
            border-radius: 4px;
            background: #4c84ff;
            color: white;
            cursor: pointer;
        }
    
        .delete-btn {
            padding: 4px 12px;
            border: none;
            border-radius: 4px;
            background: #dc3545;
            color: white;
            cursor: pointer;
            transition: all 0.3s;
            }
            
            .delete-btn:hover {
                background: #c82333;
        }
    
        /* 作业管理样式 */
        .homework-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
    
        .homework-item {
            display: grid;
            grid-template-columns: 1fr auto auto;
            align-items: center;
            padding: 12px;
            background: #f5f7fa;
            border-radius: 4px;
            gap: 16px;
        }
    
        .homework-info {
            display: flex;
            align-items: center;
            gap: 12px;
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
    
        .completion-rate {
            color: #666;
            font-size: 14px;
            text-align: right;
            min-width: 80px;
        }
    
        .homework-actions {
            display: flex;
            gap: 8px;
            min-width: 140px;
            justify-content: flex-end;
        }
    
        /* 学情分析样式 */
        .analysis-content {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
    
        .class-stats {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
    
        .stat-item {
            display: flex;
            gap: 8px;
        }
    
        .analysis-charts {
            display: flex;
            gap: 20px;
            height: 200px;
        }
    
        .chart {
            flex: 1;
            background: #f5f7fa;
            border-radius: 4px;
        }
    
        /* 学生管理样式 */
        .member-list {
            width: 300px;
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
        }
    
        .member-header {
            margin-bottom: 16px;
        }
    
        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
    
        .member-header h3 {
            margin: 0;
            font-size: 18px;
            color: #333;
        }
    
        .search-box {
            display: flex;
            gap: 8px;
            margin-bottom: -4px;
        }
    
        .search-box input {
            flex: 1;
            padding: 6px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    
        .search-btn {
            padding: 6px 12px;
            background: #4c84ff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    
        .add-btn {
            padding: 10px 0;
            margin-top: 16px;
            background-color: #4c84ff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
        }
    
        .column-header {
            display: grid;
            grid-template-columns: 1fr auto;
            padding: 4px 8px;
            border-bottom: 1px solid #eee;
            font-weight: bold;
            color: #666;
            margin-bottom: 8px;
        }
    
        .member-item {
            display: grid;
            grid-template-columns: 1fr auto;
            align-items: center;
            padding: 8px;
            background: #f5f7fa;
            border-radius: 4px;
        }
    
        .member-name {
            font-size: 14px;
            color: #333;
        }
    
        .member-actions {
            display: flex;
            gap: 8px;
            justify-content: flex-end;
        }
    
        .view-stats-btn,
        .remove-btn {
            padding: 4px 12px;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            min-width: 50px;
        }
    
        .view-stats-btn {
            background-color: #4c84ff;
        }
    
        .remove-btn {
            background-color: #dc3545;
        }
    
        /* 预览资源对话框 */
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
    
        .form-group {
            margin-bottom: 16px;
        }
    
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #666;
            font-size: 14px;
        }
    
        .form-group input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
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
    
        .close-btn {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
        }
    
        .student-stats-modal {
            max-width: 600px;
            width: 90%;
        }
    
        .student-stats {
            margin-bottom: 20px;
        }
    
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 16px;
            border-bottom: 1px solid #eee;
        }
    
        .modal-footer {
            margin-top: 20px;
            display: flex;
            justify-content: flex-end;
        }
    
        .chart-placeholder {
            height: 150px;
            background-color: #f5f7fa;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
        }
    
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    
        .btn.primary {
            background-color: #4c84ff;
            color: white;
        }
    }
</style>