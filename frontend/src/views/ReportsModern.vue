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
          <el-button type="primary" @click="showGenerateDialog = true">
            <el-icon><Plus /></el-icon>
            Generate Report
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计和过滤器 -->
    <div class="stats-and-filters">
      <div class="reports-stats">
        <div class="stat-card">
          <div class="stat-number">{{ reports.length }}</div>
          <div class="stat-label">Total Reports</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ completedReports }}</div>
          <div class="stat-label">Completed</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ pendingReports }}</div>
          <div class="stat-label">Pending</div>
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
                <span class="info-value">{{ report.repository || 'N/A' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Created:</span>
                <span class="info-value">{{ formatRelativeTime(report.created_at) }}</span>
              </div>
              <div class="info-row" v-if="report.summary">
                <span class="info-label">Summary:</span>
                <span class="info-value summary">{{ report.summary }}</span>
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
                :label="sub.name || sub.repository" 
                :value="sub.id"
              >
                <div class="subscription-option">
                  <span class="option-name">{{ sub.name || sub.repository }}</span>
                  <span class="option-url">{{ sub.url }}</span>
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
          <div class="content-display" v-html="viewingReport.content"></div>
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
  WarningFilled
} from '@element-plus/icons-vue'
import { reportsAPI, subscriptionAPI } from '@/api'

// 响应式数据
const loading = ref(false)
const generating = ref(false)
const deleting = ref(false)
const reports = ref([])
const subscriptions = ref([])

// 对话框状态
const showGenerateDialog = ref(false)
const showDeleteDialog = ref(false)
const showViewDialog = ref(false)
const deleteTarget = ref(null)
const viewingReport = ref(null)

// 过滤器
const filterType = ref('')
const filterStatus = ref('')
const searchQuery = ref('')

// 表单数据
const generateForm = ref({
  subscriptionId: '',
  reportType: 'daily',
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
  reports.value.filter(r => r.status === 'completed').length
)

const pendingReports = computed(() => 
  reports.value.filter(r => r.status === 'pending').length
)

// 方法
const loadReports = async () => {
  loading.value = true
  try {
    const response = await reportsAPI.getReports()
    reports.value = response.data || response || []
    ElMessage.success('Reports loaded successfully')
  } catch (error) {
    console.error('Failed to load reports:', error)
    ElMessage.error('Failed to load reports')
  } finally {
    loading.value = false
  }
}

const loadSubscriptions = async () => {
  try {
    const response = await subscriptionAPI.getSubscriptions()
    subscriptions.value = response.data || response || []
  } catch (error) {
    console.error('Failed to load subscriptions:', error)
  }
}

const generateReport = async () => {
  if (!generateFormRef.value) return
  
  try {
    await generateFormRef.value.validate()
    generating.value = true
    
    await reportsAPI.generateReport(
      generateForm.value.subscriptionId, 
      generateForm.value.reportType
    )
    
    ElMessage.success('Report generation started')
    showGenerateDialog.value = false
    
    // 重置表单
    generateForm.value = {
      subscriptionId: '',
      reportType: 'daily',
      description: ''
    }
    
    // 重新加载报告列表
    setTimeout(() => {
      loadReports()
    }, 1000)
    
  } catch (error) {
    console.error('Failed to generate report:', error)
    ElMessage.error('Failed to generate report')
  } finally {
    generating.value = false
  }
}

const viewReport = (report) => {
  viewingReport.value = report
  showViewDialog.value = true
}

const downloadReport = async (report) => {
  try {
    // 这里应该调用下载API
    ElMessage.success(`Downloading report: ${report.title || `Report #${report.id}`}`)
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
    const index = reports.value.findIndex(r => r.id === deleteTarget.value?.id)
    if (index > -1) {
      reports.value.splice(index, 1)
    }
    
    deleteTarget.value = null
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

// 生命周期
onMounted(() => {
  loadReports()
  loadSubscriptions()
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
  background: var(--gray-50);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  padding: var(--space-6);
  font-family: var(--font-mono);
  font-size: 0.875rem;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
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