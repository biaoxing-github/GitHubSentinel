<template>
  <div class="settings">
    <div class="container">
      <h1 class="page-title">系统设置</h1>
      
      <div class="settings-content">
        <el-form 
          ref="settingsForm" 
          :model="settings" 
          :rules="rules" 
          label-width="120px"
          v-loading="loading"
        >
          <!-- GitHub 配置 -->
          <el-card class="setting-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <i class="el-icon-setting"></i>
                <span>GitHub 配置</span>
              </div>
            </template>
            
            <el-form-item label="GitHub Token" prop="github_token">
              <el-input 
                v-model="settings.github_token" 
                type="password" 
                placeholder="请输入GitHub个人访问令牌"
                show-password
              />
              <div class="form-tip">用于访问GitHub API，需要repo权限</div>
            </el-form-item>
            
            <el-form-item label="API基础URL" prop="github_api_base_url">
              <el-input 
                v-model="settings.github_api_base_url" 
                placeholder="GitHub API基础URL"
              />
            </el-form-item>
          </el-card>

          <!-- 数据库配置 -->
          <el-card class="setting-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <i class="el-icon-coin"></i>
                <span>数据库配置</span>
              </div>
            </template>
            
            <el-form-item label="数据库URL" prop="database_url">
              <el-input 
                v-model="settings.database_url" 
                placeholder="数据库连接URL"
              />
              <div class="form-tip">支持SQLite、PostgreSQL等</div>
            </el-form-item>
          </el-card>

          <!-- 邮件配置 -->
          <el-card class="setting-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <i class="el-icon-message"></i>
                <span>邮件配置</span>
              </div>
            </template>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="SMTP服务器" prop="smtp_server">
                  <el-input 
                    v-model="settings.smtp_server" 
                    placeholder="smtp.gmail.com"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="SMTP端口" prop="smtp_port">
                  <el-input-number 
                    v-model="settings.smtp_port" 
                    :min="1" 
                    :max="65535"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="smtp_username">
                  <el-input 
                    v-model="settings.smtp_username" 
                    placeholder="邮箱用户名"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="密码" prop="smtp_password">
                  <el-input 
                    v-model="settings.smtp_password" 
                    type="password" 
                    placeholder="邮箱密码或应用密码"
                    show-password
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="启用TLS">
              <el-switch v-model="settings.smtp_use_tls" />
            </el-form-item>
          </el-card>

          <!-- AI 配置 -->
          <el-card class="setting-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <i class="el-icon-cpu"></i>
                <span>AI 配置</span>
              </div>
            </template>
            
            <el-form-item label="OpenAI API Key" prop="openai_api_key">
              <el-input 
                v-model="settings.openai_api_key" 
                type="password" 
                placeholder="请输入OpenAI API密钥"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="AI模型" prop="openai_model">
              <el-select v-model="settings.openai_model" style="width: 100%">
                <el-option label="GPT-3.5 Turbo" value="gpt-3.5-turbo" />
                <el-option label="GPT-4" value="gpt-4" />
                <el-option label="GPT-4 Turbo" value="gpt-4-turbo-preview" />
              </el-select>
            </el-form-item>
          </el-card>

          <!-- 系统配置 -->
          <el-card class="setting-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <i class="el-icon-setting"></i>
                <span>系统配置</span>
              </div>
            </template>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="日志级别" prop="log_level">
                  <el-select v-model="settings.log_level" style="width: 100%">
                    <el-option label="DEBUG" value="DEBUG" />
                    <el-option label="INFO" value="INFO" />
                    <el-option label="WARNING" value="WARNING" />
                    <el-option label="ERROR" value="ERROR" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最大工作线程" prop="max_workers">
                  <el-input-number 
                    v-model="settings.max_workers" 
                    :min="1" 
                    :max="20"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="默认报告频率" prop="default_report_frequency">
                  <el-select v-model="settings.default_report_frequency" style="width: 100%">
                    <el-option label="每日" value="daily" />
                    <el-option label="每周" value="weekly" />
                    <el-option label="每月" value="monthly" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="启用调度">
                  <el-switch v-model="settings.schedule_enabled" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="启用通知">
                  <el-switch v-model="settings.enable_notifications" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-card>

          <!-- 操作按钮 -->
          <div class="form-actions">
            <el-button 
              type="primary" 
              size="large" 
              @click="saveSettings"
              :loading="saving"
            >
              保存设置
            </el-button>
            <el-button 
              size="large" 
              @click="resetSettings"
            >
              重置
            </el-button>
            <el-button 
              size="large" 
              @click="testConnections"
              :loading="testing"
            >
              测试连接
            </el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { settingsAPI } from '@/api/index.js'

export default {
  name: 'Settings',
  setup() {
    const loading = ref(false)
    const saving = ref(false)
    const testing = ref(false)
    const settingsForm = ref(null)

    const settings = reactive({
      github_token: '',
      github_api_base_url: 'https://api.github.com',
      database_url: 'sqlite:///./github_sentinel.db',
      redis_url: 'redis://localhost:6379/0',
      smtp_server: '',
      smtp_port: 587,
      smtp_username: '',
      smtp_password: '',
      smtp_use_tls: true,
      slack_webhook_url: '',
      schedule_enabled: true,
      default_report_frequency: 'daily',
      openai_api_key: '',
      openai_model: 'gpt-3.5-turbo',
      log_level: 'INFO',
      max_workers: 4,
      enable_notifications: true
    })

    const rules = {
      github_token: [
        { required: true, message: '请输入GitHub Token', trigger: 'blur' }
      ],
      smtp_server: [
        { required: false, message: '请输入SMTP服务器地址', trigger: 'blur' }
      ],
      smtp_username: [
        { required: false, message: '请输入SMTP用户名', trigger: 'blur' }
      ]
    }

    const loadSettings = async () => {
      loading.value = true
      try {
        const data = await settingsAPI.getSettings()
        Object.assign(settings, data)
        ElMessage.success('设置加载成功')
      } catch (error) {
        console.error('加载设置失败:', error)
        ElMessage.error('加载设置失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        loading.value = false
      }
    }

    const saveSettings = async () => {
      if (!settingsForm.value) return
      
      try {
        await settingsForm.value.validate()
        saving.value = true
        
        await settingsAPI.updateSettings(settings)
        ElMessage.success('设置保存成功')
      } catch (error) {
        if (error.response) {
          ElMessage.error('保存设置失败: ' + (error.response.data?.detail || error.message))
        } else {
          console.error('表单验证失败:', error)
        }
      } finally {
        saving.value = false
      }
    }

    const resetSettings = async () => {
      try {
        await ElMessageBox.confirm('确定要重置所有设置吗？', '确认重置', {
          type: 'warning'
        })
        
        await loadSettings()
        ElMessage.success('设置已重置')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('重置设置失败')
        }
      }
    }

    const testConnections = async () => {
      testing.value = true
      try {
        const validation = await settingsAPI.validateSettings()
        
        const results = validation.validation_results
        let message = '连接测试结果:\n'
        message += `GitHub: ${results.github_token ? '✓' : '✗'}\n`
        message += `数据库: ${results.database_configured ? '✓' : '✗'}\n`
        message += `邮件: ${results.email_configured ? '✓' : '✗'}\n`
        message += `OpenAI: ${results.openai_configured ? '✓' : '✗'}`
        
        if (validation.overall_valid) {
          ElMessage.success(message)
        } else {
          ElMessage.warning(message)
        }
      } catch (error) {
        ElMessage.error('测试连接失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        testing.value = false
      }
    }

    onMounted(() => {
      loadSettings()
    })

    return {
      loading,
      saving,
      testing,
      settingsForm,
      settings,
      rules,
      saveSettings,
      resetSettings,
      testConnections
    }
  }
}
</script>

<style scoped>
.settings {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px 0;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 30px;
  color: #333;
  text-align: center;
}

.settings-content {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.setting-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.form-actions {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.form-actions .el-button {
  margin: 0 10px;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-card {
  border: 1px solid #ebeef5;
}

.el-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}
</style> 