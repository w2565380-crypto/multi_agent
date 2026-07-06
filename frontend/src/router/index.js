import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import ProjectList from '../pages/ProjectList.vue'
import WorkbenchPage from '../pages/WorkbenchPage.vue'
import AgentFilesPage from '../pages/AgentFilesPage.vue'
import LoginPage from '../pages/LoginPage.vue'
import UserProfile from '../pages/UserProfile.vue'
import ChangePassword from '../pages/ChangePassword.vue'
import ChangeUsername from '../pages/ChangeUsername.vue'
import { useAuthStore } from '../stores/auth.js'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { guest: true }
  },
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'ProjectList',
    component: ProjectList,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:projectId',
    name: 'Workbench',
    component: WorkbenchPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/agent/:type',
    name: 'AgentFiles',
    component: AgentFilesPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile/password',
    name: 'ChangePassword',
    component: ChangePassword,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile/username',
    name: 'ChangeUsername',
    component: ChangeUsername,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局导航守卫
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  // 需要登录的页面
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next('/login')
  }
  // 已登录用户访问登录页 → 跳转首页
  else if (to.meta.guest && auth.isLoggedIn) {
    next('/')
  }
  else {
    next()
  }
})

export default router
