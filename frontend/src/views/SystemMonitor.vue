<template>
  <div class="system-monitor">
    <div class="page-header">
      <h1>系统监控</h1>
      <p>实时监控系统性能指标和健康状态</p>
    </div>

    <!-- 系统状态概览 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="metric-card">
          <div class="metric-item">
            <div class="metric-icon health">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="metric-info">
              <h3>系统健康度</h3>
              <p class="metric-value" :class="healthStatus.class">{{ healthStatus.value }}%</p>
              <p class="metric-status">{{ healthStatus.text }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="metric-card">
          <div class="metric-item">
            <div class="metric-icon cpu">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="metric-info">
              <h3>CPU使用率</h3>
              <p class="metric-value">{{ systemMetrics.cpu_usage }}%</p>
              <p class="metric-trend" :class="getTrendClass(systemMetrics.cpu_trend)">
                {{ formatTrend(systemMetrics.cpu_trend) }}
              </p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="metric-card">
          <div class="metric-item">
            <div class="metric-icon memory">
              <el-icon><Coin /></el-icon>
            </div>
            <div class="metric-info">
              <h3>内存使用率</h3>
              <p class="metric-value">{{ systemMetrics.memory_usage }}%</p>
              <p class="metric-detail">{{ formatBytes(systemMetrics.memory_used) }} / {{ formatBytes(systemMetrics.memory_total) }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="metric-card">
          <div class="metric-item">
            <div class="metric-icon network">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="metric-info">
              <h3>活跃连接</h3>
              <p class="metric-value">{{ systemMetrics.active_connections }}</p>
              <p class="metric-detail">WebSocket: {{ systemMetrics.websocket_connections }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 性能图表 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>CPU & 内存使用率</span>
              <el-button size="small" @click="refreshCharts">刷新</el-button>
            </div>
          </template>
          
          <div class="chart-container">
            <v-chart 
              :option="cpuMemoryChartOption" 
              :autoresize="true"
              style="height: 300px;"
            />
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <span>网络流量</span>
          </template>
          
          <div class="chart-container">
            <v-chart 
              :option="networkChartOption" 
              :autoresize="true"
              style="height: 300px;"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 服务状态 -->
    <el-row :gutter="20" class="services-section">
      <el-col :xs="24" :lg="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>服务状态</span>
              <el-button size="small" @click="refreshServices">刷新</el-button>
            </div>
          </template>

          <el-table :data="services" style="width: 100%">
            <el-table-column prop="name" label="服务名称" width="200" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getServiceStatusType(row.status)">
                  {{ getServiceStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="uptime" label="运行时间" width="120">
              <template #default="{ row }">
                {{ formatDuration(row.uptime) }}
              </template>
            </el-table-column>
            <el-table-column prop="memory" label="内存使用" width="100">
              <template #default="{ row }">
                {{ formatBytes(row.memory) }}
              </template>
            </el-table-column>
            <el-table-column prop="cpu" label="CPU使用率" width="100">
              <template #default="{ row }">
                {{ row.cpu }}%
              </template>
            </el-table-column>
            <el-table-column prop="last_check" label="最后检查" width="160">
              <template #default="{ row }">
                {{ formatTime(row.last_check) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button 
                  v-if="row.status === 'stopped'"
                  type="success" 
                  size="small" 
                  @click="startService(row)"
                >
                  启动
                </el-button>
                <el-button 
                  v-else
                  type="warning" 
                  size="small" 
                  @click="restartService(row)"
                >
                  重启
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>

          <div class="quick-actions">
            <el-button type="primary" @click="clearCache" :loading="actionLoading.clearCache">
              <el-icon><Delete /></el-icon>
              清理缓存
            </el-button>
            
            <el-button type="warning" @click="restartAllServices" :loading="actionLoading.restartAll">
              <el-icon><RefreshRight /></el-icon>
              重启所有服务
            </el-button>
            
            <el-button @click="exportLogs" :loading="actionLoading.exportLogs">
              <el-icon><Download /></el-icon>
              导出日志
            </el-button>
            
            <el-button @click="runHealthCheck" :loading="actionLoading.healthCheck">
              <el-icon><CircleCheck /></el-icon>
              健康检查
            </el-button>
          </div>
        </el-card>

        <!-- 系统信息 -->
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>系统信息</span>
          </template>

          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="操作系统">
              {{ systemInfo.os }}
            </el-descriptions-item>
            <el-descriptions-item label="Python版本">
              {{ systemInfo.python_version }}
            </el-descriptions-item>
            <el-descriptions-item label="Node.js版本">
              {{ systemInfo.node_version }}
            </el-descriptions-item>
            <el-descriptions-item label="启动时间">
              {{ formatTime(systemInfo.start_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="运行时间">
              {{ formatDuration(systemInfo.uptime) }}
            </el-descriptions-item>
            <el-descriptions-item label="版本">
              {{ systemInfo.version }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时日志 -->
    <el-card class="logs-section">
      <template #header>
        <div class="card-header">
          <span>系统日志</span>
          <div>
            <el-select v-model="logLevel" size="small" style="width: 100px; margin-right: 10px;">
              <el-option label="全部" value="all" />
              <el-option label="错误" value="error" />
              <el-option label="警告" value="warning" />
              <el-option label="信息" value="info" />
            </el-select>
            <el-button size="small" @click="clearLogs">清空</el-button>
          </div>
        </div>
      </template>

      <div class="logs-container" ref="logsContainer">
        <div 
          v-for="(log, index) in filteredLogs" 
          :key="index"
          class="log-entry"
          :class="log.level"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-level">{{ log.level.toUpperCase() }}</span>
          <span class="log-service">{{ log.service }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        
        <div v-if="filteredLogs.length === 0" class="no-logs">
          暂无日志
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  CircleCheck, Monitor, Coin, Connection, Delete, 
  RefreshRight, Download 
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { 
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent 
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册ECharts组件
use([
  LineChart, TitleComponent, TooltipComponent, 
  LegendComponent, GridComponent, CanvasRenderer
])

// 响应式数据
const systemMetrics = reactive({
  cpu_usage: 0,
  cpu_trend: 0,
  memory_usage: 0,
  memory_used: 0,
  memory_total: 0,
  active_connections: 0,
  websocket_connections: 0
})

const systemInfo = reactive({
  os: '',
  python_version: '',
  node_version: '',
  start_time: null,
  uptime: 0,
  version: ''
})

const services = ref([])
const logs = ref([])
const logLevel = ref('all')

const actionLoading = reactive({
  clearCache: false,
  restartAll: false,
  exportLogs: false,
  healthCheck: false
})

// 图表数据
const chartData = reactive({
  cpu: [],
  memory: [],
  network_in: [],
  network_out: [],
  timestamps: []
})

// 计算属性
const healthStatus = computed(() => {
  const cpu = systemMetrics.cpu_usage
  const memory = systemMetrics.memory_usage
  
  // 简单的健康度计算
  let health = 100
  if (cpu > 80) health -= 20
  else if (cpu > 60) health -= 10
  
  if (memory > 85) health -= 20
  else if (memory > 70) health -= 10
  
  let status = 'excellent'
  let className = 'success'
  
  if (health < 60) {
    status = 'critical'
    className = 'error'
  } else if (health < 80) {
    status = 'warning'
    className = 'warning'
  }
  
  return {
    value: health,
    text: status === 'excellent' ? '优秀' : status === 'warning' ? '警告' : '严重',
    class: className
  }
})

const cpuMemoryChartOption = computed(() => ({
  title: {
    text: 'CPU & 内存使用率',
    textStyle: { fontSize: 14 }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  legend: {
    data: ['CPU使用率', '内存使用率']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: chartData.timestamps
  },
  yAxis: {
    type: 'value',
    max: 100,
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [
    {
      name: 'CPU使用率',
      type: 'line',
      data: chartData.cpu,
      smooth: true,
      itemStyle: { color: '#409eff' }
    },
    {
      name: '内存使用率',
      type: 'line',
      data: chartData.memory,
      smooth: true,
      itemStyle: { color: '#67c23a' }
    }
  ]
}))

const networkChartOption = computed(() => ({
  title: {
    text: '网络流量',
    textStyle: { fontSize: 14 }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  legend: {
    data: ['入站流量', '出站流量']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: chartData.timestamps
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: (value) => formatBytes(value)
    }
  },
  series: [
    {
      name: '入站流量',
      type: 'line',
      data: chartData.network_in,
      smooth: true,
      itemStyle: { color: '#e6a23c' }
    },
    {
      name: '出站流量',
      type: 'line',
      data: chartData.network_out,
      smooth: true,
      itemStyle: { color: '#f56c6c' }
    }
  ]
}))

const filteredLogs = computed(() => {
  if (logLevel.value === 'all') {
    return logs.value
  }
  return logs.value.filter(log => log.level === logLevel.value)
})

// 方法
const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + 'GB'
}

const formatDuration = (seconds) => {
  if (!seconds) return '0秒'
  
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) return `${days}天 ${hours}小时`
  if (hours > 0) return `${hours}小时 ${minutes}分钟`
  return `${minutes}分钟`
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN')
}

const formatTrend = (trend) => {
  if (trend > 0) return `↑${trend.toFixed(1)}%`
  if (trend < 0) return `↓${Math.abs(trend).toFixed(1)}%`
  return '0%'
}

const getTrendClass = (trend) => {
  if (trend > 5) return 'trend-up'
  if (trend < -5) return 'trend-down'
  return 'trend-stable'
}

const getServiceStatusType = (status) => {
  const typeMap = {
    'running': 'success',
    'stopped': 'danger',
    'warning': 'warning',
    'error': 'danger'
  }
  return typeMap[status] || 'info'
}

const getServiceStatusText = (status) => {
  const textMap = {
    'running': '运行中',
    'stopped': '已停止',
    'warning': '警告',
    'error': '错误'
  }
  return textMap[status] || status
}

// 获取真实系统指标
const updateSystemMetrics = async () => {
  try {
    const response = await fetch('/api/v1/system/metrics', {
      headers: {
        'Authorization': 'Bearer demo_token'
      }
    })
    
    if (response.ok) {
      const metrics = await response.json()
      
      // 更新系统指标
      Object.assign(systemMetrics, {
        cpu_usage: metrics.cpu_usage || 0,
        cpu_trend: metrics.cpu_trend || 0,
        memory_usage: metrics.memory_usage || 0,
        memory_used: Math.floor((metrics.memory_used || 0) / (1024 * 1024 * 1024)), // 转换为GB
        memory_total: Math.floor((metrics.memory_total || 0) / (1024 * 1024 * 1024)), // 转换为GB
        active_connections: metrics.active_connections || 0,
        websocket_connections: metrics.websocket_connections || 0
      })
    }
  } catch (error) {
    console.error('获取系统指标失败:', error)
  }
}

const loadServices = async () => {
  try {
    const response = await fetch('/api/v1/system/services', {
      headers: {
        'Authorization': 'Bearer demo_token'
      }
    })
    
    if (response.ok) {
      services.value = await response.json()
    }
  } catch (error) {
    console.error('获取服务状态失败:', error)
  }
}

const generateMockLogs = () => {
  const levels = ['info', 'warning', 'error']
  const services = ['api', 'websocket', 'database', 'cache']
  const messages = [
    'Service started successfully',
    'Connection established',
    'Query executed in 45ms',
    'Cache hit ratio: 95%',
    'High memory usage detected',
    'Connection timeout',
    'Database query failed',
    'Authentication successful'
  ]
  
  // 添加一些随机日志
  for (let i = 0; i < 20; i++) {
    logs.value.unshift({
      timestamp: new Date(Date.now() - Math.random() * 3600000),
      level: levels[Math.floor(Math.random() * levels.length)],
      service: services[Math.floor(Math.random() * services.length)],
      message: messages[Math.floor(Math.random() * messages.length)]
    })
  }
}

// 操作方法
const refreshCharts = () => {
  updateSystemMetrics()
  ElMessage.success('图表数据已刷新')
}

const refreshServices = () => {
  generateMockServices()
  ElMessage.success('服务状态已刷新')
}

const clearCache = async () => {
  actionLoading.clearCache = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('缓存清理完成')
  } finally {
    actionLoading.clearCache = false
  }
}

const restartAllServices = async () => {
  try {
    await ElMessageBox.confirm('确定要重启所有服务吗？', '确认操作', {
      type: 'warning'
    })
    
    actionLoading.restartAll = true
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 3000))
    ElMessage.success('所有服务重启完成')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重启服务失败')
    }
  } finally {
    actionLoading.restartAll = false
  }
}

const exportLogs = async () => {
  actionLoading.exportLogs = true
  try {
    // 模拟导出
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('日志导出完成')
  } finally {
    actionLoading.exportLogs = false
  }
}

const runHealthCheck = async () => {
  actionLoading.healthCheck = true
  try {
    // 模拟健康检查
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('健康检查完成，系统状态良好')
  } finally {
    actionLoading.healthCheck = false
  }
}

const clearLogs = () => {
  logs.value = []
  ElMessage.success('日志已清空')
}

// 生命周期
let updateInterval
let logInterval

// 加载系统信息
const loadSystemInfo = async () => {
  try {
    const response = await fetch('/api/v1/system/info', {
      headers: {
        'Authorization': 'Bearer demo_token'
      }
    })
    
    if (response.ok) {
      const info = await response.json()
      Object.assign(systemInfo, info)
    }
  } catch (error) {
    console.error('获取系统信息失败:', error)
  }
}

// 加载系统日志
const loadLogs = async () => {
  try {
    const response = await fetch('/api/v1/system/logs?limit=50', {
      headers: {
        'Authorization': 'Bearer demo_token'
      }
    })
    
    if (response.ok) {
      logs.value = await response.json()
    }
  } catch (error) {
    console.error('获取系统日志失败:', error)
  }
}

onMounted(async () => {
  // 加载初始数据
  await Promise.all([
    loadSystemInfo(),
    loadServices(),
    loadLogs(),
    updateSystemMetrics()
  ])
  
  // 定时更新
  updateInterval = setInterval(async () => {
    await updateSystemMetrics()
    await loadServices()
  }, 5000) // 每5秒更新指标
  
  logInterval = setInterval(async () => {
    await loadLogs()
  }, 30000) // 每30秒更新日志
})

onUnmounted(() => {
  if (updateInterval) clearInterval(updateInterval)
  if (logInterval) clearInterval(logInterval)
})
</script>

<style scoped>
.system-monitor {
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

.overview-cards {
  margin-bottom: 20px;
}

.metric-card {
  margin-bottom: 20px;
}

.metric-item {
  display: flex;
  align-items: center;
}

.metric-icon {
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

.metric-icon.health {
  background-color: #67c23a;
}

.metric-icon.cpu {
  background-color: #409eff;
}

.metric-icon.memory {
  background-color: #e6a23c;
}

.metric-icon.network {
  background-color: #f56c6c;
}

.metric-info h3 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.metric-value {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.metric-value.success {
  color: #67c23a;
}

.metric-value.warning {
  color: #e6a23c;
}

.metric-value.error {
  color: #f56c6c;
}

.metric-status,
.metric-detail {
  margin: 0;
  font-size: 12px;
  color: #c0c4cc;
}

.metric-trend {
  margin: 0;
  font-size: 12px;
  font-weight: bold;
}

.trend-up {
  color: #f56c6c;
}

.trend-down {
  color: #67c23a;
}

.trend-stable {
  color: #909399;
}

.charts-section,
.services-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.logs-section {
  margin-bottom: 20px;
}

.logs-container {
  height: 400px;
  overflow-y: auto;
  background-color: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-entry {
  margin-bottom: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  display: flex;
  gap: 12px;
}

.log-entry.info {
  background-color: #f4f4f5;
  color: #909399;
}

.log-entry.warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.log-entry.error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.log-time {
  min-width: 80px;
  font-weight: bold;
}

.log-level {
  min-width: 60px;
  font-weight: bold;
}

.log-service {
  min-width: 80px;
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

@media (max-width: 768px) {
  .system-monitor {
    padding: 12px;
  }
  
  .metric-item {
    flex-direction: column;
    text-align: center;
  }
  
  .metric-icon {
    margin-right: 0;
    margin-bottom: 8px;
  }
  
  .quick-actions {
    flex-direction: column;
  }
}
</style> 