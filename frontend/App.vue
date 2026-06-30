<template>
  <div class="app-container">
    <!-- 左侧工具栏侧边栏 -->
    <aside class="sidebar">
      <!-- 标题 -->
      <div class="sidebar-title">
        <span class="logo-dot" :class="{ 'pulse': isSystemActive }"></span>
        AI多智能体协同系统
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" active-class="nav-active" exact-active-class="nav-active">
          <span class="nav-icon">🏠</span>
          <span class="nav-label">首页</span>
        </router-link>
        <router-link to="/workbench" class="nav-item" active-class="nav-active">
          <span class="nav-icon">💼</span>
          <span class="nav-label">工作台</span>
        </router-link>
      </nav>

      <div class="sidebar-divider"></div>

      <!-- 智能体列表 -->
      <div class="agent-list">
        <router-link
          v-for="(agent, index) in agents"
          :key="index"
          :to="`/agent/${agent.type}`"
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

      <!-- 系统状态 -->
      <div class="system-status">
        <div class="status-indicator" :class="{ active: isSystemActive }"></div>
        <span>{{ isSystemActive ? '系统运行中' : '系统待机' }}</span>
      </div>
    </aside>

    <!-- 路由视图 -->
    <router-view />
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'

// 系统状态（与工作台共享）
const isSystemActive = ref(true)

// 侧边栏智能体数据（与工作台共享）
const agents = ref([
  {
    name: 'AI产品经理',
    avatar: '产',
    type: 'pm',
    description: '需求规划、PRD输出',
    isWorking: false,
    status: ''
  },
  {
    name: 'AI程序员',
    avatar: '开',
    type: 'dev',
    description: '编码、接口开发',
    isWorking: false,
    status: ''
  },
  {
    name: 'AI测试工程师',
    avatar: '测',
    type: 'test',
    description: '用例、缺陷检测',
    isWorking: false,
    status: ''
  },
  {
    name: 'AI运维助理',
    avatar: '运',
    type: 'op',
    description: '部署、性能监控',
    isWorking: false,
    status: ''
  }
])

// 提供给子组件（WorkbenchPage）
provide('isSystemActive', isSystemActive)
provide('agents', agents)
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "SF Pro Display", sans-serif;
}
body {
  background: linear-gradient(135deg, #F5F5F7 0%, #E8E8ED 100%);
  min-height: 100vh;
}
#app {
  height: 100%;
}
</style>

<style scoped>
.app-container {
  display: flex;
  color: #1D1D1F;
  min-height: 100vh;
}

/* 左侧工具栏侧边栏 */
.sidebar {
  width: 240px;
  background: rgba(28,28,30,0.85);
  backdrop-filter: blur(24px);
  padding: 24px 12px;
  display: flex;
  flex-direction: column;
  color: #fff;
  flex-shrink: 0;
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
  width: 12px;
  height: 12px;
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
.sidebar-nav {
  margin-bottom: 12px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  text-decoration: none;
  color: rgba(255,255,255,0.75);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}
.nav-item:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}
.nav-active {
  background: rgba(0,122,255,0.2);
  color: #fff;
}
.nav-icon {
  font-size: 16px;
}
.nav-label {
  font-size: 14px;
}

.sidebar-divider {
  height: 1px;
  background: rgba(255,255,255,0.12);
  margin: 8px 8px 16px;
}

/* 智能体列表 */
.agent-list {
  flex: 1;
}
.agent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 8px;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 6px;
  transition: all 0.2s ease;
  position: relative;
  text-decoration: none;
  color: inherit;
}
.agent-item:hover {
  background: rgba(255,255,255,0.1);
}
.agent-item.active,
.agent-active {
  background: rgba(0,122,255,0.22);
}
.agent-item.working {
  background: rgba(52,199,89,0.15);
}
.agent-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  position: relative;
}
.working-indicator {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 10px;
  height: 10px;
  background: #34C759;
  border-radius: 50%;
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
.agent-info h4 {
  font-size: 14px;
  font-weight: 500;
}
.agent-info p {
  font-size: 11px;
  color: #86868B;
}
.agent-status {
  font-size: 10px;
  color: #34C759;
  display: block;
  margin-top: 2px;
}

/* 系统状态指示 */
.system-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  font-size: 12px;
}
.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #86868B;
  transition: all 0.3s ease;
}
.status-indicator.active {
  background: #34C759;
  box-shadow: 0 0 8px rgba(52,199,89,0.6);
}
</style>
