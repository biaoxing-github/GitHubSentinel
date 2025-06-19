<template>
  <div class="reports-modern">
    <!-- 现代化页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <h1 class="page-title">Reports</h1>
          <p class="page-description">Generate and manage repository analysis reports</p>
        </div>
        <div class="header-actions">
          <el-button @click="loadReports" :loading="loading">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
          <el-button type="primary" @click="showGenerateDialog = true" :disabled="!!currentTaskId">
            <el-icon><Plus /></el-icon>
            Generate Report
          </el-button>
          <el-button type="success" @click="startQuickAnalysis" :disabled="!!currentTaskId">
            <el-icon><DataBoard /></el-icon>
            Quick Analysis
          </el-button>
        </div>
      </div>
    </div>

    <!-- 进度追踪区域 -->
    <div v-if="currentTaskId" class="progress-section">
      <ProgressTracker 
        :task-id="currentTaskId"
        :task-name="currentTaskName"
        @task-completed="onTaskCompleted"
        @task-failed="onTaskFailed"
        @retry-task="onRetryTask"
      />
    </div>

    <!-- 统计和过滤器 -->
    <div class="stats-and-filters">
      <div class="reports-stats">
        <div class="stat-card">
          <div class="stat-number">{{ totalReports }}</div>
          <div class="stat-label">Total Reports</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ completedReports }}</div>
          <div class="stat-label">Completed</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ pendingReports }}</div>
          <div class="stat-label">Generating</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ failedReports }}</div>
          <div class="stat-label">Failed</div>
        </div>
      </div>
      
      <div class="filters-section">
        <el-select v-model="filterType" placeholder="Filter by type" style="width: 150px" clearable>
          <el-option label="Daily" value="daily" />
          <el-option label="Weekly" value="weekly" />
          <el-option label="Monthly" value="monthly" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Filter by status" style="width: 150px" clearable>
          <el-option label="Completed" value="completed" />
          <el-option label="Pending" value="pending" />
          <el-option label="Failed" value="failed" />
        </el-select>
        <el-input 
          v-model="searchQuery" 
          placeholder="Search reports..." 
          style="width: 200px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 报告列表 -->
    <div class="reports-container">
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>
      
      <div v-else-if="filteredReports.length === 0" class="empty-state-modern">
        <div class="icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="title">No Reports Found</div>
        <div class="description">
          {{ reports.length === 0 ? 'Generate your first report to get started' : 'Try adjusting your filters' }}
        </div>
        <el-button v-if="reports.length === 0" type="primary" @click="showGenerateDialog = true">
          Generate First Report
        </el-button>
      </div>
      
      <div v-else class="reports-grid">
        <div v-for="report in filteredReports" :key="report.id" class="report-card-modern">
          <div class="card-header-modern">
            <div class="card-title-section">
              <h3 class="report-title">{{ report.title || `Report #${report.id}` }}</h3>
              <div class="report-meta-inline">
                <el-tag :type="getStatusTagType(report.status)" size="small">
                  {{ getStatusName(report.status) }}
                </el-tag>
                <el-tag type="info" size="small">
                  {{ getTypeName(report.report_type) }}
                </el-tag>
              </div>
            </div>
            <div class="card-actions-header">
              <el-dropdown @command="handleAction">
                <el-button text>
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="`view-${report.id}`">
                      <el-icon><View /></el-icon>
                      View Details
                    </el-dropdown-item>
                    <el-dropdown-item :command="`download-${report.id}`">
                      <el-icon><Download /></el-icon>
                      Download
                    </el-dropdown-item>
                    <el-dropdown-item :command="`delete-${report.id}`" divided>
                      <el-icon><Delete /></el-icon>
                      Delete
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
          
          <div class="card-content-modern">
            <div class="report-info">
              <div class="info-row">
                <span class="info-label">Repository:</span>
                <span class="info-value">{{ getRepositoryName(report) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Created:</span>
                <span class="info-value">{{ formatRelativeTime(report.created_at) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Period:</span>
                <span class="info-value">{{ formatPeriod(report) }}</span>
              </div>
              <div class="info-row" v-if="report.summary">
                <span class="info-label">Summary:</span>
                <span class="info-value summary">{{ report.summary }}</span>
              </div>
              <div class="info-row" v-if="report.total_activities > 0">
                <span class="info-label">Activities:</span>
                <span class="info-value">{{ report.total_activities }} activities</span>
              </div>
            </div>
          </div>
          
          <div class="card-footer-modern">
            <div class="report-stats">
              <span class="stat-item" v-if="report.file_size">
                <el-icon><Document /></el-icon>
                {{ formatFileSize(report.file_size) }}
              </span>
              <span class="stat-item">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(report.created_at) }}
              </span>
            </div>
            <div class="quick-actions">
              <el-button size="small" @click="viewReport(report)">
                <el-icon><View /></el-icon>
                View
              </el-button>
              <el-button size="small" @click="downloadReport(report)">
                <el-icon><Download /></el-icon>
                Download
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 生成报告对话框 -->
    <el-dialog 
      v-model="showGenerateDialog" 
      title="Generate New Report" 
      width="500px"
      class="modern-dialog"
    >
      <div class="dialog-content-modern">
        <el-form :model="generateForm" label-position="top" :rules="generateRules" ref="generateFormRef">
          <el-form-item label="Subscription" prop="subscriptionId">
            <el-select 
              v-model="generateForm.subscriptionId" 
              placeholder="Select a subscription" 
              style="width: 100%"
              filterable
            >
              <el-option 
                v-for="sub in subscriptions" 
                :key="sub.id" 
                :label="sub.repository" 
                :value="sub.id"
              >
                <div class="subscription-option">
                  <span class="option-name">{{ sub.repository }}</span>
                  <span class="option-url">{{ sub.repository_url || sub.repository }}</span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="Report Type" prop="reportType">
            <el-radio-group v-model="generateForm.reportType">
              <el-radio-button label="daily">Daily</el-radio-button>
              <el-radio-button label="weekly">Weekly</el-radio-button>
              <el-radio-button label="monthly">Monthly</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="Format" prop="format">
            <el-radio-group v-model="generateForm.format">
              <el-radio-button label="html">HTML</el-radio-button>
              <el-radio-button label="markdown">Markdown</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="Description" prop="description">
            <el-input 
              v-model="generateForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="Optional description for this report..."
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer-modern">
          <el-button @click="showGenerateDialog = false">Cancel</el-button>
          <el-button type="primary" @click="generateReport" :loading="generating">
            Generate Report
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog 
      v-model="showDeleteDialog" 
      title="Confirm Deletion" 
      width="400px"
      class="modern-dialog"
    >
      <div class="dialog-content-modern">
        <div class="warning-content">
          <el-icon class="warning-icon"><WarningFilled /></el-icon>
          <div class="warning-text">
            <p>Are you sure you want to delete this report?</p>
            <p class="warning-detail">
              <strong>{{ deleteTarget?.title || `Report #${deleteTarget?.id}` }}</strong>
            </p>
            <p class="warning-note">This action cannot be undone.</p>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer-modern">
          <el-button @click="showDeleteDialog = false">Cancel</el-button>
          <el-button type="danger" @click="deleteReport" :loading="deleting">
            Delete Report
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 报告查看对话框 -->
    <el-dialog 
      v-model="showViewDialog" 
      :title="viewingReport?.title || 'Report Details'" 
      width="80%" 
      top="5vh"
      class="modern-dialog report-view-dialog"
    >
      <div class="report-view-content" v-if="viewingReport">
        <div class="report-header-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Repository">
              {{ viewingReport.repository || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="Type">
              {{ getTypeName(viewingReport.report_type) }}
            </el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="getStatusTagType(viewingReport.status)">
                {{ getStatusName(viewingReport.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Created">
              {{ formatDate(viewingReport.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="report-content-section" v-if="viewingReport.content">
          <h3>Report Content</h3>
          <div class="format-toggle" style="margin-bottom: 16px;">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="rendered">Rendered</el-radio-button>
              <el-radio-button label="source">Source</el-radio-button>
            </el-radio-group>
          </div>
          
          <!-- 渲染模式 -->
          <div v-if="viewMode === 'rendered'" class="content-display">
            <!-- HTML 格式显示 -->
            <div v-if="viewingReport.format === 'html'" class="html-content">
              <iframe 
                v-if="isFullHtmlDocument(viewingReport.content)"
                :srcdoc="viewingReport.content"
                class="html-iframe"
                sandbox="allow-same-origin"
              ></iframe>
              <div v-else v-html="viewingReport.content"></div>
            </div>
            <!-- Markdown 格式渲染 -->
            <div v-else-if="viewingReport.format === 'markdown' || viewingReport.format === 'md'" 
                 class="markdown-content" 
                 v-html="renderMarkdown(viewingReport.content)">
            </div>
            <!-- 其他格式 -->
            <pre v-else class="plain-content">{{ viewingReport.content }}</pre>
          </div>
          
          <!-- 源码模式 -->
          <div v-else class="source-display">
            <pre class="source-content">{{ viewingReport.content }}</pre>
          </div>
        </div>
        
        <div v-else class="no-content">
          <el-icon><Document /></el-icon>
          <p>No content available for this report</p>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer-modern">
          <el-button @click="showViewDialog = false">Close</el-button>
          <el-button type="primary" @click="downloadReport(viewingReport)">
            <el-icon><Download /></el-icon>
            Download
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Plus,
  Search,
  Document,
  View,
  Download,
  Delete,
  MoreFilled,
  Calendar,
  WarningFilled,
  DataBoard
} from '@element-plus/icons-vue'
import api, { reportsAPI, subscriptionAPI } from '@/api'
import ProgressTracker from '@/components/ProgressTracker.vue'

// 响应式数据
const loading = ref(false)
const generating = ref(false)
const deleting = ref(false)
const reports = ref([])
const subscriptions = ref([])
const reportStats = ref({
  total_reports: 0,
  completed_reports: 0,
  generating_reports: 0,
  failed_reports: 0
})

// 对话框状态
const showGenerateDialog = ref(false)
const showDeleteDialog = ref(false)
const showViewDialog = ref(false)
const deleteTarget = ref(null)
const viewingReport = ref(null)
const viewMode = ref('rendered')

// 过滤器
const filterType = ref('')
const filterStatus = ref('')
const searchQuery = ref('')

// 进度追踪
const currentTaskId = ref('')
const currentTaskName = ref('')

// 表单数据
const generateForm = ref({
  subscriptionId: '',
  reportType: 'daily',
  format: 'html',
  description: ''
})

const generateFormRef = ref()

// 表单验证规则
const generateRules = {
  subscriptionId: [
    { required: true, message: 'Please select a subscription', trigger: 'change' }
  ],
  reportType: [
    { required: true, message: 'Please select a report type', trigger: 'change' }
  ]
}

// 计算属性
const filteredReports = computed(() => {
  let filtered = reports.value

  if (filterType.value) {
    filtered = filtered.filter(report => report.report_type === filterType.value)
  }

  if (filterStatus.value) {
    filtered = filtered.filter(report => report.status === filterStatus.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(report => 
      (report.title && report.title.toLowerCase().includes(query)) ||
      (report.repository && report.repository.toLowerCase().includes(query)) ||
      (report.summary && report.summary.toLowerCase().includes(query))
    )
  }

  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const completedReports = computed(() => 
  reportStats.value.completed_reports
)

const pendingReports = computed(() => 
  reportStats.value.generating_reports
)

const failedReports = computed(() => 
  reportStats.value.failed_reports
)

const totalReports = computed(() => 
  reportStats.value.total_reports
)

// 方法
const loadReports = async () => {
  loading.value = true
  try {
    const response = await reportsAPI.getReports()
    console.log('Reports API response:', response)
    
    // 处理不同的响应格式
    let reportsData = []
    if (response.reports) {
      // 如果响应有 reports 字段（ReportListResponse 格式）
      reportsData = response.reports
    } else if (Array.isArray(response.data)) {
      // 如果 response.data 是数组
      reportsData = response.data
    } else if (Array.isArray(response)) {
      // 如果 response 直接是数组
      reportsData = response
    }
    
    // 确保 reports 始终是数组
    reports.value = Array.isArray(reportsData) ? reportsData : []
    console.log('Processed reports:', reports.value)
    
    if (reports.value.length > 0) {
      ElMessage.success(`成功加载 ${reports.value.length} 个报告`)
    } else {
      ElMessage.info('暂无报告数据')
    }
  } catch (error) {
    console.error('Failed to load reports:', error)
    ElMessage.error('加载报告失败: ' + (error.response?.data?.detail || error.message))
    // 确保在错误情况下也是数组
    reports.value = []
  } finally {
    loading.value = false
  }
}

const loadSubscriptions = async () => {
  try {
    console.log('🔄 开始加载订阅数据...')
    const response = await subscriptionAPI.getSubscriptions()
    console.log('📦 订阅API响应:', response)
    
    // 确保 subscriptions 始终是数组
    const data = response.data || response || []
    console.log('📋 处理后的订阅数据:', data.subscriptions)
    
    subscriptions.value = Array.isArray(data.subscriptions) ? data.subscriptions : []
    console.log('✅ 订阅数据设置完成，数量:', subscriptions)
    
    if (subscriptions.value.length > 0) {
      console.log('📝 第一个订阅示例:', subscriptions.value[0])
    }
  } catch (error) {
    console.error('❌ 加载订阅失败:', error)
    // 确保在错误情况下也是数组
    subscriptions.value = []
  }
}

const loadReportStats = async () => {
  try {
    const stats = await reportsAPI.getReportStats()
    reportStats.value = stats
  } catch (error) {
    console.error('Failed to load report stats:', error)
    // 保持默认值
  }
}

const generateReport = async () => {
  if (!generateFormRef.value) return
  
  try {
    await generateFormRef.value.validate()
    generating.value = true
    
    // 获取选中的订阅信息
    const selectedSubscription = subscriptions.value.find(sub => sub.id === generateForm.value.subscriptionId)
    const repoName = selectedSubscription ? selectedSubscription.repository : 'unknown-repo'
    
    // 使用WebSocket API启动报告生成（带进度推送）
    const response = await api.post('/websocket/generate-report', {
      repo_name: repoName,
      report_type: generateForm.value.reportType
    })
    
    console.log('报告生成API响应:', response)
    
    // 设置当前任务
    const responseData = response.data || response
    currentTaskId.value = responseData.task_id
    currentTaskName.value = responseData.message || `生成报告: ${repoName} (${generateForm.value.reportType})`
    
    ElMessage.success('报告生成任务已启动，请查看进度')
    showGenerateDialog.value = false
    
    // 重置表单
    generateForm.value = {
      subscriptionId: '',
      reportType: 'daily',
      format: 'html',
      description: ''
    }
    
  } catch (error) {
    console.error('Failed to generate report:', error)
    ElMessage.error('启动报告生成失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

// 进度追踪相关函数
const startQuickAnalysis = async () => {
  try {
    const response = await api.post('/websocket/start-analysis', {
      repo_name: 'demo-repository',
      analysis_type: 'comprehensive'
    })
    
    currentTaskId.value = response.data.task_id
    currentTaskName.value = `AI分析: ${response.data.repo_name}`
    
    ElMessage.success('AI分析任务已启动')
  } catch (error) {
    console.error('启动AI分析失败:', error)
    ElMessage.error('启动AI分析失败: ' + (error.response?.data?.detail || error.message))
  }
}

const onTaskCompleted = (data) => {
  ElMessage.success('任务完成!')
  console.log('任务完成结果:', data)
  
  // 如果是报告生成任务，重新加载报告列表和统计
  if (data.report) {
    loadReports()
    loadReportStats()
    ElMessage({
      message: '报告生成完成！已添加到报告列表',
      type: 'success',
      duration: 5000
    })
  }
  
  // 如果是AI分析任务，显示分析结果
  if (data.analysis) {
    ElMessage({
      message: 'AI分析完成！请查看分析结果',
      type: 'success',
      duration: 5000
    })
  }
  
  // 清理任务状态
  setTimeout(() => {
    currentTaskId.value = ''
    currentTaskName.value = ''
  }, 3000)
}

const onTaskFailed = (message) => {
  ElMessage.error(`任务失败: ${message}`)
  // 清理任务状态
  setTimeout(() => {
    currentTaskId.value = ''
    currentTaskName.value = ''
  }, 2000)
}

const onRetryTask = async (taskId) => {
  try {
    if (taskId.startsWith('report_')) {
      // 重新启动报告生成
      const response = await api.post('/websocket/generate-report', {
        repo_name: 'demo-repository',
        report_type: 'monthly'
      })
      currentTaskId.value = response.data.task_id
      currentTaskName.value = response.data.message
    } else if (taskId.startsWith('analysis_')) {
      // 重新启动AI分析
      await startQuickAnalysis()
    }
    
    ElMessage.success('任务已重新启动')
  } catch (error) {
    ElMessage.error('重新启动任务失败: ' + (error.response?.data?.detail || error.message))
  }
}

const viewReport = (report) => {
  viewingReport.value = report
  showViewDialog.value = true
}

const downloadReport = async (report) => {
  try {
    const response = await reportsAPI.downloadReport(report.id)
    
    // 创建下载链接
    const blob = new Blob([response.data], { type: response.headers['content-type'] })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 从响应头获取文件名，或使用默认文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = `${report.title || `Report_${report.id}`}.html`
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename=(.+)/)
      if (filenameMatch) {
        filename = filenameMatch[1].replace(/"/g, '')
      }
    }
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`Report downloaded: ${filename}`)
  } catch (error) {
    console.error('Failed to download report:', error)
    ElMessage.error('Failed to download report')
  }
}

const confirmDelete = (report) => {
  deleteTarget.value = report
  showDeleteDialog.value = true
}

const deleteReport = async () => {
  if (!deleteTarget.value) return
  
  deleting.value = true
  try {
    await reportsAPI.deleteReport(deleteTarget.value.id)
    ElMessage.success('Report deleted successfully')
    showDeleteDialog.value = false
    
    // 从列表中移除
    const targetId = deleteTarget.value.id
    const index = reports.value.findIndex(r => r.id === targetId)
    if (index > -1) {
      reports.value.splice(index, 1)
    }
    
    deleteTarget.value = null
    
    // 刷新统计数据和报告列表
    await loadReportStats()
    await loadReports()
  } catch (error) {
    console.error('Failed to delete report:', error)
    ElMessage.error('Failed to delete report')
  } finally {
    deleting.value = false
  }
}

const handleAction = (command) => {
  const [action, id] = command.split('-')
  const report = reports.value.find(r => r.id === parseInt(id))
  
  if (!report) return
  
  switch (action) {
    case 'view':
      viewReport(report)
      break
    case 'download':
      downloadReport(report)
      break
    case 'delete':
      confirmDelete(report)
      break
  }
}

// 工具方法
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatRelativeTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor(diff / (1000 * 60))

  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  return 'Just now'
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

const getStatusName = (status) => {
  const statusMap = {
    completed: 'Completed',
    pending: 'Pending',
    failed: 'Failed',
    processing: 'Processing'
  }
  return statusMap[status] || 'Unknown'
}

const getStatusTagType = (status) => {
  const typeMap = {
    completed: 'success',
    pending: 'warning',
    failed: 'danger',
    processing: 'info'
  }
  return typeMap[status] || 'info'
}

const getTypeName = (type) => {
  const typeMap = {
    daily: 'Daily Report',
    weekly: 'Weekly Report',
    monthly: 'Monthly Report'
  }
  return typeMap[type] || 'Report'
}

const getRepositoryName = (report) => {
  if (report.repository) {
    return report.repository
  } else if (report.subscription) {
    return report.subscription.name || report.subscription.repository
  } else {
    return 'N/A'
  }
}

const formatPeriod = (report) => {
  if (report.report_type === 'daily') {
    return 'Daily'
  } else if (report.report_type === 'weekly') {
    return 'Weekly'
  } else if (report.report_type === 'monthly') {
    return 'Monthly'
  } else {
    return 'N/A'
  }
}

// Markdown 渲染方法
const renderMarkdown = (markdown) => {
  if (!markdown) return ''
  
  // 简单的 Markdown 渲染器
  let html = markdown
    // 标题
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    // 粗体
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    // 斜体
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    // 链接
    .replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" target="_blank">$1</a>')
    // 代码块
    .replace(/```([^`]+)```/gim, '<pre><code>$1</code></pre>')
    // 行内代码
    .replace(/`([^`]+)`/gim, '<code>$1</code>')
    // 表格
    .replace(/\|(.+)\|/gim, (match, content) => {
      const cells = content.split('|').map(cell => cell.trim())
      return '<tr>' + cells.map(cell => `<td>${cell}</td>`).join('') + '</tr>'
    })
    // 换行
    .replace(/\n/gim, '<br>')
  
  // 包装表格
  if (html.includes('<tr>')) {
    html = html.replace(/(<tr>.*<\/tr>)/gims, '<table class="markdown-table">$1</table>')
  }
  
  return html
}

const isFullHtmlDocument = (content) => {
  // 简单的判断逻辑，可以根据实际需求进行调整
  return content.includes('<!DOCTYPE html>') || content.includes('<html>') || content.includes('<body>')
}

// 生命周期
onMounted(() => {
  loadReports()
  loadSubscriptions()
  loadReportStats()
})
</script>

<style scoped>
.reports-modern {
  padding: 0;
  background: var(--bg-secondary);
  min-height: calc(100vh - 144px);
}

/* 页面头部 */
.page-header {
  background: var(--bg-card);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  margin-bottom: var(--space-8);
  overflow: hidden;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-8);
}

.header-main {
  flex: 1;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
  line-height: 1.2;
}

.page-description {
  color: var(--text-secondary);
  font-size: 1rem;
  margin: 0;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

/* 统计和过滤器 */
.stats-and-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
  gap: var(--space-6);
}

.reports-stats {
  display: flex;
  gap: var(--space-4);
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  padding: var(--space-4);
  text-align: center;
  min-width: 100px;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-600);
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: var(--space-1);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filters-section {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

/* 报告容器 */
.reports-container {
  background: var(--bg-card);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.loading-state {
  padding: var(--space-8);
}

.empty-state-modern {
  text-align: center;
  padding: var(--space-16) var(--space-8);
  color: var(--text-muted);
}

.empty-state-modern .icon {
  font-size: 4rem;
  margin-bottom: var(--space-4);
  color: var(--gray-300);
}

.empty-state-modern .title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}

.empty-state-modern .description {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: var(--space-6);
}

/* 报告网格 */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: var(--space-6);
  padding: var(--space-8);
}

.report-card-modern {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  transition: var(--transition);
}

.report-card-modern:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-6) var(--space-6) var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.card-title-section {
  flex: 1;
  min-width: 0;
}

.report-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
  line-height: 1.3;
}

.report-meta-inline {
  display: flex;
  gap: var(--space-2);
}

.card-content-modern {
  padding: var(--space-4) var(--space-6);
}

.report-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
  min-width: 80px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.875rem;
  color: var(--text-secondary);
  flex: 1;
}

.info-value.summary {
  color: var(--text-muted);
  font-style: italic;
  line-height: 1.4;
}

.card-footer-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6) var(--space-6);
  border-top: 1px solid var(--border-light);
}

.report-stats {
  display: flex;
  gap: var(--space-4);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.75rem;
  color: var(--text-muted);
}

.quick-actions {
  display: flex;
  gap: var(--space-2);
}

/* 对话框样式 */
.modern-dialog {
  .el-dialog__header {
    background: var(--bg-card);
    border-bottom: 1px solid var(--border-color);
    padding: var(--space-6);
  }

  .el-dialog__body {
    padding: 0;
  }
}

.dialog-content-modern {
  padding: var(--space-6);
}

.dialog-footer-modern {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-6);
  border-top: 1px solid var(--border-color);
  background: var(--bg-card);
}

.subscription-option {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.option-name {
  font-weight: 500;
  color: var(--text-primary);
}

.option-url {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

/* 警告内容 */
.warning-content {
  display: flex;
  gap: var(--space-4);
  align-items: flex-start;
}

.warning-icon {
  font-size: 2rem;
  color: var(--warning-color);
  flex-shrink: 0;
}

.warning-text {
  flex: 1;
}

.warning-text p {
  margin: 0 0 var(--space-2) 0;
  color: var(--text-secondary);
}

.warning-detail {
  font-family: var(--font-mono);
  background: var(--gray-100);
  padding: var(--space-2);
  border-radius: var(--border-radius-sm);
  font-size: 0.875rem;
}

.warning-note {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
}

/* 报告查看对话框 */
.report-view-dialog {
  .el-dialog__body {
    max-height: 70vh;
    overflow-y: auto;
  }
}

.report-view-content {
  padding: var(--space-6);
}

.report-header-info {
  margin-bottom: var(--space-6);
}

.report-content-section {
  margin-top: var(--space-6);
}

.report-content-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.content-display {
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 24px;
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
}

.progress-section {
  margin-bottom: var(--space-6);
}

.markdown-content {
  line-height: 1.6;
  color: var(--text-primary);
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  margin: 16px 0 8px 0;
  color: var(--text-primary);
}

.markdown-content h1 {
  font-size: 24px;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 8px;
}

.markdown-content h2 {
  font-size: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 4px;
}

.markdown-content h3 {
  font-size: 16px;
}

.markdown-content strong {
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-content em {
  font-style: italic;
  color: var(--text-secondary);
}

.markdown-content code {
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: var(--color-primary);
}

.markdown-content pre {
  background: var(--bg-tertiary);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
}

.markdown-content pre code {
  background: none;
  padding: 0;
  color: var(--text-primary);
}

.markdown-content .markdown-table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  border: 1px solid var(--border-color);
}

.markdown-content .markdown-table td {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  text-align: left;
}

.markdown-content .markdown-table tr:nth-child(even) {
  background: var(--bg-tertiary);
}

.markdown-content a {
  color: var(--color-primary);
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.source-display {
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 24px;
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
}

.source-content {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.plain-content {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  background: var(--bg-tertiary);
  padding: 16px;
  border-radius: 8px;
}

.format-toggle {
  display: flex;
  justify-content: flex-end;
}

.html-iframe {
  width: 100%;
  height: 600px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
}

.html-content {
  width: 100%;
}

.no-content {
  text-align: center;
  padding: var(--space-12);
  color: var(--text-muted);
}

.no-content .el-icon {
  font-size: 3rem;
  margin-bottom: var(--space-4);
  color: var(--gray-300);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-and-filters {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-4);
  }
  
  .reports-stats {
    justify-content: center;
  }
  
  .filters-section {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .reports-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--space-4);
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-end;
  }
  
  .reports-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-3);
  }
  
  .card-footer-modern {
    flex-direction: column;
    gap: var(--space-3);
    align-items: stretch;
  }
  
  .quick-actions {
    justify-content: center;
  }
}
</style> 