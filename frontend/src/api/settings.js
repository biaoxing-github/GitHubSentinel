import request from './request'

// 获取系统设置
export const getSettings = async () => {
  const response = await request.get('/settings/')
  return response.data
}

// 更新系统设置
export const updateSettings = async (settingsData) => {
  const response = await request.put('/settings/', settingsData)
  return response.data
}

// 获取用户设置
export const getUserSettings = async (userId) => {
  const response = await request.get(`/settings/user/${userId}`)
  return response.data
}

// 更新用户设置
export const updateUserSettings = async (userId, settingsData) => {
  const response = await request.put(`/settings/user/${userId}`, settingsData)
  return response.data
}

// 重置设置为默认值
export const resetSettings = async () => {
  const response = await request.post('/settings/reset')
  return response.data
}

// 导出设置
export const exportSettings = async () => {
  const response = await request.get('/settings/export')
  return response.data
}

// 导入设置
export const importSettings = async (settingsData) => {
  const response = await request.post('/settings/import', settingsData)
  return response.data
} 