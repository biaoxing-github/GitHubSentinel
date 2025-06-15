<template>
  <div class="dashboard-modern">
    <!-- 现代化页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <h1 class="page-title">Dashboard</h1>
          <p class="page-description">Monitor your GitHub repositories and track system performance</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
          <el-button @click="exportData">
            <el-icon><Download /></el-icon>
            Export
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片网格 -->
    <div class="stats-grid">
      <div 
        v-for="stat in stats" 
        :key="stat.key" 
        class="stats-card-modern"
        :class="`stats-${stat.key}`"
      >
        <div class="stats-header">
          <div class="stats-icon" :style="{ background: stat.color }">
            <el-icon>
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stats-trend" :class="stat.trend > 0 ? 'positive' : 'negative'">
            <el-icon>
              <component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" />
            </el-icon>
            <span>{{ Math.abs(stat.trend) }}%</span>
          </div>
        </div>
        <div class="stats-content">
          <div class="stats-number-modern">{{ stat.value }}</div>
          <div class="stats-label-modern">{{ stat.label }}</div>
        </div>
        <div class="stats-footer">
          <div class="progress-modern">
            <div 
              class="progress-bar-modern" 
              :style="{ 
                width: stat.progress + '%',
                background: stat.color 
              }"
            ></div>
          </div>
          <span class="stats-subtitle">{{ stat.subtitle }}</span>
        </div>
      </div>
    </div>

    <!-- 主要内容网格 -->
    <div class="content-grid">
      <!-- 活动监控面板 -->
      <div class="panel-modern activity-panel">
        <div class="panel-header-modern">
          <div class="panel-title">
            <el-icon><TrendCharts /></el-icon>
            <h3>Recent Activity</h3>
          </div>
          <div class="panel-actions">
            <el-button size="small" text @click="viewAllActivities">
              View All
            </el-button>
          </div>
        </div>
        <div class="panel-content-modern">
          <!-- 筛选器 -->
          <div class="activity-filters">
            <el-select 
              v-model="selectedRepository" 
              placeholder="All Repositories"
              size="small"
              style="width: 150px"
              @change="onRepositoryChange"
              clearable
            >
              <el-option label="All Repositories" value="" />
              <el-option 
                v-for="repo in repositories" 
                :key="repo" 
                :label="repo" 
                :value="repo" 
              />
            </el-select>
            
            <el-select 
              v-model="selectedActivityType" 
              placeholder="Activity Type"
              size="small"
              style="width: 120px"
              @change="onActivityTypeChange"
              clearable
            >
              <el-option label="All" value="" />
              <el-option label="Issues" value="issue" />
              <el-option label="PRs" value="pull_request" />
              <el-option label="Commits" value="commit" />
            </el-select>

            <el-select 
              v-model="selectedTimePeriod" 
              placeholder="Time Period"
              size="small"
              style="width: 100px"
              @change="onTimePeriodChange"
            >
              <el-option label="1 Day" :value="1" />
              <el-option label="3 Days" :value="3" />
              <el-option label="7 Days" :value="7" />
              <el-option label="All" :value="0" />
            </el-select>
          </div>
          
          <div class="activity-timeline">
            <div 
              v-for="activity in displayedActivities" 
              :key="activity.id" 
              class="activity-item-modern"
            >
              <div class="activity-indicator" :class="`activity-${activity.type}`">
                <el-icon>
                  <component :is="getActivityIcon(activity.type)" />
                </el-icon>
              </div>
              <div class="activity-content">
                <div class="activity-header">
                  <span class="activity-title">{{ activity.title }}</span>
                  <span class="activity-time">{{ formatRelativeTime(activity.time) }}</span>
                </div>
                <p class="activity-description">{{ activity.description }}</p>
                <div class="activity-meta">
                  <span class="activity-repo">{{ activity.repository }}</span>
                  <el-tag 
                    :type="getActivityTagType(activity.type)" 
                    size="small"
                  >
                    {{ activity.tag || activity.type }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <div v-if="filteredActivities.length === 0" class="no-activities">
              <el-icon><Document /></el-icon>
              <span>No activities found</span>
            </div>
            
            <div v-if="filteredActivities.length > 5" class="view-more">
              <el-button size="small" text @click="viewAllActivities">
                View {{ filteredActivities.length - 5 }} more activities
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统状态面板 -->
      <div class="panel-modern status-panel">
        <div class="panel-header-modern">
          <div class="panel-title">
            <el-icon><Monitor /></el-icon>
            <h3>System Status</h3>
          </div>
          <div class="status-indicator" :class="systemStatus.overall === 'All Systems Operational' ? 'online' : 'issues'">
            <span class="status-dot"></span>
            {{ systemStatus.overall }}
          </div>
        </div>
        <div class="panel-content-modern">
          <div class="status-list">
            <div 
              v-for="service in systemServices" 
              :key="service.name" 
              class="status-item"
            >
              <div class="service-info">
                <div class="service-name">{{ service.name }}</div>
                <div class="service-description">{{ service.description }}</div>
              </div>
              <div class="service-status" :class="service.status">
                <span class="status-text">{{ service.statusText }}</span>
                <div class="status-badge" :class="service.status"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速操作面板 -->
      <div class="panel-modern actions-panel">
        <div class="panel-header-modern">
          <div class="panel-title">
            <el-icon><Operation /></el-icon>
            <h3>Quick Actions</h3>
          </div>
        </div>
        <div class="panel-content-modern">
          <div class="actions-grid">
            <button 
              v-for="action in quickActions" 
              :key="action.id"
              class="action-card"
              :class="`action-${action.type}`"
              @click="handleQuickAction(action)"
            >
              <div class="action-icon">
                <el-icon>
                  <component :is="getActionIcon(action.icon)" />
                </el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">{{ action.title }}</div>
                <div class="action-description">{{ action.description }}</div>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- 性能图表面板 -->
      <div class="panel-modern chart-panel">
        <div class="panel-header-modern">
          <div class="panel-title">
            <el-icon><DataAnalysis /></el-icon>
            <h3>Performance Metrics</h3>
          </div>
          <div class="panel-actions">
            <el-select v-model="chartPeriod" size="small" style="width: 120px">
              <el-option label="Last 7 days" value="7d" />
              <el-option label="Last 30 days" value="30d" />
              <el-option label="Last 90 days" value="90d" />
            </el-select>
          </div>
        </div>
        <div class="panel-content-modern">
          <div class="chart-container">
            <div class="chart-placeholder">
              <el-icon><TrendCharts /></el-icon>
              <p>Performance chart will be displayed here</p>
              <el-button size="small" type="primary">View Details</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  Refresh,
  Download,
  TrendCharts,
  Monitor,
  Operation,
  DataAnalysis,
  ArrowUp,
  ArrowDown,
  FolderOpened,
  Search,
  Document,
  Warning,
  Plus,
  DocumentAdd,
  MoreFilled
} from '@element-plus/icons-vue'
import dashboardAPI from '@/api/dashboard'
import { formatRelativeTime } from '@/utils/time'

// 响应式数据
const loading = ref(false)
const dashboardStats = ref({
  repositories: 0,
  repositories_trend: 0,
  active_scans: 0,
  active_scans_trend: 0,
  reports_generated: 0,
  reports_generated_trend: 0,
  active_alerts: 0,
  active_alerts_trend: 0
})
const recentActivities = ref([])
const systemStatus = ref({
  overall: 'Loading...',
  services: {}
})
const quickActions = ref([])
const performanceMetrics = ref({
  response_time: 0,
  success_rate: 0,
  activity_count: 0,
  active_repositories: 0,
  health_score: 0
})

// 筛选相关数据
const selectedRepository = ref('')
const selectedActivityType = ref('issue') // 默认选择issue
const selectedTimePeriod = ref(7) // 默认7天
const repositories = ref([])
const chartPeriod = ref('7d')

// 计算属性 - 筛选后的活动
const filteredActivities = computed(() => {
  let filtered = recentActivities.value

  // 按时间周期筛选
  if (selectedTimePeriod.value > 0) {
    const cutoffTime = new Date()
    cutoffTime.setDate(cutoffTime.getDate() - selectedTimePeriod.value)
    filtered = filtered.filter(activity => {
      const activityTime = new Date(activity.time)
      return activityTime >= cutoffTime
    })
  }

  // 按仓库筛选
  if (selectedRepository.value) {
    filtered = filtered.filter(activity => 
      activity.repository === selectedRepository.value
    )
  }

  // 按活动类型筛选
  if (selectedActivityType.value) {
    filtered = filtered.filter(activity => 
      activity.type === selectedActivityType.value
    )
  }

  return filtered
})

// 计算属性 - 显示的活动（最多5条）
const displayedActivities = computed(() => {
  return filteredActivities.value.slice(0, 5)
})

// 计算属性 - 将API数据转换为组件需要的格式
const stats = computed(() => [
  {
    key: 'repositories',
    label: 'Repositories',
    value: dashboardStats.value.repositories,
    trend: dashboardStats.value.repositories_trend,
    icon: 'FolderOpened',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    progress: 75,
    subtitle: 'Total monitored'
  },
  {
    key: 'active_scans',
    label: 'Active Scans',
    value: dashboardStats.value.active_scans,
    trend: dashboardStats.value.active_scans_trend,
    icon: 'Search',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    progress: 60,
    subtitle: 'Currently running'
  },
  {
    key: 'reports_generated',
    label: 'Reports Generated',
    value: dashboardStats.value.reports_generated,
    trend: dashboardStats.value.reports_generated_trend,
    icon: 'Document',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    progress: 85,
    subtitle: 'This month'
  },
  {
    key: 'active_alerts',
    label: 'Active Alerts',
    value: dashboardStats.value.active_alerts,
    trend: dashboardStats.value.active_alerts_trend,
    icon: 'Warning',
    color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    progress: 30,
    subtitle: 'Need attention'
  }
])

// 计算属性 - 处理系统状态数据
const systemServices = computed(() => {
  if (!systemStatus.value.services) return []
  
  return Object.values(systemStatus.value.services).map(service => ({
    name: service.name,
    description: service.description,
    status: service.status,
    statusText: service.status === 'operational' ? 'Operational' : 
                service.status === 'degraded' ? 'Degraded' : 'Down',
    lastCheck: service.last_check
  }))
})

// 方法
const loadDashboardData = async () => {
  loading.value = true
  try {
    console.log('🔄 开始加载Dashboard数据...')
    
    // 并行加载所有数据
    const [statsData, activityData, statusData, actionsData, performanceData] = await Promise.all([
      dashboardAPI.getDashboardStats(),
      dashboardAPI.getRecentActivity(selectedTimePeriod.value),
      dashboardAPI.getSystemStatus(),
      dashboardAPI.getQuickActions(),
      dashboardAPI.getPerformanceMetrics(chartPeriod.value)
    ])

    console.log('📊 Stats数据:', statsData)
    console.log('📋 Activity数据:', activityData)
    console.log('🔧 Status数据:', statusData)
    console.log('⚡ Actions数据:', actionsData)
    console.log('📊 Performance数据:', performanceData)

    dashboardStats.value = statsData
    recentActivities.value = activityData
    systemStatus.value = statusData
    quickActions.value = actionsData
    performanceMetrics.value = performanceData

    // 提取仓库列表并设置默认选择
    const repoSet = new Set()
    activityData.forEach(activity => {
      if (activity.repository && activity.repository !== 'N/A') {
        repoSet.add(activity.repository)
      }
    })
    repositories.value = Array.from(repoSet).sort()
    
    // 默认选择第一个仓库
    if (repositories.value.length > 0 && !selectedRepository.value) {
      selectedRepository.value = repositories.value[0]
    }

    console.log('✅ Dashboard数据加载完成')
    console.log('Recent Activities:', recentActivities.value)
    console.log('System Status:', systemStatus.value)
    console.log('Quick Actions:', quickActions.value)
    console.log('📁 仓库列表:', repositories.value)
    console.log('🎯 默认选择仓库:', selectedRepository.value)

    ElMessage.success('Dashboard data loaded successfully')
  } catch (error) {
    console.error('💥 Failed to load dashboard data:', error)
    ElMessage.error('Failed to load dashboard data: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await loadDashboardData()
}

const handleQuickAction = (action) => {
  // 这里可以根据 action.action 进行路由跳转或其他操作
  ElMessage.info(`Quick action: ${action.title}`)
}

// 生命周期
onMounted(() => {
  loadDashboardData()
})

// 工具方法
const getActivityIcon = (type) => {
  const iconMap = {
    'report': Document,
    'subscription': Plus,
    'commit': DocumentAdd,
    'issue': Warning,
    'pull_request': DocumentAdd,
    'pr': DocumentAdd
  }
  return iconMap[type] || Document
}

const getActivityTagType = (type) => {
  const typeMap = {
    'report': 'primary',
    'subscription': 'success',
    'commit': 'info',
    'issue': 'warning',
    'pull_request': 'primary',
    'pr': 'primary'
  }
  return typeMap[type] || 'info'
}

const getStatusColor = (status) => {
  const colorMap = {
    'operational': '#67C23A',
    'degraded': '#E6A23C',
    'down': '#F56C6C'
  }
  return colorMap[status] || '#909399'
}

const getActionIcon = (iconName) => {
  const iconMap = {
    'WarningFilled': Warning,
    'Setting': MoreFilled,
    'DocumentAdd': DocumentAdd,
    'Plus': Plus
  }
  return iconMap[iconName] || DocumentAdd
}

// 筛选方法
const onRepositoryChange = () => {
  console.log('🔄 仓库筛选变更:', selectedRepository.value)
}

const onActivityTypeChange = () => {
  console.log('🔄 活动类型筛选变更:', selectedActivityType.value)
}

// 查看所有活动
const router = useRouter()

const viewAllActivities = () => {
  // 跳转到Activities页面
  router.push('/activities')
}

const executeAction = (actionKey) => {
  ElMessage.info(`Execute action: ${actionKey}`)
}

const exportData = () => {
  ElMessage.info('Export data')
}

const onTimePeriodChange = async () => {
  console.log('🔄 时间周期筛选变更:', selectedTimePeriod.value)
  try {
    const activityData = await dashboardAPI.getRecentActivity(selectedTimePeriod.value)
    recentActivities.value = activityData
    
    // 重新提取仓库列表
    const repoSet = new Set()
    activityData.forEach(activity => {
      if (activity.repository && activity.repository !== 'N/A') {
        repoSet.add(activity.repository)
      }
    })
    repositories.value = Array.from(repoSet).sort()
    
    console.log('✅ 活动数据重新加载完成')
  } catch (error) {
    console.error('💥 重新加载活动数据失败:', error)
    ElMessage.error('Failed to reload activity data')
  }
}
</script>

<style scoped>
.dashboard-modern {
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

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.stats-card-modern {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.stats-card-modern:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.stats-trend {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.875rem;
  font-weight: 600;
}

.stats-trend.positive {
  color: var(--success-color);
}

.stats-trend.negative {
  color: var(--danger-color);
}

.stats-content {
  margin-bottom: var(--space-4);
}

.stats-number-modern {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: var(--space-1);
}

.stats-label-modern {
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
}

.stats-footer {
  margin-top: var(--space-4);
}

.progress-modern {
  width: 100%;
  height: 4px;
  background: var(--gray-200);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: var(--space-2);
}

.progress-bar-modern {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.stats-subtitle {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-top: var(--space-2);
  display: block;
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
}

.panel-modern {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: var(--transition);
}

.panel-modern:hover {
  box-shadow: var(--shadow-md);
}

.panel-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6) var(--space-6) var(--space-4);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-card);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.panel-title h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.panel-content-modern {
  padding: var(--space-6);
}

/* 活动时间线 */
.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.activity-item-modern {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-4);
  border-radius: var(--border-radius-sm);
  transition: var(--transition);
}

.activity-item-modern:hover {
  background: var(--gray-50);
}

.activity-indicator {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  flex-shrink: 0;
}

.activity-commit {
  background: var(--primary-500);
}

.activity-issue {
  background: var(--warning-color);
}

.activity-pr {
  background: var(--success-color);
}

.activity-release {
  background: var(--info-color);
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-1);
}

.activity-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.activity-time {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.activity-description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0 0 var(--space-2) 0;
  line-height: 1.4;
}

.activity-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-repo {
  color: var(--text-muted);
  font-size: 0.75rem;
  font-family: var(--font-mono);
}

/* 系统状态 */
.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.875rem;
  font-weight: 500;
}

.status-indicator.online {
  color: var(--success-color);
}

.status-indicator.issues {
  color: var(--danger-color);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success-color);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--border-light);
}

.service-info {
  flex: 1;
}

.service-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.service-description {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-top: var(--space-1);
}

.service-status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-text {
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.service-status.healthy .status-text {
  color: var(--success-color);
}

.service-status.healthy .status-badge {
  background: var(--success-color);
}

.service-status.warning .status-text {
  color: var(--warning-color);
}

.service-status.warning .status-badge {
  background: var(--warning-color);
}

/* 快速操作 */
.actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.action-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: var(--bg-card);
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
}

.action-card:hover {
  border-color: var(--primary-300);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.action-content {
  flex: 1;
  min-width: 0;
}

.action-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  margin-bottom: var(--space-1);
}

.action-description {
  color: var(--text-muted);
  font-size: 0.75rem;
  line-height: 1.3;
}

/* 图表面板 */
.chart-container {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: var(--text-muted);
}

.chart-placeholder .el-icon {
  font-size: 3rem;
  margin-bottom: var(--space-4);
  color: var(--gray-300);
}

.chart-placeholder p {
  margin: 0 0 var(--space-4) 0;
  font-size: 0.875rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
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
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .activity-item-modern {
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .activity-indicator {
    align-self: flex-start;
  }
}

/* 活动面板样式 */
.activity-filters {
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-color);
}

.activity-timeline {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item-modern {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-color);
  transition: var(--transition);
}

.activity-item-modern:hover {
  background: var(--bg-hover);
}

.activity-item-modern:last-child {
  border-bottom: none;
}

.activity-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  flex-shrink: 0;
}

.activity-indicator.activity-commit {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.activity-indicator.activity-issue {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.activity-indicator.activity-pull_request,
.activity-indicator.activity-pr {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.activity-indicator.activity-release {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.activity-indicator.activity-report {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.activity-indicator.activity-subscription {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-1);
}

.activity-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  line-height: 1.4;
  flex: 1;
  margin-right: var(--space-2);
}

.activity-time {
  color: var(--text-muted);
  font-size: 0.75rem;
  flex-shrink: 0;
}

.activity-description {
  color: var(--text-secondary);
  font-size: 0.75rem;
  line-height: 1.4;
  margin: 0 0 var(--space-2) 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.activity-meta {
  display: flex;
  gap: var(--space-2);
  align-items: center;
  font-size: 0.75rem;
}

.activity-repo {
  color: var(--text-muted);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-activities {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  color: var(--text-muted);
  font-size: 0.875rem;
}

.no-activities .el-icon {
  font-size: 2rem;
  margin-bottom: var(--space-2);
}

.view-more {
  text-align: center;
  padding: var(--space-3);
  border-top: 1px solid var(--border-color);
}
</style> 