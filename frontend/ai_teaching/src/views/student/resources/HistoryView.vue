<template>
    <div class="history-view">
        <!-- 顶部搜索和操作区 -->
        <div class="top-actions">
            <div class="search-bar">
                <input type="text" v-model="searchQuery" placeholder="搜索作业名称" @input="handleSearch" />
                <button class="search-btn" @click="handleSearch">搜索</button>
            </div>
            <div class="action-buttons">
                <button class="delete-btn" @click="deleteSelected" :disabled="selectedItems.length === 0">
                    删除选中 ({{ selectedItems.length }})
                </button>
            </div>
        </div>

        <!-- 练习题历史列表 -->
        <div class="resources-list">
            <div class="resource-section">
                <h3>练习题生成历史</h3>
                <div class="resource-items">
                    <div class="resource-item" v-for="item in filteredExercises" :key="'exercise-' + item.id">
                        <div class="item-checkbox">
                            <input type="checkbox" :id="'check-' + item.id" v-model="selectedItems" :value="item.id" />
                        </div>
                        <div class="item-info">
                            <div class="sequence-number">#{{ item.sequence_number }}</div>
                            <div class="title">{{ item.assignment_name }}</div>
                        </div>
                        <div class="exercise-info">
                            <div class="count">{{ item.exercise_count }}道题</div>
                            <div class="date">{{ formatDate(item.created_at) }}</div>
                        </div>
                        <div class="action-btns">
                            <button class="view-btn" @click="viewExercise(item)">查看</button>
                            <button class="practice-btn" @click="practiceExercise(item)">自主作答</button>
                        </div>
                    </div>
                    <div v-if="filteredExercises.length === 0" class="empty-message">
                        暂无练习题生成历史记录
                    </div>
                </div>
            </div>
        </div>

        <!-- 确认删除对话框 -->
        <div class="delete-dialog" v-if="showDeleteDialog">
            <div class="dialog-content">
                <h3>确认删除</h3>
                <p>确定要删除选中的 {{ selectedItems.length }} 条记录吗？此操作不可撤销。</p>
                <div class="dialog-buttons">
                    <button class="cancel-btn" @click="showDeleteDialog = false">取消</button>
                    <button class="confirm-btn" @click="confirmDelete">确认删除</button>
                </div>
            </div>
        </div>

        <!-- 练习题详情弹窗 -->
        <div class="exercise-modal" v-if="showExerciseModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>练习题详情</h3>
                    <button class="close-btn" @click="closeExerciseModal">×</button>
                </div>
                <div class="modal-body">
                    <div class="exercise-details">
                        <div class="detail-header">
                            <h4>{{ currentExercise?.assignment_name }}</h4>
                            <div class="detail-meta">
                                <span>序号: #{{ currentExercise?.sequence_number }}</span>
                                <span>生成时间: {{ formatDate(currentExercise?.created_at) }}</span>
                            </div>
                        </div>
                        <div class="exercises-list">
                            <div v-for="(exercise, index) in currentExerciseQuestions" :key="index"
                                class="exercise-item">
                                <div class="exercise-header">
                                    <span class="exercise-number">题目 {{ index + 1 }}</span>
                                    <span class="exercise-type">{{ exercise.type }}</span>
                                </div>
                                <div class="exercise-content">{{ exercise.content }}</div>
                                <div class="exercise-footer">
                                    <div class="answer-section">
                                        <strong>正确答案：</strong> {{ exercise.answers }}
                                    </div>
                                    <div class="difficulty">难度: {{ exercise.difficulty }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

interface ExerciseRecord {
    id: number;
    assignment_id: number;
    assignment_name: string;
    sequence_number: number;
    exercise_count: number;
    exercises: any[];
    created_at: string;
    updated_at: string;
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
const searchQuery = ref('');
const exercises = ref<ExerciseRecord[]>([]);
const selectedItems = ref<number[]>([]);
const showDeleteDialog = ref(false);

// 弹窗状态
const showExerciseModal = ref(false);
const currentExercise = ref<ExerciseRecord | null>(null);
const currentExerciseQuestions = ref<ExerciseQuestion[]>([]);

// 搜索过滤
const filteredExercises = computed(() => {
    if (!searchQuery.value) return exercises.value;
    const query = searchQuery.value.toLowerCase();
    return exercises.value.filter(item =>
        item.assignment_name.toLowerCase().includes(query)
    );
});

// 获取练习题历史
const fetchExercises = async () => {
    try {
        const userId = localStorage.getItem('userId');
        const response = await axios.get(`http://localhost:8000/student/${userId}/exercises/history`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        exercises.value = response.data.map((item: any) => ({
            ...item,
            exercise_count: item.exercises ? item.exercises.length : 0
        }));
    } catch (error) {
        console.error('获取练习题历史失败:', error);
    }
};

// 获取所有数据
const fetchAllData = async () => {
    try {
        await fetchExercises();
    } catch (error) {
        console.error('获取历史记录错误:', error);
        window.$showToast('获取历史记录失败', 'error');
    }
};

// 查看练习题
const viewExercise = async (exercise: ExerciseRecord) => {
    try {
        // 获取练习题详情
        const response = await axios.get(`http://localhost:8000/student/exercises/${exercise.id}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        currentExercise.value = exercise;
        currentExerciseQuestions.value = response.data.exercises || [];
        showExerciseModal.value = true;
    } catch (error) {
        console.error('获取练习题详情失败:', error);
    }
};

// 自主作答练习题
const practiceExercise = (exercise: ExerciseRecord) => {
    // 导航到作答页面，并传递练习题ID
    router.push(`/student/exercises/practice/${exercise.id}`);
};

// 关闭练习题弹窗
const closeExerciseModal = () => {
    showExerciseModal.value = false;
    currentExercise.value = null;
    currentExerciseQuestions.value = [];
};

// 处理搜索
const handleSearch = () => {
    // 搜索逻辑由计算属性处理
    console.log('搜索:', searchQuery.value);
};

// 格式化日期
const formatDate = (dateString: string | undefined) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 删除选中记录
const deleteSelected = () => {
    if (selectedItems.value.length === 0) return;
    showDeleteDialog.value = true;
};

// 确认删除
const confirmDelete = async () => {
    try {
        const response = await axios.delete(`http://localhost:8000/student/exercises/batch-delete`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            data: {
                record_ids: selectedItems.value
            }
        });

        window.$showToast('删除成功', 'success');
        selectedItems.value = [];
        showDeleteDialog.value = false;
        fetchAllData();
    } catch (error) {
        console.error('删除错误:', error);
        window.$showToast('删除失败', 'error');
    }
};

// 在组件挂载时获取数据
onMounted(() => {
    fetchAllData();
});
</script>

<style scoped>
.history-view {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.top-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}

.search-bar {
    display: flex;
    gap: 10px;
    flex: 1;
    max-width: 500px;
}

.search-bar input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.search-btn {
    padding: 8px 20px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
    }
    
    .search-btn:hover {
        background-color: #2f86c0;
    }
    
    .action-buttons {
        display: flex;
        gap: 10px;
    }
    
    .delete-btn {
        padding: 8px 20px;
        background-color: #e74c3c;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    
    .delete-btn:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
    
    .resources-list {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 20px;
        overflow-y: auto;
    }
    
    .resource-section {
        background: white;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .resource-section h3 {
        margin: 0 0 16px 0;
        font-size: 16px;
        color: #333;
    }
    
    .resource-items {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .resource-item {
        display: flex;
        align-items: center;
        padding: 12px;
        background: #f5f7fa;
        border-radius: 4px;
        transition: all 0.3s;
    }
    
    .resource-item:hover {
        background: #f0f2f5;
    }
    
    .item-checkbox {
        margin-right: 16px;
    }
    
    .item-info {
        display: flex;
        align-items: center;
        gap: 10px;
        flex: 1;
    }
    
    .sequence-number {
        font-weight: bold;
        color: #3498db;
        min-width: 40px;
    }
    
    .title {
        flex: 1;
        font-size: 14px;
        color: #333;
    }
    
    .exercise-info {
        display: flex;
        gap: 20px;
        margin-right: 20px;
    }
    
    .count {
        font-size: 14px;
        color: #666;
    }
    
    .date {
        color: #666;
        font-size: 14px;
    }
    
    .action-btns {
        display: flex;
        gap: 8px;
    }
    
    .view-btn,
    .practice-btn {
        padding: 6px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s;
        color: white;
    }
    
    .view-btn {
        background-color: #3498db;
    }
    
    .practice-btn {
        background-color: #27ae60;
    }
    
    .view-btn:hover {
        background-color: #2980b9;
    }
    
    .practice-btn:hover {
        background-color: #219653;
    }
    
    .empty-message {
        text-align: center;
        color: #999;
        padding: 20px;
    }
    
    /* 练习题详情弹窗 */
    .exercise-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .modal-content {
        background: white;
        width: 80%;
        max-width: 800px;
        max-height: 80vh;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    .modal-header {
        padding: 16px;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .modal-header h3 {
        margin: 0;
        color: #333;
    }
    
    .close-btn {
        background: none;
        border: none;
        font-size: 24px;
        color: #666;
        cursor: pointer;
    }
    
    .modal-body {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
    }
    
    .detail-header {
        margin-bottom: 20px;
    }
    
    .detail-header h4 {
        margin: 0 0 8px 0;
        color: #333;
        font-size: 18px;
    }
    
    .detail-meta {
        display: flex;
        gap: 20px;
        color: #666;
        font-size: 14px;
    }
    
    .exercises-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .exercise-item {
        padding: 16px;
        border: 1px solid #eee;
        border-radius: 4px;
        background: #f9f9f9;
    }
    
    .exercise-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .exercise-number {
        font-weight: bold;
        color: #333;
    }
    
    .exercise-type {
        background: #3498db;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    
    .exercise-content {
        margin-bottom: 16px;
        line-height: 1.5;
    }
    
    .exercise-footer {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        font-size: 14px;
    }
    
    .answer-section {
        flex: 1;
        background: #f0f2f5;
        padding: 8px;
        border-radius: 4px;
    }
    
    .difficulty {
        color: #666;
        font-size: 12px;
        margin-left: 12px;
    }
    
    .delete-dialog {
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
    
    .dialog-content {
        background-color: white;
        border-radius: 8px;
        padding: 24px;
        width: 400px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    
    .dialog-content h3 {
        margin-top: 0;
        color: #e74c3c;
    }
    
    .dialog-buttons {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: 20px;
    }
    
    .cancel-btn,
    .confirm-btn {
        padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.cancel-btn {
    background-color: #ecf0f1;
    color: #7f8c8d;
}

.confirm-btn {
    background-color: #e74c3c;
    color: white;
}
</style>