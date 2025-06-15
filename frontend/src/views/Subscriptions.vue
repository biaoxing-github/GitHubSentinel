<template>
  <div class="subscriptions">
    <div class="page-header">
      <h1>订阅管理</h1>
      <el-button type="primary" @click="showAddDialog = true">
        <i class="el-icon-plus"></i> 添加订阅
      </el-button>
    </div>

    <div class="subscriptions-content">
      <el-table :data="subscriptions" style="width: 100%" v-loading="loading">
        <el-table-column prop="repository" label="仓库" width="200">
          <template #default="scope">
            <el-link :href="`https://github.com/${scope.row.repository}`" target="_blank">
              {{ scope.row.repository }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="frequency" label="频率" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.frequency === 'daily' ? 'success' : 'info'">
              {{ scope.row.frequency === 'daily' ? '每日' : '每周' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
              {{ scope.row.status === 'active' ? '激活' : '暂停' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="监控选项" width="200">
          <template #default="scope">
            <div class="monitor-options">
              <el-tag v-if="scope.row.monitor_commits" size="small" type="info">提交</el-tag>
              <el-tag v-if="scope.row.monitor_issues" size="small" type="warning">问题</el-tag>
              <el-tag v-if="scope.row.monitor_pull_requests" size="small" type="success">PR</el-tag>
              <el-tag v-if="scope.row.monitor_releases" size="small" type="danger">发布</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editSubscription(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteSubscription(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加订阅对话框 -->
    <el-dialog v-model="showAddDialog" title="添加订阅" width="600px">
      <el-form :model="newSubscription" label-width="120px" :rules="subscriptionRules" ref="addFormRef">
        <el-form-item label="仓库" prop="repository">
          <el-input v-model="newSubscription.repository" placeholder="例如: langchain-ai/langchain"/>
        </el-form-item>
        <el-form-item label="频率" prop="frequency">
          <el-select v-model="newSubscription.frequency" placeholder="请选择频率">
            <el-option label="每日" value="daily"/>
            <el-option label="每周" value="weekly"/>
          </el-select>
        </el-form-item>
        <el-form-item label="监控选项">
          <el-checkbox-group v-model="monitorOptions">
            <el-checkbox label="monitor_commits">提交</el-checkbox>
            <el-checkbox label="monitor_issues">问题</el-checkbox>
            <el-checkbox label="monitor_pull_requests">拉取请求</el-checkbox>
            <el-checkbox label="monitor_releases">发布</el-checkbox>
            <el-checkbox label="monitor_discussions">讨论</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addSubscription" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑订阅对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑订阅" width="600px">
      <el-form :model="editingSubscription" label-width="120px" :rules="subscriptionRules" ref="editFormRef">
        <el-form-item label="仓库">
          <el-input v-model="editingSubscription.repository" disabled/>
        </el-form-item>
        <el-form-item label="频率" prop="frequency">
          <el-select v-model="editingSubscription.frequency" placeholder="请选择频率">
            <el-option label="每日" value="daily"/>
            <el-option label="每周" value="weekly"/>
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="editingSubscription.status" placeholder="请选择状态">
            <el-option label="激活" value="active"/>
            <el-option label="暂停" value="paused"/>
          </el-select>
        </el-form-item>
        <el-form-item label="监控选项">
          <el-checkbox-group v-model="editMonitorOptions">
            <el-checkbox label="monitor_commits">提交</el-checkbox>
            <el-checkbox label="monitor_issues">问题</el-checkbox>
            <el-checkbox label="monitor_pull_requests">拉取请求</el-checkbox>
            <el-checkbox label="monitor_releases">发布</el-checkbox>
            <el-checkbox label="monitor_discussions">讨论</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <!-- 通知配置 -->
        <el-divider content-position="left">通知配置</el-divider>
        
        <el-form-item label="邮件通知">
          <el-switch v-model="editingSubscription.enable_email_notification"/>
        </el-form-item>
        
        <el-form-item label="通知邮箱" v-if="editingSubscription.enable_email_notification">
          <div style="width: 100%;">
            <el-tag
              v-for="(email, index) in editingSubscription.notification_emails"
              :key="index"
              closable
              @close="removeEmail(index)"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              {{ email }}
            </el-tag>
            <el-input
              v-if="showEmailInput"
              ref="emailInputRef"
              v-model="newEmail"
              size="small"
              style="width: 200px; margin-right: 8px;"
              placeholder="输入邮箱地址"
              @keyup.enter="addEmail"
              @blur="addEmail"
            />
            <el-button v-else size="small" @click="showEmailInput = true">+ 添加邮箱</el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="Slack通知">
          <el-switch v-model="editingSubscription.enable_slack_notification"/>
        </el-form-item>
        
        <el-form-item label="Slack Webhook" v-if="editingSubscription.enable_slack_notification">
          <div style="width: 100%;">
            <el-tag
              v-for="(webhook, index) in editingSubscription.notification_slack_webhooks"
              :key="index"
              closable
              @close="removeSlackWebhook(index)"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              {{ webhook.substring(0, 50) }}...
            </el-tag>
            <el-input
              v-if="showSlackInput"
              ref="slackInputRef"
              v-model="newSlackWebhook"
              size="small"
              style="width: 300px; margin-right: 8px;"
              placeholder="输入Slack Webhook URL"
              @keyup.enter="addSlackWebhook"
              @blur="addSlackWebhook"
            />
            <el-button v-else size="small" @click="showSlackInput = true">+ 添加Webhook</el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="自定义Webhook">
          <el-switch v-model="editingSubscription.enable_webhook_notification"/>
        </el-form-item>
        
        <el-form-item label="Webhook URL" v-if="editingSubscription.enable_webhook_notification">
          <div style="width: 100%;">
            <el-tag
              v-for="(webhook, index) in editingSubscription.notification_custom_webhooks"
              :key="index"
              closable
              @close="removeCustomWebhook(index)"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              {{ webhook.substring(0, 50) }}...
            </el-tag>
            <el-input
              v-if="showWebhookInput"
              ref="webhookInputRef"
              v-model="newCustomWebhook"
              size="small"
              style="width: 300px; margin-right: 8px;"
              placeholder="输入自定义Webhook URL"
              @keyup.enter="addCustomWebhook"
              @blur="addCustomWebhook"
            />
            <el-button v-else size="small" @click="showWebhookInput = true">+ 添加Webhook</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateSubscription" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { subscriptionAPI } from '@/api'

export default {
  name: 'Subscriptions',
  setup() {
    const subscriptions = ref([])
    const loading = ref(false)
    const submitting = ref(false)
    const showAddDialog = ref(false)
    const showEditDialog = ref(false)
    const addFormRef = ref(null)
    const editFormRef = ref(null)
    
    const newSubscription = ref({
      repository: '',
      frequency: 'daily'
    })
    
    const editingSubscription = ref({
      id: null,
      repository: '',
      frequency: 'daily',
      status: 'active',
      enable_email_notification: true,
      enable_slack_notification: false,
      enable_webhook_notification: false,
      notification_emails: [],
      notification_slack_webhooks: [],
      notification_custom_webhooks: []
    })
    
    const monitorOptions = ref(['monitor_commits', 'monitor_issues', 'monitor_pull_requests', 'monitor_releases'])
    const editMonitorOptions = ref([])
    
    // 通知配置相关
    const showEmailInput = ref(false)
    const showSlackInput = ref(false)
    const showWebhookInput = ref(false)
    const newEmail = ref('')
    const newSlackWebhook = ref('')
    const newCustomWebhook = ref('')
    const emailInputRef = ref(null)
    const slackInputRef = ref(null)
    const webhookInputRef = ref(null)
    
    const subscriptionRules = reactive({
      repository: [
        { required: true, message: '请输入仓库名称', trigger: 'blur' },
        { pattern: /^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/, message: '请输入正确的仓库格式，如: owner/repo', trigger: 'blur' }
      ],
      frequency: [
        { required: true, message: '请选择频率', trigger: 'change' }
      ]
    })

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString('zh-CN')
    }

    const loadSubscriptions = async () => {
      loading.value = true
      try {
        console.log('开始加载订阅数据...')
        const response = await subscriptionAPI.getSubscriptions()
        console.log('订阅数据响应:', response)
        
        subscriptions.value = response.subscriptions || response || []
        ElMessage.success(`加载了 ${subscriptions.value.length} 个订阅`)
      } catch (error) {
        console.error('加载订阅数据失败:', error)
        ElMessage.error(`加载订阅数据失败: ${error.message}`)
        subscriptions.value = []
      } finally {
        loading.value = false
      }
    }

    const addSubscription = async () => {
      if (!addFormRef.value) return
      
      try {
        await addFormRef.value.validate()
      } catch {
        return
      }

      submitting.value = true
      try {
        console.log('开始添加订阅:', newSubscription.value)
        
        const subscriptionData = {
          user_id: 1, // 临时使用固定用户ID
          repository: newSubscription.value.repository,
          frequency: newSubscription.value.frequency,
          monitor_commits: monitorOptions.value.includes('monitor_commits'),
          monitor_issues: monitorOptions.value.includes('monitor_issues'),
          monitor_pull_requests: monitorOptions.value.includes('monitor_pull_requests'),
          monitor_releases: monitorOptions.value.includes('monitor_releases'),
          monitor_discussions: monitorOptions.value.includes('monitor_discussions')
        }
        
        const response = await subscriptionAPI.createSubscription(subscriptionData)
        console.log('添加订阅响应:', response)
        
        showAddDialog.value = false
        newSubscription.value = {
          repository: '',
          frequency: 'daily'
        }
        monitorOptions.value = ['monitor_commits', 'monitor_issues', 'monitor_pull_requests', 'monitor_releases']
        
        ElMessage.success('添加订阅成功')
        await loadSubscriptions()
        
      } catch (error) {
        console.error('添加订阅失败:', error)
        ElMessage.error(`添加订阅失败: ${error.message}`)
      } finally {
        submitting.value = false
      }
    }

    const editSubscription = (subscription) => {
      editingSubscription.value = {
        id: subscription.id,
        repository: subscription.repository,
        frequency: subscription.frequency,
        status: subscription.status,
        enable_email_notification: subscription.enable_email_notification ?? true,
        enable_slack_notification: subscription.enable_slack_notification ?? false,
        enable_webhook_notification: subscription.enable_webhook_notification ?? false,
        notification_emails: subscription.notification_emails ? JSON.parse(subscription.notification_emails) : [],
        notification_slack_webhooks: subscription.notification_slack_webhooks ? JSON.parse(subscription.notification_slack_webhooks) : [],
        notification_custom_webhooks: subscription.notification_custom_webhooks ? JSON.parse(subscription.notification_custom_webhooks) : []
      }
      
      // 设置监控选项
      editMonitorOptions.value = []
      if (subscription.monitor_commits) editMonitorOptions.value.push('monitor_commits')
      if (subscription.monitor_issues) editMonitorOptions.value.push('monitor_issues')
      if (subscription.monitor_pull_requests) editMonitorOptions.value.push('monitor_pull_requests')
      if (subscription.monitor_releases) editMonitorOptions.value.push('monitor_releases')
      if (subscription.monitor_discussions) editMonitorOptions.value.push('monitor_discussions')
      
      showEditDialog.value = true
    }

    const updateSubscription = async () => {
      if (!editFormRef.value) return
      
      try {
        await editFormRef.value.validate()
      } catch {
        return
      }

      submitting.value = true
      try {
        const updateData = {
          frequency: editingSubscription.value.frequency,
          status: editingSubscription.value.status,
          monitor_commits: editMonitorOptions.value.includes('monitor_commits'),
          monitor_issues: editMonitorOptions.value.includes('monitor_issues'),
          monitor_pull_requests: editMonitorOptions.value.includes('monitor_pull_requests'),
          monitor_releases: editMonitorOptions.value.includes('monitor_releases'),
          monitor_discussions: editMonitorOptions.value.includes('monitor_discussions'),
          enable_email_notification: editingSubscription.value.enable_email_notification,
          enable_slack_notification: editingSubscription.value.enable_slack_notification,
          enable_webhook_notification: editingSubscription.value.enable_webhook_notification,
          notification_emails: editingSubscription.value.notification_emails,
          notification_slack_webhooks: editingSubscription.value.notification_slack_webhooks,
          notification_custom_webhooks: editingSubscription.value.notification_custom_webhooks
        }
        
        await subscriptionAPI.updateSubscription(editingSubscription.value.id, updateData)
        
        showEditDialog.value = false
        ElMessage.success('更新订阅成功')
        await loadSubscriptions()
        
      } catch (error) {
        console.error('更新订阅失败:', error)
        ElMessage.error(`更新订阅失败: ${error.message}`)
      } finally {
        submitting.value = false
      }
    }

    const deleteSubscription = async (subscription) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除订阅 "${subscription.repository}" 吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger'
          }
        )
        
        await subscriptionAPI.deleteSubscription(subscription.id)
        ElMessage.success('删除订阅成功')
        await loadSubscriptions()
        
      } catch (error) {
        if (error === 'cancel') {
          ElMessage.info('已取消删除')
        } else {
          console.error('删除订阅失败:', error)
          ElMessage.error(`删除订阅失败: ${error.message}`)
        }
      }
    }

    // 通知配置方法
    const addEmail = () => {
      if (newEmail.value && newEmail.value.includes('@')) {
        if (!editingSubscription.value.notification_emails.includes(newEmail.value)) {
          editingSubscription.value.notification_emails.push(newEmail.value)
        }
        newEmail.value = ''
        showEmailInput.value = false
      }
    }
    
    const removeEmail = (index) => {
      editingSubscription.value.notification_emails.splice(index, 1)
    }
    
    const addSlackWebhook = () => {
      if (newSlackWebhook.value && newSlackWebhook.value.startsWith('https://hooks.slack.com/')) {
        if (!editingSubscription.value.notification_slack_webhooks.includes(newSlackWebhook.value)) {
          editingSubscription.value.notification_slack_webhooks.push(newSlackWebhook.value)
        }
        newSlackWebhook.value = ''
        showSlackInput.value = false
      }
    }
    
    const removeSlackWebhook = (index) => {
      editingSubscription.value.notification_slack_webhooks.splice(index, 1)
    }
    
    const addCustomWebhook = () => {
      if (newCustomWebhook.value && newCustomWebhook.value.startsWith('http')) {
        if (!editingSubscription.value.notification_custom_webhooks.includes(newCustomWebhook.value)) {
          editingSubscription.value.notification_custom_webhooks.push(newCustomWebhook.value)
        }
        newCustomWebhook.value = ''
        showWebhookInput.value = false
      }
    }
    
    const removeCustomWebhook = (index) => {
      editingSubscription.value.notification_custom_webhooks.splice(index, 1)
    }

    onMounted(() => {
      loadSubscriptions()
    })

    return {
      subscriptions,
      loading,
      submitting,
      showAddDialog,
      showEditDialog,
      addFormRef,
      editFormRef,
      newSubscription,
      editingSubscription,
      monitorOptions,
      editMonitorOptions,
      subscriptionRules,
      // 通知配置
      showEmailInput,
      showSlackInput,
      showWebhookInput,
      newEmail,
      newSlackWebhook,
      newCustomWebhook,
      emailInputRef,
      slackInputRef,
      webhookInputRef,
      // 方法
      formatDate,
      addSubscription,
      editSubscription,
      updateSubscription,
      deleteSubscription,
      addEmail,
      removeEmail,
      addSlackWebhook,
      removeSlackWebhook,
      addCustomWebhook,
      removeCustomWebhook
    }
  }
}
</script>

<style scoped>
.subscriptions {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #333;
}

.subscriptions-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.monitor-options {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.monitor-options .el-tag {
  margin: 0;
}
</style> 