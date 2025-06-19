# PWA 图标资源说明

## 所需图标文件

为了使 GitHub Sentinel 正常作为 PWA 应用运行，需要在 `public` 目录下创建以下图标文件：

### 必需的图标文件：

1. **pwa-192x192.png** (192x192像素)
   - 用于应用图标显示
   - 建议使用高质量的PNG格式

2. **pwa-512x512.png** (512x512像素) 
   - 用于高分辨率设备和启动屏幕
   - 同时用作maskable图标

3. **favicon.ico** (16x16, 32x32, 48x48像素)
   - 浏览器标签页图标

4. **apple-touch-icon.png** (180x180像素)
   - iOS设备添加到主屏幕时使用

5. **masked-icon.svg**
   - Safari固定标签页使用的SVG图标

### 可选的图标文件：

- **pwa-64x64.png** (64x64像素) - 小尺寸显示
- **dashboard-icon.png** (96x96像素) - 快捷方式图标
- **activities-icon.png** (96x96像素) - 快捷方式图标

## 设计建议

### 图标设计原则：
1. **简洁明了**：图标应该简单易识别
2. **品牌一致**：保持与 GitHub Sentinel 品牌风格一致
3. **高对比度**：确保在各种背景下都清晰可见
4. **适合缩放**：在不同尺寸下都应保持清晰

### 推荐的设计元素：
- 使用GitHub主题色：#24292e (深灰)、#0366d6 (蓝色)
- 包含监控/守卫相关的图形元素
- 可考虑使用：望远镜、雷达、盾牌、眼睛等象征性图案

## 创建图标的方法

### 方法1：使用在线工具
推荐使用以下在线PWA图标生成器：
- [PWA Asset Generator](https://github.com/elegantapp/pwa-asset-generator)
- [Favicon Generator](https://realfavicongenerator.net/)
- [PWA Builder](https://www.pwabuilder.com/)

### 方法2：手动创建
1. 创建一个512x512的主图标（PNG格式）
2. 使用图像编辑软件缩放到各种尺寸
3. 确保每个尺寸都进行了优化

### 方法3：使用命令行工具
```bash
# 安装PWA资源生成器
npm install -g pwa-asset-generator

# 从一个主图标生成所有需要的资源
pwa-asset-generator logo.png public --icon-only --favicon --type png
```

## 图标文件位置

所有图标文件应放置在 `frontend/public/` 目录下：

```
frontend/public/
├── favicon.ico
├── apple-touch-icon.png
├── masked-icon.svg
├── pwa-64x64.png
├── pwa-192x192.png
├── pwa-512x512.png
├── dashboard-icon.png
├── activities-icon.png
└── manifest.json
```

## 验证PWA图标

创建图标后，可以通过以下方式验证：

1. **Chrome DevTools**：
   - 打开开发者工具
   - 转到 Application 标签
   - 查看 Manifest 部分
   - 检查图标是否正确加载

2. **PWA测试工具**：
   - [PWA Builder](https://www.pwabuilder.com/)
   - [Lighthouse PWA 审计](https://developers.google.com/web/tools/lighthouse)

3. **真机测试**：
   - 在移动设备上访问应用
   - 尝试"添加到主屏幕"功能
   - 验证图标显示是否正确

## 图标更新后的操作

更新图标后：
1. 清除浏览器缓存
2. 重新构建项目：`npm run build`
3. 在移动设备上重新添加PWA到主屏幕

## 临时解决方案

如果暂时没有专业设计的图标，可以：
1. 使用文字图标生成器创建简单的文字logo
2. 从免费图标库下载合适的图标并进行修改
3. 使用简单的几何图形组合

建议尽快创建专业的品牌图标以提升用户体验。 