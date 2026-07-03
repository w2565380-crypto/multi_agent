<template>
  <main class="main-wrap">
    <Particles
      :particleCount="150"
      :particleSpread="8"
      :speed="0.08"
      :particleColors="['#ffffff']"
      :particleBaseSize="120"
      :sizeRandomness="1"
      :moveParticlesOnHover="true"
      :particleHoverFactor="0.5"
      :disableRotation="false"
    />
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-title">
        <div class="agent-head">
          <div>
            <h1>{{ agent.name }}</h1>
            <span>{{ agent.description }}</span>
            <span v-if="projectName" class="project-context">📁 {{ projectName }}</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <span class="file-count">共 {{ files.length }} 个文件</span>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar glass-card" v-if="files.length > 0">
      <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <circle cx="11" cy="11" r="8"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        :placeholder="`搜索 ${agent.name} 接收的文件...`"
      >
      <span v-if="searchQuery" class="search-clear" @click="searchQuery = ''">✕</span>
    </div>

    <!-- MD 文件列表 -->
    <div class="glass-card" v-if="files.length > 0">
      <div class="card-head">
        <h2>📄 接收到的 Markdown 文件</h2>
        <span v-if="searchQuery" class="search-result-hint">
          找到 {{ filteredFiles.length }} / {{ files.length }} 个文件
        </span>
        <span v-else class="live-indicator">● 实时同步</span>
      </div>

      <div v-if="filteredFiles.length === 0" class="empty-search">
        <span class="empty-search-icon">🔍</span>
        <p>未找到匹配 "{{ searchQuery }}" 的文件</p>
      </div>

      <div class="file-list" v-else>
        <div
          v-for="(file, index) in filteredFiles"
          :key="file.id"
          class="file-card"
          :class="{ 'fade-in': file.isNew }"
          @click="openFile(file)"
        >
          <div class="file-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <rect x="4" y="2" width="16" height="20" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <line x1="8" y1="7" x2="16" y2="7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              <line x1="8" y1="11" x2="16" y2="11" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              <line x1="8" y1="15" x2="12" y2="15" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="file-info">
            <h4>{{ file.name }}</h4>
            <p class="file-preview">{{ file.preview }}</p>
            <div class="file-meta">
              <span class="file-time">{{ file.receivedAt }}</span>
              <span class="file-type">.md</span>
            </div>
          </div>
          <div class="file-arrow">→</div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="glass-card empty-state" v-else>
      <div class="empty-icon">📭</div>
      <h3>暂无接收文件</h3>
      <p>当后端推送 Markdown 文件后，将在此处显示</p>
      <p class="empty-hint">文件由 AI 智能体自动同步，无需手动导入</p>
    </div>

    <!-- 文件详情弹窗 -->
    <div class="modal-overlay" v-if="selectedFile" @click.self="closeFile">
      <div class="modal-content glass-card">
        <div class="modal-header">
          <div>
            <h3>{{ selectedFile.name }}</h3>
            <span class="modal-agent">{{ agent.name }} · {{ selectedFile.receivedAt }}</span>
          </div>
          <button class="btn-close" @click="closeFile">✕</button>
        </div>
        <div class="modal-body">
          <div class="markdown-preview" v-html="renderedContent"></div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../stores/project.js'
import Particles from '../components/Particles.vue'

const route = useRoute()
const store = useProjectStore()

// 项目上下文
const projectId = computed(() => route.query.projectId)
const projectName = computed(() => {
  if (!projectId.value) return ''
  const p = store.getProjectById(Number(projectId.value))
  return p ? p.name : ''
})

// 智能体配置映射
const agentConfig = {
  pm:   { name: 'AI产品经理',   avatar: '产', description: '需求规划、PRD输出' },
  dev:  { name: 'AI程序员',     avatar: '开', description: '编码、接口开发' },
  test: { name: 'AI测试工程师', avatar: '测', description: '用例、缺陷检测' },
  op:   { name: 'AI运维助理',   avatar: '运', description: '部署、性能监控' }
}

const agent = computed(() => agentConfig[route.params.type] || agentConfig.pm)

// 模拟 MD 文件数据
const mockFiles = {
  pm: [
    {
      id: 1,
      name: '用户登录模块PRD_v2.3.md',
      preview: '## 需求概述\n\n用户登录模块需要支持手机号+验证码、邮箱+密码两种方式...',
      content: `# 用户登录模块 PRD v2.3

## 需求概述
用户登录模块需要支持以下登录方式：
- 手机号 + 验证码登录
- 邮箱 + 密码登录
- 第三方 OAuth 登录（微信、企业微信）

## 功能需求
### 1. 手机号验证码登录
- 输入手机号，点击获取验证码
- 60秒倒计时，防止重复发送
- 验证码 6 位数字，有效期 5 分钟

### 2. 邮箱密码登录
- 支持邮箱格式校验
- 密码长度 6-20 位
- 错误 3 次锁定 15 分钟

## 非功能需求
- 登录响应时间 < 500ms
- 支持 1000 并发登录
- 敏感信息加密传输`,
      receivedAt: '2026-06-30 10:30',
      isNew: false
    },
    {
      id: 2,
      name: '智能体对话界面交互设计.md',
      preview: '## 交互流程\n\n1. 用户进入对话界面\n2. 选择目标智能体\n3. 发送消息...',
      content: `# 智能体对话界面交互设计

## 交互流程
1. 用户进入对话界面
2. 选择目标智能体或群发
3. 输入消息内容
4. 支持 @ 提及特定智能体
5. 消息支持撤回（2分钟内）

## 界面布局
- 左侧：智能体列表
- 中间：对话区域
- 右侧：任务上下文面板

## 消息类型
- 文本消息
- Markdown 渲染消息
- 任务卡片消息
- 文件分享消息`,
      receivedAt: '2026-06-29 16:45',
      isNew: false
    },
    {
      id: 3,
      name: 'Q3产品路线图规划.md',
      preview: '## Q3 重点方向\n\n- 多智能体协同效率提升\n- 自动化测试覆盖率...',
      content: `# Q3 产品路线图规划

## Q3 重点方向
- 多智能体协同效率提升 40%
- 自动化测试覆盖率达到 90%
- 新增运维监控大屏
- 移动端适配（iOS/Android）

## 里程碑
| 时间 | 里程碑 | 负责人 |
|------|--------|--------|
| 7月 | 智能体 API 重构 | AI程序员 |
| 8月 | 自动化测试平台 | AI测试工程师 |
| 9月 | 运维大屏上线 | AI运维助理 |`,
      receivedAt: '2026-06-28 09:15',
      isNew: false
    }
  ],
  dev: [
    {
      id: 4,
      name: 'API接口设计文档_v1.0.md',
      preview: '## 接口规范\n\n所有接口遵循 RESTful 设计，返回统一 JSON 格式...',
      content: `# API 接口设计文档 v1.0

## 接口规范
所有接口遵循 RESTful 设计，返回统一 JSON 格式：
\`\`\`json
{
  "code": 200,
  "data": {},
  "message": "success"
}
\`\`\`

## 智能体相关接口
- \`GET /api/agents\` - 获取智能体列表
- \`POST /api/agents/:id/message\` - 发送消息
- \`GET /api/agents/:id/tasks\` - 获取任务列表

## 认证方式
- JWT Token 认证
- Token 有效期 24 小时
- 支持 Refresh Token 续期`,
      receivedAt: '2026-06-30 11:20',
      isNew: false
    },
    {
      id: 5,
      name: '前端组件开发规范.md',
      preview: '## 组件命名\n\n- 页面组件：PascalCase，如 UserProfile\n- 通用组件：kebab-case...',
      content: `# 前端组件开发规范

## 组件命名
- 页面组件：PascalCase（UserProfile.vue）
- 通用组件：PascalCase（GlassCard.vue）
- 目录命名：kebab-case（user-profile/）

## 文件结构
\`\`\`
src/
  pages/       # 页面组件
  components/  # 通用组件
  router/      # 路由配置
  stores/      # 状态管理
\`\`\`

## 样式规范
- 使用 scoped 样式
- 遵循 Apple Design 风格
- 磨砂玻璃效果统一封装`,
      receivedAt: '2026-06-29 14:30',
      isNew: false
    }
  ],
  test: [
    {
      id: 6,
      name: '登录模块测试用例.md',
      preview: '## 测试范围\n\n覆盖手机号登录、邮箱登录、异常场景、并发测试...',
      content: `# 登录模块测试用例

## 测试范围
- 功能测试：手机号登录、邮箱登录、OAuth 登录
- 异常测试：错误密码、过期验证码、网络超时
- 性能测试：1000 并发登录
- 安全测试：SQL 注入、XSS 攻击、暴力破解

## 用例统计
| 类型 | 用例数 | 通过 | 失败 | 阻塞 |
|------|--------|------|------|------|
| 功能 | 45 | 42 | 2 | 1 |
| 异常 | 20 | 18 | 2 | 0 |
| 性能 | 5 | 5 | 0 | 0 |
| 安全 | 8 | 7 | 1 | 0 |`,
      receivedAt: '2026-06-30 09:00',
      isNew: false
    }
  ],
  op: [
    {
      id: 7,
      name: '服务器部署方案_v2.md',
      preview: '## 部署架构\n\n采用 Docker + K8s 集群部署，Nginx 反向代理...',
      content: `# 服务器部署方案 v2

## 部署架构
- Docker 容器化部署
- Kubernetes 集群管理
- Nginx 反向代理 + 负载均衡
- Redis 缓存层
- PostgreSQL 主从复制

## 环境配置
| 环境 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| 开发 | 2核 | 4GB | 50GB |
| 测试 | 4核 | 8GB | 100GB |
| 生产 | 8核 | 16GB | 200GB |

## 监控指标
- CPU 使用率 < 70%
- 内存使用率 < 80%
- 接口响应时间 < 200ms
- 错误率 < 0.1%`,
      receivedAt: '2026-06-28 17:00',
      isNew: false
    },
    {
      id: 8,
      name: 'CDN加速配置指南.md',
      preview: '## CDN 配置\n\n静态资源通过 CDN 分发，缓存策略如下...',
      content: `# CDN 加速配置指南

## CDN 配置
- 静态资源（JS/CSS/图片）通过 CDN 分发
- 缓存时间：静态资源 7 天，HTML 不缓存
- 支持 Gzip/Brotli 压缩

## 域名配置
- 主站：app.example.com
- CDN：cdn.example.com
- API：api.example.com

## 性能优化
- 图片懒加载
- 代码分割（Code Splitting）
- 预加载关键资源
- HTTP/2 多路复用`,
      receivedAt: '2026-06-27 10:45',
      isNew: false
    }
  ]
}

const files = ref([])
const selectedFile = ref(null)
const searchQuery = ref('')

// 搜索过滤
const filteredFiles = computed(() => {
  if (!searchQuery.value.trim()) return files.value
  const q = searchQuery.value.toLowerCase()
  return files.value.filter(f =>
    f.name.toLowerCase().includes(q)
  )
})

// 当前无后端文件接口，使用模拟数据
const fetchFiles = (type) => {
  files.value = (mockFiles[type] || []).map(f => ({ ...f, isNew: true }))
  setTimeout(() => files.value.forEach(f => f.isNew = false), 600)
}

// 路由变化时加载对应智能体的模拟文件
watch(() => route.params.type, (type) => {
  selectedFile.value = null
  searchQuery.value = ''
  fetchFiles(type)
}, { immediate: true })

// 简单的 Markdown 渲染（将 ## 转为标题，- 转为列表等）
const renderedContent = computed(() => {
  if (!selectedFile.value) return ''
  let html = selectedFile.value.content
    // 代码块
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
    // 行内代码
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    // 标题
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // 表格
    .replace(/^\|(.+)\|$/gm, (match) => {
      if (match.includes('---')) return ''
      const cells = match.split('|').filter(c => c.trim())
      return '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>'
    })
    // 加粗
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 无序列表
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // 换行
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>')
  return html
})

const openFile = (file) => {
  selectedFile.value = file
}

const closeFile = () => {
  selectedFile.value = null
}
</script>

<style scoped>
.main-wrap {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #1e1e24;
  position: relative;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.agent-head {
  display: flex;
  align-items: center;
  gap: 16px;
}
.agent-avatar-lg {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: white;
}
.avatar-pm { background: #007AFF; }
.avatar-dev { background: #34C759; }
.avatar-test { background: #FF9500; }
.avatar-op { background: #AF52DE; }
.page-title h1 {
  font-size: 26px;
  font-weight: 600;
  color: #d0d0d8;
}
.page-title span {
  color: #888899;
  font-size: 14px;
}
.project-context {
  color: #007AFF !important;
  font-size: 12px !important;
  display: block;
  margin-top: 4px;
  font-weight: 500;
}
.header-actions .file-count {
  font-size: 14px;
  color: #86868B;
  background: rgba(255,255,255,0.6);
  padding: 6px 14px;
  border-radius: 8px;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding: 12px 18px !important;
}
.search-icon {
  color: #666680;
  flex-shrink: 0;
}
.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  color: #d0d0d8;
  outline: none;
  font-family: inherit;
}
.search-input::placeholder {
  color: #555570;
}
.search-clear {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  color: #888899;
  transition: all 0.2s;
  flex-shrink: 0;
}
.search-clear:hover {
  background: rgba(255,255,255,0.15);
  color: #d0d0d8;
}
.search-result-hint {
  font-size: 12px;
  color: #7c9aff;
  font-weight: 500;
}
.empty-search {
  text-align: center;
  padding: 40px 20px;
}
.empty-search-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 12px;
}
.empty-search p {
  font-size: 14px;
  color: #86868B;
}

/* 磨砂玻璃卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(16px);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 20px;
  margin-bottom: 20px;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-head h2 {
  font-size: 17px;
  font-weight: 600;
  color: #d0d0d8;
}
.live-indicator {
  font-size: 12px;
  color: #34C759;
}

/* 文件列表 */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.file-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(255,255,255,0.05);
}
.file-card:hover {
  background: rgba(255,255,255,0.06);
  transform: translateX(4px);
  border-color: rgba(255,255,255,0.08);
}
.file-card.fade-in {
  animation: fadeSlideIn 0.4s ease;
}
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateX(-12px); }
  to { opacity: 1; transform: translateX(0); }
}
.file-icon {
  color: #7c9aff;
  flex-shrink: 0;
}
.file-info {
  flex: 1;
  min-width: 0;
}
.file-info h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #d0d0d8;
}
.file-preview {
  font-size: 12px;
  color: #888899;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 6px;
}
.file-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}
.file-time {
  font-size: 11px;
  color: #666680;
}
.file-type {
  font-size: 10px;
  padding: 1px 6px;
  background: rgba(124, 154, 255, 0.15);
  color: #7c9aff;
  border-radius: 4px;
}
.file-arrow {
  font-size: 18px;
  color: #555570;
  transition: transform 0.2s;
}
.file-card:hover .file-arrow {
  transform: translateX(4px);
  color: #7c9aff;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #d0d0d8;
}
.empty-state p {
  font-size: 14px;
  color: #888899;
  margin-bottom: 4px;
}
.empty-hint {
  font-size: 12px !important;
  color: #555570 !important;
  margin-top: 8px;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.modal-content {
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0,0,0,0.08);
}
.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
}
.modal-agent {
  font-size: 12px;
  color: #86868B;
  display: block;
  margin-top: 4px;
}
.btn-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.06);
  cursor: pointer;
  font-size: 16px;
  color: #86868B;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-close:hover {
  background: rgba(0,0,0,0.12);
  color: #1D1D1F;
}
.modal-body {
  overflow-y: auto;
  flex: 1;
}

/* Markdown 渲染样式 */
.markdown-preview {
  font-size: 14px;
  line-height: 1.8;
  color: #1D1D1F;
}
.markdown-preview :deep(h1) {
  font-size: 22px;
  font-weight: 700;
  margin: 16px 0 12px;
  color: #1D1D1F;
}
.markdown-preview :deep(h2) {
  font-size: 18px;
  font-weight: 600;
  margin: 14px 0 10px;
  color: #1D1D1F;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(0,0,0,0.08);
}
.markdown-preview :deep(h3) {
  font-size: 15px;
  font-weight: 600;
  margin: 12px 0 8px;
}
.markdown-preview :deep(strong) {
  font-weight: 600;
  color: #007AFF;
}
.markdown-preview :deep(li) {
  margin-left: 20px;
  margin-bottom: 4px;
}
.markdown-preview :deep(.code-block) {
  background: rgba(28,28,30,0.06);
  border-radius: 8px;
  padding: 14px 16px;
  margin: 12px 0;
  overflow-x: auto;
  font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
}
.markdown-preview :deep(.inline-code) {
  background: rgba(0,122,255,0.08);
  color: #007AFF;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Cascadia Code', monospace;
  font-size: 13px;
}
.markdown-preview :deep(tr) {
  display: flex;
  gap: 0;
}
.markdown-preview :deep(td) {
  padding: 4px 12px;
  border: 1px solid rgba(0,0,0,0.08);
  font-size: 13px;
}
</style>
