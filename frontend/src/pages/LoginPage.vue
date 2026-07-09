<template>
  <div class="login-container">
    <DotField
      :dotRadius="1.5"
      :dotSpacing="16"
      :bulgeStrength="80"
      :glowRadius="180"
      gradientFrom="rgba(140, 110, 250, 0.4)"
      gradientTo="rgba(110, 90, 210, 0.3)"
      glowColor="#0a0a1a"
    />

    <div class="login-card glass-card">
      <div class="login-header">
        <span class="logo-dot pulse"></span>
        <h1>AI多智能体协同系统</h1>
        <p>登录或注册账号以开始使用</p>
      </div>

      <!-- Tab 切换 -->
      <div class="tab-row">
        <button class="tab-btn" :class="{ active: mode === 'login' }" @click="switchMode('login')">登录</button>
        <button class="tab-btn" :class="{ active: mode === 'register' }" @click="switchMode('register')">注册</button>
      </div>

      <!-- 表单 -->
      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="form.userName"
            class="apple-input"
            :placeholder="mode === 'login' ? '请输入用户名' : '2-50位，仅限数字和字母'"
            maxlength="50"
            @input="clearError"
          >
          <span v-if="errors.userName" class="field-error">{{ errors.userName }}</span>
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="form.password"
            class="apple-input"
            type="password"
            :placeholder="mode === 'login' ? '请输入密码' : '至少6位，仅限字母和数字'"
            @input="clearError"
          >
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <div class="form-group" v-if="mode === 'register'">
          <label>确认密码</label>
          <input
            v-model="form.confirmPassword"
            class="apple-input"
            type="password"
            placeholder="再次输入密码"
            @input="clearError"
          >
          <span v-if="errors.confirmPassword" class="field-error">{{ errors.confirmPassword }}</span>
        </div>

        <!-- 错误提示 -->
        <div v-if="serverError" class="server-error">{{ serverError }}</div>

        <button class="btn-submit" type="submit" :disabled="loading">
          <span v-if="loading" class="btn-spinner"></span>
          {{ loading ? '处理中...' : (mode === 'login' ? '登 录' : '注 册') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import DotField from '../components/DotField.vue'

const router = useRouter()
const auth = useAuthStore()

const mode = ref('login')
const loading = ref(false)
const serverError = ref('')

const form = reactive({
  userName: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  userName: '',
  password: '',
  confirmPassword: ''
})

const switchMode = (m) => {
  mode.value = m
  clearError()
  serverError.value = ''
}

const clearError = () => {
  errors.userName = ''
  errors.password = ''
  errors.confirmPassword = ''
  serverError.value = ''
}

// 验证用户名：仅数字和字母
const validateUserName = (val) => {
  if (!val) return '请输入用户名'
  if (val.length < 2 || val.length > 50) return '用户名长度需在 2-50 位之间'
  if (!/^[a-zA-Z0-9]+$/.test(val)) return '用户名仅限数字和字母'
  return ''
}

// 验证密码：仅限字母和数字
const validatePassword = (val) => {
  if (!val) return '请输入密码'
  if (mode.value === 'register') {
    if (val.length < 6) return '密码至少 6 位'
    if (!/^[a-zA-Z0-9]+$/.test(val)) return '密码仅限字母和数字'
  }
  return ''
}

const handleSubmit = async () => {
  // 前端校验
  const uErr = validateUserName(form.userName)
  const pErr = validatePassword(form.password)
  if (uErr) { errors.userName = uErr; return }
  if (pErr) { errors.password = pErr; return }
  if (mode.value === 'register' && form.password !== form.confirmPassword) {
    errors.confirmPassword = '两次密码输入不一致'
    return
  }

  loading.value = true
  serverError.value = ''

  try {
    if (mode.value === 'login') {
      await auth.login(form.userName, form.password)
    } else {
      await auth.register(form.userName, form.password)
      // 注册成功后自动登录
      await auth.login(form.userName, form.password)
    }
    window.location.href = '/'
  } catch (err) {
    serverError.value = err.message || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; position: relative; overflow: hidden;
  background: #0a0a14;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
}

/* 删掉旧的 orb 装饰 */

.login-card {
  position: relative; z-index: 1;
  width: 400px; max-width: 90vw; padding: 36px 32px;
}
.glass-card {
  background: rgba(20, 20, 35, 0.75);
  backdrop-filter: blur(24px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.08);
}

.login-header { text-align: center; margin-bottom: 28px; }
.logo-dot {
  display: inline-block; width: 14px; height: 14px;
  background: #007AFF; border-radius: 50%; margin-bottom: 12px;
}
.logo-dot.pulse { animation: pulse 2s infinite; }
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.6; }
}
.login-header h1 { font-size: 22px; font-weight: 700; color: #e0e0f0; margin-bottom: 6px; }
.login-header p { font-size: 14px; color: #8888a0; }

.tab-row { display: flex; gap: 0; margin-bottom: 24px; background: rgba(255,255,255,0.06); border-radius: 10px; padding: 3px; }
.tab-btn {
  flex: 1; padding: 10px 0; border: none; border-radius: 8px;
  font-size: 15px; font-weight: 500; cursor: pointer;
  background: transparent; color: #7777a0; transition: all 0.2s;
}
.tab-btn.active { background: rgba(130, 100, 240, 0.3); color: #c0b0ff; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }

.login-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; font-weight: 500; color: #8888a0; }

.apple-input {
  padding: 12px 14px; border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1); font-size: 15px;
  outline: none; font-family: inherit; background: rgba(255,255,255,0.06);
  transition: border 0.2s; color: #e0e0f0;
}
.apple-input:focus { border-color: #8264e0; }
.apple-input::placeholder { color: #555570; }

.field-error { font-size: 12px; color: #FF3B30; }
.server-error {
  font-size: 13px; color: #FF3B30; text-align: center;
  padding: 10px; background: rgba(255,59,48,0.06); border-radius: 8px;
}

.btn-submit {
  width: 100%; padding: 13px 0; border: none; border-radius: 12px;
  background: linear-gradient(135deg, #7c5ce7, #5a3fd4); color: white;
  font-size: 16px; font-weight: 600;
  cursor: pointer; transition: all 0.2s; margin-top: 4px;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn-submit:hover { background: linear-gradient(135deg, #8e6ef0, #6a4fe4); }
.btn-submit:disabled { background: #44445a; cursor: not-allowed; }

.btn-spinner {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
