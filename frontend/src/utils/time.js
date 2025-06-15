/**
 * 时间工具函数
 * 统一使用北京时间显示
 */

/**
 * 将UTC时间转换为北京时间
 * @param {string|Date} timeString - UTC时间字符串或Date对象
 * @returns {Date} 北京时间Date对象
 */
export const toBeijingTime = (timeString) => {
  const utcTime = new Date(timeString)
  // 北京时间是UTC+8
  const beijingTime = new Date(utcTime.getTime() + 8 * 60 * 60 * 1000)
  return beijingTime
}

/**
 * 格式化相对时间（北京时间）
 * @param {string|Date} timeString - 时间字符串或Date对象
 * @returns {string} 相对时间字符串
 */
export const formatRelativeTime = (timeString) => {
  const time = toBeijingTime(timeString)
  const now = toBeijingTime(new Date())
  const diffInSeconds = Math.floor((now - time) / 1000)
  
  if (diffInSeconds < 60) return `${diffInSeconds}s ago`
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`
  return `${Math.floor(diffInSeconds / 2592000)}mo ago`
}

/**
 * 格式化日期（北京时间）
 * @param {string|Date} timeString - 时间字符串或Date对象
 * @param {string} format - 格式化模式
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (timeString, format = 'YYYY-MM-DD HH:mm:ss') => {
  const time = toBeijingTime(timeString)
  
  const year = time.getFullYear()
  const month = String(time.getMonth() + 1).padStart(2, '0')
  const day = String(time.getDate()).padStart(2, '0')
  const hours = String(time.getHours()).padStart(2, '0')
  const minutes = String(time.getMinutes()).padStart(2, '0')
  const seconds = String(time.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 获取时间周期的开始时间（北京时间）
 * @param {number} days - 天数
 * @returns {Date} 开始时间
 */
export const getTimeRangeStart = (days) => {
  const now = toBeijingTime(new Date())
  const startTime = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  return startTime
}

/**
 * 获取当前北京时间
 * @returns {Date} 当前北京时间
 */
export const getCurrentBeijingTime = () => {
  return toBeijingTime(new Date())
} 