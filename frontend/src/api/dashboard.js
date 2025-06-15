import request from './request'

// 获取仪表板统计数据
export const getDashboardStats = async () => {
  const response = await request.get('/dashboard/stats')
  return response
}

// 获取最近活动
export const getRecentActivity = async (days = 0) => {
  const response = await request.get('/dashboard/recent-activity', {
    params: { days }
  })
  return response
}

// 获取系统状态
export const getSystemStatus = async () => {
  const response = await request.get('/dashboard/system-status')
  return response
}

// 获取快速操作
export const getQuickActions = async () => {
  const response = await request.get('/dashboard/quick-actions')
  return response
}

// 获取性能指标
export const getPerformanceMetrics = async (period = '7d') => {
  const response = await request.get('/dashboard/performance-metrics', {
    params: { period }
  })
  return response
}

export default {
  getDashboardStats,
  getRecentActivity,
  getSystemStatus,
  getQuickActions,
  getPerformanceMetrics
} 