<template>
  <main class="main-wrap">
    <div class="page-header">
      <div class="page-title">
        <router-link to="/profile" class="back-link">← 返回个人中心</router-link>
        <h1>✏️ 修改用户名</h1>
        <span>设置新的用户名</span>
      </div>
    </div>

    <div class="glass-card">
      <form @submit.prevent="handleSubmit" class="edit-form">
        <div class="form-group">
          <label>当前用户名</label>
          <input class="apple-input" :value="auth.user?.userName" disabled>
        </div>
        <div class="form-group">
          <label>新用户名</label>
          <input v-model="form.newUserName" class="apple-input" placeholder="2-50位，仅限数字和字母">
          <span v-if="errors.newUserName" class="field-error">{{ errors.newUserName }}</span>
        </div>
        <div v-if="message" class="msg" :class="msgType">{{ message }}</div>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          <span v-if="loading" class="btn-spinner"></span>
          {{ loading ? '修改中...' : '确认修改' }}
        </button>
      </form>
    </div>
  </main>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const message = ref('')
const msgType = ref('success')

const form = reactive({ newUserName: '' })
const errors = reactive({ newUserName: '' })

const handleSubmit = async () => {
  errors.newUserName = ''
  message.value = ''

  if (!form.newUserName) { errors.newUserName = '请输入新用户名'; return }
  if (form.newUserName.length < 2 || form.newUserName.length > 50) { errors.newUserName = '用户名需 2-50 位'; return }
  if (!/^[a-zA-Z0-9]+$/.test(form.newUserName)) { errors.newUserName = '用户名仅限数字和字母'; return }

  loading.value = true
  try {
    const res = await fetch(`/api/users/${auth.user.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_name: form.newUserName })
    })
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data.detail || `修改失败 (${res.status})`)
    }
    auth.user.userName = form.newUserName
    auth.saveUser()
    router.replace('/profile?msg=用户名修改成功')
    return
  } catch (err) {
    message.value = err.message
    msgType.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.main-wrap { flex: 1; padding: 24px; overflow-y: auto; background: linear-gradient(135deg, #F5F5F7 0%, #E8E8ED 100%); }
.page-header { margin-bottom: 24px; }
.back-link { font-size: 13px; color: #007AFF; text-decoration: none; display: inline-block; margin-bottom: 12px; }
.back-link:hover { opacity: 0.8; }
.page-title h1 { font-size: 26px; font-weight: 600; margin-bottom: 4px; }
.page-title span { color: #86868B; font-size: 14px; }

.glass-card {
  background: rgba(255,255,255,0.72); backdrop-filter: blur(20px);
  border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  border: 1px solid rgba(255,255,255,0.9); padding: 24px;
}
.edit-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; font-weight: 500; color: #86868B; }

.apple-input {
  padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(0,0,0,0.1);
  font-size: 14px; outline: none; font-family: inherit;
  background: rgba(255,255,255,0.8); transition: border 0.2s;
}
.apple-input:focus { border-color: #007AFF; }
.apple-input:disabled { background: rgba(0,0,0,0.04); color: #86868B; cursor: not-allowed; }

.field-error { font-size: 12px; color: #FF3B30; }

.msg { font-size: 13px; padding: 10px 14px; border-radius: 8px; text-align: center; }
.msg.success { background: rgba(52,199,89,0.1); color: #34C759; }
.msg.error { background: rgba(255,59,48,0.06); color: #FF3B30; }

.btn { padding: 10px 24px; border-radius: 8px; border: none; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; }
.btn-primary { background: #007AFF; color: white; }
.btn-primary:hover { background: #0062CC; }
.btn-primary:disabled { background: #86868B; cursor: not-allowed; }

.btn-spinner {
  display: inline-block; width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
