/**
 * HTTP 请求配置
 * 统一的 axios 实例
 */
import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api/v1',  // 使用相对路径，通过Vite代理访问后端
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: false
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API调用失败:', error)
    return Promise.reject(error)
  }
)

export default request 