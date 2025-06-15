import request from './request'

// 获取报告列表
export const getReports = async (params = {}) => {
  const response = await request.get('/reports/', { params })
  return response.data
}

// 获取单个报告
export const getReport = async (reportId) => {
  const response = await request.get(`/reports/${reportId}`)
  return response.data
}

// 生成报告
export const generateReport = async (params) => {
  // 支持两种调用方式：对象参数和分别传参
  if (typeof params === 'object' && params.subscription_id) {
    const response = await request.post('/reports/generate', params)
    return response.data
  } else {
    // 兼容旧的调用方式
    const [subscriptionId, reportType] = arguments
    const response = await request.post('/reports/generate', {
      subscription_id: subscriptionId,
      report_type: reportType,
      format: 'html'
    })
    return response.data
  }
}

// 删除报告
export const deleteReport = async (reportId) => {
  const response = await request.delete(`/reports/${reportId}`)
  return response.data
}

// 获取报告统计
export const getReportStats = async () => {
  const response = await request.get('/reports/stats/summary')
  return response.data
} 