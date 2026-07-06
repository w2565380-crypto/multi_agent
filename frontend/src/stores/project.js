import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProjectStore = defineStore('project', () => {
  const projectList = ref([])
  const currentProjectId = ref(null)
  const lastCreateMsg = ref('')

  const currentProject = computed(() =>
    projectList.value.find(p => p.id === currentProjectId.value) || null
  )

  // 【接口 6】获取用户项目列表 — 返回数组
  const fetchProjects = async (userId) => {
    try {
      const res = await fetch(`/api/projects/?user_id=${userId}`)
      if (res.ok) {
        const data = await res.json()
        projectList.value = Array.isArray(data) ? data.map(p => ({
          id: p.id, name: p.title, description: p.description || '',
          status: p.status, createdAt: p.created_at,
        })) : []
      }
    } catch { /* ignore */ }
    return projectList.value
  }

  const selectProject = (id) => { currentProjectId.value = id }

  const getProjectById = (id) => {
    return projectList.value.find(p => p.id === Number(id)) || null
  }

  // 【接口 1】创建项目
  const createProject = async (projectData, userId) => {
    const res = await fetch(`/api/projects/create?user_id=${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: projectData.name, description: projectData.description })
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '创建失败')

    const p = { id: data.project_id, name: projectData.name,
      description: projectData.description, status: data.status }
    projectList.value.unshift(p)
    return data // 返回完整响应（含 message）
  }

  // 【接口 4】获取项目详情 — 轮询用
  const fetchProjectStatus = async (id) => {
    try {
      const res = await fetch(`/api/projects/${id}`)
      if (!res.ok) return null
      const data = await res.json()
      const p = projectList.value.find(proj => proj.id === id)
      if (p) {
        p.status = data.status
        p.description = data.description || p.description
      }
      return data
    } catch { return null }
  }

  // 【接口 2】审批项目
  const approveProject = async (id, approved, feedback = '') => {
    const params = new URLSearchParams({ approved })
    if (!approved && feedback) params.append('feedback', feedback)
    const res = await fetch(`/api/projects/${id}/approve?${params}`, { method: 'POST' })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '审批失败')
    const p = projectList.value.find(proj => proj.id === id)
    if (p) p.status = 'RUNNING'
    return data
  }

  // 【接口 3】获取预览 URL
  const fetchPreviewUrl = async (projectId) => {
    const project = projectList.value.find(p => p.id === Number(projectId))
    if (!project) return null
    project.previewLoading = true
    try {
      const res = await fetch(`/api/projects/${projectId}/preview-url`)
      if (!res.ok) return null
      const data = await res.json()
      if (data.success && data.preview_url) {
        project.previewUrl = data.preview_url
        return data.preview_url
      }
    } catch { /* ignore */ }
    finally { project.previewLoading = false }
    return null
  }

  // 【接口 7】获取 QA 测试报告
  const fetchQaReport = async (projectId) => {
    try {
      const res = await fetch(`/api/projects/${projectId}/qa-report`)
      if (!res.ok) return null
      const data = await res.json()
      return data.qa_report || null
    } catch { return null }
  }

  return {
    projectList, currentProjectId, currentProject, lastCreateMsg,
    fetchProjects, selectProject, getProjectById,
    createProject, fetchProjectStatus, approveProject, fetchPreviewUrl, fetchQaReport
  }
})
