<template>
  <div class="reports">
    <div class="page-header">
      <h1>报告管理</h1>
      <el-button type="primary" @click="showGenerateDialog = true">
        <i class="el-icon-document-add"></i> 生成报告
      </el-button>
    </div>

    <div class="reports-content">
      <el-table :data="reports" style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="报告标题" width="300"/>
        <el-table-column prop="repository" label="仓库" width="200">
          <template #default="scope">
            <el-link :href="`https://github.com/${scope.row.repository}`" target="_blank" v-if="scope.row.repository">
              {{ scope.row.repository }}
            </el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120">
          <template #default="scope">
            <el-tag>{{ getTypeName(scope.row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusName(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="viewReport(scope.row)" :disabled="scope.row.status !== 'completed'">
              查看
            </el-button>
            <el-button size="small" type="danger" @click="deleteReport(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 生成报告对话框 -->
    <el-dialog v-model="showGenerateDialog" title="生成报告" width="500px">
      <el-form :model="generateForm" label-width="100px" :rules="generateRules" ref="generateFormRef">
        <el-form-item label="选择订阅" prop="subscriptionId">
          <el-select v-model="generateForm.subscriptionId" placeholder="请选择要生成报告的订阅" style="width: 100%">
            <el-option
              v-for="subscription in subscriptions"
              :key="subscription.id"
              :label="`${subscription.repository} (${subscription.frequency === 'daily' ? '每日' : '每周'})`"
              :value="subscription.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="报告类型" prop="reportType">
          <el-select v-model="generateForm.reportType" placeholder="请选择报告类型" style="width: 100%">
            <el-option label="日报" value="daily"/>
            <el-option label="周报" value="weekly"/>
            <el-option label="月报" value="monthly"/>
          </el-select>
        </el-form-item>
        <el-form-item label="报告标题" prop="title">
          <el-input v-model="generateForm.title" placeholder="自定义报告标题（可选）"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" @click="generateReport" :loading="generating">生成</el-button>
      </template>
    </el-dialog>

    <!-- 报告查看对话框 -->
    <el-dialog v-model="showViewDialog" :title="viewingReport?.title || '报告详情'" width="80%" top="5vh">
      <div class="report-content" v-if="viewingReport">
        <div class="report-meta">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="仓库">{{ viewingReport.repository || '-' }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ getTypeName(viewingReport.type) }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(viewingReport.status)">
                {{ getStatusName(viewingReport.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(viewingReport.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="report-body" v-if="viewingReport.content">
          <h3>报告内容</h3>
          <div class="content-wrapper" v-html="viewingReport.content"></div>
        </div>
        <div class="no-content" v-else>
          <el-empty description="暂无报告内容" />
        </div>
      </div>
      <template #footer>
        <el-button @click="showViewDialog = false">关闭</el-button>
        <el-button type="primary" @click="downloadReport" v-if="viewingReport?.content">下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { reportsAPI, subscriptionAPI } from '@/api'

export default {
  name: 'Reports',
  setup() {
    const reports = ref([])
    const subscriptions = ref([])
    const loading = ref(false)
    const generating = ref(false)
    const showGenerateDialog = ref(false)
    const showViewDialog = ref(false)
    const generateFormRef = ref(null)
    const viewingReport = ref(null)

    const generateForm = ref({
      subscriptionId: null,
      reportType: 'daily',
      title: ''
    })

    const generateRules = reactive({
      subscriptionId: [
        { required: true, message: '请选择订阅', trigger: 'change' }
      ],
      reportType: [
        { required: true, message: '请选择报告类型', trigger: 'change' }
      ]
    })

    const getTypeName = (type) => {
      const names = { daily: '日报', weekly: '周报', monthly: '月报' }
      return names[type] || type
    }

    const getStatusName = (status) => {
      const names = { 
        pending: '等待中', 
        processing: '生成中', 
        completed: '已完成', 
        failed: '失败' 
      }
      return names[status] || status
    }

    const getStatusType = (status) => {
      const types = { 
        pending: 'info', 
        processing: 'warning', 
        completed: 'success', 
        failed: 'danger' 
      }
      return types[status] || 'info'
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString('zh-CN')
    }

    const loadSubscriptions = async () => {
      try {
        const response = await subscriptionAPI.getSubscriptions()
        subscriptions.value = response.subscriptions || response || []
        console.log('加载订阅列表:', subscriptions.value.length)
      } catch (error) {
        console.error('加载订阅列表失败:', error)
        ElMessage.error('加载订阅列表失败')
        subscriptions.value = []
      }
    }

    const loadReports = async () => {
      loading.value = true
      try {
        console.log('开始加载报告数据...')
        const response = await reportsAPI.getReports()
        console.log('报告数据响应:', response)
        
        reports.value = response.reports || response || []
        ElMessage.success(`加载了 ${reports.value.length} 个报告`)
      } catch (error) {
        console.error('加载报告数据失败:', error)
        ElMessage.error(`加载报告数据失败: ${error.message}`)
        reports.value = []
      } finally {
        loading.value = false
      }
    }

    const generateReport = async () => {
      if (!generateFormRef.value) return
      
      try {
        await generateFormRef.value.validate()
      } catch {
        return
      }

      generating.value = true
      try {
        ElMessage.info('开始生成报告...')
        
        const response = await reportsAPI.generateReport(
          generateForm.value.subscriptionId, 
          generateForm.value.reportType
        )
        console.log('生成报告响应:', response)
        
        showGenerateDialog.value = false
        generateForm.value = {
          subscriptionId: null,
          reportType: 'daily',
          title: ''
        }
        
        ElMessage.success('报告生成任务已启动，请稍后查看')
        
        // 延迟重新加载报告列表
        setTimeout(() => {
          loadReports()
        }, 2000)
        
      } catch (error) {
        console.error('生成报告失败:', error)
        ElMessage.error(`生成报告失败: ${error.message}`)
      } finally {
        generating.value = false
      }
    }

    const viewReport = async (report) => {
      try {
        // 获取完整的报告详情
        const response = await reportsAPI.getReport(report.id)
        viewingReport.value = response
        showViewDialog.value = true
      } catch (error) {
        console.error('获取报告详情失败:', error)
        ElMessage.error('获取报告详情失败')
      }
    }

    const downloadReport = () => {
      if (!viewingReport.value?.content) return
      
      const blob = new Blob([viewingReport.value.content], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${viewingReport.value.title || 'report'}.html`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      ElMessage.success('报告下载成功')
    }

    const deleteReport = async (report) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除报告 "${report.title}" 吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger'
          }
        )
        
        // TODO: 实现删除API
        ElMessage.info('删除功能开发中...')
        
      } catch (error) {
        if (error === 'cancel') {
          ElMessage.info('已取消删除')
        }
      }
    }

    onMounted(async () => {
      await loadSubscriptions()
      await loadReports()
    })

    return {
      reports,
      subscriptions,
      loading,
      generating,
      showGenerateDialog,
      showViewDialog,
      generateFormRef,
      generateForm,
      generateRules,
      viewingReport,
      getTypeName,
      getStatusName,
      getStatusType,
      formatDate,
      generateReport,
      viewReport,
      downloadReport,
      deleteReport
    }
  }
}
</script>

<style scoped>
.reports {
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

.reports-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.report-content {
  max-height: 70vh;
  overflow-y: auto;
}

.report-meta {
  margin-bottom: 20px;
}

.report-body h3 {
  margin: 20px 0 10px 0;
  color: #333;
}

.content-wrapper {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  line-height: 1.6;
}

.no-content {
  text-align: center;
  padding: 40px 0;
}
</style> 