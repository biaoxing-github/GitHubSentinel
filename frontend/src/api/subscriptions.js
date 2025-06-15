import request from './request'

// 获取订阅列表
export const getSubscriptions = async (params = {}) => {
  const response = await request.get('/subscriptions/', { params })
  return response.data
}

// 获取单个订阅
export const getSubscription = async (subscriptionId) => {
  const response = await request.get(`/subscriptions/${subscriptionId}`)
  return response.data
}

// 创建订阅
export const createSubscription = async (subscriptionData) => {
  const response = await request.post('/subscriptions/', subscriptionData)
  return response.data
}

// 更新订阅
export const updateSubscription = async (subscriptionId, subscriptionData) => {
  const response = await request.put(`/subscriptions/${subscriptionId}`, subscriptionData)
  return response.data
}

// 删除订阅
export const deleteSubscription = async (subscriptionId) => {
  const response = await request.delete(`/subscriptions/${subscriptionId}`)
  return response.data
}

// 获取订阅统计
export const getSubscriptionStats = async () => {
  const response = await request.get('/subscriptions/stats/summary')
  return response.data
} 