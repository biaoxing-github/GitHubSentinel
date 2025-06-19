<template>
  <div class="websocket-monitor">
    <div class="page-header">
      <h1>WebSocket 连接监控</h1>
      <p>实时查看WebSocket连接状态和统计信息</p>
    </div>

    <!-- 连接状态卡片 -->
    <el-row :gutter="20" class="status-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="status-card">
          <div class="status-item">
            <div class="status-icon" :class="statusClass">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="status-info">
              <h3>连接状态</h3>
              <p class="status-value" :class="statusClass">{{ statusText }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="status-card">
          <div class="status-item">
            <div class="status-icon success">
              <el-icon><MessageBox /></el-icon>
            </div>
            <div class="status-info">
              <h3>已接收消息</h3>
              <p class="status-value">{{ stats.messagesReceived }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="status-card">
          <div class="status-item">
            <div class="status-icon info">
              <el-icon><Upload /></el-icon>
            </div>
            <div class="status-info">
              <h3>已发送消息</h3>
              <p class="status-value">{{ stats.messagesSent }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="status-card">
          <div class="status-item">
            <div class="status-icon warning">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="status-info">
              <h3>运行时间</h3>
              <p class="status-value">{{ formattedUptime }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细信息区域 -->
    <el-row :gutter="20" class="detail-section">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>连接详情</span>
              <el-button 
                type="primary" 
                size="small" 
                @click="refreshStats"
                :loading="refreshing"
              >
                刷新
              </el-button>
            </div>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="连接状态">
              <el-tag :type="statusTagType">{{ statusText }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="连接时间">
              {{ formattedConnectedAt }}
            </el-descriptions-item>
            <el-descriptions-item label="重连次数">
              {{ stats.reconnectCount }}
            </el-descriptions-item>
            <el-descriptions-item label="最后心跳">
              {{ formattedLastHeartbeat }}
            </el-descriptions-item>
            <el-descriptions-item label="最后错误">
              <span v-if="stats.lastError" class="error-text">{{ stats.lastError }}</span>
              <span v-else class="success-text">无错误</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <span>订阅频道</span>
          </template>

          <div v-if="stats.subscribedChannels && stats.subscribedChannels.length > 0">
            <el-tag 
              v-for="channel in stats.subscribedChannels" 
              :key="channel"
              style="margin: 4px;"
              type="info"
            >
              {{ channel }}
            </el-tag>
          </div>
          <el-empty v-else description="暂无订阅频道" :image-size="120" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时日志 -->
    <el-card class="log-section">
      <template #header>
        <div class="card-header">
          <span>实时日志</span>
          <div>
            <el-button size="small" @click="clearLogs">清空日志</el-button>
            <el-switch 
              v-model="autoScroll"
              inactive-text="自动滚动"
              style="margin-left: 10px;"
            />
          </div>
        </div>
      </template>

      <div class="log-container" ref="logContainer">
        <div 
          v-for="(log, index) in logs" 
          :key="index"
          class="log-item"
          :class="log.type"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-type">{{ log.type.toUpperCase() }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        <div v-if="logs.length === 0" class="no-logs">
          暂无日志记录
        </div>
      </div>
    </el-card>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button 
        v-if="connectionStatus === 'disconnected'" 
        type="primary" 
        @click="reconnect"
        :loading="connecting"
      >
        重新连接
      </el-button>
      <el-button 
        v-else 
        type="danger" 
        @click="disconnect"
      >
        断开连接
      </el-button>
      
      <el-button @click="sendPing">发送心跳</el-button>
      <el-button @click="getStatus">获取状态</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection, MessageBox, Upload, Clock } from '@element-plus/icons-vue'
import { WebSocketManager } from '@/api/llm'

// 响应式数据
const connectionStatus = ref('disconnected')
const stats = reactive({
  messagesReceived: 0,
  messagesSent: 0,
  reconnectCount: 0,
  connectedAt: null,
  lastHeartbeat: null,
  subscribedChannels: [],
  uptime: 0,
  lastError: null
})

const logs = ref([])
const refreshing = ref(false)
const connecting = ref(false)
const autoScroll = ref(true)
const logContainer = ref(null)

// WebSocket管理器实例
let wsManager = null

// 计算属性
const statusClass = computed(() => {
  const statusMap = {
    'connected': 'success',
    'connecting': 'warning',
    'reconnecting': 'warning',
    'disconnected': 'error'
  }
  return statusMap[connectionStatus.value] || 'error'
})

const statusText = computed(() => {
  const textMap = {
    'connected': '已连接',
    'connecting': '连接中',
    'reconnecting': '重连中',
    'disconnected': '已断开'
  }
  return textMap[connectionStatus.value] || '未知'
})

const statusTagType = computed(() => {
  const typeMap = {
    'connected': 'success',
    'connecting': 'warning',
    'reconnecting': 'warning',
    'disconnected': 'danger'
  }
  return typeMap[connectionStatus.value] || 'danger'
})

const formattedUptime = computed(() => {
  if (!stats.uptime) return '0秒'
  
  const seconds = Math.floor(stats.uptime / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days}天 ${hours % 24}小时`
  if (hours > 0) return `${hours}小时 ${minutes % 60}分钟`
  if (minutes > 0) return `${minutes}分钟 ${seconds % 60}秒`
  return `${seconds}秒`
})

const formattedConnectedAt = computed(() => {
  return stats.connectedAt ? 
    new Date(stats.connectedAt).toLocaleString('zh-CN') : 
    '未连接'
})

const formattedLastHeartbeat = computed(() => {
  return stats.lastHeartbeat ? 
    new Date(stats.lastHeartbeat).toLocaleString('zh-CN') : 
    '无心跳'
})

// 方法
const addLog = (type, message) => {
  logs.value.unshift({
    type,
    message,
    timestamp: new Date()
  })
  
  // 限制日志数量
  if (logs.value.length > 100) {
    logs.value = logs.value.slice(0, 100)
  }
  
  // 自动滚动
  if (autoScroll.value) {
    nextTick(() => {
      if (logContainer.value) {
        logContainer.value.scrollTop = 0
      }
    })
  }
}

const formatTime = (timestamp) => {
  return timestamp.toLocaleTimeString('zh-CN')
}

const updateStats = () => {
  if (wsManager) {
    const newStats = wsManager.getConnectionStats()
    Object.assign(stats, newStats)
    connectionStatus.value = wsManager.getConnectionStatus()
  }
}

const refreshStats = async () => {
  refreshing.value = true
  try {
    updateStats()
    addLog('info', '状态信息已刷新')
  } finally {
    refreshing.value = false
  }
}

const reconnect = async () => {
  connecting.value = true
  try {
    if (wsManager) {
      // 这里应该获取实际的token
      const token = localStorage.getItem('user_token') || 'demo_token'
      wsManager.connect(token)
      addLog('info', '正在尝试重新连接...')
    }
  } finally {
    connecting.value = false
  }
}

const disconnect = () => {
  if (wsManager) {
    wsManager.disconnect()
    addLog('info', '主动断开连接')
  }
}

const sendPing = () => {
  if (wsManager) {
    wsManager.ping()
    addLog('info', '发送心跳包')
  }
}

const getStatus = () => {
  if (wsManager) {
    wsManager.getStatus()
    addLog('info', '请求状态信息')
  }
}

const clearLogs = () => {
  logs.value = []
  ElMessage.success('日志已清空')
}

// 生命周期
onMounted(() => {
  // 初始化WebSocket管理器
  wsManager = new WebSocketManager()
  
  // 监听所有事件
  wsManager.on('statusChange', (data) => {
    connectionStatus.value = data.status
    if (data.stats) {
      Object.assign(stats, data.stats)
    }
    addLog('info', `连接状态变更: ${data.status}`)
  })
  
  wsManager.on('connected', (data) => {
    addLog('success', 'WebSocket连接已建立')
    updateStats()
  })
  
  wsManager.on('disconnected', () => {
    addLog('error', 'WebSocket连接已断开')
    updateStats()
  })
  
  wsManager.on('reconnecting', (data) => {
    addLog('warning', `正在重连... (${data.attempt}/${data.maxAttempts})`)
  })
  
  wsManager.on('error', (data) => {
    addLog('error', `连接错误: ${data.error.message || data.error}`)
  })
  
  wsManager.on('message', (data) => {
    addLog('info', `收到消息: ${data.type}`)
    updateStats()
  })
  
  wsManager.on('heartbeat', () => {
    addLog('success', '心跳响应正常')
    updateStats()
  })
  
  // 定时更新统计信息
  const updateInterval = setInterval(updateStats, 1000)
  
  onUnmounted(() => {
    clearInterval(updateInterval)
    if (wsManager) {
      wsManager.clearAllListeners()
    }
  })
  
  // 初始连接
  const token = localStorage.getItem('user_token') || 'demo_token'
  if (token) {
    wsManager.connect(token)
  }
})
</script>

<style scoped>
.websocket-monitor {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.status-cards {
  margin-bottom: 20px;
}

.status-card {
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  align-items: center;
}

.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.status-icon.success {
  background-color: #67c23a;
}

.status-icon.warning {
  background-color: #e6a23c;
}

.status-icon.error {
  background-color: #f56c6c;
}

.status-icon.info {
  background-color: #409eff;
}

.status-info h3 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.status-value {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.status-value.success {
  color: #67c23a;
}

.status-value.warning {
  color: #e6a23c;
}

.status-value.error {
  color: #f56c6c;
}

.detail-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-text {
  color: #f56c6c;
}

.success-text {
  color: #67c23a;
}

.log-section {
  margin-bottom: 20px;
}

.log-container {
  height: 300px;
  overflow-y: auto;
  background-color: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-item {
  margin-bottom: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  display: flex;
  gap: 12px;
}

.log-item.success {
  background-color: #f0f9ff;
  color: #67c23a;
}

.log-item.error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.log-item.warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.log-item.info {
  background-color: #f4f4f5;
  color: #909399;
}

.log-time {
  min-width: 80px;
  font-weight: bold;
}

.log-type {
  min-width: 60px;
  font-weight: bold;
}

.log-message {
  flex: 1;
}

.no-logs {
  text-align: center;
  color: #c0c4cc;
  padding: 40px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .websocket-monitor {
    padding: 12px;
  }
  
  .status-item {
    flex-direction: column;
    text-align: center;
  }
  
  .status-icon {
    margin-right: 0;
    margin-bottom: 8px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style> 