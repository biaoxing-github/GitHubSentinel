/**
 * API 配置文件
 * 统一管理后台API调用
 */
import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api/v1',  // 使用相对路径，通过Vite代理访问后端
  timeout: 60 * 60 * 1000, // 60分钟超时（3600000ms）
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: false
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加默认的Authorization头
    config.headers.Authorization = 'Bearer demo_token'
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API调用失败:', error)
    return Promise.reject(error)
  }
)

// API调用方法
export const userAPI = {
  // 获取用户列表
  getUsers: (params = {}) => api.get('/users', { params }),
  
  // 根据ID获取用户
  getUser: (id) => api.get(`/users/${id}`),
  
  // 创建用户
  createUser: (userData) => api.post('/users', userData),
  
  // 更新用户
  updateUser: (id, userData) => api.put(`/users/${id}`, userData),
  
  // 删除用户
  deleteUser: (id) => api.delete(`/users/${id}`),
  
  // 获取用户统计
  getUserStats: () => api.get('/users/stats/count')
}

export const subscriptionAPI = {
  // 获取所有订阅
  getSubscriptions: (params = {}) => api.get('/subscriptions', { params }),
  
  // 获取用户订阅
  getUserSubscriptions: (userId, params = {}) => api.get(`/subscriptions/user/${userId}`, { params }),
  
  // 根据ID获取订阅
  getSubscription: (id) => api.get(`/subscriptions/${id}`),
  
  // 创建订阅
  createSubscription: (subscriptionData) => api.post('/subscriptions', subscriptionData),
  
  // 更新订阅
  updateSubscription: (id, subscriptionData) => api.put(`/subscriptions/${id}`, subscriptionData),
  
  // 删除订阅
  deleteSubscription: (id) => api.delete(`/subscriptions/${id}`),
  
  // 获取订阅活动
  getSubscriptionActivities: (id, params = {}) => api.get(`/subscriptions/${id}/activities`, { params }),
  
  // 手动同步订阅
  syncSubscription: (id) => api.post(`/subscriptions/${id}/sync`),
  
  // 获取订阅统计
  getSubscriptionStats: () => api.get('/subscriptions/stats/summary')
}

export const systemAPI = {
  // 健康检查
  healthCheck: () => api.get('/health')
}

export const settingsAPI = {
  // 获取系统设置
  getSettings: () => api.get('/settings'),
  
  // 更新系统设置
  updateSettings: (settings) => api.put('/settings', settings),
  
  // 获取配置文件
  getConfigFile: () => api.get('/settings/config-file'),
  
  // 重新加载配置
  reloadConfig: () => api.post('/settings/reload'),
  
  // 验证设置
  validateSettings: () => api.get('/settings/validation')
}

export const reportsAPI = {
  // 获取报告列表
  getReports: (params = {}) => api.get('/reports', { params }),
  
  // 根据ID获取报告
  getReport: (id) => api.get(`/reports/${id}`),
  
  // 创建报告
  createReport: (reportData) => api.post('/reports', reportData),
  
  // 生成报告
  generateReport: (data) => api.post('/reports/generate', data),
  
  // 下载报告
  downloadReport: async (id) => {
    const response = await axios.get(`/api/v1/reports/${id}/download`, {
      responseType: 'blob'
    })
    return response
  },
  
  // 删除报告
  deleteReport: (id) => api.delete(`/reports/${id}`),
  
  // 获取报告模板
  getReportTemplates: () => api.get('/reports/templates/'),
  
  // 获取报告统计
  getReportStats: () => api.get('/reports/stats/summary')
}

export const dashboardAPI = {
  // 获取仪表板统计数据
  getStats: () => api.get('/dashboard/stats'),
  
  // 获取活动图表数据
  getActivityChart: (days = 7) => api.get('/dashboard/activity-chart', { params: { days } }),
  
  // 获取仓库统计数据
  getRepositoryStats: () => api.get('/dashboard/repository-stats'),
  
  // 获取最近活动
  getRecentActivity: () => api.get('/dashboard/recent-activity'),
  
  // 获取系统状态
  getSystemStatus: () => api.get('/dashboard/system-status'),
  
  // 获取快速操作
  getQuickActions: () => api.get('/dashboard/quick-actions'),
  
  // 获取性能指标
  getPerformanceMetrics: () => api.get('/dashboard/performance-metrics')
}

export default api 