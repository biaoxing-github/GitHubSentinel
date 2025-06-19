<template>
  <div class="notification-rules">
    <div class="page-header">
      <h1>通知规则管理</h1>
      <p>配置和管理各种类型的通知规则</p>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        创建规则
      </el-button>
      <el-button @click="refreshRules" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 规则列表 -->
    <el-card>
      <el-table 
        :data="filteredRules" 
        v-loading="loading"
        empty-text="暂无通知规则"
      >
        <el-table-column prop="rule_id" label="规则ID" width="200" show-overflow-tooltip />
        
        <el-table-column prop="rule_type" label="规则类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getRuleTypeTag(row.rule_type)">
              {{ getRuleTypeName(row.rule_type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="触发条件" min-width="200">
          <template #default="{ row }">
            <div class="conditions">
              <el-tag 
                v-for="(value, key) in row.conditions" 
                :key="key"
                size="small"
                style="margin: 2px;"
              >
                {{ key }}: {{ formatConditionValue(value) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="执行动作" min-width="200">
          <template #default="{ row }">
            <div class="actions">
              <el-tag 
                v-if="row.actions.websocket_notify"
                type="info"
                size="small"
                style="margin: 2px;"
              >
                WebSocket通知
              </el-tag>
              <el-tag 
                v-if="row.actions.email_notify"
                type="success"
                size="small"
                style="margin: 2px;"
              >
                邮件通知
              </el-tag>
              <el-tag 
                v-if="row.actions.external_notify && row.actions.external_notify.length > 0"
                type="warning"
                size="small"
                style="margin: 2px;"
              >
                外部通知({{ row.actions.external_notify.length }})
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-switch 
              v-model="row.enabled" 
              @change="toggleRule(row)"
              :loading="row.updating"
            />
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editRule(row)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="deleteRule(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑规则对话框 -->
    <el-dialog 
      :title="editingRule ? '编辑规则' : '创建规则'"
      v-model="dialogVisible"
      width="600px"
      :before-close="handleDialogClose"
    >
      <el-form 
        :model="ruleForm" 
        :rules="ruleFormRules"
        ref="ruleFormRef"
        label-width="100px"
      >
        <el-form-item label="规则类型" prop="rule_type">
          <el-select v-model="ruleForm.rule_type" placeholder="请选择规则类型" style="width: 100%">
            <el-option label="活动通知" value="activity" />
            <el-option label="阈值监控" value="threshold" />
            <el-option label="定时任务" value="schedule" />
            <el-option label="AI洞察" value="ai_insight" />
          </el-select>
        </el-form-item>

        <el-form-item label="触发条件" prop="conditions">
          <el-card shadow="never" style="width: 100%;">
            <div v-if="ruleForm.rule_type === 'activity'">
              <el-form-item label="仓库名称">
                <el-input v-model="ruleForm.conditions.repository" placeholder="留空表示所有仓库" />
              </el-form-item>
              <el-form-item label="活动类型">
                <el-select v-model="ruleForm.conditions.activity_types" multiple placeholder="选择活动类型">
                  <el-option label="Push" value="push" />
                  <el-option label="Pull Request" value="pull_request" />
                  <el-option label="Issue" value="issue" />
                  <el-option label="Release" value="release" />
                </el-select>
              </el-form-item>
            </div>

            <div v-else-if="ruleForm.rule_type === 'threshold'">
              <el-form-item label="监控指标">
                <el-select v-model="ruleForm.conditions.metric" placeholder="选择监控指标">
                  <el-option label="响应时间" value="response_time" />
                  <el-option label="错误率" value="error_rate" />
                  <el-option label="请求量" value="request_count" />
                </el-select>
              </el-form-item>
              <el-form-item label="阈值">
                <el-input-number v-model="ruleForm.conditions.threshold" :min="0" />
              </el-form-item>
              <el-form-item label="比较方式">
                <el-select v-model="ruleForm.conditions.operator">
                  <el-option label="大于" value="gt" />
                  <el-option label="小于" value="lt" />
                  <el-option label="等于" value="eq" />
                </el-select>
              </el-form-item>
            </div>

            <div v-else-if="ruleForm.rule_type === 'schedule'">
              <el-form-item label="时间间隔">
                <el-input v-model="ruleForm.conditions.interval" placeholder="如: 1h, 30m, 24h" />
              </el-form-item>
              <el-form-item label="执行时间">
                <el-time-picker 
                  v-model="ruleForm.conditions.time"
                  format="HH:mm"
                  placeholder="选择执行时间"
                />
              </el-form-item>
            </div>

            <div v-else-if="ruleForm.rule_type === 'ai_insight'">
              <el-form-item label="洞察类型">
                <el-select v-model="ruleForm.conditions.insight_types" multiple>
                  <el-option label="趋势分析" value="trend" />
                  <el-option label="异常检测" value="anomaly" />
                  <el-option label="性能建议" value="performance" />
                </el-select>
              </el-form-item>
              <el-form-item label="置信度阈值">
                <el-slider v-model="ruleForm.conditions.confidence" :min="0" :max="100" show-stops />
              </el-form-item>
            </div>
          </el-card>
        </el-form-item>

        <el-form-item label="执行动作" prop="actions">
          <el-card shadow="never" style="width: 100%;">
            <el-checkbox v-model="ruleForm.actions.websocket_notify">WebSocket实时通知</el-checkbox>
            <el-checkbox v-model="ruleForm.actions.email_notify">邮件通知</el-checkbox>
            
            <el-form-item label="外部通知" style="margin-top: 15px;">
              <el-checkbox-group v-model="ruleForm.actions.external_notify">
                <el-checkbox label="wechat">微信</el-checkbox>
                <el-checkbox label="dingtalk">钉钉</el-checkbox>
                <el-checkbox label="telegram">Telegram</el-checkbox>
                <el-checkbox label="discord">Discord</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-card>
        </el-form-item>

        <el-form-item label="启用状态">
          <el-switch v-model="ruleForm.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleDialogClose">取消</el-button>
        <el-button type="primary" @click="saveRule" :loading="saving">
          {{ editingRule ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { 
  createNotificationRule, 
  getNotificationRules, 
  updateNotificationRule,
  deleteNotificationRule 
} from '@/api/llm'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingRule = ref(null)
const ruleFormRef = ref(null)

const rules = ref([])
const filteredRules = computed(() => rules.value)

// 表单数据
const ruleForm = reactive({
  rule_type: '',
  conditions: {},
  actions: {
    websocket_notify: true,
    email_notify: false,
    external_notify: []
  },
  enabled: true
})

// 表单验证规则
const ruleFormRules = {
  rule_type: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ]
}

// 方法
const getRuleTypeTag = (type) => {
  const tagMap = {
    'activity': 'primary',
    'threshold': 'warning',
    'schedule': 'info',
    'ai_insight': 'success'
  }
  return tagMap[type] || 'info'
}

const getRuleTypeName = (type) => {
  const nameMap = {
    'activity': '活动通知',
    'threshold': '阈值监控',
    'schedule': '定时任务',
    'ai_insight': 'AI洞察'
  }
  return nameMap[type] || type
}

const formatConditionValue = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return String(value)
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const resetForm = () => {
  Object.assign(ruleForm, {
    rule_type: '',
    conditions: {},
    actions: {
      websocket_notify: true,
      email_notify: false,
      external_notify: []
    },
    enabled: true
  })
}

const showCreateDialog = () => {
  editingRule.value = null
  resetForm()
  dialogVisible.value = true
}

const editRule = (rule) => {
  editingRule.value = rule
  Object.assign(ruleForm, {
    rule_type: rule.rule_type,
    conditions: { ...rule.conditions },
    actions: { ...rule.actions },
    enabled: rule.enabled
  })
  dialogVisible.value = true
}

const handleDialogClose = () => {
  dialogVisible.value = false
  editingRule.value = null
  resetForm()
  ruleFormRef.value?.clearValidate()
}

const saveRule = async () => {
  try {
    await ruleFormRef.value?.validate()
    saving.value = true

    const ruleData = {
      rule_type: ruleForm.rule_type,
      conditions: ruleForm.conditions,
      actions: ruleForm.actions,
      enabled: ruleForm.enabled
    }

    if (editingRule.value) {
      // 更新规则
      await updateNotificationRule(editingRule.value.rule_id, ruleData)
      ElMessage.success('规则更新成功')
    } else {
      // 创建规则
      await createNotificationRule(ruleData)
      ElMessage.success('规则创建成功')
    }

    handleDialogClose()
    refreshRules()
  } catch (error) {
    console.error('保存规则失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存规则失败')
  } finally {
    saving.value = false
  }
}

const toggleRule = async (rule) => {
  rule.updating = true
  try {
    await updateNotificationRule(rule.rule_id, {
      enabled: rule.enabled
    })
    ElMessage.success(`规则已${rule.enabled ? '启用' : '禁用'}`)
  } catch (error) {
    console.error('更新规则状态失败:', error)
    rule.enabled = !rule.enabled // 回滚状态
    ElMessage.error('更新规则状态失败')
  } finally {
    rule.updating = false
  }
}

const deleteRule = async (rule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则 "${rule.rule_id}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteNotificationRule(rule.rule_id)
    ElMessage.success('规则删除成功')
    refreshRules()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除规则失败:', error)
      ElMessage.error('删除规则失败')
    }
  }
}

const refreshRules = async () => {
  loading.value = true
  try {
    const response = await getNotificationRules()
    rules.value = response.data || []
  } catch (error) {
    console.error('获取规则列表失败:', error)
    ElMessage.error('获取规则列表失败')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  refreshRules()
})
</script>

<style scoped>
.notification-rules {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
}

.conditions,
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.el-form-item {
  margin-bottom: 15px;
}

.el-card :deep(.el-card__body) {
  padding: 15px;
}

@media (max-width: 768px) {
  .notification-rules {
    padding: 12px;
  }
  
  .toolbar {
    flex-direction: column;
  }
  
  .el-dialog {
    width: 95% !important;
    margin: 5vh auto;
  }
}
</style> 