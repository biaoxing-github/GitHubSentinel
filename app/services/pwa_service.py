"""
PWA (Progressive Web App) 服务 (v0.3.0)
提供离线缓存、桌面安装、系统级通知、触摸手势等PWA功能
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class PWAService:
    """PWA 服务"""
    
    def __init__(self):
        self.settings = get_settings()
        self.cache_version = "v0.3.0"
        self.app_name = "GitHubSentinel"
        self.app_short_name = "GH-Sentinel"
        
    def generate_manifest(self, request: Request) -> Dict[str, Any]:
        """生成 Web App Manifest"""
        base_url = str(request.base_url).rstrip('/')
        
        manifest = {
            "name": self.app_name,
            "short_name": self.app_short_name,
            "description": "GitHub 仓库活动监控与智能分析平台",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#1f2937",
            "orientation": "portrait-primary",
            "scope": "/",
            "lang": "zh-CN",
            "dir": "ltr",
            
            "icons": [
                {
                    "src": f"{base_url}/static/icons/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": f"{base_url}/static/icons/icon-96x96.png",
                    "sizes": "96x96",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": f"{base_url}/static/icons/icon-128x128.png",
                    "sizes": "128x128",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": f"{base_url}/static/icons/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": f"{base_url}/static/icons/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": f"{base_url}/static/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": f"{base_url}/static/icons/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png",
                    "purpose": "maskable any"
                },
                {
                    "src": f"{base_url}/static/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "maskable any"
                }
            ],
            
            "screenshots": [
                {
                    "src": f"{base_url}/static/screenshots/desktop-screenshot.png",
                    "sizes": "1280x720",
                    "type": "image/png",
                    "form_factor": "wide",
                    "label": "桌面端界面"
                },
                {
                    "src": f"{base_url}/static/screenshots/mobile-screenshot.png",
                    "sizes": "390x844",
                    "type": "image/png",
                    "form_factor": "narrow",
                    "label": "移动端界面"
                }
            ],
            
            "categories": ["productivity", "developer", "business"],
            
            "shortcuts": [
                {
                    "name": "仪表板",
                    "short_name": "Dashboard",
                    "description": "查看项目仪表板",
                    "url": "/dashboard",
                    "icons": [
                        {
                            "src": f"{base_url}/static/icons/shortcut-dashboard.png",
                            "sizes": "96x96"
                        }
                    ]
                },
                {
                    "name": "订阅管理",
                    "short_name": "Subscriptions",
                    "description": "管理仓库订阅",
                    "url": "/subscriptions",
                    "icons": [
                        {
                            "src": f"{base_url}/static/icons/shortcut-subscriptions.png",
                            "sizes": "96x96"
                        }
                    ]
                },
                {
                    "name": "AI分析",
                    "short_name": "AI Analysis",
                    "description": "智能分析和对话",
                    "url": "/ai-chat",
                    "icons": [
                        {
                            "src": f"{base_url}/static/icons/shortcut-ai.png",
                            "sizes": "96x96"
                        }
                    ]
                }
            ],
            
            "prefer_related_applications": False,
            
            "edge_side_panel": {
                "preferred_width": 400
            }
        }
        
        return manifest
    
    def generate_service_worker(self) -> str:
        """生成 Service Worker"""
        service_worker_content = f'''
// GitHubSentinel Service Worker v{self.cache_version}
const CACHE_NAME = 'githubsentinel-{self.cache_version}';
const DYNAMIC_CACHE = 'githubsentinel-dynamic-{self.cache_version}';

// 需要缓存的静态资源
const STATIC_ASSETS = [
    '/',
    '/dashboard',
    '/subscriptions',
    '/activities',
    '/reports',
    '/ai-chat',
    '/static/css/app.css',
    '/static/js/app.js',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/manifest.json'
];

// API 缓存策略配置
const API_CACHE_STRATEGIES = {{
    '/api/dashboard/': 'cache-first',
    '/api/subscriptions/': 'network-first',
    '/api/activities/': 'network-first',
    '/api/reports/': 'cache-first',
    '/api/llm/': 'network-only'
}};

// 安装事件
self.addEventListener('install', event => {{
    console.log('[SW] 安装 Service Worker');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {{
                console.log('[SW] 缓存静态资源');
                return cache.addAll(STATIC_ASSETS);
            }})
            .then(() => {{
                console.log('[SW] 跳过等待，立即激活');
                return self.skipWaiting();
            }})
    );
}});

// 激活事件
self.addEventListener('activate', event => {{
    console.log('[SW] 激活 Service Worker');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {{
                return Promise.all(
                    cacheNames.map(cacheName => {{
                        if (cacheName !== CACHE_NAME && cacheName !== DYNAMIC_CACHE) {{
                            console.log('[SW] 删除旧缓存:', cacheName);
                            return caches.delete(cacheName);
                        }}
                    }})
                );
            }})
            .then(() => {{
                console.log('[SW] 声明控制所有客户端');
                return self.clients.claim();
            }})
    );
}});

// 拦截请求
self.addEventListener('fetch', event => {{
    const {{ request }} = event;
    const url = new URL(request.url);
    
    // 跳过非同源请求
    if (url.origin !== location.origin) {{
        return;
    }}
    
    // 跳过WebSocket请求
    if (request.headers.get('upgrade') === 'websocket') {{
        return;
    }}
    
    event.respondWith(handleRequest(request));
}});

// 处理请求的主要逻辑
async function handleRequest(request) {{
    const url = new URL(request.url);
    const pathname = url.pathname;
    
    // API 请求处理
    if (pathname.startsWith('/api/')) {{
        return handleApiRequest(request);
    }}
    
    // 静态资源处理
    if (pathname.startsWith('/static/')) {{
        return handleStaticRequest(request);
    }}
    
    // 页面请求处理
    return handlePageRequest(request);
}}

// 处理 API 请求
async function handleApiRequest(request) {{
    const pathname = new URL(request.url).pathname;
    
    // 确定缓存策略
    let strategy = 'network-first'; // 默认策略
    for (const [pattern, cacheStrategy] of Object.entries(API_CACHE_STRATEGIES)) {{
        if (pathname.startsWith(pattern)) {{
            strategy = cacheStrategy;
            break;
        }}
    }}
    
    switch (strategy) {{
        case 'cache-first':
            return cacheFirst(request);
        case 'network-first':
            return networkFirst(request);
        case 'network-only':
            return networkOnly(request);
        default:
            return networkFirst(request);
    }}
}}

// 处理静态资源请求
async function handleStaticRequest(request) {{
    return cacheFirst(request);
}}

// 处理页面请求
async function handlePageRequest(request) {{
    try {{
        // 先尝试网络请求
        const response = await fetch(request);
        
        // 如果成功，缓存响应
        if (response.ok) {{
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }}
        
        return response;
    }} catch (error) {{
        // 网络失败，尝试从缓存获取
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {{
            return cachedResponse;
        }}
        
        // 返回离线页面
        return caches.match('/offline.html') || new Response('离线状态', {{
            status: 503,
            statusText: 'Service Unavailable'
        }});
    }}
}}

// 缓存优先策略
async function cacheFirst(request) {{
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {{
        return cachedResponse;
    }}
    
    try {{
        const response = await fetch(request);
        if (response.ok) {{
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }}
        return response;
    }} catch (error) {{
        return new Response('资源不可用', {{
            status: 503,
            statusText: 'Service Unavailable'
        }});
    }}
}}

// 网络优先策略
async function networkFirst(request) {{
    try {{
        const response = await fetch(request);
        if (response.ok) {{
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, response.clone());
        }}
        return response;
    }} catch (error) {{
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {{
            return cachedResponse;
        }}
        throw error;
    }}
}}

// 仅网络策略
async function networkOnly(request) {{
    return fetch(request);
}}

// 后台同步
self.addEventListener('sync', event => {{
    console.log('[SW] 后台同步:', event.tag);
    
    if (event.tag === 'background-sync-activities') {{
        event.waitUntil(syncActivities());
    }}
}});

// 同步活动数据
async function syncActivities() {{
    try {{
        console.log('[SW] 开始同步活动数据');
        
        // 获取待同步的数据
        const pendingData = await getPendingData();
        if (pendingData.length === 0) {{
            return;
        }}
        
        // 发送数据到服务器
        for (const data of pendingData) {{
            await fetch('/api/sync/activities', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify(data)
            }});
        }}
        
        // 清除已同步的数据
        await clearPendingData();
        
        console.log('[SW] 活动数据同步完成');
    }} catch (error) {{
        console.error('[SW] 同步失败:', error);
    }}
}}

// 获取待同步数据
async function getPendingData() {{
    return []; // 这里应该从 IndexedDB 或其他存储中获取
}}

// 清除待同步数据
async function clearPendingData() {{
    // 清除存储中的待同步数据
}}

// 推送通知处理
self.addEventListener('push', event => {{
    console.log('[SW] 收到推送消息');
    
    let notification = {{
        title: 'GitHubSentinel',
        body: '您有新的通知',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        tag: 'default',
        requireInteraction: false
    }};
    
    if (event.data) {{
        try {{
            const data = event.data.json();
            notification = {{
                ...notification,
                ...data
            }};
        }} catch (error) {{
            console.error('[SW] 解析推送数据失败:', error);
            notification.body = event.data.text();
        }}
    }}
    
    event.waitUntil(
        self.registration.showNotification(notification.title, notification)
    );
}});

// 通知点击处理
self.addEventListener('notificationclick', event => {{
    console.log('[SW] 通知被点击:', event.notification);
    
    event.notification.close();
    
    const action = event.action || 'default';
    let url = '/';
    
    // 根据通知数据确定跳转URL
    if (event.notification.data) {{
        url = event.notification.data.url || '/';
    }}
    
    event.waitUntil(
        clients.matchAll({{ type: 'window' }})
            .then(clientList => {{
                // 查找已打开的窗口
                for (const client of clientList) {{
                    if (client.url === url && 'focus' in client) {{
                        return client.focus();
                    }}
                }}
                // 打开新窗口
                if (clients.openWindow) {{
                    return clients.openWindow(url);
                }}
            }})
    );
}});

// 消息处理
self.addEventListener('message', event => {{
    console.log('[SW] 收到消息:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {{
        self.skipWaiting();
    }}
    
    if (event.data && event.data.type === 'GET_VERSION') {{
        event.ports[0].postMessage({{
            version: '{self.cache_version}',
            caches: {{
                static: CACHE_NAME,
                dynamic: DYNAMIC_CACHE
            }}
        }});
    }}
}});

console.log('[SW] Service Worker 已加载 v{self.cache_version}');
'''
        return service_worker_content.strip()
    
    def generate_offline_page(self) -> str:
        """生成离线页面"""
        offline_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>离线状态 - GitHubSentinel</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .offline-container {
            text-align: center;
            padding: 2rem;
            max-width: 500px;
        }
        
        .offline-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        .offline-title {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        
        .offline-message {
            font-size: 1.1rem;
            opacity: 0.8;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        
        .retry-button {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .retry-button:hover {
            background: #2563eb;
        }
        
        .cached-links {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .cached-links h3 {
            margin-bottom: 1rem;
            opacity: 0.9;
        }
        
        .cached-links a {
            color: #60a5fa;
            text-decoration: none;
            display: block;
            margin: 0.5rem 0;
            padding: 0.5rem;
            border-radius: 0.25rem;
            transition: background 0.3s;
        }
        
        .cached-links a:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="offline-container">
        <div class="offline-icon">📡</div>
        <h1 class="offline-title">您当前处于离线状态</h1>
        <p class="offline-message">
            无法连接到 GitHubSentinel 服务器。<br>
            请检查您的网络连接并稍后重试。
        </p>
        
        <button class="retry-button" onclick="location.reload()">
            重新加载
        </button>
        
        <div class="cached-links">
            <h3>可用的离线页面：</h3>
            <a href="/dashboard">📊 仪表板</a>
            <a href="/subscriptions">📋 订阅管理</a>
            <a href="/activities">🔄 活动记录</a>
            <a href="/reports">📈 报告中心</a>
        </div>
    </div>
    
    <script>
        // 检查网络状态
        function checkOnlineStatus() {
            if (navigator.onLine) {
                location.reload();
            }
        }
        
        // 监听网络状态变化
        window.addEventListener('online', checkOnlineStatus);
        
        // 定期检查网络状态
        setInterval(checkOnlineStatus, 30000);
    </script>
</body>
</html>
'''
        return offline_html.strip()
    
    def get_install_prompt_config(self) -> Dict[str, Any]:
        """获取应用安装提示配置"""
        return {
            "install_prompt": {
                "title": "安装 GitHubSentinel",
                "message": "将 GitHubSentinel 添加到主屏幕，享受更好的使用体验！",
                "buttons": {
                    "install": "立即安装",
                    "cancel": "暂不安装",
                    "later": "稍后提醒"
                }
            },
            "features": [
                "🚀 更快的启动速度",
                "📱 原生应用体验",
                "🔔 系统级通知",
                "📡 离线访问支持",
                "🎯 快捷方式支持"
            ]
        }
    
    def get_notification_config(self) -> Dict[str, Any]:
        """获取通知配置"""
        return {
            "notification": {
                "enabled": True,
                "types": [
                    {
                        "id": "activity",
                        "name": "活动通知",
                        "description": "仓库有新活动时通知",
                        "default": True
                    },
                    {
                        "id": "report",
                        "name": "报告通知",
                        "description": "报告生成完成时通知",
                        "default": True
                    },
                    {
                        "id": "ai_insight",
                        "name": "AI洞察通知",
                        "description": "AI分析完成时通知",
                        "default": False
                    },
                    {
                        "id": "system",
                        "name": "系统通知",
                        "description": "系统公告和更新通知",
                        "default": True
                    }
                ]
            }
        }
    
    def generate_client_config(self) -> Dict[str, Any]:
        """生成客户端配置"""
        return {
            "pwa": {
                "version": self.cache_version,
                "app_name": self.app_name,
                "cache_strategy": "cache-first",
                "offline_support": True,
                "background_sync": True,
                "push_notifications": True
            },
            "features": {
                "service_worker": True,
                "web_app_manifest": True,
                "offline_page": True,
                "install_prompt": True,
                "notification_api": True,
                "background_sync": True
            },
            "cache": {
                "static_cache": f"githubsentinel-{self.cache_version}",
                "dynamic_cache": f"githubsentinel-dynamic-{self.cache_version}",
                "max_age": 7 * 24 * 60 * 60,  # 7天
                "max_entries": 100
            }
        }


# 全局PWA服务实例
pwa_service = PWAService() 