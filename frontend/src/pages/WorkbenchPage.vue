<template>
  <main class="main-wrap">
    <div class="page-header">
      <div class="page-title">
        <h1>{{ project?.name || '项目工作台' }}</h1>
        <span class="project-subtitle">{{ statusLabel }}</span>
      </div>
      <span v-if="project" class="project-status-tag" :class="statusTagClass">{{ statusLabel }}</span>
    </div>

    <div class="glass-card chat-card">
      <div class="card-head">
        <h2>多AI智能体实时协同对话</h2>
        <button class="btn-small" @click="refreshStatus">刷新</button>
      </div>

      <div class="chat-area" ref="chatArea">
        <template v-for="msg in chatMessages" :key="msg.id">
          <div class="chat-item">
            <div class="chat-avatar" :class="`avatar-${msg.agentType}`">{{ msg.avatar }}</div>
            <div class="chat-bubble">
              <div class="name">{{ msg.agentName }}</div>
              <div class="text" v-if="msg.content">{{ msg.content }}</div>
              <div v-if="msg.file" class="file-card" @click="openFileModal(msg)">
                <span class="file-icon">📄</span>
                <div class="file-info">
                  <span class="file-name">{{ msg.file }}</span>
                  <span class="file-hint">点击查看完整内容</span>
                </div>
              </div>
              <div class="message-time">{{ msg.timestamp }}</div>
            </div>
          </div>
        </template>
        <div v-if="loading" class="typing-indicator">
          <div class="typing-dots"><span></span><span></span><span></span></div>
          <span>正在拉取消息...</span>
        </div>
        <div class="chat-empty" v-if="!loading && chatMessages.length === 0">暂无协同消息</div>
      </div>

      <div class="bottom-bar">
        <input v-model="inputText" class="bottom-input" :placeholder="inputPlaceholder" @keyup.enter="handleSend" />
        <template v-if="project?.status === 'PENDING_APPROVAL'">
          <button class="btn btn-reject" @click="handleReject" :disabled="submitting">驳回修改</button>
          <button class="btn btn-approve" @click="handleApprove" :disabled="submitting">同意开发</button>
        </template>
        <template v-else-if="project?.status === 'COMPLETED'">
          <button class="btn btn-modify" @click="handleModify" :disabled="!inputText.trim() || modifying">修改项目</button>
          <button v-if="!previewUrl" class="btn btn-preview" @click="loadPreview">获取预览</button>
          <button v-else class="btn btn-preview" @click="openPreview">🔗 预览项目</button>
          <a class="btn btn-download" :href="`/api/projects/${project.id}/download`" download>📥 下载</a>
        </template>
        <button v-else class="btn btn-send" @click="handleSend" :disabled="!inputText.trim()">发送</button>
      </div>
    </div>

    <div class="modal-overlay" v-if="fileModal.open" @click.self="fileModal.open = false">
      <div class="modal-content">
        <div class="modal-header"><h3>{{ fileModal.title }}</h3><button class="btn-close" @click="fileModal.open = false">✕</button></div>
        <div class="modal-body md-full" v-html="mdToHtml(fileModal.content)"></div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../stores/project.js'

const mdToHtml = (md) => {
  if (!md) return ''
  return md.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/^### (.+)$/gm,'<h4>$1</h4>').replace(/^## (.+)$/gm,'<h3>$1</h3>').replace(/^# (.+)$/gm,'<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/^- (.+)$/gm,'<li>$1</li>').replace(/(<li>.*<\/li>\n?)+/g,'<ul>$&</ul>')
    .replace(/^(?!<[hulc/])[^\n]+$/gm,'<p>$&</p>').replace(/\n/g,'')
}

const route = useRoute()
const store = useProjectStore()
const chatArea = ref(null)
const project = ref(null)
const chatMessages = ref([])
const loading = ref(false)
const submitting = ref(false)
const modifying = ref(false)
const revising = ref(false)
const inputText = ref('')
let pollTimer = null
const prdLoaded = ref(false)
const qaLoaded = ref(false)
const fileModal = reactive({ open: false, title: '', content: '' })
const previewUrl = ref('')

const statusMap = { INITIAL:'项目初始化', PM_WORKING:'产品经理规划中', PENDING_APPROVAL:'待审批', RUNNING:'开发测试中', COMPLETED:'已完成', active:'进行中', completed:'已完成' }
const statusLabel = computed(() => statusMap[project.value?.status] || statusMap[project.value?.status?.toLowerCase()] || project.value?.status || '')
const statusTagClass = computed(() => { const s = project.value?.status; if (s==='PENDING_APPROVAL') return 'tag-approval'; if (s==='COMPLETED') return 'tag-completed'; return 'tag-active' })
const inputPlaceholder = computed(() => {
  if (project.value?.status === 'PENDING_APPROVAL') return '输入驳回修改意见...'
  if (project.value?.status === 'COMPLETED') return '输入项目需要修改的地方...'
  return '输入消息...'
})

const handleModify = async () => {
  const txt = inputText.value.trim()
  if (!txt || modifying.value) return
  modifying.value = true
  addMsg('我','我','pm',`修改需求：${txt}`)
  try {
    const res = await fetch(`/api/projects/${project.value.id}/revise?feedback=${encodeURIComponent(txt)}`, { method: 'POST' })
    const data = await res.json()
    if (res.ok && data.success) {
      project.value.status = 'RUNNING'
      revising.value = true
      qaLoaded.value = false
      addMsg('系统','系','pm', data.message || '代码重构指令已下达，程序员正在修改代码...')
    }
  } catch { /* ignore */ }
  inputText.value = ''
  modifying.value = false
}

const scrollBottom = () => nextTick(() => { if (chatArea.value) chatArea.value.scrollTop = chatArea.value.scrollHeight })
const getTime = () => new Date().toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit'})
const addMsg = (name, avatar, type, content, opts = {}) => {
  chatMessages.value.push({ id: Date.now()+Math.random(), agentName:name, avatar, agentType:type, content:content||'', ...opts, timestamp:getTime() })
  scrollBottom()
  saveMessages()
}

// 持久化聊天记录到 localStorage
const msgKey = () => `project_msgs_${project.value?.id}`
const saveMessages = () => {
  if (project.value) localStorage.setItem(msgKey(), JSON.stringify(chatMessages.value))
}
const loadMessages = () => {
  if (!project.value) return
  const saved = localStorage.getItem(msgKey())
  if (saved) {
    try { chatMessages.value = JSON.parse(saved) } catch { /* ignore */ }
  }
}

const fetchStatus = async () => {
  if (!project.value) return
  const data = await store.fetchProjectStatus(project.value.id)
  if (!data) return
  project.value.status = data.status || project.value.status
  if (data.messages?.length) {
    [...data.messages].sort((a,b) => (a.time||'').localeCompare(b.time||'')).forEach(m => {
      if (!chatMessages.value.find(c => c.id===m.id)) addMsg(m.agent_name||'AI产品经理', m.agent_name==='AI产品经理'?'产':m.agent_name?.charAt(0)||'系', m.agent_type||'pm', m.message||m.content||'', { id:m.id })
    })
    chatMessages.value.sort((a,b) => a.id-b.id)
  }
  if (data.status==='PENDING_APPROVAL' && !prdLoaded.value) await loadPrd()
  if (data.status==='COMPLETED' && !qaLoaded.value) await loadQa()
  if (data.status==='COMPLETED' && revising.value) {
    revising.value = false
    addMsg('系统','系','pm','项目已完成修改，请查看最新成果。')
    await loadQa()
  }
}

const loadPrd = async () => {
  if (prdLoaded.value) return
  try {
    const res = await fetch(`/api/projects/${project.value.id}/prd`)
    if (!res.ok) return
    const data = await res.json()
    if (data.prd_content) { prdLoaded.value = true; addMsg('AI产品经理','产','pm','需求规划完成，请审批 PRD 文档。', { file:'PRD.md', fileContent:data.prd_content }) }
  } catch { /* ignore */ }
}

const loadQa = async () => {
  if (qaLoaded.value) return
  try {
    const res = await fetch(`/api/projects/${project.value.id}/qa-report`)
    if (!res.ok) return
    const data = await res.json()
    if (data.qa_report) { qaLoaded.value = true; addMsg('AI测试工程师','测','test','测试完成，请查看测试报告。', { file:'QA测试报告.md', fileContent:data.qa_report }) }
  } catch { /* ignore */ }
}

const refreshStatus = () => { loading.value = true; fetchStatus().finally(() => loading.value = false) }

const openFileModal = (msg) => { if (msg.fileContent) { fileModal.title = `📄 ${msg.file}`; fileModal.content = msg.fileContent; fileModal.open = true } }

const loadPreview = async () => {
  if (previewUrl.value || project.value?.status !== 'COMPLETED') return
  const url = await store.fetchPreviewUrl(project.value.id)
  if (url) previewUrl.value = url
}

const handleSend = () => {
  const txt = inputText.value.trim(); if (!txt) return
  if (project.value?.status === 'PENDING_APPROVAL') return handleReject()
  if (project.value?.status === 'COMPLETED') return handleModify()
  addMsg('我','我','pm',txt); inputText.value = ''
}

const handleApprove = async () => {
  submitting.value = true
  try { await store.approveProject(project.value.id, true); project.value.status = 'RUNNING'; addMsg('系统','系','pm','审批通过，项目进入开发测试阶段。') } catch(e) { alert(e.message) }
  submitting.value = false
}

const handleReject = async () => {
  const fb = inputText.value.trim(); inputText.value = ''; submitting.value = true
  try {
    await store.approveProject(project.value.id, false, fb)
    project.value.status = 'RUNNING'
    prdLoaded.value = false                     // 重置，等待新 PRD
    addMsg('系统','系','pm',`已驳回${fb?'：'+fb:''}，产品经理将重新规划。`)
  } catch(e) { alert(e.message) }
  submitting.value = false
}

const openPreview = () => { if (previewUrl.value) window.open(previewUrl.value, '_blank') }

watch(() => route.params.projectId, async (id) => {
  if (!id) return
  store.selectProject(Number(id)); project.value = store.getProjectById(Number(id))
  loading.value = true; chatMessages.value = []
  // 恢复持久化的聊天记录，并检查是否已有 PRD/QA
  loadMessages()
  prdLoaded.value = chatMessages.value.some(m => m.file === 'PRD.md')
  qaLoaded.value = chatMessages.value.some(m => m.file === 'QA测试报告.md')
  if (store.lastCreateMsg) { addMsg('系统','系','pm',store.lastCreateMsg); store.lastCreateMsg = '' }
  await fetchStatus()
  if (project.value?.status === 'COMPLETED') loadPreview()
  loading.value = false; scrollBottom()
}, { immediate: true })

onMounted(() => { pollTimer = setInterval(() => { if (project.value) fetchStatus() }, 5000) })
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.main-wrap { flex: 1; padding: 24px; overflow-y: auto; background: #1e1e24; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title h1 { font-size: 26px; font-weight: 600; color: #d0d0d8; margin-bottom: 4px; }
.project-subtitle { color: #888899; font-size: 14px; }
.project-status-tag { font-size: 13px; padding: 6px 14px; border-radius: 20px; font-weight: 500; white-space: nowrap; }
.tag-active { background: rgba(88,86,214,0.15); color: #5856D6; }
.tag-completed { background: rgba(52,199,89,0.15); color: #34C759; }
.tag-approval { background: rgba(245,158,11,0.15); color: #F59E0B; }
.glass-card { background: rgba(255,255,255,0.03); backdrop-filter: blur(16px); border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.06); padding: 20px; margin-bottom: 20px; }
.chat-card { display: flex; flex-direction: column; min-height: calc(100vh - 130px); }
.card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-shrink: 0; }
.card-head h2 { font-size: 17px; font-weight: 600; color: #d0d0d8; }
.btn-small { padding: 6px 12px; font-size: 13px; background: rgba(88,86,214,0.1); color: #5856D6; border: 1px solid rgba(88,86,214,0.3); border-radius: 6px; cursor: pointer; }

.chat-area { flex: 1; overflow-y: auto; padding-right: 8px; margin-bottom: 12px; min-height: 200px; }
.chat-item { margin-bottom: 14px; display: flex; gap: 10px; }
.chat-avatar { width: 28px; height: 28px; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.avatar-pm { background: #007AFF; } .avatar-dev { background: #34C759; } .avatar-test { background: #FF9500; } .avatar-op { background: #AF52DE; }
.chat-bubble { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 10px 14px; max-width: 75%; border: 1px solid rgba(255,255,255,0.06); }
.chat-bubble .name { font-size: 12px; font-weight: 500; margin-bottom: 4px; color: #5856D6; }
.chat-bubble .text { font-size: 13px; line-height: 1.5; color: #d0d0d8; margin-bottom: 4px; }
.chat-bubble .message-time { font-size: 10px; color: #555570; margin-top: 6px; }

.file-card { display: flex; align-items: center; gap: 10px; background: rgba(124,154,255,0.08); border: 1px solid rgba(124,154,255,0.15); border-radius: 8px; padding: 10px 12px; cursor: pointer; transition: all 0.2s; margin: 6px 0; }
.file-card:hover { background: rgba(124,154,255,0.15); }
.file-icon { font-size: 22px; }
.file-info { display: flex; flex-direction: column; gap: 2px; }
.file-name { font-size: 13px; color: #7c9aff; font-weight: 500; }
.file-hint { font-size: 11px; color: #8888a0; }
.chat-empty { text-align: center; padding: 40px; color: #555570; font-size: 14px; }

.typing-indicator { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: rgba(255,255,255,0.03); border-radius: 12px; margin-bottom: 14px; font-size: 12px; color: #888899; }
.typing-dots { display: flex; gap: 3px; } .typing-dots span { width: 6px; height: 6px; background: #5856D6; border-radius: 50%; animation: typing 1.4s infinite ease-in-out; }
.typing-dots span:nth-child(1){animation-delay:0s} .typing-dots span:nth-child(2){animation-delay:.2s} .typing-dots span:nth-child(3){animation-delay:.4s}
@keyframes typing { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-4px)} }

.bottom-bar { display: flex; align-items: center; gap: 8px; flex-shrink: 0; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.05); }
.bottom-input { flex: 1; padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); font-size: 14px; outline: none; font-family: inherit; background: rgba(255,255,255,0.06); color: #d0d0d8; transition: border 0.2s; }
.bottom-input:focus { border-color: #5856D6; } .bottom-input::placeholder { color: #555570; }

.btn { padding: 10px 20px; border-radius: 10px; border: none; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; white-space: nowrap; flex-shrink: 0; }
.btn-send { background: #5856D6; color: white; } .btn-send:hover { background: #6C63FF; } .btn-send:disabled { background: #44445a; cursor: not-allowed; }
.btn-approve { background: #34C759; color: white; } .btn-approve:hover { background: #30B350; } .btn-approve:disabled { background: #44445a; cursor: not-allowed; }
.btn-reject { background: rgba(255,69,58,0.15); color: #FF453A; border: 1px solid rgba(255,69,58,0.25); } .btn-reject:hover { background: rgba(255,69,58,0.25); }
.btn-preview { background: #007AFF; color: white; } .btn-preview:hover { background: #0062CC; }
.btn-modify { background: #FF9500; color: white; } .btn-modify:hover { background: #E68600; }
.btn-download { background: #34C759; color: white; text-decoration: none; } .btn-download:hover { background: #30B350; }
.btn-send { background: #5856D6; color: white; } .btn-send:hover { background: #6C63FF; } .btn-send:disabled { background: #44445a; cursor: not-allowed; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-content { width: 90%; max-width: 720px; max-height: 80vh; background: #1e1e28; border-radius: 16px; padding: 24px; border: 1px solid rgba(255,255,255,0.08); animation: slideUp 0.3s ease; display: flex; flex-direction: column; }
@keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-shrink: 0; }
.modal-header h3 { font-size: 18px; font-weight: 600; color: #d0d0d8; }
.btn-close { width: 32px; height: 32px; border-radius: 50%; border: none; background: rgba(255,255,255,0.06); cursor: pointer; font-size: 16px; color: #888899; display: flex; align-items: center; justify-content: center; }
.btn-close:hover { background: rgba(255,255,255,0.12); color: #d0d0d8; }

.md-full { flex: 1; overflow-y: auto; font-size: 13px; line-height: 1.8; color: #d0d0d8; background: rgba(255,255,255,0.03); border-radius: 8px; padding: 16px; border: 1px solid rgba(255,255,255,0.06); }
.md-full :deep(h2) { font-size: 20px; font-weight: 700; margin: 20px 0 12px; color: #e8e8f8; }
.md-full :deep(h3) { font-size: 16px; font-weight: 600; margin: 16px 0 8px; color: #d8d8f0; }
.md-full :deep(h4) { font-size: 14px; font-weight: 600; margin: 12px 0 6px; color: #c8c8e8; }
.md-full :deep(p) { margin-bottom: 8px; } .md-full :deep(ul) { padding-left: 20px; margin-bottom: 10px; }
.md-full :deep(li) { margin-bottom: 4px; } .md-full :deep(strong) { color: #e8e8f8; }
.md-full :deep(code) { background: rgba(124,154,255,0.15); color: #7c9aff; padding: 1px 5px; border-radius: 4px; font-size: 12px; }
</style>
