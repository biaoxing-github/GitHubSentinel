<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 顶部导航 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon><Monitor /></el-icon>
            <span class="logo-text">GitHub Sentinel</span>
          </div>
          <el-menu
            :default-active="activeIndex"
            class="header-menu"
            mode="horizontal"
            background-color="#001529"
            text-color="#fff"
            active-text-color="#409EFF"
            router
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>仪表板</span>
            </el-menu-item>
            <el-menu-item index="/subscriptions">
              <el-icon><Star /></el-icon>
              <span>订阅管理</span>
            </el-menu-item>
            <el-menu-item index="/reports">
              <el-icon><Document /></el-icon>
              <span>报告中心</span>
            </el-menu-item>
            <el-menu-item index="/settings">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>

      <!-- 主内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <span>© 2024 GitHub Sentinel. All rights reserved.</span>
          <span>Version 1.0.0</span>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Monitor, House, Star, Document, Setting } from '@element-plus/icons-vue'

const route = useRoute()

const activeIndex = computed(() => {
  return route.path
})
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
}

.app-container {
  height: 100%;
}

.app-header {
  background-color: #001529;
  padding: 0;
  height: 64px !important;
  
  .header-content {
    display: flex;
    align-items: center;
    height: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
    
    .logo {
      display: flex;
      align-items: center;
      color: #fff;
      font-size: 20px;
      font-weight: bold;
      margin-right: 50px;
      
      .el-icon {
        margin-right: 8px;
        font-size: 24px;
        color: #409EFF;
      }
    }
    
    .header-menu {
      border: none;
      flex: 1;
      
      .el-menu-item {
        border-bottom: 2px solid transparent;
        
        &:hover {
          background-color: rgba(255, 255, 255, 0.1);
        }
        
        &.is-active {
          border-bottom-color: #409EFF;
          background-color: rgba(64, 158, 255, 0.1);
        }
      }
    }
  }
}

.app-main {
  background-color: #f5f7fa;
  min-height: calc(100vh - 124px);
  padding: 24px;
}

.app-footer {
  background-color: #fff;
  border-top: 1px solid #e6e8eb;
  height: 60px !important;
  display: flex;
  align-items: center;
  
  .footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
    color: #666;
    font-size: 14px;
  }
}

// 全局样式
.page-container {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-header {
  margin-bottom: 24px;
  
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #1f2329;
    margin-bottom: 8px;
  }
  
  .page-description {
    color: #646a73;
    font-size: 14px;
  }
}
</style> 