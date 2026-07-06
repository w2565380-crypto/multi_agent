<template>
  <!-- 登录页：无侧边栏，全屏展示 -->
  <router-view v-if="isLoginPage" />

    <!-- 主布局：侧边栏 + 内容 -->
    <div class="app-container" v-else>
      <!-- 收缩/展开按钮 -->
      <button class="sidebar-toggle" @click="sidebarOpen = !sidebarOpen" :title="sidebarOpen ? '收起工具栏' : '展开工具栏'">
        <span class="toggle-arrow">{{ sidebarOpen ? '◀' : '▶' }}</span>
      </button>

      <!-- 左侧工具栏侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: !sidebarOpen }">
      <div class="sidebar-title">
        <span class="logo-dot" :class="{ 'pulse': isSystemActive }"></span>
        AI智能体公司
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" active-class="nav-active" exact-active-class="nav-active">
          <span class="nav-icon">🏠</span>
          <span class="nav-label">首页</span>
        </router-link>
        <router-link to="/projects" class="nav-item" active-class="nav-active">
          <span class="nav-icon">📁</span>
          <span class="nav-label">项目列表</span>
        </router-link>
      </nav>

      <div class="sidebar-divider"></div>

      <!-- 当前项目信息 -->
      <div class="current-project-section" v-if="currentProject">
        <div class="current-project-label">当前项目</div>
        <router-link
          :to="`/projects/${currentProject.id}`"
          class="current-project-item"
        >
          <span class="project-dot" :class="currentProject.status === 'completed' ? 'dot-done' : 'dot-active'"></span>
          <span class="current-project-name">{{ currentProject.name }}</span>
        </router-link>
      </div>
      <div class="current-project-section" v-else>
        <div class="current-project-label">当前项目</div>
        <router-link to="/projects" class="no-project-hint">
          <span class="project-dot dot-none"></span>
          <span>请选择项目</span>
        </router-link>
      </div>

      <div class="sidebar-divider"></div>

      <!-- 智能体列表（带当前项目上下文） -->
      <div class="agent-list">
        <router-link
          v-for="agent in agents"
          :key="agent.type"
          :to="agentLink(agent.type)"
          class="agent-item"
          :class="{ working: agent.isWorking }"
          active-class="agent-active"
        >
          <div class="agent-avatar" :class="`avatar-${agent.type}`">
            {{ agent.avatar }}
            <span v-if="agent.isWorking" class="working-indicator"></span>
          </div>
          <div class="agent-info">
            <h4>{{ agent.name }}</h4>
            <p>{{ agent.description }}</p>
            <span v-if="agent.status" class="agent-status">{{ agent.status }}</span>
          </div>
        </router-link>
      </div>

      <!-- 用户信息 & 退出 -->
      <div class="user-section">
        <router-link to="/profile" class="user-info">
          <img v-if="auth.user?.image" :src="auth.user.image + '?v=' + auth.imageVersion" class="user-avatar-img" alt="" />
          <span v-else class="user-avatar-icon">👤</span>
          <span class="user-name">{{ auth.user?.userName || '用户' }}</span>
        </router-link>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>

      <!-- 系统状态 -->
      <div class="system-status">
        <div class="status-indicator" :class="{ active: isSystemActive }"></div>
        <span>{{ isSystemActive ? '系统运行中' : '系统待机' }}</span>
      </div>
    </aside>

    <!-- 路由视图 -->
    <div class="content-area" :class="{ 'sidebar-hidden': !sidebarOpen }">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, provide, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useProjectStore } from './src/stores/project.js'
import { useAuthStore } from './src/stores/auth.js'

const router = useRouter()
const route = useRoute()
const store = useProjectStore()
const auth = useAuthStore()
const isSystemActive = ref(true)
const sidebarOpen = ref(false)

// 每次登录/登出时重置工具栏为收起状态
watch(() => auth.isLoggedIn, () => {
  sidebarOpen.value = false
})

const isLoginPage = computed(() => route.name === 'Login')

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

// 当前项目
const currentProject = computed(() => store.currentProject)

// 智能体链接（带项目参数）
const agentLink = (type) => {
  const projectId = store.currentProjectId
  return projectId ? `/agent/${type}?projectId=${projectId}` : `/agent/${type}`
}

// 智能体数据
const agents = ref([
  { name: 'AI产品经理',   avatar: '🧑‍💻', type: 'pm',   description: '需求规划、PRD输出', isWorking: false, status: '' },
  { name: 'AI程序员',     avatar: '🧑‍💻', type: 'dev',  description: '编码、接口开发',     isWorking: false, status: '' },
  { name: 'AI测试工程师', avatar: '🧑‍💻', type: 'test', description: '用例、缺陷检测',     isWorking: false, status: '' }
])

// 提供给子组件
provide('isSystemActive', isSystemActive)
provide('agents', agents)
</script>

<style>
* {
  margin: 0; padding: 0; box-sizing: border-box;
}
html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "SF Pro Display", sans-serif;
}
body {
  background: linear-gradient(135deg, #F5F5F7 0%, #E8E8ED 100%);
  min-height: 100vh;
}
#app { height: 100%; }
</style>

<style scoped>
.app-container {
  display: flex;
  color: #1D1D1F;
  min-height: 100vh;
  position: relative;
}

.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 240px;
  background: rgba(28,28,30,0.85);
  backdrop-filter: blur(24px);
  padding: 24px 12px;
  display: flex;
  flex-direction: column;
  color: #fff;
  z-index: 40;
  overflow: hidden;
  transition: transform 0.3s ease;
}
.sidebar.collapsed {
  transform: translateX(-100%);
}

/* router-view 内容区 —— 通过 margin-left 过渡左右伸缩 */
.content-area {
  margin-left: 240px;
  transition: margin-left 0.3s ease;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.content-area.sidebar-hidden {
  margin-left: 0;
}

/* 侧边栏切换按钮 */
.sidebar-toggle {
  position: fixed;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  z-index: 50;
  width: 24px;
  height: 48px;
  border: none;
  background: rgba(28,28,30,0.7);
  backdrop-filter: blur(8px);
  color: rgba(255,255,255,0.7);
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  padding: 0;
}
.sidebar-toggle:hover {
  background: rgba(28,28,30,0.9);
  color: #fff;
  width: 28px;
}
.toggle-arrow {
  font-size: 11px;
  transition: transform 0.3s ease;
}
.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 28px;
  padding-left: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.sidebar-title .logo-dot {
  width: 12px; height: 12px;
  background: #007AFF;
  border-radius: 50%;
  transition: all 0.3s ease;
}
.sidebar-title .logo-dot.pulse {
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
}

/* 导航菜单 */
.sidebar-nav { margin-bottom: 12px; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: 10px;
  text-decoration: none;
  color: rgba(255,255,255,0.75);
  font-size: 14px; font-weight: 500;
  transition: all 0.2s ease;
}
.nav-item:hover { background: rgba(255,255,255,0.1); color: #fff; }
.nav-active { background: rgba(0,122,255,0.2); color: #fff; }
.nav-icon { font-size: 16px; }
.nav-label { font-size: 14px; }

.sidebar-divider {
  height: 1px;
  background: rgba(255,255,255,0.12);
  margin: 8px 8px 12px;
}

/* 当前项目 */
.current-project-section {
  padding: 0 8px;
  margin-bottom: 4px;
}
.current-project-label {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  padding-left: 6px;
}
.current-project-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; border-radius: 8px;
  text-decoration: none;
  color: rgba(255,255,255,0.9);
  font-size: 13px; font-weight: 500;
  transition: all 0.2s;
  background: rgba(255,255,255,0.06);
}
.current-project-item:hover { background: rgba(255,255,255,0.12); }
.current-project-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.no-project-hint {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; border-radius: 8px;
  text-decoration: none;
  color: rgba(255,255,255,0.4);
  font-size: 13px;
  transition: all 0.2s;
}
.no-project-hint:hover { color: rgba(255,255,255,0.7); background: rgba(255,255,255,0.06); }
.project-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.dot-active { background: #007AFF; box-shadow: 0 0 6px rgba(0,122,255,0.5); }
.dot-done { background: #34C759; }
.dot-none { background: rgba(255,255,255,0.2); }

/* 智能体列表 */
.agent-list { flex: 1; }
.agent-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 8px; border-radius: 10px;
  cursor: pointer; margin-bottom: 6px;
  transition: all 0.2s ease;
  position: relative;
  text-decoration: none;
  color: inherit;
}
.agent-item:hover { background: rgba(255,255,255,0.1); }
.agent-item.active,
.agent-active { background: rgba(0,122,255,0.22); }
.agent-item.working { background: rgba(52,199,89,0.15); }
.agent-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 500; position: relative;
}
.working-indicator {
  position: absolute; top: -2px; right: -2px;
  width: 10px; height: 10px;
  background: #34C759; border-radius: 50%;
  border: 2px solid rgba(28,28,30,0.85);
  animation: working-pulse 1s infinite;
}
@keyframes working-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
.avatar-pm { background: #007AFF; }
.avatar-dev { background: #34C759; }
.avatar-test { background: #FF9500; }
.avatar-op { background: #AF52DE; }
.agent-info h4 { font-size: 14px; font-weight: 500; }
.agent-info p { font-size: 11px; color: #86868B; }
.agent-status { font-size: 10px; color: #34C759; display: block; margin-top: 2px; }

/* 用户区 */
.user-section {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; margin-bottom: 8px;
  background: rgba(255,255,255,0.06); border-radius: 10px;
}
.user-info {
  display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 500;
  text-decoration: none; color: inherit; flex: 1; min-width: 0;
}
.user-info:hover { color: #fff; }
.user-avatar-icon { font-size: 16px; }
.user-avatar-img {
  width: 24px; height: 24px; border-radius: 50%; object-fit: cover;
}
.user-name {
  max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.logout-btn {
  padding: 4px 10px; font-size: 11px;
  background: rgba(255,59,48,0.15); color: #FF453A;
  border: 1px solid rgba(255,59,48,0.2); border-radius: 6px;
  cursor: pointer; transition: all 0.2s;
}
.logout-btn:hover { background: rgba(255,59,48,0.25); }

/* 系统状态 */
.system-status {
  display: flex; align-items: center; gap: 8px;
  padding: 12px;
  background: rgba(255,255,255,0.1);
  border-radius: 8px; font-size: 12px;
}
.status-indicator {
  width: 8px; height: 8px; border-radius: 50%;
  background: #86868B;
  transition: all 0.3s ease;
}
.status-indicator.active {
  background: #34C759;
  box-shadow: 0 0 8px rgba(52,199,89,0.6);
}
</style>
