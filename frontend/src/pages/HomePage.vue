<template>
  <div class="home-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </div>

    <!-- 主内容 -->
    <div class="home-content">
      <div class="hero-section">
        <div class="logo-icon">
          <span class="logo-dot pulse"></span>
          <span class="logo-text">AI</span>
        </div>
        <h1 class="hero-title">AI多智能体协同系统</h1>
        <p class="hero-subtitle">多AI智能体实时协同 · 敏捷项目全流程模拟</p>
        <p class="hero-desc">
          模拟企业级 AI 产品经理、程序员、测试工程师、运维助理<br>
          四大智能体协同工作，自动化任务流转与实时沟通
        </p>
        <router-link to="/workbench" class="cta-button">
          <span>进入工作台</span>
          <span class="cta-arrow">→</span>
        </router-link>
      </div>

      <!-- 智能体特性卡片 -->
      <div class="feature-cards">
        <div class="feature-card" v-for="agent in featuredAgents" :key="agent.name">
          <div class="feature-avatar" :class="`avatar-${agent.type}`">{{ agent.avatar }}</div>
          <h3>{{ agent.name }}</h3>
          <p>{{ agent.description }}</p>
        </div>
      </div>

      <!-- 底部版本信息 -->
      <div class="home-footer">
        <span>v1.0.0</span>
        <span class="dot-sep">·</span>
        <span>Vue 3 + Vite</span>
        <span class="dot-sep">·</span>
        <span>Apple Design</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const featuredAgents = ref([
  {
    name: 'AI产品经理',
    avatar: '产',
    type: 'pm',
    description: '需求规划、PRD撰写、原型设计，驱动项目方向'
  },
  {
    name: 'AI程序员',
    avatar: '开',
    type: 'dev',
    description: '接口开发、前端渲染、代码重构，保障交付质量'
  },
  {
    name: 'AI测试工程师',
    avatar: '测',
    type: 'test',
    description: '功能测试、兼容性验证、自动化回归'
  },
  {
    name: 'AI运维助理',
    avatar: '运',
    type: 'op',
    description: '部署监控、性能优化、安全加固'
  }
])
</script>

<style scoped>
.home-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #F5F5F7 0%, #E8E8ED 50%, #F0F0F5 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰光球 */
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: float 6s ease-in-out infinite;
}
.orb-1 {
  width: 300px;
  height: 300px;
  background: rgba(0, 122, 255, 0.3);
  top: -10%;
  left: -5%;
  animation-delay: 0s;
}
.orb-2 {
  width: 250px;
  height: 250px;
  background: rgba(175, 82, 222, 0.3);
  bottom: -10%;
  right: -5%;
  animation-delay: -2s;
}
.orb-3 {
  width: 200px;
  height: 200px;
  background: rgba(52, 199, 89, 0.25);
  top: 60%;
  left: 40%;
  animation-delay: -4s;
}
@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

/* 主内容区 */
.home-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 40px;
  max-width: 800px;
}

/* Hero 区域 */
.logo-icon {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
}
.logo-dot {
  width: 16px;
  height: 16px;
  background: #007AFF;
  border-radius: 50%;
}
.logo-dot.pulse {
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.6; }
}
.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #007AFF;
  letter-spacing: 2px;
}

.hero-title {
  font-size: 42px;
  font-weight: 700;
  color: #1D1D1F;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}
.hero-subtitle {
  font-size: 18px;
  color: #86868B;
  font-weight: 400;
  margin-bottom: 16px;
}
.hero-desc {
  font-size: 15px;
  color: #6E6E73;
  line-height: 1.8;
  margin-bottom: 36px;
}

/* CTA 按钮 */
.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: #007AFF;
  color: white;
  border-radius: 12px;
  font-size: 17px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.35);
}
.cta-button:hover {
  background: #0062CC;
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0, 122, 255, 0.45);
}
.cta-arrow {
  transition: transform 0.3s ease;
}
.cta-button:hover .cta-arrow {
  transform: translateX(4px);
}

/* 智能体特性卡片 */
.feature-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 48px;
}
.feature-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  border-radius: 14px;
  padding: 20px 16px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}
.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}
.feature-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0 auto 12px;
}
.avatar-pm { background: #007AFF; }
.avatar-dev { background: #34C759; }
.avatar-test { background: #FF9500; }
.avatar-op { background: #AF52DE; }
.feature-card h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #1D1D1F;
}
.feature-card p {
  font-size: 12px;
  color: #86868B;
  line-height: 1.5;
}

/* 底部 */
.home-footer {
  margin-top: 48px;
  font-size: 12px;
  color: #86868B;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.dot-sep {
  color: #C7C7CC;
}
</style>
