<template>
  <div class="ai-chat">
    <div class="chat-header">
      <h2>🤖 AI 智能分析助手</h2>
      <div class="header-actions">
        <el-button 
          type="primary" 
          size="small" 
          @click="clearConversation"
          :loading="isClearing"
        >
          清空对话
        </el-button>
        <el-dropdown @command="handleAnalysisType">
          <el-button type="info" size="small">
            分析类型 <el-icon><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="comprehensive">综合分析</el-dropdown-item>
              <el-dropdown-item command="security">安全分析</el-dropdown-item>
              <el-dropdown-item command="performance">性能分析</el-dropdown-item>
              <el-dropdown-item command="quality">质量分析</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="chat-container" ref="chatContainer">
      <div class="chat-messages">
        <div 
          v-for="message in messages" 
          :key="message.id" 
          :class="['message', message.type]"
        >
          <div class="message-avatar">
            <el-icon v-if="message.type === 'user'"><user /></el-icon>
            <el-icon v-else><robot /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(message.content)"></div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        
        <div v-if="isLoading" class="message ai typing">
          <div class="message-avatar">
            <el-icon><robot /></el-icon>
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

    <div class="chat-input-container">
      <div class="context-selector" v-if="showContextSelector">
        <el-select 
          v-model="selectedRepository" 
          placeholder="选择仓库作为上下文"
          clearable
          size="small"
        >
          <el-option
            v-for="repo in repositories"
            :key="repo.repository"
            :label="repo.repository"
            :value="repo.repository"
          />
        </el-select>
      </div>
      
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入您的问题或选择仓库进行分析..."
          @keydown.enter.prevent="handleEnter"
          :disabled="isLoading"
        />
        
        <div class="input-actions">
          <el-button 
            size="small" 
            @click="toggleContextSelector"
          >
            <el-icon><setting /></el-icon>
            上下文
          </el-button>
          
          <el-button 
            type="primary" 
            @click="sendMessage"
            :loading="isLoading"
            :disabled="!inputMessage.trim()"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>

    <!-- 快速分析按钮 -->
    <div class="quick-analysis" v-if="repositories.length > 0">
      <h3>快速分析</h3>
      <div class="quick-buttons">
        <el-button 
          v-for="repo in repositories.slice(0, 3)" 
          :key="repo.repository"
          size="small"
          @click="quickAnalyze(repo.repository)"
          :loading="isAnalyzing === repo.repository"
        >
          分析 {{ repo.repository }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, User, Robot, Setting } from '@element-plus/icons-vue'
import { getSubscriptions } from '@/api/subscriptions'
import { chatWithAI, analyzeRepository, clearConversation as clearAIConversation } from '@/api/llm'

// 响应式数据
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const isClearing = ref(false)
const isAnalyzing = ref('')
const repositories = ref([])
const selectedRepository = ref('')
const showContextSelector = ref(false)
const analysisType = ref('comprehensive')
const chatContainer = ref(null)

// 计算属性
const hasMessages = computed(() => messages.value.length > 0)

// 方法
const loadRepositories = async () => {
  try {
    const response = await getSubscriptions()
    repositories.value = response.data || []
  } catch (error) {
    console.error('加载仓库列表失败:', error)
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = {
    id: Date.now(),
    type: 'user',
    content: inputMessage.value,
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  
  const messageText = inputMessage.value
  inputMessage.value = ''
  isLoading.value = true

  scrollToBottom()

  try {
    // 构建上下文数据
    let contextData = null
    if (selectedRepository.value) {
      contextData = {
        repository: { name: selectedRepository.value },
        analysis_request: true
      }
    }

    const response = await chatWithAI({
      message: messageText,
      context_data: contextData,
      stream: false
    })

    const aiMessage = {
      id: Date.now(),
      type: 'ai',
      content: response.response,
      timestamp: new Date()
    }

    messages.value.push(aiMessage)
    scrollToBottom()

  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败，请重试')
    
    const errorMessage = {
      id: Date.now(),
      type: 'ai',
      content: '抱歉，我暂时无法回复您的消息。请稍后重试。',
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const quickAnalyze = async (repository) => {
  isAnalyzing.value = repository
  
  try {
    const response = await analyzeRepository({
      repository: repository,
      analysis_type: analysisType.value,
      timeframe: '30d'
    })

    const analysisMessage = {
      id: Date.now(),
      type: 'ai',
      content: `## ${repository} ${getAnalysisTypeText(analysisType.value)}结果\n\n${response.analysis.analysis}`,
      timestamp: new Date()
    }

    messages.value.push(analysisMessage)
    scrollToBottom()

    ElMessage.success('分析完成')

  } catch (error) {
    console.error('快速分析失败:', error)
    ElMessage.error('分析失败，请重试')
  } finally {
    isAnalyzing.value = ''
  }
}

const clearConversation = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有对话记录吗？', '确认操作', {
      type: 'warning'
    })

    isClearing.value = true
    await clearAIConversation()
    messages.value = []
    ElMessage.success('对话已清空')

  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空对话失败:', error)
      ElMessage.error('清空对话失败')
    }
  } finally {
    isClearing.value = false
  }
}

const handleAnalysisType = (type) => {
  analysisType.value = type
  ElMessage.info(`已切换到${getAnalysisTypeText(type)}模式`)
}

const getAnalysisTypeText = (type) => {
  const typeMap = {
    comprehensive: '综合分析',
    security: '安全分析',
    performance: '性能分析',
    quality: '质量分析'
  }
  return typeMap[type] || '综合分析'
}

const toggleContextSelector = () => {
  showContextSelector.value = !showContextSelector.value
}

const handleEnter = (event) => {
  if (!event.shiftKey) {
    sendMessage()
  }
}

const formatMessage = (content) => {
  // 简单的Markdown渲染
  return content
    .replace(/### (.*)/g, '<h3>$1</h3>')
    .replace(/## (.*)/g, '<h2>$1</h2>')
    .replace(/# (.*)/g, '<h1>$1</h1>')
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

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 生命周期
onMounted(() => {
  loadRepositories()
  
  // 添加欢迎消息
  messages.value.push({
    id: 1,
    type: 'ai',
    content: '您好！我是 GitHubSentinel 的 AI 分析助手。我可以帮您：\n\n• 分析 GitHub 仓库的活动和趋势\n• 回答代码和项目相关问题\n• 提供开发建议和最佳实践\n• 解释技术概念和代码模式\n\n请选择一个仓库或直接向我提问！',
    timestamp: new Date()
  })
})
</script>

<style scoped>
.ai-chat {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.chat-header {
  background: white;
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.chat-messages {
  max-width: 800px;
  margin: 0 auto;
}

.message {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 10px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #409eff;
  color: white;
}

.message.ai .message-avatar {
  background: #67c23a;
  color: white;
}

.message-content {
  max-width: 70%;
  background: white;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

.message-text {
  line-height: 1.6;
  word-break: break-word;
}

.message-text :deep(h1),
.message-text :deep(h2), 
.message-text :deep(h3) {
  margin: 10px 0 5px 0;
  color: inherit;
}

.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', monospace;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 5px;
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  height: 20px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

.chat-input-container {
  background: white;
  border-top: 1px solid #e4e7ed;
  padding: 20px;
}

.context-selector {
  margin-bottom: 15px;
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quick-analysis {
  background: white;
  margin: 20px;
  padding: 20px;
  border-radius: 8px;
  border-top: 1px solid #e4e7ed;
}

.quick-analysis h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.quick-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    padding: 15px;
  }
  
  .chat-container {
    padding: 15px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .chat-input-container {
    padding: 15px;
  }
  
  .quick-analysis {
    margin: 15px;
    padding: 15px;
  }
}
</style> 