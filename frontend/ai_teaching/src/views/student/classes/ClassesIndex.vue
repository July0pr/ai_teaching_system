<template>
    <div class="classes-index">
        <div class="header">
            <h2>我的班级</h2>
        </div>

        <div class="class-cards">
            <div v-for="classItem in classes" :key="classItem.id" class="class-card">
                <div class="class-info">
                    <h3>{{ classItem.name }}</h3>
                    <div class="info-row">
                        <span class="label">教授科目：</span>
                        <span class="value">{{ classItem.subjects }}</span>
                        <span class="status" :class="classItem.status">{{ classItem.status }}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">学生人数：</span>
                        <span class="value">{{ classItem.studentCount }}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">教师：</span>
                        <span class="value">{{ classItem.teacherName }}</span>
                    </div>
                </div>
                <button class="enter-btn" @click="enterClass(classItem.id)">进入班级</button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

interface ClassItem {
    id: number;
    name: string;
    subjects: string;
    studentCount: number;
    status: string;
    teacherName: string;
}

const router = useRouter();
const classes = ref<ClassItem[]>([]);

// 获取班级列表
const fetchClasses = async () => {
    try {
        const studentId = localStorage.getItem('userId');
        if (!studentId) {
            throw new Error('未找到学生信息');
        }

        const response = await fetch(`http://localhost:8000/students/${studentId}/classes`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('获取班级列表失败');
        }

        const data = await response.json();

        // 转换数据格式
        classes.value = await Promise.all(data.map(async (cls: any) => {
            try {
                // 获取班级学生数量
                const studentsResponse = await fetch(`http://localhost:8000/classes/${cls.id}/students`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (!studentsResponse.ok) {
                    throw new Error(`获取班级学生数量失败: ${cls.class_name}`);
                }

                const studentsData = await studentsResponse.json();

                // 获取教师信息
                const teacherResponse = await fetch(`http://localhost:8000/users/${cls.teacher_id}`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (!teacherResponse.ok) {
                    throw new Error(`获取教师信息失败: ${cls.teacher_id}`);
                }

                const teacherData = await teacherResponse.json();

                return {
                    id: cls.id,
                    name: cls.class_name,
                    subjects: cls.subjects || '暂无',
                    studentCount: studentsData.length,
                    status: '进行中',  // 默认状态，实际应该根据业务逻辑确定
                    teacherName: teacherData.username
                } as ClassItem;
            } catch (innerError) {
                console.error('处理班级数据错误:', innerError);
                // 返回部分数据，避免整个列表失败
                return {
                    id: cls.id,
                    name: cls.class_name,
                    subjects: cls.subjects || '暂无',
                    studentCount: 0,
                    status: '进行中',
                    teacherName: '未知'
                } as ClassItem;
            }
        }));
    } catch (error: any) {
        console.error('获取班级列表错误:', error);
    }
};

// 进入班级
const enterClass = (classId: number) => {
    router.push(`/student/classes/${classId}`);
};

// 页面加载时获取班级列表
onMounted(() => {
    fetchClasses();
});
</script>

<style scoped>
.classes-index {
    padding: 20px;
    height: 100%;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    h2 {
        font-size: 20px;
        color: #333;
        margin: 0;
    }
    
    .class-cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        padding: 10px 0;
    }
    
    .class-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .class-info h3 {
        margin: 0 0 16px 0;
        font-size: 18px;
        color: #333;
    }
    
    .info-row {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .label {
        color: #666;
        font-size: 14px;
        width: 80px;
    }
    
    .value {
        color: #333;
        font-size: 14px;
        flex: 1;
    }
    
    .status {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        color: white;
    }
    
    .status.进行中 {
        background-color: #3498db;
    }
    
    .status.已结束 {
        background-color: #999;
    }
    
    .enter-btn {
        width: 100%;
        padding: 8px;
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .enter-btn:hover {
        /* background-color: #3a70e3; */
            background-color: #2f86c0;
}
</style>