import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './src/router/index.js'
import { useAuthStore } from './src/stores/auth.js'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 从 localStorage 恢复登录态
useAuthStore().init()

app.mount('#app')
