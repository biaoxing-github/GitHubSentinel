<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>仪表板</h1>
      <p>GitHub Sentinel 监控概览</p>
    </div>

    <div class="dashboard-content">
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-cards">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.users?.total || 0 }}</div>
              <div class="stat-label">总用户数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">📋</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.subscriptions?.total || 0 }}</div>
              <div class="stat-label">总订阅数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.reports?.total || 0 }}</div>
              <div class="stat-label">总报告数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.activities?.today || 0 }}</div>
              <div class="stat-label">今日活动</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" class="charts-section">
        <el-col :span="16">
          <div class="chart-card">
            <div class="card-header">
              <h3>活动趋势</h3>
              <el-select v-model="chartDays" @change="loadActivityChart" size="small" style="width: 100px">
                <el-option label="7天" :value="7"/>
                <el-option label="14天" :value="14"/>
                <el-option label="30天" :value="30"/>
              </el-select>
            </div>
            <div ref="activityChart" class="chart" v-loading="chartLoading"></div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="chart-card">
            <h3>订阅状态分布</h3>
            <div ref="repoChart" class="chart" v-loading="chartLoading"></div>
          </div>
        </el-col>
      </el-row>

      <!-- 最近活动 -->
      <el-row :gutter="20" class="recent-activity">
        <el-col :span="16">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>最近活动</span>
                <el-button type="text" @click="loadRecentActivities">刷新</el-button>
              </div>
            </template>
            <div v-loading="activitiesLoading">
              <div v-if="recentActivities.length === 0" class="no-data">
                <el-empty description="暂无活动数据" />
              </div>
              <div v-else>
                <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
                  <div class="activity-type">
                    <el-tag :type="getActivityTypeColor(activity.type)" size="small">
                      {{ getActivityTypeName(activity.type) }}
                    </el-tag>
                  </div>
                  <div class="activity-content">
                    <div class="activity-title">{{ activity.title }}</div>
                    <div class="activity-meta">
                      <span class="activity-repo">{{ activity.repository }}</span>
                      <span class="activity-author">by {{ activity.author }}</span>
                      <span class="activity-time">{{ formatTime(activity.created_at) }}</span>
                    </div>
                  </div>
                  <div class="activity-action">
                    <el-button type="text" size="small" @click="openActivity(activity)">查看</el-button>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <template #header>
              <span>系统状态</span>
            </template>
            <div class="status-info" v-loading="healthLoading">
              <p><strong>数据库状态:</strong> 
                <el-tag :type="systemHealth.database?.status === 'healthy' ? 'success' : 'danger'" size="small">
                  {{ systemHealth.database?.status === 'healthy' ? '正常' : '异常' }}
                </el-tag>
              </p>
              <p><strong>最后更新:</strong> {{ lastUpdated }}</p>
              <p><strong>活跃订阅:</strong> {{ stats.subscriptions?.active || 0 }}</p>
              <p><strong>本周活动:</strong> {{ stats.activities?.this_week || 0 }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { dashboardAPI } from '@/api'

export default {
  name: 'Dashboard',
  setup() {
    const stats = ref({})
    const recentActivities = ref([])
    const systemHealth = ref({})
    const loading = ref(false)
    const chartLoading = ref(false)
    const activitiesLoading = ref(false)
    const healthLoading = ref(false)
    const error = ref(null)
    const lastUpdated = ref('')
    const chartDays = ref(7)
    
    const activityChart = ref(null)
    const repoChart = ref(null)

    const getActivityTypeColor = (type) => {
      const colors = {
        'commit': 'success',
        'issue': 'warning',
        'pull_request': 'info',
        'release': 'danger',
        'discussion': 'primary'
      }
      return colors[type] || 'info'
    }

    const getActivityTypeName = (type) => {
      const names = {
        'commit': '提交',
        'issue': '问题',
        'pull_request': 'PR',
        'release': '发布',
        'discussion': '讨论'
      }
      return names[type] || type
    }

    const formatTime = (timeString) => {
      if (!timeString) return '未知时间'
      const time = new Date(timeString)
      const now = new Date()
      const diff = now - time
      
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
      return `${Math.floor(diff / 86400000)}天前`
    }

    const openActivity = (activity) => {
      if (activity.url) {
        window.open(activity.url, '_blank')
      }
    }

    const loadStats = async () => {
      try {
        const data = await dashboardAPI.getStats()
        stats.value = data
        console.log('统计数据加载成功:', data)
      } catch (error) {
        console.error('加载统计数据失败:', error)
        ElMessage.error('加载统计数据失败')
      }
    }

    const loadActivityChart = async () => {
      chartLoading.value = true
      try {
        const data = await dashboardAPI.getActivityChart(chartDays.value)
        console.log('图表数据加载成功:', data)
        
        await nextTick()
        initActivityChart(data)
      } catch (error) {
        console.error('加载图表数据失败:', error)
        ElMessage.error('加载图表数据失败')
      } finally {
        chartLoading.value = false
      }
    }

    const loadRecentActivities = async () => {
      activitiesLoading.value = true
      try {
        const data = await dashboardAPI.getRecentActivities(10)
        recentActivities.value = data
        console.log('最近活动加载成功:', data)
      } catch (error) {
        console.error('加载最近活动失败:', error)
        ElMessage.error('加载最近活动失败')
      } finally {
        activitiesLoading.value = false
      }
    }

    const loadSystemHealth = async () => {
      healthLoading.value = true
      try {
        const data = await dashboardAPI.getSystemHealth()
        systemHealth.value = data
        console.log('系统健康状态加载成功:', data)
      } catch (error) {
        console.error('加载系统健康状态失败:', error)
        ElMessage.error('加载系统状态失败')
      } finally {
        healthLoading.value = false
      }
    }

    const loadData = async () => {
      loading.value = true
      try {
        await Promise.all([
          loadStats(),
          loadRecentActivities(),
          loadSystemHealth()
        ])
        
        lastUpdated.value = new Date().toLocaleString('zh-CN')
        
        // 延迟加载图表，确保DOM已渲染
        await nextTick()
        await loadActivityChart()
        initRepoChart()
        
      } catch (error) {
        console.error('加载数据失败:', error)
        error.value = error.message
      } finally {
        loading.value = false
      }
    }

    const initActivityChart = (data) => {
      if (!activityChart.value || !data) return
      
      const chart = echarts.init(activityChart.value)
      const options = {
        title: {
          text: `最近${chartDays.value}天活动趋势`,
          textStyle: {
            fontSize: 14
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['提交', '问题', 'PR', '发布']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: data.dates || []
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '提交',
            type: 'line',
            data: data.commits || [],
            smooth: true,
            itemStyle: { color: '#67C23A' }
          },
          {
            name: '问题',
            type: 'line',
            data: data.issues || [],
            smooth: true,
            itemStyle: { color: '#E6A23C' }
          },
          {
            name: 'PR',
            type: 'line',
            data: data.pull_requests || [],
            smooth: true,
            itemStyle: { color: '#409EFF' }
          },
          {
            name: '发布',
            type: 'line',
            data: data.releases || [],
            smooth: true,
            itemStyle: { color: '#F56C6C' }
          }
        ]
      }
      chart.setOption(options)
      
      // 监听窗口变化
      window.addEventListener('resize', () => {
        chart.resize()
      })
    }

    const initRepoChart = () => {
      if (!repoChart.value) return
      
      const chart = echarts.init(repoChart.value)
      const options = {
        title: {
          text: '订阅状态分布',
          textStyle: {
            fontSize: 14
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [
          {
            name: '订阅状态',
            type: 'pie',
            radius: '50%',
            data: [
              { 
                value: stats.value.subscriptions?.active || 0, 
                name: '活跃订阅',
                itemStyle: { color: '#67C23A' }
              },
              { 
                value: stats.value.subscriptions?.paused || 0, 
                name: '暂停订阅',
                itemStyle: { color: '#E6A23C' }
              }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      chart.setOption(options)
      
      // 监听窗口变化
      window.addEventListener('resize', () => {
        chart.resize()
      })
    }

    onMounted(() => {
      loadData()
    })

    return {
      stats,
      recentActivities,
      systemHealth,
      loading,
      chartLoading,
      activitiesLoading,
      healthLoading,
      error,
      lastUpdated,
      chartDays,
      activityChart,
      repoChart,
      getActivityTypeColor,
      getActivityTypeName,
      formatTime,
      openActivity,
      loadData,
      loadActivityChart,
      loadRecentActivities
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h1 {
  margin: 0 0 10px 0;
  color: #333;
}

.dashboard-header p {
  margin: 0;
  color: #666;
}

.dashboard-content {
  max-width: 1200px;
}

.stats-cards {
  margin-bottom: 30px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  color: #409EFF;
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.chart-card h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #333;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart {
  height: 300px;
}

.recent-activity {
  margin-bottom: 30px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-type {
  margin-right: 12px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.activity-meta {
  font-size: 12px;
  color: #999;
}

.activity-meta span {
  margin-right: 12px;
}

.activity-action {
  margin-left: 12px;
}

.status-info p {
  margin: 8px 0;
  color: #666;
}

.no-data {
  text-align: center;
  padding: 40px 0;
}
</style> 