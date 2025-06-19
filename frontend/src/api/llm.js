/**
 * LLM 智能分析 API 接口 (v0.3.0)
 * 基于 LangChain 的高级 AI 分析和对话查询功能
 */

import apiClient from './index'

/**
 * 与AI进行对话
 * @param {Object} data - 对话数据
 * @param {string} data.message - 用户消息
 * @param {Object} data.context_data - 上下文数据
 * @param {boolean} data.stream - 是否流式输出
 * @returns {Promise} 对话响应
 */
export const chatWithAI = (data) => {
  return apiClient.post('/llm/chat', data)
}

/**
 * 智能分析仓库
 * @param {Object} data - 分析请求数据
 * @param {string} data.repository - 仓库名称 (owner/repo)
 * @param {string} data.analysis_type - 分析类型 (comprehensive/security/performance/quality)
 * @param {string} data.timeframe - 时间范围
 * @returns {Promise} 分析结果
 */
export const analyzeRepository = (data) => {
  return apiClient.post('/llm/analyze', data)
}

/**
 * 生成智能摘要
 * @param {Object} data - 摘要请求数据
 * @param {string} data.repository - 仓库名称
 * @param {string} data.timeframe - 时间范围
 * @param {number} data.days - 天数
 * @returns {Promise} 摘要结果
 */
export const generateSmartSummary = (data) => {
  return apiClient.post('/llm/smart-summary', data)
}

/**
 * 搜索并分析
 * @param {Object} data - 搜索请求数据
 * @param {string} data.query - 搜索查询
 * @param {Object} data.context_data - 上下文数据
 * @returns {Promise} 搜索分析结果
 */
export const searchAndAnalyze = (data) => {
  return apiClient.post('/llm/search', data)
}

/**
 * 清除对话历史
 * @returns {Promise} 清除结果
 */
export const clearConversation = () => {
  return apiClient.delete('/llm/conversation')
}

/**
 * 获取LLM服务状态
 * @returns {Promise} 服务状态
 */
export const getLLMStatus = () => {
  return apiClient.get('/llm/status')
}

/**
 * 批量分析多个仓库
 * @param {Object} data - 批量分析数据
 * @param {Array} data.repositories - 仓库列表
 * @param {string} data.analysis_type - 分析类型
 * @returns {Promise} 批量分析结果
 */
export const batchAnalyzeRepositories = (repositories, analysis_type = 'comprehensive') => {
  return apiClient.post('/llm/batch-analyze', {
    repositories,
    analysis_type
  })
}

// WebSocket 相关接口

/**
 * 创建通知规则
 * @param {Object} data - 通知规则数据
 * @param {string} data.rule_type - 规则类型
 * @param {Object} data.conditions - 触发条件
 * @param {Object} data.actions - 执行动作
 * @returns {Promise} 创建结果
 */
export const createNotificationRule = (data) => {
  return apiClient.post('/websocket/notification-rules', data)
}

/**
 * 获取通知规则列表
 * @returns {Promise} 通知规则列表
 */
export const getNotificationRules = () => {
  return apiClient.get('/websocket/notification-rules')
}

/**
 * 更新通知规则
 * @param {string} ruleId - 规则ID
 * @param {Object} data - 更新的规则数据
 * @returns {Promise} 更新结果
 */
export const updateNotificationRule = (ruleId, data) => {
  return apiClient.put(`/websocket/notification-rules/${ruleId}`, data)
}

/**
 * 删除通知规则
 * @param {string} ruleId - 规则ID
 * @returns {Promise} 删除结果
 */
export const deleteNotificationRule = (ruleId) => {
  return apiClient.delete(`/websocket/notification-rules/${ruleId}`)
}

/**
 * 广播消息
 * @param {Object} data - 广播数据
 * @param {string} data.message - 广播消息
 * @param {string} data.channel - 频道名称
 * @param {Array} data.target_users - 目标用户ID列表
 * @returns {Promise} 广播结果
 */
export const broadcastMessage = (data) => {
  return apiClient.post('/websocket/broadcast', data)
}

/**
 * 获取WebSocket服务统计
 * @returns {Promise} 统计信息
 */
export const getWebSocketStats = () => {
  return apiClient.get('/websocket/stats')
}

/**
 * 发送测试通知
 * @returns {Promise} 测试结果
 */
export const sendTestNotification = () => {
  return apiClient.post('/websocket/test-notification')
}

/**
 * 获取用户订阅的频道
 * @returns {Promise} 频道列表
 */
export const getUserChannels = () => {
  return apiClient.get('/websocket/channels')
}

/**
 * 订阅频道
 * @param {string} channel - 频道名称
 * @returns {Promise} 订阅结果
 */
export const subscribeChannel = (channel) => {
  return apiClient.post(`/websocket/subscribe/${channel}`)
}

/**
 * 取消订阅频道
 * @param {string} channel - 频道名称
 * @returns {Promise} 取消订阅结果
 */
export const unsubscribeChannel = (channel) => {
  return apiClient.delete(`/websocket/subscribe/${channel}`)
}

// PWA 相关接口

/**
 * 获取应用安装配置
 * @returns {Promise} 安装配置
 */
export const getInstallConfig = () => {
  return apiClient.get('/pwa/install-config')
}

/**
 * 获取通知配置
 * @returns {Promise} 通知配置
 */
export const getNotificationConfig = () => {
  return apiClient.get('/pwa/notification-config')
}

/**
 * 获取客户端配置
 * @returns {Promise} 客户端配置
 */
export const getClientConfig = () => {
  return apiClient.get('/pwa/client-config')
}

/**
 * 追踪应用安装统计
 * @param {Object} data - 统计数据
 * @param {string} data.event_type - 事件类型
 * @param {string} data.user_agent - 用户代理
 * @param {string} data.platform - 平台信息
 * @returns {Promise} 统计结果
 */
export const trackInstallMetrics = (data) => {
  return apiClient.post('/pwa/install-metrics', data)
}

/**
 * 获取缓存状态
 * @returns {Promise} 缓存状态
 */
export const getCacheStatus = () => {
  return apiClient.get('/pwa/cache-status')
}

// WebSocket 连接管理
export class WebSocketManager {
  constructor() {
    this.ws = null
    this.token = null
    this.eventListeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.connectionStatus = 'disconnected' // 'disconnected', 'connecting', 'connected', 'reconnecting'
    this.lastHeartbeat = null
    this.heartbeatInterval = null
    this.heartbeatTimeout = 30000 // 30秒心跳超时
    this.subscribedChannels = new Set()
    this.connectionStats = {
      connectedAt: null,
      reconnectCount: 0,
      messagesReceived: 0,
      messagesSent: 0,
      lastError: null
    }
  }

  /**
   * 连接WebSocket
   * @param {string} token - 用户token
   */
  connect(token) {
    this.token = token
    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/api/v1/websocket/connect?token=${token}`
    
    try {
      this.connectionStatus = 'connecting'
      this.emit('statusChange', { status: this.connectionStatus })
      
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('✅ WebSocket连接已建立')
        this.connectionStatus = 'connected'
        this.connectionStats.connectedAt = new Date()
        this.connectionStats.reconnectCount = this.reconnectAttempts
        this.reconnectAttempts = 0
        
        // 启动心跳
        this.startHeartbeat()
        
        // 重新订阅之前的频道
        this.subscribedChannels.forEach(channel => {
          this.subscribe(channel)
        })
        
        this.emit('connected', { stats: this.connectionStats })
        this.emit('statusChange', { status: this.connectionStatus, stats: this.connectionStats })
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.connectionStats.messagesReceived++
          this.lastHeartbeat = new Date()
          
          // 处理不同类型的消息
          if (data.type === 'pong') {
            this.emit('heartbeat', data)
          } else if (data.type === 'connection_established') {
            this.emit('connection_established', data)
          } else if (data.type === 'activity_notification') {
            this.emit('activity_notification', data)
          } else if (data.type === 'ai_insight') {
            this.emit('ai_insight', data)
          } else if (data.type === 'rule_triggered') {
            this.emit('rule_triggered', data)
          }
          
          this.emit('message', data)
          this.emit(data.type, data)
        } catch (error) {
          console.error('❌ 解析WebSocket消息失败:', error)
          this.connectionStats.lastError = error.message
          this.emit('parseError', { error: error.message, rawData: event.data })
        }
      }
      
      this.ws.onclose = () => {
        console.log('❌ WebSocket连接已关闭')
        this.connectionStatus = 'disconnected'
        this.stopHeartbeat()
        this.emit('disconnected', { stats: this.connectionStats })
        this.emit('statusChange', { status: this.connectionStatus, stats: this.connectionStats })
        this.attemptReconnect()
      }
      
      this.ws.onerror = (error) => {
        console.error('💥 WebSocket错误:', error)
        this.connectionStats.lastError = error.message || 'WebSocket连接错误'
        this.emit('error', { error, stats: this.connectionStats })
      }
      
    } catch (error) {
      console.error('💥 WebSocket连接失败:', error)
      this.connectionStatus = 'disconnected'
      this.connectionStats.lastError = error.message
      this.emit('connectError', { error: error.message, stats: this.connectionStats })
    }
  }

  /**
   * 断开WebSocket连接
   */
  disconnect() {
    this.stopHeartbeat()
    this.connectionStatus = 'disconnected'
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.emit('statusChange', { status: this.connectionStatus })
  }

  /**
   * 发送消息
   * @param {Object} message - 消息内容
   */
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
      this.connectionStats.messagesSent++
      return true
    } else {
      console.warn('⚠️ WebSocket未连接，无法发送消息')
      this.emit('sendError', { message: '连接未建立', originalMessage: message })
      return false
    }
  }

  /**
   * 订阅频道
   * @param {string} channel - 频道名称
   */
  subscribe(channel) {
    this.subscribedChannels.add(channel)
    if (this.send({
      type: 'subscribe',
      channel: channel
    })) {
      this.emit('subscribed', { channel })
    }
  }

  /**
   * 取消订阅频道
   * @param {string} channel - 频道名称
   */
  unsubscribe(channel) {
    this.subscribedChannels.delete(channel)
    if (this.send({
      type: 'unsubscribe',
      channel: channel
    })) {
      this.emit('unsubscribed', { channel })
    }
  }

  /**
   * 启动心跳检测
   */
  startHeartbeat() {
    this.stopHeartbeat() // 清除可能存在的旧定时器
    
    this.heartbeatInterval = setInterval(() => {
      if (this.connectionStatus === 'connected') {
        this.ping()
        
        // 检查心跳超时
        if (this.lastHeartbeat && (new Date() - this.lastHeartbeat > this.heartbeatTimeout)) {
          console.warn('⚠️ 心跳超时，准备重连')
          this.connectionStatus = 'reconnecting'
          this.emit('statusChange', { status: this.connectionStatus })
          this.disconnect()
        }
      }
    }, 10000) // 每10秒发送一次心跳
  }

  /**
   * 停止心跳检测
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 发送心跳
   */
  ping() {
    this.send({ type: 'ping' })
  }

  /**
   * 获取连接状态
   */
  getStatus() {
    this.send({ type: 'get_status' })
  }

  /**
   * 添加事件监听器
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   */
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event).push(callback)
  }

  /**
   * 移除事件监听器
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   */
  off(event, callback) {
    if (this.eventListeners.has(event)) {
      const listeners = this.eventListeners.get(event)
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  /**
   * 触发事件
   * @param {string} event - 事件名称
   * @param {*} data - 事件数据
   */
  emit(event, data) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`❌ 事件监听器错误 (${event}):`, error)
        }
      })
    }
  }

  /**
   * 尝试重连
   */
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.token) {
      this.reconnectAttempts++
      this.connectionStatus = 'reconnecting'
      console.log(`🔄 尝试重连 WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      this.emit('reconnecting', { 
        attempt: this.reconnectAttempts, 
        maxAttempts: this.maxReconnectAttempts,
        delay: this.reconnectDelay * this.reconnectAttempts
      })
      this.emit('statusChange', { status: this.connectionStatus })
      
      setTimeout(() => {
        this.connect(this.token)
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('❌ WebSocket 重连失败，已达到最大重试次数')
      this.connectionStatus = 'disconnected'
      this.emit('reconnectFailed', { 
        attempts: this.reconnectAttempts,
        maxAttempts: this.maxReconnectAttempts
      })
      this.emit('statusChange', { status: this.connectionStatus })
    }
  }

  /**
   * 获取连接状态
   * @returns {string} 连接状态
   */
  getConnectionStatus() {
    return this.connectionStatus
  }

  /**
   * 获取连接统计信息
   * @returns {Object} 统计信息
   */
  getConnectionStats() {
    return {
      ...this.connectionStats,
      subscribedChannels: Array.from(this.subscribedChannels),
      connectionStatus: this.connectionStatus,
      lastHeartbeat: this.lastHeartbeat,
      uptime: this.connectionStats.connectedAt ? 
        new Date() - this.connectionStats.connectedAt : 0
    }
  }

  /**
   * 清理所有事件监听器
   */
  clearAllListeners() {
    this.eventListeners.clear()
  }

  /**
   * 重置连接统计
   */
  resetStats() {
    this.connectionStats = {
      connectedAt: null,
      reconnectCount: 0,
      messagesReceived: 0,
      messagesSent: 0,
      lastError: null
    }
    this.reconnectAttempts = 0
  }
}

// 全局WebSocket实例
export const websocketManager = new WebSocketManager() 