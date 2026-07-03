<template>
  <main class="main-wrap">
    <LightRays
      raysColor="#5227FF"
      :raysSpeed="0.8"
      :lightSpread="0.6"
      :rayLength="1.2"
      :followMouse="true"
      :mouseInfluence="0.15"
      :fadeDistance="0.8"
      :saturation="0.6"
    />
    <div class="main-content">
    <div class="page-header">
      <div class="page-title">
        <h1 class="page-heading">
          <BlurText text="项目列表" :delay="150" :stepDuration="0.3" animateBy="words" />
        </h1>
        <BlurText
          text="选择一个项目查看工作台与智能体协同详情"
          :delay="80"
          :stepDuration="0.25"
          animateBy="words"
          className="page-subtitle"
        />
      </div>
      <button class="btn btn-chroma" @click="showCreateModal = true">+ 新建项目</button>
    </div>

    <!-- ChromaGrid 项目卡片 -->
    <div class="chroma-wrapper" v-if="projects.length > 0">
      <ChromaGrid
        :items="projectItems"
        :columns="2"
        :radius="320"
        :damping="0.4"
        @card-click="enterProject"
      >
        <template #card="{ item }">
          <div class="project-card-inner">
            <div class="project-icon-area">
              <span class="project-letter">{{ item.name?.charAt(0) }}</span>
            </div>
            <div class="project-content">
              <div class="project-head">
                <h3 class="project-name">{{ item.name }}</h3>
                <span class="status-badge" :class="item.status">
                  {{ item.status === 'completed' ? '已完成' : '进行中' }}
                </span>
              </div>
              <p class="project-desc">{{ item.description }}</p>
              <div class="project-footer">
                <span class="project-meta">{{ item.metaText }}</span>
                <div class="project-stats" v-if="item.stats">
                  <span>{{ item.stats.completed }}/{{ item.stats.total }} 任务</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </ChromaGrid>
    </div>

    <!-- 空状态 -->
    <div class="glass-card empty-state" v-else>
      <div class="empty-icon">📭</div>
      <h3>暂无项目</h3>
      <p>创建你的第一个 AI 协作项目</p>
      <button class="btn btn-primary" @click="showCreateModal = true">+ 新建项目</button>
    </div>

    <!-- 新建项目弹窗 -->
    <div class="modal-overlay" v-if="showCreateModal" @click.self="showCreateModal = false">
      <div class="modal-content glass-card">
        <div class="modal-header">
          <h3>新建 AI 协作项目</h3>
          <button class="btn-close" @click="showCreateModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>项目名称</label>
            <input
              v-model="newProject.name"
              class="apple-input"
              placeholder="例如：智慧园区管理系统"
              @keyup.enter="handleCreate"
            >
          </div>
          <div class="form-group">
            <label>项目描述</label>
            <textarea
              v-model="newProject.description"
              class="apple-input textarea"
              placeholder="简要描述项目目标和范围..."
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="showCreateModal = false">取消</button>
          <button class="btn btn-primary" @click="handleCreate" :disabled="!newProject.name.trim()">
            创建项目
          </button>
        </div>
      </div>
    </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/project.js'
import { useAuthStore } from '../stores/auth.js'
import ChromaGrid from '../components/ChromaGrid.vue'
import BlurText from '../components/BlurText.vue'
import LightRays from '../components/LightRays.vue'

const router = useRouter()
const store = useProjectStore()
const auth = useAuthStore()

const projects = ref([])
const showCreateModal = ref(false)
const newProject = ref({ name: '', description: '' })

const GRADIENTS = [
  { gradient: 'linear-gradient(145deg, #3B82F6 0%, #0a0a1a 100%)', border: '#3B82F6' },
  { gradient: 'linear-gradient(145deg, #10B981 0%, #0a0a1a 100%)', border: '#10B981' },
  { gradient: 'linear-gradient(145deg, #8B5CF6 0%, #0a0a1a 100%)', border: '#8B5CF6' },
  { gradient: 'linear-gradient(145deg, #F59E0B 0%, #0a0a1a 100%)', border: '#F59E0B' },
  { gradient: 'linear-gradient(165deg, #EC4899 0%, #0a0a1a 100%)', border: '#EC4899' },
  { gradient: 'linear-gradient(145deg, #06B6D4 0%, #0a0a1a 100%)', border: '#06B6D4' },
]

onMounted(async () => {
  await store.fetchProjects(auth.user.id)
  projects.value = store.projectList
})

const projectItems = computed(() =>
  projects.value.map((p, i) => {
    const g = GRADIENTS[i % GRADIENTS.length]
    return {
      name: p.name,
      description: p.description,
      status: p.status,
      gradient: g.gradient,
      borderColor: g.border,
      metaText: p.status === 'completed'
        ? `完成于 ${p.completedAt}`
        : `创建于 ${p.createdAt}`,
      stats: p.stats,
      _id: p.id,
    }
  })
)

const enterProject = ({ item }) => {
  store.selectProject(item._id)
  router.push(`/projects/${item._id}`)
}

const handleCreate = async () => {
  if (!newProject.value.name.trim()) return
  try {
    const result = await store.createProject({
      name: newProject.value.name.trim(),
      description: newProject.value.description.trim()
    }, auth.user.id)
    store.lastCreateMsg = result.message || '项目创建成功'
  } catch (e) {
    alert(e.message)
    return
  }
  showCreateModal.value = false
  newProject.value = { name: '', description: '' }
  projects.value = store.projectList
}
</script>

<style scoped>
.main-wrap {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  position: relative;
  background: #e8e8ed;
}
.main-content {
  position: relative;
  z-index: 1;
}
.chroma-wrapper {
  min-height: 400px;
}

/* 页头 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-title .page-heading {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 6px;
  color: #1D1D1F;
}
.page-title .page-subtitle {
  color: #86868B;
  font-size: 15px;
  margin: 0;
}

/* 按钮 */
.btn {
  padding: 8px 18px; border-radius: 8px; border: none;
  font-size: 14px; font-weight: 500; cursor: pointer;
  transition: all 0.2s;
}
.btn-primary { background: #007AFF; color: white; }
.btn-primary:hover { background: #0062CC; }
.btn-primary:disabled { background: #86868B; cursor: not-allowed; }
.btn-chroma {
  background: linear-gradient(145deg, #3B82F6 0%, #0a0a1a 100%);
  color: #fff;
  border: 1px solid #3B82F6;
  transition: all 0.3s ease;
}
.btn-chroma:hover {
  background: linear-gradient(145deg, #4B92FF 0%, #1a1a3a 100%);
  border-color: #60A5FA;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.25);
}
.btn-ghost {
  background: rgba(255,255,255,0.6); backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.1);
}
.btn-ghost:hover { background: rgba(255,255,255,0.9); }

/* ========== 项目卡片内部 ========== */
.project-card-inner {
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 220px;
  color: #fff;
}

.project-icon-area {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.project-letter {
  width: 48px; height: 48px;
  border-radius: 14px;
  background: rgba(255,255,255,0.12);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.project-content { flex: 1; display: flex; flex-direction: column; }

.project-head {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 8px;
}
.project-name {
  font-size: 18px; font-weight: 600;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.status-badge {
  font-size: 11px; padding: 3px 10px; border-radius: 20px;
  font-weight: 500; white-space: nowrap; flex-shrink: 0;
}
.status-badge.active {
  background: rgba(59,130,246,0.25); color: #93C5FD;
}
.status-badge.completed {
  background: rgba(16,185,129,0.25); color: #6EE7B7;
}

.project-desc {
  font-size: 13px; color: rgba(255,255,255,0.6);
  line-height: 1.5; flex: 1;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 16px; padding-top: 14px;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.project-meta { font-size: 12px; color: rgba(255,255,255,0.4); }
.project-stats {
  font-size: 12px; color: rgba(255,255,255,0.55);
  font-weight: 500;
}

/* ========== 空状态 ========== */
.glass-card {
  background: rgba(255,255,255,0.72); backdrop-filter: blur(20px);
  border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  border: 1px solid rgba(255,255,255,0.9);
  padding: 20px;
}
.empty-state {
  text-align: center; padding: 60px 20px;
}
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.empty-state p { font-size: 14px; color: #86868B; margin-bottom: 20px; }

/* ========== 弹窗 ========== */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}
.modal-content {
  width: 90%; max-width: 480px;
  animation: slideUp 0.3s ease;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px;
}
.modal-header h3 { font-size: 18px; font-weight: 600; }
.btn-close {
  width: 32px; height: 32px; border-radius: 50%; border: none;
  background: rgba(0,0,0,0.06); cursor: pointer; font-size: 16px;
  color: #86868B; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.btn-close:hover { background: rgba(0,0,0,0.12); color: #1D1D1F; }
.modal-body { margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label {
  display: block; font-size: 13px; font-weight: 500;
  color: #86868B; margin-bottom: 6px;
}
.apple-input {
  width: 100%; padding: 10px 14px; border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.1); font-size: 14px;
  outline: none; font-family: inherit; box-sizing: border-box;
  background: rgba(255,255,255,0.8); transition: border 0.2s;
}
.apple-input:focus { border-color: #007AFF; }
.textarea { resize: vertical; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; }
</style>
