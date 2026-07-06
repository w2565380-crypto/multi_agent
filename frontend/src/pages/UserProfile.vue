<template>
  <main class="main-wrap">
    <Threads
      :color="[1, 1, 1]"
      :amplitude="1.0"
      :distance="0.2"
      :enableMouseInteraction="true"
    />
    <div class="page-header">
      <div class="page-title">
        <h1>个人中心</h1>
        <span>管理你的账户信息与安全设置</span>
      </div>
    </div>

    <div class="glass-card profile-card">
      <div class="profile-avatar" @click="triggerUpload">
        <img v-if="auth.user?.image" :src="auth.user.image + '?v=' + auth.imageVersion" class="avatar-img" alt="头像" />
        <span v-else class="avatar-text">{{ auth.user?.userName?.charAt(0) }}</span>
        <div class="avatar-overlay"><span class="camera-icon">📷</span></div>
      </div>
      <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="handleUpload" />

      <div class="username-row">
        <span class="username-text">
          {{ auth.user?.userName }}
          <router-link to="/profile/username" class="edit-icon" title="修改用户名">✎</router-link>
        </span>
      </div>
      <div class="user-id-text">ID: {{ auth.user?.id }}</div>
    </div>

    <div v-if="successMsg" class="success-toast">{{ successMsg }}</div>

    <router-link to="/profile/password" class="btn btn-primary btn-password">修改密码</router-link>

    <div class="delete-row">
      <span class="delete-hint">注销后将永久删除账号及所有项目数据</span>
      <button class="btn btn-delete" @click="showDeleteModal = true">注销账号</button>
    </div>

    <div class="modal-overlay" v-if="showDeleteModal" @click.self="showDeleteModal = false">
      <div class="modal-content glass-card">
        <div class="modal-header">
          <h3>确认注销账号</h3>
          <button class="btn-close" @click="showDeleteModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="modal-warning">此操作将永久删除账号 <strong>{{ auth.user?.userName }}</strong> 及所有关联数据，不可恢复。</p>
          <p class="modal-hint">请输入用户名确认：</p>
          <input v-model="deleteConfirm" class="apple-input" :placeholder="`输入 ${auth.user?.userName} 确认`">
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showDeleteModal = false">取消</button>
          <button class="btn btn-danger" :disabled="deleteConfirm !== auth.user?.userName || deleting" @click="handleDeleteAccount">
            <span v-if="deleting" class="btn-spinner"></span>
            {{ deleting ? '注销中...' : '确认注销' }}
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import Threads from '../components/Threads.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const successMsg = ref('')

watch(() => route.query.msg, (msg) => {
  if (msg) { successMsg.value = msg; router.replace({ query: {} }); setTimeout(() => { successMsg.value = '' }, 3000) }
}, { immediate: true })

const deleting = ref(false)
const showDeleteModal = ref(false)
const deleteConfirm = ref('')
const fileInput = ref(null)
const uploading = ref(false)

const triggerUpload = () => fileInput.value?.click()

const handleUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`/api/users/${auth.user.id}/upload-avatar`, { method: 'POST', body: formData })
    if (!res.ok) {
      const d = await res.json().catch(() => ({}))
      throw new Error(d.detail || '上传失败')
    }
    const resData = await res.json()
    const imageUrl = resData.avatar_url || resData.image_url
    if (imageUrl) {
      auth.user.image = imageUrl.replace(/^https?:\/\/[^/]+/, '')
      auth.imageVersion = Date.now()
      auth.saveUser()
    }
    successMsg.value = '头像上传成功'
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err) {
    successMsg.value = '⚠️ ' + (err.message || '上传失败')
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

const handleDeleteAccount = async () => {
  if (deleteConfirm.value !== auth.user?.userName) return
  deleting.value = true
  try {
    const res = await fetch(`/api/users/${auth.user.id}`, { method: 'DELETE' })
    if (!res.ok && res.status !== 204) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || `注销失败 (${res.status})`)
    }
    auth.logout()
    router.push('/login')
  } catch (err) {
    showDeleteModal.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.main-wrap { flex: 1; padding: 24px; overflow-y: auto; background: #1e1e24; position: relative; }
.page-header { margin-bottom: 24px; position: relative; z-index: 1; }
.page-title h1 { font-size: 26px; font-weight: 600; margin-bottom: 4px; color: #d0d0d8; }
.page-title span { color: #888899; font-size: 14px; }

.glass-card {
  background: rgba(255,255,255,0.03); backdrop-filter: blur(16px);
  border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.06); padding: 20px; margin-bottom: 20px;
  position: relative; z-index: 1;
}

.profile-card {
  display: flex; flex-direction: column; align-items: center;
  padding: 32px 20px 24px;
}

.profile-avatar {
  width: 120px; height: 120px; border-radius: 50%;
  background: linear-gradient(135deg, #5856D6 0%, #3B82F6 100%);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; position: relative; cursor: pointer; overflow: hidden;
  margin-bottom: 16px;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.avatar-text { font-size: 46px; font-weight: 700; color: white; }
.avatar-overlay {
  position: absolute; inset: 0; border-radius: 50%;
  background: rgba(0,0,0,0.35); display: flex; align-items: center;
  justify-content: center; opacity: 0; transition: opacity 0.2s;
}
.profile-avatar:hover .avatar-overlay { opacity: 1; }
.camera-icon { font-size: 24px; }

.username-row {
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 4px;
}
.username-text {
  font-size: 18px; font-weight: 600; color: #d0d0d8;
  position: relative;
}
.edit-icon {
  position: absolute; right: -22px; top: 50%; transform: translateY(-50%);
  font-size: 15px; color: #888899; text-decoration: none;
  opacity: 0; transition: opacity 0.2s;
}
.username-text:hover .edit-icon { opacity: 1; }
.edit-icon:hover { color: #7c9aff; }

.user-id-text {
  font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
  font-size: 13px; color: #7c9aff; margin-bottom: 20px;
}

.btn-password {
  max-width: 260px; margin: 0 auto; display: flex;
  position: relative; z-index: 1;
}

.delete-row {
  display: flex; align-items: center; gap: 10px;
  position: fixed; right: 24px; bottom: 24px;
  z-index: 10;
}
.delete-hint { font-size: 12px; color: #FF453A; }

.success-toast {
  padding: 12px 20px; margin-bottom: 16px;
  background: rgba(52,199,89,0.15); color: #34C759;
  border-radius: 10px; font-size: 14px; font-weight: 500;
  animation: fadeSlideIn 0.3s ease; position: relative; z-index: 1;
}
@keyframes fadeSlideIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }

.btn { padding: 10px 24px; border-radius: 8px; border: none; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; text-decoration: none; white-space: nowrap; flex-shrink: 0; }
.btn-primary { background: #5856D6; color: white; }
.btn-primary:hover { background: #6C63FF; }
.btn-primary:disabled { background: #44445a; cursor: not-allowed; }
.btn-danger { background: #FF3B30; color: white; }
.btn-danger:hover { background: #E0352B; }
.btn-danger:disabled { background: #44445a; cursor: not-allowed; }
.btn-ghost { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); color: #d0d0d8; }
.btn-ghost:hover { background: rgba(255,255,255,0.12); }
.btn-delete { background: transparent; color: #FF453A; font-size: 13px; padding: 6px 12px; border: 1px solid rgba(255,69,58,0.3); border-radius: 6px; }
.btn-delete:hover { background: rgba(255,69,58,0.12); }

.btn-spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px); display: flex; align-items: center;
  justify-content: center; z-index: 100;
}
.modal-content { width: 90%; max-width: 440px; padding: 24px; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.modal-header h3 { font-size: 18px; font-weight: 600; color: #d0d0d8; }
.btn-close { width: 32px; height: 32px; border-radius: 50%; border: none; background: rgba(255,255,255,0.06); cursor: pointer; font-size: 16px; color: #888899; display: flex; align-items: center; justify-content: center; }
.btn-close:hover { background: rgba(255,255,255,0.12); color: #d0d0d8; }
.modal-warning { font-size: 14px; color: #FF453A; line-height: 1.6; margin-bottom: 14px; }
.modal-warning strong { font-weight: 600; color: #d0d0d8; }
.modal-hint { font-size: 13px; color: #888899; margin-bottom: 8px; }

.apple-input {
  width: 100%; padding: 10px 14px; border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.1); font-size: 14px;
  outline: none; font-family: inherit; box-sizing: border-box;
  background: rgba(255,255,255,0.06); transition: border 0.2s; color: #d0d0d8;
}
.apple-input:focus { border-color: #5856D6; }
.apple-input::placeholder { color: #555570; }

.modal-footer { display: flex; justify-content: flex-end; gap: 10px; }
</style>
