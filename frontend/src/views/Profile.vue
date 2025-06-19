<template>
  <div class="profile">
    <div class="page-header">
      <h1>个人资料</h1>
      <p>管理您的账户信息和偏好设置</p>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <!-- 基本信息 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-button type="primary" @click="editMode = !editMode">
                {{ editMode ? '取消编辑' : '编辑资料' }}
              </el-button>
            </div>
          </template>

          <el-form 
            :model="userInfo" 
            :rules="formRules"
            ref="userFormRef"
            label-width="100px"
            :disabled="!editMode"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="userInfo.username" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="userInfo.email" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓名" prop="full_name">
                  <el-input v-model="userInfo.full_name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="电话" prop="phone">
                  <el-input v-model="userInfo.phone" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="GitHub Token" prop="github_token">
              <el-input 
                v-model="userInfo.github_token" 
                type="password"
                show-password
                placeholder="用于GitHub API访问"
              />
            </el-form-item>

            <el-form-item label="个人简介" prop="bio">
              <el-input 
                v-model="userInfo.bio" 
                type="textarea"
                :rows="3"
                placeholder="介绍一下您自己..."
              />
            </el-form-item>

            <el-form-item v-if="editMode">
              <el-button type="primary" @click="saveProfile" :loading="saving">
                保存更改
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 通知设置 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <span>通知设置</span>
          </template>

          <div class="notification-settings">
            <div class="setting-item">
              <div class="setting-info">
                <h4>邮件通知</h4>
                <p>接收重要活动和系统消息的邮件通知</p>
              </div>
              <el-switch v-model="settings.email_notifications" @change="updateSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h4>WebSocket实时通知</h4>
                <p>在浏览器中接收实时通知</p>
              </div>
              <el-switch v-model="settings.websocket_notifications" @change="updateSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h4>移动设备推送</h4>
                <p>向移动设备发送推送通知</p>
              </div>
              <el-switch v-model="settings.push_notifications" @change="updateSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h4>活动摘要</h4>
                <p>定期接收监控活动的摘要报告</p>
              </div>
              <el-switch v-model="settings.activity_digest" @change="updateSettings" />
            </div>
          </div>
        </el-card>

        <!-- 隐私设置 -->
        <el-card>
          <template #header>
            <span>隐私与安全</span>
          </template>

          <div class="privacy-settings">
            <div class="setting-item">
              <div class="setting-info">
                <h4>公开个人资料</h4>
                <p>允许其他用户查看您的基本信息</p>
              </div>
              <el-switch v-model="settings.public_profile" @change="updateSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h4>数据分析</h4>
                <p>允许系统收集使用数据以改进服务</p>
              </div>
              <el-switch v-model="settings.analytics" @change="updateSettings" />
            </div>

            <el-button type="danger" @click="changePassword">修改密码</el-button>
            <el-button type="warning" @click="exportData">导出数据</el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <!-- 头像和基本信息 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <span>头像</span>
          </template>

          <div class="avatar-section">
            <el-avatar :size="120" :src="userInfo.avatar" class="avatar">
              <span v-if="!userInfo.avatar">{{ userInfo.username?.charAt(0)?.toUpperCase() }}</span>
            </el-avatar>
            
            <div class="avatar-actions">
              <el-upload
                class="avatar-uploader"
                action="/api/upload/avatar"
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                :on-success="handleAvatarSuccess"
                accept="image/*"
              >
                <el-button type="primary" size="small">上传头像</el-button>
              </el-upload>
            </div>
          </div>
        </el-card>

        <!-- 账户统计 -->
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <span>账户统计</span>
          </template>

          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="注册时间">
              {{ formatDate(userInfo.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="最后登录">
              {{ formatDate(userInfo.last_login) }}
            </el-descriptions-item>
            <el-descriptions-item label="监控仓库">
              {{ stats.repositories }} 个
            </el-descriptions-item>
            <el-descriptions-item label="接收通知">
              {{ stats.notifications }} 条
            </el-descriptions-item>
            <el-descriptions-item label="生成报告">
              {{ stats.reports }} 份
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 快速操作 -->
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>

          <div class="quick-actions">
            <el-button @click="$router.push('/websocket-monitor')">
              <el-icon><Connection /></el-icon>
              WebSocket监控
            </el-button>
            
            <el-button @click="$router.push('/notification-rules')">
              <el-icon><Bell /></el-icon>
              通知规则
            </el-button>
            
            <el-button @click="$router.push('/system-monitor')">
              <el-icon><Monitor /></el-icon>
              系统监控
            </el-button>
            
            <el-button @click="$router.push('/settings')">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 修改密码对话框 -->
    <el-dialog title="修改密码" v-model="passwordDialogVisible" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef">
        <el-form-item label="当前密码" prop="current_password">
          <el-input 
            v-model="passwordForm.current_password" 
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input 
            v-model="passwordForm.new_password" 
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input 
            v-model="passwordForm.confirm_password" 
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPasswordChange" :loading="changingPassword">
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, Bell, Monitor, Setting } from '@element-plus/icons-vue'

// 响应式数据
const editMode = ref(false)
const saving = ref(false)
const passwordDialogVisible = ref(false)
const changingPassword = ref(false)

const userFormRef = ref(null)
const passwordFormRef = ref(null)

const userInfo = reactive({
  username: 'developer',
  email: 'developer@example.com',
  full_name: '开发者',
  phone: '+86 138 0000 0000',
  github_token: '',
  bio: '热爱技术的全栈开发者，专注于GitHub仓库监控和自动化工具开发。',
  avatar: '',
  created_at: '2023-01-15T08:30:00Z',
  last_login: new Date().toISOString()
})

const settings = reactive({
  email_notifications: true,
  websocket_notifications: true,
  push_notifications: false,
  activity_digest: true,
  public_profile: false,
  analytics: true
})

const stats = reactive({
  repositories: 12,
  notifications: 156,
  reports: 28
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ]
}

const passwordRules = {
  current_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 方法
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const saveProfile = async () => {
  try {
    await userFormRef.value?.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    editMode.value = false
    ElMessage.success('个人资料保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请检查输入信息')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  userFormRef.value?.resetFields()
}

const updateSettings = async () => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('设置已更新')
  } catch (error) {
    ElMessage.error('设置更新失败')
  }
}

const changePassword = () => {
  passwordDialogVisible.value = true
  // 清空表单
  Object.assign(passwordForm, {
    current_password: '',
    new_password: '',
    confirm_password: ''
  })
}

const submitPasswordChange = async () => {
  try {
    await passwordFormRef.value?.validate()
    changingPassword.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    passwordDialogVisible.value = false
    ElMessage.success('密码修改成功')
  } catch (error) {
    console.error('密码修改失败:', error)
    ElMessage.error('密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

const exportData = async () => {
  try {
    await ElMessageBox.confirm(
      '导出的数据将包含您的个人信息、设置和活动记录。确定要继续吗？',
      '导出个人数据',
      {
        confirmButtonText: '确定导出',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 模拟导出
    ElMessage.info('正在准备导出数据...')
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('数据导出完成，请检查下载文件')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('数据导出失败')
    }
  }
}

const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('头像必须是图片格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

const handleAvatarSuccess = (response) => {
  userInfo.avatar = response.url
  ElMessage.success('头像上传成功')
}

// 生命周期
onMounted(() => {
  // 这里可以从API加载用户数据
  console.log('Profile page mounted')
})
</script>

<style scoped>
.profile {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-settings,
.privacy-settings {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: #fafafa;
}

.setting-info h4 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 14px;
}

.setting-info p {
  margin: 0;
  color: #909399;
  font-size: 12px;
}

.avatar-section {
  text-align: center;
}

.avatar {
  margin-bottom: 16px;
}

.avatar-actions {
  display: flex;
  justify-content: center;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.privacy-settings .el-button {
  margin-top: 16px;
  margin-right: 12px;
}

@media (max-width: 768px) {
  .profile {
    padding: 12px;
  }
  
  .setting-item {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .setting-info {
    text-align: center;
  }
}
</style> 