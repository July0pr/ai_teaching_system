<template>
    <div class="class-detail">
        <!-- 顶部班级信息 -->
        <div class="class-header">
            <div class="class-info">
                <h2>{{ classInfo.name }}</h2>
                <span class="info-item">学生人数: {{ classInfo.studentCount }}</span>
                <span class="info-item">教授科目：{{ classInfo.subjects }}</span>
                <span class="info-item">班主任: {{ classInfo.teacherName }}</span>
            </div>
            <button class="exit-btn" @click="leaveClass">退出班级</button>
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
                            @click="filterResourcesByType('图片')">图集</button>
                        <button class="tab-btn" :class="{ active: activeResourceType === '课件' }"
                            @click="filterResourcesByType('课件')">课件</button>
                        <button class="tab-btn" :class="{ active: activeResourceType === '视频' }"
                            @click="filterResourcesByType('视频')">视频</button>
                        <button class="tab-btn" :class="{ active: activeResourceType === '文献' }"
                            @click="filterResourcesByType('文献')">文献</button>
                    </div>
                    <div class="resource-list">
                        <div v-for="resource in filteredResources" :key="resource.id" class="resource-item">
                            <span class="resource-name">{{ resource.resource_name }}</span>
                            <span class="resource-date">{{ formatUploadDate(resource.created_at) }}上传</span>
                            <div class="resource-actions">
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
                                <span class="status" :class="homework.status">{{ homework.status }}</span>
                            </div>
                            <span class="completion-rate">{{ getCompletionRate(homework) }}完成</span>
                            <div class="homework-actions">
                                <button class="action-btn" @click="viewHomework(homework)">查看</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 学情分析 -->
                <div class="section analysis-section">
                    <h3>学情分析</h3>
                    <div class="analysis-content">
                        <div class="personal-stats">
                            <div class="stat-item">
                                <span class="stat-label">个人排名：</span>
                                <span class="stat-value">{{ studentStats.rank }}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">知识点掌握程度：</span>
                                <span class="stat-value">{{ studentStats.masteryRate }}%</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">学习效果预测：</span>
                                <span class="stat-value">{{ studentStats.prediction }}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">综合评价：</span>
                                <span class="stat-value">{{ studentStats.evaluation }}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">学习建议：</span>
                                <span class="stat-value">{{ studentStats.suggestion }}</span>
                            </div>
                        </div>
                        <div class="analysis-charts">
                            <div class="chart subject-performance">
                                <!-- 各科成绩水平图表 -->
                            </div>
                            <div class="chart study-time">
                                <!-- 各科学习时间占比图表 -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 右侧成员列表 -->
            <div class="member-list">
                <div class="member-header">
                    <h3>成员列表</h3>
                    <div class="search-box">
                        <input type="text" placeholder="搜索" v-model="searchQuery" />
                        <button class="search-btn" @click="searchStudents">搜索</button>
                    </div>
                </div>
                <div class="member-items">
                    <div v-for="student in filteredStudents" :key="student.id" class="member-item">
                        <div class="avatar">{{ getInitials(student.name) }}</div>
                        <span class="member-name">{{ student.name }}</span>
                    </div>
                </div>
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
                    <iframe
                        v-if="previewingResource?.resource_type === '课件' || previewingResource?.resource_type === '文献'"
                        :src="previewingResource?.file_path" frameborder="0"></iframe>
                    <video v-else-if="previewingResource?.resource_type === '视频'" :src="previewingResource?.file_path"
                        controls></video>
                    <img v-else-if="previewingResource?.resource_type === '图片'" :src="previewingResource?.file_path"
                        alt="预览图片" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

interface ClassInfo {
    id: number;
    name: string;
    studentCount: number;
    teacherName: string;
    subjects: string;
}

interface Student {
    id: number;
    name: string;
    studentId?: string;
}

interface Subject {
    name: string;
    status: string;
}

interface Resource {
    id: number;
    resource_name: string;
    resource_type: string;
    file_path: string;
    created_at: string;
}

interface Homework {
    id: number;
    title: string;
    description: string;
    due_date: string;
    created_at: string;
    completion_count: number;
    total_students: number;
    status: string;
}

interface StudentStats {
    rank: string;
    masteryRate: number;
    prediction: string;
    evaluation: string;
    suggestion: string;
}

const route = useRoute();
const router = useRouter();
const classId = computed(() => Number(route.params.id));
const searchQuery = ref('');

// 班级信息
const classInfo = ref<ClassInfo>({
    id: 0,
    name: '',
    studentCount: 0,
    teacherName: '',
    subjects: ''
});

// 学生列表
const students = ref<Student[]>([]);
const filteredStudents = computed(() => {
    if (!searchQuery.value) return students.value;
    return students.value.filter(student =>
        student.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        (student.studentId && student.studentId.includes(searchQuery.value))
    );
});

// 科目列表
const subjects = ref<Subject[]>([]);

// 资源相关
const resources = ref<Resource[]>([]);
const activeResourceType = ref('all');
const filteredResources = computed(() => {
    if (activeResourceType.value === 'all') return resources.value;
    return resources.value.filter(resource => resource.resource_type === activeResourceType.value);
});
const showPreview = ref(false);
const previewingResource = ref<Resource | null>(null);

// 作业列表
const homeworkList = ref<Homework[]>([]);

// 学生学情统计
const studentStats = ref<StudentStats>({
    rank: '暂无排名',
    masteryRate: 0,
    prediction: '暂无预测',
    evaluation: '暂无评价',
    suggestion: '暂无建议'
});

// 初始化页面数据
const initData = async () => {
    try {
        await Promise.all([
            fetchClassInfo(),
            fetchSubjects(),
            fetchResources(),
            fetchHomeworks(),
            fetchStudents(),
            fetchStudentStats()
        ]);
    } catch (error) {
        console.error('初始化页面数据失败:', error);
    }
};

// 获取班级信息
const fetchClassInfo = async () => {
    try {
        const response = await fetch(`http://localhost:8000/classes/${classId.value}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取班级信息失败');
        }

        const data = await response.json();

        // 获取教师信息
        const teacherResponse = await fetch(`http://localhost:8000/users/${data.teacher_id}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!teacherResponse.ok) {
            throw new Error('获取教师信息失败');
        }

        const teacherData = await teacherResponse.json();

        // 获取学生人数
        const studentsResponse = await fetch(`http://localhost:8000/classes/${classId.value}/students`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!studentsResponse.ok) {
            throw new Error('获取学生列表失败');
        }

        const studentsData = await studentsResponse.json();

        classInfo.value = {
            id: data.id,
            name: data.class_name,
            studentCount: studentsData.length,
            teacherName: teacherData.username,
            subjects: data.subjects || '暂无'
        };
    } catch (error) {
        console.error('获取班级信息错误:', error);
        // 使用默认数据
        classInfo.value = {
            id: classId.value,
            name: '软件2202班',
            studentCount: 45,
            teacherName: '林老师',
            subjects: '数据结构'
        };
    }
};

// 获取班级科目
const fetchSubjects = async () => {
    try {
        // 假设科目信息包含在班级信息的subjects字段中，格式为逗号分隔的字符串
        if (classInfo.value.subjects) {
            const subjectNames = classInfo.value.subjects.split('、');
            subjects.value = subjectNames.map(name => ({
                name,
                status: Math.random() > 0.3 ? '进行中' : '已结束'
            }));
        }

        if (subjects.value.length === 0) {
            // 使用模拟数据
            subjects.value = [
                { name: '数据结构', status: '进行中' },
                { name: '嵌入式开发', status: '进行中' },
                { name: '大学物理（上）', status: '已结束' },
                { name: '大学生心理健康教育', status: '已结束' },
                { name: '大学生英语写作', status: '已结束' }
            ];
        }
    } catch (error) {
        console.error('获取班级科目错误:', error);
        // 使用默认数据
        subjects.value = [
            { name: '数据结构', status: '进行中' },
            { name: '嵌入式开发', status: '进行中' },
            { name: '大学物理（上）', status: '已结束' },
            { name: '大学生心理健康教育', status: '已结束' },
            { name: '大学生英语写作', status: '已结束' }
        ];
    }
};

// 获取班级资源
const fetchResources = async () => {
    try {
        const response = await fetch(`http://localhost:8000/classes/${classId.value}/resources`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取班级资源失败');
        }

        const data = await response.json();
        resources.value = data;
    } catch (error) {
        console.error('获取班级资源错误:', error);
        // 使用默认数据
        resources.value = [
            {
                id: 1,
                resource_name: '关于数据结构的文献研究',
                resource_type: '文献',
                file_path: '/path/to/document1.pdf',
                created_at: '2023-09-27T10:30:00'
            },
            {
                id: 2,
                resource_name: '高等数学第二章PPT',
                resource_type: '课件',
                file_path: '/path/to/ppt1.pptx',
                created_at: '2023-09-10T14:20:00'
            },
            {
                id: 3,
                resource_name: '古诗词鉴赏专题',
                resource_type: '课件',
                file_path: '/path/to/ppt2.pptx',
                created_at: '2023-05-10T09:15:00'
            },
            {
                id: 4,
                resource_name: '积分中值定理详解',
                resource_type: '课件',
                file_path: '/path/to/document2.pdf',
                created_at: '2023-01-02T16:45:00'
            }
        ];
    }
};

// 获取班级作业
const fetchHomeworks = async () => {
    try {
        const response = await fetch(`http://localhost:8000/classes/${classId.value}/assignments`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取班级作业失败');
        }

        const data = await response.json();
        const userId = localStorage.getItem('userId');

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

                // 获取当前学生的提交状态
                const statusResponse = await fetch(`http://localhost:8000/students/${userId}/assignments/${homework.id}/status`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                let status = new Date(homework.due_date) < new Date() ? '已结束' : '进行中';
                if (statusResponse.ok) {
                    const statusData = await statusResponse.json();
                    if (statusData.submitted) {
                        status = '已提交';
                    }
                }

                return {
                    ...homework,
                    completion_count: submissionsData.length,
                    total_students: classInfo.value.studentCount,
                    status
                };
            } catch (error) {
                console.error('获取作业信息错误:', error);
                return {
                    ...homework,
                    completion_count: Math.floor(Math.random() * classInfo.value.studentCount),
                    total_students: classInfo.value.studentCount,
                    status: new Date(homework.due_date) < new Date() ? '已结束' : '进行中'
                };
            }
        }));
    } catch (error) {
        console.error('获取班级作业错误:', error);
        // 使用默认数据
        homeworkList.value = [
            {
                id: 1,
                title: '第一学期第五次测试',
                description: '覆盖第五章内容',
                due_date: new Date(Date.now() + 86400000 * 5).toISOString(), // 5天后
                created_at: '2023-11-01T10:00:00',
                completion_count: 30,
                total_students: 45,
                status: '进行中'
            },
            {
                id: 2,
                title: '第一学期第四次测试',
                description: '覆盖第四章内容',
                due_date: new Date(Date.now() + 86400000 * 2).toISOString(), // 2天后
                created_at: '2023-10-20T10:00:00',
                completion_count: 44,
                total_students: 45,
                status: '已提交'
            },
            {
                id: 3,
                title: '期中测试',
                description: '覆盖第一至第三章内容',
                due_date: '2023-10-10T23:59:59',
                created_at: '2023-10-01T10:00:00',
                completion_count: 45,
                total_students: 45,
                status: '已结束'
            },
            {
                id: 4,
                title: '第一学期第二次测试',
                description: '覆盖第二章内容',
                due_date: '2023-09-20T23:59:59',
                created_at: '2023-09-10T10:00:00',
                completion_count: 40,
                total_students: 45,
                status: '已结束'
            }
        ];
    }
};

// 获取班级学生
const fetchStudents = async () => {
    try {
        const response = await fetch(`http://localhost:8000/classes/${classId.value}/students`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取班级学生失败');
        }

        const data = await response.json();

        // 确保data是数组
        if (!Array.isArray(data)) {
            throw new Error('学生数据格式错误');
        }

        students.value = await Promise.all(data.map(async (student: any) => {
            try {
                // 检查student是否包含必要的id信息
                const studentId = typeof student === 'object' ? student.id : student;

                if (!studentId) {
                    throw new Error('无效的学生ID');
                }

                const studentResponse = await fetch(`http://localhost:8000/users/${studentId}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (!studentResponse.ok) {
                    throw new Error(`获取学生信息失败: ${studentId}`);
                }

                const studentData = await studentResponse.json();

                if (!studentData || !studentData.username) {
                    throw new Error(`学生数据不完整: ${studentId}`);
                }

                return {
                    id: studentData.id,
                    name: studentData.username,
                    studentId: `20230${studentData.id}`
                };
            } catch (error) {
                console.error('获取单个学生信息错误:', error);
                // 返回一个带有默认值的对象，而不是抛出错误
                return {
                    id: typeof student === 'object' ? student.id : student,
                    name: `未知学生`,
                    studentId: `未知学号`
                };
            }
        }));
    } catch (error) {
        console.error('获取班级学生错误:', error);
        // 使用默认数据
        students.value = [
            { id: 1, name: '林雨婷', studentId: '202301001' },
            { id: 2, name: '赵亮', studentId: '202301002' },
            { id: 3, name: '王明', studentId: '202301003' },
            { id: 4, name: '李华', studentId: '202301004' },
            { id: 5, name: '张伟', studentId: '202301005' }
        ];
    }
};

// 过滤资源类型
const filterResourcesByType = (type: string) => {
    activeResourceType.value = type;
};

// 格式化上传日期
const formatUploadDate = (dateString: string) => {
    if (!dateString) return '未知时间';
    const date = new Date(dateString);
    return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
};

// 获取学生姓名首字母
const getInitials = (name: string) => {
    if (!name) return '';
    return name.charAt(0);
};

// 获取作业状态
const getHomeworkStatus = (homework: Homework) => {
    return homework.status;
};

// 获取作业完成率
const getCompletionRate = (homework: Homework) => {
    return `${homework.completion_count}/${homework.total_students}`;
};

// 判断作业是否已结束
const isHomeworkEnded = (homework: Homework) => {
    return homework.status === '已结束';
};

// 查看作业
const viewHomework = (homework: Homework) => {
    router.push(`/student/assignments/${homework.id}`);
};

// 搜索学生
const searchStudents = () => {
    // 直接使用computed过滤
};

// 预览资源
const previewResource = (resource: Resource) => {
    previewingResource.value = resource;
    showPreview.value = true;
};

// 关闭预览
const closePreview = () => {
    showPreview.value = false;
    previewingResource.value = null;
};

// 下载资源
const downloadResource = async (resource: Resource) => {
    try {
        const response = await fetch(`http://localhost:8000/classes/resources/${resource.id}/download`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error(`下载失败: ${response.status}`);
        }

        // 获取文件名
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = resource.resource_name;
        if (contentDisposition) {
            const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        // 创建下载链接
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('下载资源失败:', error);
        alert('下载资源失败，请稍后重试');
    }
};

// 退出班级
const leaveClass = async () => {
    if (confirm('确定要退出班级吗？')) {
        try {
            const userId = localStorage.getItem('userId');
            const response = await fetch(`http://localhost:8000/students/${userId}/classes/${classId.value}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('退出班级失败');
            }

            router.push('/student/classes');
        } catch (error) {
            console.error('退出班级错误:', error);
            alert('退出班级失败，请稍后重试');
        }
    }
};

// 获取学生学情统计
const fetchStudentStats = async () => {
    try {
        const userId = localStorage.getItem('userId');
        const response = await fetch(`http://localhost:8000/students/${userId}/performance`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取学情统计失败');
        }

        const data = await response.json();
        studentStats.value = {
            rank: data.rank,
            masteryRate: data.mastery_rate,
            prediction: data.prediction,
            evaluation: data.evaluation,
            suggestion: data.suggestion
        };
    } catch (error) {
        console.error('获取学情统计错误:', error);
        // 使用默认数据
        studentStats.value = {
            rank: '暂无排名',
            masteryRate: 0,
            prediction: '暂无预测',
            evaluation: '暂无评价',
            suggestion: '暂无建议'
        };
    }
};

// 页面加载时初始化数据
onMounted(() => {
    initData();
});
</script>

<style scoped>
.class-detail {
    padding: 20px;
    height: 100%;
}

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

.info-item {
    color: #666;
}

.exit-btn {
    padding: 8px 20px;
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
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

/* 课程资源样式 */
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
    background: #3498db;
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
    min-width: 140px;
    justify-content: flex-end;
}

.action-btn {
    padding: 4px 12px;
    border: none;
    border-radius: 4px;
    background: #3498db;
    color: white;
    cursor: pointer;
}

.action-btn.disabled {
    background: #999;
    cursor: not-allowed;
}

/* 状态样式 */
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

.status.已提交 {
    background-color: #52c41a;
    color: white;
}

.status.未提交 {
    background-color: #faad14;
    color: white;
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

.personal-stats {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.stat-item {
    display: flex;
    gap: 8px;
}

.stat-label {
    font-weight: bold;
    min-width: 120px;
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

/* 成员列表样式 */
.member-list {
    width: 300px;
    background: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.member-header {
    margin-bottom: 16px;
}

.search-box {
    display: flex;
    gap: 8px;
    margin-top: 12px;
}

.search-box input {
    flex: 1;
    padding: 6px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.search-btn {
    padding: 6px 12px;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.member-items {
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;
    max-height: calc(100% - 80px);
}

.member-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px;
    background: #f5f7fa;
    border-radius: 4px;
}

.avatar {
    width: 40px;
    height: 40px;
    background: #3498db;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: bold;
}

/* 预览对话框样式 */
.preview-dialog {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
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
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #eee;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
}

.preview-body {
    flex: 1;
    overflow: auto;
    padding: 16px;
}

.preview-body iframe,
.preview-body video,
.preview-body img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}
</style>