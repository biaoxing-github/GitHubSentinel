<template>
  <div class="activities-modern">
    <!-- 现代化页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <h1 class="page-title">Activities</h1>
          <p class="page-description">View all repository activities and events</p>
        </div>
        <div class="header-actions">
          <el-button @click="refreshActivities" :loading="loading">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filters-section">
      <div class="filters-row">
        <el-select 
          v-model="selectedRepository" 
          placeholder="Select Repository" 
          style="width: 250px"
          @change="onRepositoryChange"
          clearable
        >
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
          style="width: 150px"
          @change="onActivityTypeChange"
          clearable
        >
          <el-option label="All" value="" />
          <el-option label="Issues" value="issue" />
          <el-option label="Pull Requests" value="pull_request" />
          <el-option label="Commits" value="commit" />
          <el-option label="Releases" value="release" />
          <el-option label="Reports" value="report" />
          <el-option label="Subscriptions" value="subscription" />
        </el-select>

        <el-select 
          v-model="selectedTimePeriod" 
          placeholder="Time Period"
          style="width: 120px"
          @change="onTimePeriodChange"
        >
          <el-option label="1 Day" :value="1" />
          <el-option label="3 Days" :value="3" />
          <el-option label="7 Days" :value="7" />
          <el-option label="30 Days" :value="30" />
          <el-option label="All Time" :value="0" />
        </el-select>

        <el-input 
          v-model="searchQuery" 
          placeholder="Search activities..." 
          style="width: 200px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 活动列表 -->
    <div class="activities-container">
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>
      
      <div v-else-if="filteredActivities.length === 0" class="empty-state-modern">
        <div class="icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="title">No Activities Found</div>
        <div class="description">
          {{ activities.length === 0 ? 'No activities available' : 'Try adjusting your filters' }}
        </div>
      </div>
      
      <div v-else class="activities-list">
        <div 
          v-for="activity in paginatedActivities" 
          :key="activity.id" 
          class="activity-item-detailed"
        >
          <div class="activity-indicator" :class="`activity-${activity.type}`">
            <el-icon>
              <component :is="getActivityIcon(activity.type)" />
            </el-icon>
          </div>
          <div class="activity-content">
            <div class="activity-header">
              <span class="activity-title">{{ activity.title }}</span>
              <div class="activity-meta-right">
                <el-tag 
                  :type="getActivityTagType(activity.type)" 
                  size="small"
                >
                  {{ activity.tag || activity.type }}
                </el-tag>
                <span class="activity-time">{{ formatRelativeTime(activity.time) }}</span>
              </div>
            </div>
            <p class="activity-description">{{ activity.description }}</p>
            <div class="activity-meta">
              <span class="activity-repo">
                <el-icon><FolderOpened /></el-icon>
                {{ activity.repository }}
              </span>
              <span class="activity-author" v-if="activity.author">
                <el-icon><User /></el-icon>
                {{ activity.author }}
              </span>
              <span class="activity-status" v-if="activity.status">
                Status: {{ activity.status }}
              </span>
            </div>
            <div class="activity-actions" v-if="activity.url">
              <el-button size="small" text @click="openActivity(activity)">
                <el-icon><Link /></el-icon>
                View Details
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-container" v-if="filteredActivities.length > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredActivities.length"
          layout="prev, pager, next, total"
          @current-change="onPageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Search,
  Document,
  FolderOpened,
  User,
  Link,
  Upload,
  Warning,
  Share,
  Star,
  Plus,
  DocumentAdd
} from '@element-plus/icons-vue'
import dashboardAPI from '@/api/dashboard'
import { formatRelativeTime } from '@/utils/time'

// 响应式数据
const loading = ref(false)
const activities = ref([])
const repositories = ref([])
const selectedRepository = ref('')
const selectedActivityType = ref('')
const selectedTimePeriod = ref(7) // 默认7天
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const filteredActivities = computed(() => {
  let filtered = activities.value

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

  // 按搜索关键词筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(activity => 
      activity.title.toLowerCase().includes(query) ||
      activity.description.toLowerCase().includes(query) ||
      activity.repository.toLowerCase().includes(query)
    )
  }

  return filtered
})

const paginatedActivities = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredActivities.value.slice(start, end)
})

// 方法
const loadActivities = async () => {
  loading.value = true
  try {
    console.log('🔄 加载所有活动数据...')
    
    const data = await dashboardAPI.getRecentActivity(selectedTimePeriod.value)
    activities.value = data
    
    // 提取仓库列表
    const repoSet = new Set()
    data.forEach(activity => {
      if (activity.repository && activity.repository !== 'N/A') {
        repoSet.add(activity.repository)
      }
    })
    repositories.value = Array.from(repoSet).sort()
    
    console.log('✅ 活动数据加载完成:', data.length, '个活动')
    console.log('📁 仓库列表:', repositories.value)
    
  } catch (error) {
    console.error('💥 加载活动数据失败:', error)
    ElMessage.error('Failed to load activities: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const onTimePeriodChange = async () => {
  console.log('🔄 时间周期筛选变更:', selectedTimePeriod.value)
  currentPage.value = 1 // 重置到第一页
  await loadActivities() // 重新加载数据
}

const refreshActivities = async () => {
  await loadActivities()
}

const onRepositoryChange = () => {
  currentPage.value = 1
}

const onActivityTypeChange = () => {
  currentPage.value = 1
}

const onPageChange = (page) => {
  currentPage.value = page
}

const getActivityIcon = (type) => {
  const iconMap = {
    'report': Document,
    'subscription': Plus,
    'commit': DocumentAdd,
    'issue': Warning,
    'pull_request': Share,
    'pr': Share,
    'release': Star
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
    'pr': 'primary',
    'release': 'success'
  }
  return typeMap[type] || 'info'
}

const openActivity = (activity) => {
  if (activity.url) {
    window.open(activity.url, '_blank')
  }
}

// 生命周期
onMounted(() => {
  loadActivities()
})
</script>

<style scoped>
.activities-modern {
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

/* 筛选器 */
.filters-section {
  background: var(--bg-card);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  padding: var(--space-6);
  margin-bottom: var(--space-8);
}

.filters-row {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  flex-wrap: wrap;
}

/* 活动容器 */
.activities-container {
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

/* 活动列表 */
.activities-list {
  padding: var(--space-6);
}

.activity-item-detailed {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-6);
  border-bottom: 1px solid var(--border-color);
  transition: var(--transition);
}

.activity-item-detailed:hover {
  background: var(--bg-hover);
}

.activity-item-detailed:last-child {
  border-bottom: none;
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
  margin-bottom: var(--space-2);
  gap: var(--space-4);
}

.activity-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.4;
  flex: 1;
}

.activity-meta-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.activity-time {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.activity-description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0 0 var(--space-3) 0;
}

.activity-meta {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: var(--space-2);
}

.activity-repo,
.activity-author,
.activity-status {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.activity-actions {
  margin-top: var(--space-2);
}

/* 分页 */
.pagination-container {
  padding: var(--space-6);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
}
</style> 