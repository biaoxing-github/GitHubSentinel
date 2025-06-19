<template>
  <div id="app" class="modern-app">
    <el-container class="app-container">
      <!-- 现代化顶部导航 -->
      <el-header class="modern-header">
        <div class="header-content">
          <div class="logo-section">
            <div class="logo-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="logo-text">
              <h1>GitHub Sentinel</h1>
              <span class="logo-subtitle">Repository Monitoring Platform</span>
            </div>
          </div>
          
          <nav class="main-navigation">
            <!-- 主要页面 -->
            <router-link 
              v-for="item in mainNavigationItems" 
              :key="item.path"
              :to="item.path" 
              class="nav-item"
              :class="{ active: isActiveRoute(item.path) }"
            >
              <el-icon>
                <component :is="item.icon" />
              </el-icon>
              <span>{{ item.label }}</span>
            </router-link>
            
            <!-- 监控工具下拉菜单 -->
            <el-dropdown trigger="hover" class="nav-dropdown">
              <span class="nav-item dropdown-trigger">
                <el-icon><Monitor /></el-icon>
                <span class="nav-text">Monitoring</span>
                <el-icon class="arrow-icon"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu class="nav-dropdown-menu">
                  <el-dropdown-item v-for="tool in monitoringTools" :key="tool.path" @click="navigateTo(tool.path)">
                    <div class="dropdown-link">
                      <el-icon><component :is="tool.icon" /></el-icon>
                      <span>{{ tool.label }}</span>
                    </div>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <!-- AI助手下拉菜单 -->
            <el-dropdown trigger="hover" class="nav-dropdown">
              <span class="nav-item dropdown-trigger">
                <el-icon><ChatDotRound /></el-icon>
                <span class="nav-text">AI Assistant</span>
                <el-icon class="arrow-icon"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu class="nav-dropdown-menu">
                  <el-dropdown-item v-for="ai in aiTools" :key="ai.path" @click="navigateTo(ai.path)">
                    <div class="dropdown-link">
                      <el-icon><component :is="ai.icon" /></el-icon>
                      <span>{{ ai.label }}</span>
                    </div>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </nav>
          
          <div class="header-actions">
            <el-button class="action-btn" circle>
              <el-icon><Bell /></el-icon>
            </el-button>
            <el-button class="action-btn" circle>
              <el-icon><User /></el-icon>
            </el-button>
          </div>
        </div>
      </el-header>

      <!-- 现代化主内容区域 -->
      <el-main class="modern-main">
        <div class="main-content">
          <transition name="page-fade" mode="out-in">
            <router-view />
          </transition>
        </div>
      </el-main>

      <!-- 现代化底部 -->
      <el-footer class="modern-footer">
        <div class="footer-content">
          <div class="footer-info">
            <span class="copyright">© 2024 GitHub Sentinel</span>
            <span class="version">v2.0.0</span>
          </div>
          <div class="footer-links">
            <a href="#" class="footer-link">Documentation</a>
            <a href="#" class="footer-link">Support</a>
            <a href="#" class="footer-link">Privacy</a>
          </div>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Monitor, 
  House, 
  Star, 
  Document, 
  Setting, 
  Bell, 
  User,
  Connection,
  Notification,
  DataBoard,
  ChatDotRound,
  ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 主要导航项
const mainNavigationItems = ref([
  { path: '/', label: 'Dashboard', icon: 'House' },
  { path: '/subscriptions', label: 'Subscriptions', icon: 'Star' },
  { path: '/reports', label: 'Reports', icon: 'Document' },
  { path: '/profile', label: 'Profile', icon: 'User' },
  { path: '/settings', label: 'Settings', icon: 'Setting' }
])

// 监控工具分组
const monitoringTools = ref([
  { path: '/websocket-monitor', label: 'WebSocket Monitor', icon: 'Connection' },
  { path: '/notification-rules', label: 'Notifications', icon: 'Notification' },
  { path: '/system-monitor', label: 'System Monitor', icon: 'DataBoard' }
])

// AI助手工具分组
const aiTools = ref([
  { path: '/chat', label: 'AI Chat', icon: 'ChatDotRound' },
  { path: '/chat?mode=analysis', label: 'Smart Analysis', icon: 'DataBoard' },
  { path: '/chat?mode=report', label: 'Report Generator', icon: 'Document' }
])

const isActiveRoute = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

const navigateTo = (path) => {
  router.push(path)
}
</script>

<style lang="scss">
// 导入现代化样式
@import './style/modern.css';

// 全局重置和基础样式
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: var(--font-sans);
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.3s ease;
}

#app {
  height: 100vh;
  background: var(--bg-secondary);
}

.modern-app {
  height: 100%;
  
  .app-container {
    height: 100%;
    background: var(--bg-secondary);
  }
}

// 页面过渡动画
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.3s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

// 现代化头部样式
.modern-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  padding: 0;
  height: 72px !important;
  transition: all 0.3s ease;
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 100%;
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 var(--space-6);
    
    .logo-section {
      display: flex;
      align-items: center;
      gap: var(--space-4);
      
      .logo-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
        border-radius: var(--border-radius);
        color: white;
        transition: all 0.3s ease;
        
        &:hover {
          transform: scale(1.05);
          box-shadow: var(--shadow-md);
        }
        
        .el-icon {
          font-size: 24px;
        }
      }
      
      .logo-text {
        h1 {
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--text-primary);
          margin: 0;
          line-height: 1.2;
          transition: color 0.3s ease;
        }
        
        .logo-subtitle {
          font-size: 0.75rem;
          color: var(--text-muted);
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          transition: color 0.3s ease;
        }
      }
    }
    
    .main-navigation {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      
      .nav-item {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-3) var(--space-4);
        border-radius: var(--border-radius-sm);
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.3s ease;
        position: relative;
        
        &:hover {
          background: var(--bg-hover);
          color: var(--text-primary);
          transform: translateY(-1px);
        }
        
        &.active {
          background: var(--primary-50);
          color: var(--primary-600);
          
          &::after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            height: 2px;
            background: var(--primary-500);
            border-radius: 1px;
          }
        }
        
        .el-icon {
          font-size: 16px;
        }
      }
      
      .nav-dropdown {
        .dropdown-trigger {
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            background: var(--bg-hover);
            color: var(--primary-600);
            
            .arrow-icon {
              transform: rotate(180deg);
            }
          }
          
          .arrow-icon {
            font-size: 12px;
            margin-left: var(--space-1);
            transition: transform 0.3s ease;
          }
        }
      }
    }
    
    .nav-text {
      display: inline-block;
    }
    
    @media (max-width: 768px) {
      .nav-text {
        display: none;
      }
    }
    
    // 美化下拉菜单
    .nav-dropdown-menu {
      margin-top: var(--space-1);
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius-lg);
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
      background: var(--bg-card);
      min-width: 200px;
      padding: var(--space-2);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      
      .dropdown-link {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        width: 100%;
        color: var(--text-secondary);
        text-decoration: none;
        padding: var(--space-3) var(--space-4);
        border-radius: var(--border-radius);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        font-weight: 500;
        font-size: 0.875rem;
        
        &:hover {
          color: var(--primary-600);
          background: linear-gradient(135deg, var(--primary-50), var(--primary-100));
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
        }
        
        .el-icon {
          font-size: 18px;
          color: var(--primary-500);
          transition: all 0.3s ease;
        }
        
        span {
          font-weight: 600;
          letter-spacing: 0.025em;
        }
      }
    }
    
    // 确保下拉菜单项正确显示
    :deep(.el-dropdown-menu__item) {
      padding: 0 !important;
      margin: 2px 4px;
      border-radius: var(--border-radius-sm);
      
      &:hover {
        background: transparent !important;
      }
      
      &:focus {
        background: transparent !important;
      }
    }
    
    .header-actions {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      
      .action-btn {
        width: 40px;
        height: 40px;
        border: 1px solid var(--border-color);
        background: var(--bg-card);
        color: var(--text-secondary);
        transition: all 0.3s ease;
        
        &:hover {
          background: var(--bg-hover);
          color: var(--text-primary);
          border-color: var(--primary-300);
          transform: translateY(-1px);
          box-shadow: var(--shadow-sm);
        }
      }
    }
  }
}

// 现代化主内容区域
.modern-main {
  background: var(--bg-secondary);
  padding: var(--space-6);
  overflow-y: auto;
  
  .main-content {
    max-width: 1400px;
    margin: 0 auto;
    min-height: calc(100vh - 144px);
  }
}

// 现代化底部
.modern-footer {
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
  padding: var(--space-4) 0;
  height: 72px !important;
  
  .footer-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 var(--space-6);
    
    .footer-info {
      display: flex;
      align-items: center;
      gap: var(--space-4);
      
      .copyright {
        color: var(--text-secondary);
        font-size: 0.875rem;
      }
      
      .version {
        background: var(--primary-50);
        color: var(--primary-600);
        padding: var(--space-1) var(--space-2);
        border-radius: var(--border-radius-sm);
        font-size: 0.75rem;
        font-weight: 500;
      }
    }
    
    .footer-links {
      display: flex;
      align-items: center;
      gap: var(--space-4);
      
      .footer-link {
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 0.875rem;
        transition: color 0.3s ease;
        
        &:hover {
          color: var(--primary-500);
        }
      }
    }
  }
}

// 全局页面容器样式
.page-container {
  background: var(--bg-card);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.page-header {
  padding: var(--space-8) var(--space-8) var(--space-6);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-card);
  
  .page-title {
    font-size: 1.875rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: var(--space-2);
    line-height: 1.2;
  }
  
  .page-description {
    color: var(--text-secondary);
    font-size: 1rem;
    line-height: 1.5;
  }
}

.page-content {
  padding: var(--space-8);
}

// Element Plus 组件现代化覆盖
.el-button {
  border-radius: var(--border-radius-sm);
  font-weight: 500;
  transition: var(--transition);
  
  &.el-button--primary {
    background: var(--primary-600);
    border-color: var(--primary-600);
    
    &:hover {
      background: var(--primary-700);
      border-color: var(--primary-700);
      transform: translateY(-1px);
      box-shadow: var(--shadow-md);
    }
  }
  
  &.el-button--default {
    background: var(--bg-card);
    border-color: var(--border-color);
    color: var(--text-secondary);
    
    &:hover {
      background: var(--gray-50);
      border-color: var(--gray-300);
      color: var(--text-primary);
    }
  }
}

.el-card {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  
  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }
  
  .el-card__header {
    background: var(--bg-card);
    border-bottom: 1px solid var(--border-color);
    padding: var(--space-6);
  }
  
  .el-card__body {
    padding: var(--space-6);
  }
}

.el-table {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  
  th.el-table__cell {
    background: var(--gray-50);
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--border-color);
  }
  
  td.el-table__cell {
    border-bottom: 1px solid var(--border-light);
  }
  
  .el-table__row:hover {
    background: var(--gray-50);
  }
}

.el-input {
  .el-input__wrapper {
    border-radius: var(--border-radius-sm);
    border-color: var(--border-color);
    box-shadow: none;
    transition: var(--transition);
    
    &:hover {
      border-color: var(--gray-300);
    }
    
    &.is-focus {
      border-color: var(--primary-500);
      box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
    }
  }
}

.el-tag {
  border-radius: var(--border-radius-sm);
  font-weight: 500;
  
  &.el-tag--primary {
    background: var(--primary-100);
    color: var(--primary-700);
    border-color: var(--primary-200);
  }
  
  &.el-tag--success {
    background: #dcfce7;
    color: #166534;
    border-color: #bbf7d0;
  }
  
  &.el-tag--warning {
    background: #fef3c7;
    color: #92400e;
    border-color: #fde68a;
  }
  
  &.el-tag--danger {
    background: #fee2e2;
    color: #991b1b;
    border-color: #fecaca;
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .modern-header .header-content {
    padding: 0 var(--space-4);
    
    .main-navigation {
      gap: var(--space-1);
      
      .nav-item {
        padding: var(--space-2) var(--space-3);
        font-size: 0.8rem;
        
        span {
          display: none;
        }
      }
    }
  }
  
  .modern-main {
    padding: var(--space-6);
  }
}

@media (max-width: 768px) {
  .modern-header {
    .header-content {
      padding: 0 var(--space-4);
      
      .main-navigation {
        display: none;
      }
      
      .logo-text h1 {
        font-size: 1.25rem;
      }
      
      .logo-subtitle {
        display: none;
      }
    }
  }
  
  .modern-main {
    padding: var(--space-4);
  }
  
  .modern-footer {
    .footer-content {
      padding: 0 var(--space-4);
      flex-direction: column;
      gap: var(--space-2);
      
      .footer-links {
        gap: var(--space-3);
      }
    }
  }
  
  .page-header {
    padding: var(--space-6) var(--space-6) var(--space-4);
    
    .page-title {
      font-size: 1.5rem;
    }
  }
  
  .page-content {
    padding: var(--space-6);
  }
}
</style> 