<template>
  <div class="chat-page">
    <div class="chat-header">
      <div class="header-title">
        <el-icon><ChatDotRound /></el-icon>
        <h2>AI 智能助手</h2>
      </div>
      <div class="header-actions">
        <el-button @click="clearConversationHistory" type="danger" plain>
          <el-icon><Delete /></el-icon>
          清空对话
        </el-button>
      </div>
    </div>

    <div class="chat-container">
      <div class="messages-area" ref="messagesArea">
        <div v-if="messages.length === 0" class="welcome-message">
          <el-icon class="welcome-icon"><Avatar /></el-icon>
          <h3>欢迎使用 GitHub Sentinel AI 助手</h3>
          <p>我可以帮您分析代码仓库、生成报告、解答问题等</p>
          <div class="quick-actions">
            <el-button 
              v-for="action in quickActions" 
              :key="action.text"
              @click="sendQuickMessage(action.message)"
              type="primary" 
              plain
            >
              {{ action.text }}
            </el-button>
          </div>
        </div>
        
                  <div v-for="message in messages" :key="message.id" class="message-item">
            <div :class="['message-bubble', message.sender]">
              <div class="message-avatar">
                <el-icon v-if="message.sender === 'user'"><User /></el-icon>
                <el-icon v-else><Avatar /></el-icon>
              </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.text)"></div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="isLoading" class="message-item">
          <div class="message-bubble assistant">
            <div class="message-avatar">
              <el-icon class="loading-icon"><Loading /></el-icon>
            </div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="input-area">
        <div class="input-container">
          <el-input
            v-model="currentMessage"
            @keydown.enter="sendMessage"
            @keydown.ctrl.enter="sendMessage"
            placeholder="请输入您的问题... (Ctrl+Enter 发送)"
            type="textarea"
            :rows="3"
            resize="none"
            :disabled="isLoading"
            maxlength="2000"
            show-word-limit
          />
          <div class="input-actions">
            <el-upload
              :before-upload="handleFileUpload"
              :show-file-list="false"
              accept=".txt,.md,.json,.log"
            >
              <el-button type="text">
                <el-icon><Paperclip /></el-icon>
              </el-button>
            </el-upload>
            <el-button 
              @click="sendMessage" 
              type="primary" 
              :loading="isLoading"
              :disabled="!currentMessage.trim()"
            >
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ChatDotRound, 
  Delete, 
  User, 
  Avatar, 
  Loading, 
  Paperclip, 
  Promotion 
} from '@element-plus/icons-vue'
import { chatWithAI, clearConversation } from '@/api/llm'

const messages = ref([])
const currentMessage = ref('')
const isLoading = ref(false)
const messagesArea = ref(null)

const quickActions = ref([
  { text: '分析仓库活动', message: '请帮我分析最近的仓库活动趋势' },
  { text: '生成代码报告', message: '请为我生成一份详细的代码质量报告' },
  { text: '监控建议', message: '请给我一些仓库监控的最佳实践建议' },
  { text: '性能分析', message: '帮我分析项目的性能瓶颈和优化建议' }
])

let messageIdCounter = 0

onMounted(() => {
  // 初始化时可以加载历史消息
  loadConversationHistory()
})

const formatMessage = (text) => {
  // 简单的Markdown渲染
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const addMessage = (text, sender = 'user') => {
  const message = {
    id: messageIdCounter++,
    text,
    sender,
    timestamp: new Date().toISOString()
  }
  messages.value.push(message)
  scrollToBottom()
  return message
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || isLoading.value) return
  
  const userMessage = currentMessage.value.trim()
  currentMessage.value = ''
  
  // 添加用户消息
  addMessage(userMessage, 'user')
  
  try {
    isLoading.value = true
    
    // 调用AI接口
    const response = await chatWithAI({
      message: userMessage,
      context_data: {
        conversation_id: 'web-chat',
        source: 'web-interface'
      }
    })
    
    // 添加AI回复
    addMessage(response.response, 'assistant')
    
  } catch (error) {
    console.error('AI对话失败:', error)
    addMessage('抱歉，我暂时无法回答您的问题。请稍后再试。', 'assistant')
    ElMessage.error('AI对话失败，请检查网络连接')
  } finally {
    isLoading.value = false
  }
}

const sendQuickMessage = (message) => {
  currentMessage.value = message
  sendMessage()
}

const clearConversationHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空当前对话吗？此操作无法撤销。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    messages.value = []
    await clearConversation()
    ElMessage.success('对话已清空')
    
  } catch (error) {
    if (error === 'cancel') return
    console.error('清空对话失败:', error)
    ElMessage.error('清空对话失败')
  }
}

const loadConversationHistory = async () => {
  // 这里可以加载历史对话记录
  // const history = await getConversationHistory()
}

const handleFileUpload = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const fileContent = e.target.result
    const message = `请分析以下文件内容：\n\n文件名：${file.name}\n\n内容：\n${fileContent}`
    currentMessage.value = message
  }
  reader.readAsText(file)
  return false // 阻止自动上传
}
</script>

<style scoped>
.chat-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.header-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.header-title h2 {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  height: 100%;
}

.messages-area {
  flex: 1;
  padding: var(--space-4);
  overflow-y: auto;
  scroll-behavior: smooth;
}

.welcome-message {
  text-align: center;
  padding: var(--space-8);
  color: var(--text-secondary);
}

.welcome-icon {
  font-size: 3rem;
  color: var(--primary-500);
  margin-bottom: var(--space-4);
}

.welcome-message h3 {
  margin: var(--space-4) 0;
  color: var(--text-primary);
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
  margin-top: var(--space-6);
}

.message-item {
  margin-bottom: var(--space-4);
}

.message-bubble {
  display: flex;
  gap: var(--space-3);
  max-width: 80%;
}

.message-bubble.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-bubble.assistant {
  margin-right: auto;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-bubble.user .message-avatar {
  background: var(--primary-500);
  color: white;
}

.message-bubble.assistant .message-avatar {
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  background: var(--bg-card);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--border-radius);
  margin-bottom: var(--space-1);
  word-wrap: break-word;
  line-height: 1.5;
}

.message-bubble.user .message-text {
  background: var(--primary-500);
  color: white;
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: right;
}

.message-bubble.assistant .message-time {
  text-align: left;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-card);
  border-radius: var(--border-radius);
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  30% {
    opacity: 1;
    transform: scale(1);
  }
}

.input-area {
  padding: var(--space-4);
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
}

.input-container {
  position: relative;
}

.input-actions {
  position: absolute;
  bottom: var(--space-2);
  right: var(--space-2);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

:deep(.el-textarea__inner) {
  padding-bottom: 40px !important;
}

:deep(code) {
  background: var(--bg-secondary);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
}
</style> 