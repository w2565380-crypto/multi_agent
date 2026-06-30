import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import WorkbenchPage from '../pages/WorkbenchPage.vue'
import AgentFilesPage from '../pages/AgentFilesPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/workbench',
    name: 'Workbench',
    component: WorkbenchPage
  },
  {
    path: '/agent/:type',
    name: 'AgentFiles',
    component: AgentFilesPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
