import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/subscriptions',
    name: 'Subscriptions',
    component: () => import('../views/Subscriptions.vue')
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue')
  },
  {
    path: '/activities',
    name: 'Activities',
    component: () => import('../views/Activities.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  },
  {
    path: '/websocket-monitor',
    name: 'WebSocketMonitor',
    component: () => import('../views/WebSocketMonitor.vue'),
    meta: { title: 'WebSocket监控' }
  },
  {
    path: '/notification-rules',
    name: 'NotificationRules', 
    component: () => import('../views/NotificationRules.vue'),
    meta: { title: '通知规则管理' }
  },
  {
    path: '/system-monitor',
    name: 'SystemMonitor',
    component: () => import('../views/SystemMonitor.vue'),
    meta: { title: '系统监控' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { title: '个人资料' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/ChatPage.vue'),
    meta: { title: 'AI聊天助手' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 