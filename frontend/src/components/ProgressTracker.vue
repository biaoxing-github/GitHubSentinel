<template>
  <div class="progress-tracker">
    <div class="progress-header">
      <div class="progress-info">
        <h3 class="progress-title">{{ taskName }}</h3>
        <p class="progress-message">{{ currentMessage }}</p>
      </div>
      <div class="progress-controls">
        <el-button 
          v-if="canCancel && status === 'running'" 
          type="danger" 
          plain 
          size="small"
          @click="cancelTask"
        >
          取消
        </el-button>
      </div>
    </div>
    
    <div class="progress-content">
      <el-progress 
        :percentage="progress" 
        :status="progressStatus"
        :show-text="true"
        :stroke-width="12"
        class="main-progress"
      >
        <template #default="{ percentage }">
          <span class="progress-text">{{ percentage }}%</span>
        </template>
      </el-progress>
      
      <div class="progress-details">
        <div class="time-info">
          <span class="start-time">开始时间: {{ formatTime(startTime) }}</span>
          <span v-if="status === 'completed'" class="end-time">
            完成时间: {{ formatTime(endTime) }}
          </span>
          <span v-else-if="estimatedTime" class="estimated-time">
            预计剩余: {{ estimatedTime }}
          </span>
        </div>
        
        <div class="status-indicator">
          <el-tag 
            :type="statusTagType"
            :icon="statusIcon"
            class="status-tag"
          >
            {{ statusText }}
          </el-tag>
        </div>
      </div>
    </div>
    
    <!-- 完成后的结果展示 -->
    <div v-if="status === 'completed' && result" class="result-section">
      <h4>任务完成</h4>
      <div class="result-content">
        <div v-if="result.report" class="report-result">
          <el-card>
            <h5>📊 报告已生成</h5>
            <p>{{ result.report.summary }}</p>
            <div class="result-stats">
              <div class="stat-item">
                <span class="stat-label">提交数:</span>
                <span class="stat-value">{{ result.report.statistics?.total_commits || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Issue数:</span>
                <span class="stat-value">{{ result.report.statistics?.total_issues || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">PR数:</span>
                <span class="stat-value">{{ result.report.statistics?.total_prs || 0 }}</span>
              </div>
            </div>
            <el-button type="primary" @click="downloadReport">
              下载报告
            </el-button>
          </el-card>
        </div>
        
        <div v-if="result.analysis" class="analysis-result">
          <el-card>
            <h5>🤖 AI分析完成</h5>
            <div class="analysis-scores">
              <div class="score-item">
                <span class="score-label">代码质量:</span>
                <el-progress 
                  :percentage="result.analysis.score?.code_quality || 0" 
                  :show-text="true"
                  :stroke-width="8"
                />
              </div>
              <div class="score-item">
                <span class="score-label">安全性:</span>
                <el-progress 
                  :percentage="result.analysis.score?.security || 0" 
                  :show-text="true"
                  :stroke-width="8"
                />
              </div>
              <div class="score-item">
                <span class="score-label">性能:</span>
                <el-progress 
                  :percentage="result.analysis.score?.performance || 0" 
                  :show-text="true"
                  :stroke-width="8"
                />
              </div>
            </div>
            <div class="recommendations">
              <h6>🎯 建议</h6>
              <ul>
                <li v-for="rec in result.analysis.recommendations" :key="rec">
                  {{ rec }}
                </li>
              </ul>
            </div>
            <el-button type="primary" @click="viewDetailedAnalysis">
              查看详细分析
            </el-button>
          </el-card>
        </div>
      </div>
    </div>
    
    <!-- 错误信息 -->
    <div v-if="status === 'failed'" class="error-section">
      <el-alert
        title="任务执行失败"
        :description="currentMessage"
        type="error"
        show-icon
        :closable="false"
      />
      <el-button type="primary" @click="retryTask" class="retry-btn">
        重试
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Loading, 
  Check, 
  Close, 
  Warning,
  Clock
} from '@element-plus/icons-vue'
import api from '@/api'

const props = defineProps({
  taskId: {
    type: String,
    required: true
  },
  taskName: {
    type: String,
    default: '任务执行中'
  },
  canCancel: {
    type: Boolean,
    default: true
  },
  autoConnect: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['progress-update', 'task-completed', 'task-failed', 'task-cancelled'])

// 状态数据
const progress = ref(0)
const status = ref('pending')
const currentMessage = ref('准备开始...')
const startTime = ref(null)
const endTime = ref(null)
const result = ref(null)
const websocket = ref(null)

// 计算属性
const progressStatus = computed(() => {
  switch (status.value) {
    case 'completed': return 'success'
    case 'failed': return 'exception'
    case 'cancelled': return 'warning'
    default: return null
  }
})

const statusTagType = computed(() => {
  switch (status.value) {
    case 'running': return 'primary'
    case 'completed': return 'success'
    case 'failed': return 'danger'
    case 'cancelled': return 'warning'
    default: return 'info'
  }
})

const statusIcon = computed(() => {
  switch (status.value) {
    case 'running': return Loading
    case 'completed': return Check
    case 'failed': return Close
    case 'cancelled': return Warning
    default: return Clock
  }
})

const statusText = computed(() => {
  switch (status.value) {
    case 'pending': return '等待中'
    case 'running': return '执行中'
    case 'completed': return '已完成'
    case 'failed': return '失败'
    case 'cancelled': return '已取消'
    default: return '未知'
  }
})

const estimatedTime = computed(() => {
  if (status.value !== 'running' || progress.value === 0) return null
  
  const elapsed = Date.now() - new Date(startTime.value).getTime()
  const rate = progress.value / elapsed
  const remaining = ((100 - progress.value) / rate) / 1000
  
  if (remaining < 60) {
    return `${Math.round(remaining)}秒`
  } else {
    return `${Math.round(remaining / 60)}分钟`
  }
})

// WebSocket连接管理
const connectWebSocket = () => {
  if (!props.autoConnect) return
  
  try {
    const wsUrl = `ws://localhost:8000/api/v1/websocket/connect?token=demo_token`
    websocket.value = new WebSocket(wsUrl)
    
    websocket.value.onopen = () => {
      console.log('WebSocket连接已建立')
    }
    
    websocket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleProgressUpdate(data)
      } catch (error) {
        console.error('解析WebSocket消息失败:', error)
      }
    }
    
    websocket.value.onclose = () => {
      console.log('WebSocket连接已关闭')
      // 3秒后重连
      setTimeout(connectWebSocket, 3000)
    }
    
    websocket.value.onerror = (error) => {
      console.error('WebSocket错误:', error)
    }
  } catch (error) {
    console.error('WebSocket连接失败:', error)
  }
}

const handleProgressUpdate = (data) => {
  if (data.type === 'progress_update' && data.task_id === props.taskId) {
    progress.value = data.progress
    status.value = data.status
    currentMessage.value = data.message
    
    if (data.status === 'running' && !startTime.value) {
      startTime.value = data.timestamp
    }
    
    if (data.status === 'completed') {
      endTime.value = data.timestamp
      result.value = data.data
      emit('task-completed', data.data)
    } else if (data.status === 'failed') {
      emit('task-failed', data.message)
    } else if (data.status === 'cancelled') {
      emit('task-cancelled')
    }
    
    emit('progress-update', data)
  }
}

// 任务操作
const cancelTask = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消当前任务吗？',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.delete(`/websocket/cancel-task/${props.taskId}`)
    ElMessage.success('任务已取消')
    
  } catch (error) {
    if (error === 'cancel') return
    console.error('取消任务失败:', error)
    ElMessage.error('取消任务失败')
  }
}

const retryTask = () => {
  // 重置状态
  progress.value = 0
  status.value = 'pending'
  currentMessage.value = '准备重试...'
  startTime.value = null
  endTime.value = null
  result.value = null
  
  // 触发重试事件
  emit('retry-task', props.taskId)
}

const downloadReport = () => {
  if (result.value?.report?.file_path) {
    window.open(result.value.report.file_path, '_blank')
  }
}

const viewDetailedAnalysis = () => {
  if (result.value?.analysis?.detailed_report_url) {
    window.open(result.value.analysis.detailed_report_url, '_blank')
  }
}

// 工具函数
const formatTime = (timeString) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (websocket.value) {
    websocket.value.close()
  }
})

// 监听taskId变化
watch(() => props.taskId, (newTaskId) => {
  if (newTaskId) {
    // 重置状态
    progress.value = 0
    status.value = 'pending'
    currentMessage.value = '准备开始...'
    startTime.value = null
    endTime.value = null
    result.value = null
  }
})
</script>

<style scoped>
.progress-tracker {
  background: var(--bg-card);
  border-radius: var(--border-radius);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-4);
}

.progress-info {
  flex: 1;
}

.progress-title {
  margin: 0 0 var(--space-2) 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 600;
}

.progress-message {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.progress-content {
  margin-bottom: var(--space-4);
}

.main-progress {
  margin-bottom: var(--space-4);
}

.progress-text {
  font-weight: 600;
  color: var(--text-primary);
}

.progress-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
}

.time-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.status-tag {
  font-weight: 500;
}

.result-section {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-color);
}

.result-section h4 {
  margin: 0 0 var(--space-3) 0;
  color: var(--text-primary);
}

.result-stats {
  display: flex;
  gap: var(--space-4);
  margin: var(--space-3) 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary-500);
}

.analysis-scores {
  margin: var(--space-3) 0;
}

.score-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.score-label {
  min-width: 80px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.recommendations {
  margin-top: var(--space-3);
}

.recommendations h6 {
  margin: 0 0 var(--space-2) 0;
  color: var(--text-primary);
}

.recommendations ul {
  margin: 0;
  padding-left: var(--space-4);
}

.recommendations li {
  margin-bottom: var(--space-1);
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.error-section {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-color);
}

.retry-btn {
  margin-top: var(--space-3);
}

@media (max-width: 768px) {
  .progress-header {
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .progress-details {
    flex-direction: column;
    gap: var(--space-2);
    align-items: flex-start;
  }
  
  .result-stats {
    flex-direction: column;
    gap: var(--space-2);
  }
}
</style> 