<template>
  <div class="home">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">GitHub Sentinel</h1>
        <p class="hero-subtitle">AI驱动的GitHub仓库监控和报告系统</p>
        <div class="hero-buttons">
          <el-button type="primary" size="large" @click="goToDashboard">
            进入控制台
          </el-button>
          <el-button size="large" @click="goToSubscriptions">
            管理订阅
          </el-button>
        </div>
      </div>
    </div>

    <div class="features-section">
      <div class="container">
        <h2 class="section-title">核心功能</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="el-icon-monitor"></i>
            </div>
            <h3>实时监控</h3>
            <p>自动监控GitHub仓库的提交、问题、Pull Request等活动</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <i class="el-icon-document"></i>
            </div>
            <h3>智能报告</h3>
            <p>AI生成详细的活动报告和趋势分析</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <i class="el-icon-message"></i>
            </div>
            <h3>多渠道通知</h3>
            <p>支持邮件、Slack、Webhook等多种通知方式</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <i class="el-icon-time"></i>
            </div>
            <h3>定时任务</h3>
            <p>灵活的调度配置，支持每日、每周定期执行</p>
          </div>
        </div>
      </div>
    </div>

    <div class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ stats.totalRepos }}</div>
            <div class="stat-label">监控仓库</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.totalUsers }}</div>
            <div class="stat-label">活跃用户</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.totalReports }}</div>
            <div class="stat-label">生成报告</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.totalNotifications }}</div>
            <div class="stat-label">发送通知</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userAPI, subscriptionAPI } from '@/api/index.js'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()
    const stats = ref({
      totalRepos: 0,
      totalUsers: 0,
      totalReports: 0,
      totalNotifications: 0
    })

    const goToDashboard = () => {
      router.push('/dashboard')
    }

    const goToSubscriptions = () => {
      router.push('/subscriptions')
    }

    const loadStats = async () => {
      try {
        // 从后台API加载真实统计数据
        const [userStats, subStats] = await Promise.all([
          userAPI.getUserStats(),
          subscriptionAPI.getSubscriptionStats()
        ])
        
        stats.value = {
          totalRepos: subStats.total_subscriptions || 0,
          totalUsers: userStats.active_users || 0,
          totalReports: 45, // 暂时使用模拟数据，后续可接入报告API
          totalNotifications: 128 // 暂时使用模拟数据
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        // 失败时使用默认数据
        stats.value = {
          totalRepos: 0,
          totalUsers: 0,
          totalReports: 0,
          totalNotifications: 0
        }
      }
    }

    onMounted(() => {
      loadStats()
    })

    return {
      stats,
      goToDashboard,
      goToSubscriptions
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 100px 0;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: bold;
  margin-bottom: 20px;
}

.hero-subtitle {
  font-size: 1.5rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.hero-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.features-section {
  padding: 80px 0;
  background: #f8f9fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 60px;
  color: #333;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

.stats-section {
  padding: 80px 0;
  background: #2c3e50;
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-number {
  font-size: 3rem;
  font-weight: bold;
  color: #3498db;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 1.2rem;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style> 