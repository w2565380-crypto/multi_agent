import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const imageVersion = ref(0)
  const SESSION_HOURS = 24

  // 同步用户信息到 localStorage（含登录时间戳 + 头像版本号）
  const saveUser = () => {
    const payload = { ...user.value, loginAt: Date.now(), imageVer: imageVersion.value }
    localStorage.setItem('auth_user', JSON.stringify(payload))
  }

  // 是否已登录
  const isLoggedIn = computed(() => user.value !== null && user.value.id)

  // 初始化：从 localStorage 恢复登录态，过期则清除。再从接口刷新最新头像
  const init = async () => {
    try {
      const saved = localStorage.getItem('auth_user')
      if (saved) {
        const parsed = JSON.parse(saved)
        const age = Date.now() - (parsed.loginAt || 0)
        if (age > SESSION_HOURS * 3600 * 1000) {
          localStorage.removeItem('auth_user')
          return
        }
        imageVersion.value = parsed.imageVer || 0
        delete parsed.imageVer
        delete parsed.loginAt
        user.value = parsed
        // 每次页面加载从后端拉最新头像 URL
        try {
          const res = await fetch(`/api/users/${parsed.id}`)
          const data = await res.json()
          const img = data.image || data.avatar || data.avatar_url || ''
          if (img) {
            user.value.image = img  // 直接用完整 URL，不依赖 proxy
            imageVersion.value = Date.now()
            saveUser()
          }
        } catch { /* ignore */ }
      }
    } catch { /* ignore */ }
  }

  // 安全解析 JSON
  const parseBody = async (res) => {
    try {
      const text = await res.text()
      return text ? JSON.parse(text) : {}
    } catch {
      return {}
    }
  }

  // 注册
  const register = async (userName, password) => {
    const res = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_name: userName, password })
    })
    const data = await parseBody(res)
    if (!res.ok) {
      throw new Error(data.detail || `注册失败 (${res.status})`)
    }
    return data
  }

  // 登录
  const login = async (userName, password) => {
    const res = await fetch('/api/users/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_name: userName, password })
    })
    const data = await parseBody(res)
    if (!res.ok) {
      throw new Error(data.detail || `登录失败 (${res.status})`)
    }
    const imageUrl = data.image || data.avatar_url || data.avatar || data.image_url || ''
    let image = ''
    if (imageUrl) {
      image = imageUrl.replace(/^https?:\/\/[^/]+/, '')
    } else {
      try {
        const userRes = await fetch(`/api/users/${data.user_id}`)
        const userData = await userRes.json()
        const detailImage = userData.image || userData.avatar_url || userData.avatar || ''
        if (detailImage) {
          image = detailImage.replace(/^https?:\/\/[^/]+/, '')
        }
      } catch { /* ignore */ }
    }
    user.value = {
      id: data.user_id,
      userName: data.user_name,
      image
    }
    imageVersion.value = 0
    saveUser()
    return data
  }

  // 退出登录
  const logout = () => {
    user.value = null
    localStorage.removeItem('auth_user')
  }

  return { user, imageVersion, isLoggedIn, init, register, login, logout, saveUser }
})
