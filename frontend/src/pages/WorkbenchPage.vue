<template>
  <main class="main-wrap">
    <div class="page-header">
      <div class="page-title">
        <h1>企业项目模拟工作台</h1>
        <span>多AI智能体实时协同 · 敏捷项目全流程模拟</span>
      </div>
      <div class="header-actions">
        <button class="btn btn-ghost">导出项目报告</button>
        <button class="btn btn-primary">新建模拟项目</button>
      </div>
    </div>

    <!-- 数据统计卡片 -->
    <div class="glass-card">
      <div class="card-head">
        <h2>📊 项目统计概览</h2>
        <span class="live-indicator">● 实时更新</span>
      </div>
      <div class="stat-row">
        <div class="stat-item">
          <div class="stat-num">{{ stats.totalTasks }}</div>
          <div class="stat-label">当前任务总数</div>
        </div>
        <div class="stat-item">
          <div class="stat-num" :style="{ color: '#34C759' }">{{ stats.completed }}</div>
          <div class="stat-label">已开发完成</div>
        </div>
        <div class="stat-item">
          <div class="stat-num" :style="{ color: '#FF9500' }">{{ stats.testing }}</div>
          <div class="stat-label">待测试任务</div>
        </div>
        <div class="stat-item">
          <div class="stat-num" :style="{ color: '#AF52DE' }">{{ stats.planning }}</div>
          <div class="stat-label">需求规划中</div>
        </div>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: projectProgress + '%' }"></div>
      </div>
      <div class="progress-text">项目整体进度: {{ projectProgress }}%</div>
    </div>

    <!-- 任务看板 -->
    <div class="glass-card">
      <div class="card-head">
        <h2>项目任务看板（AI智能体自动流转）</h2>
        <button class="btn btn-ghost" @click="addNewTask">+ 新建任务</button>
      </div>
      <div class="task-board">
        <!-- 需求规划列 -->
        <div class="task-column">
          <h3>🟣 需求规划（AI产品经理）</h3>
          <div
            v-for="(task, index) in planningTasks"
            :key="task.id"
            class="task-card"
            :class="{ 'fade-in': task.isNew }"
            @click="showTaskDetail(task)"
          >
            <div class="task-header">
              <span class="task-tag tag-pm">{{ task.tag }}</span>
              <span class="task-priority" :class="`priority-${task.priority}`">{{ task.priority }}</span>
            </div>
            <h4>{{ task.title }}</h4>
            <p>{{ task.description }}</p>
            <div class="task-footer">
              <span class="task-time">{{ task.createdAt }}</span>
              <span class="task-assignee">{{ task.assignee }}</span>
            </div>
          </div>
        </div>
        <!-- 开发中列 -->
        <div class="task-column">
          <h3>🟢 开发实现（AI程序员）</h3>
          <div
            v-for="(task, index) in developmentTasks"
            :key="task.id"
            class="task-card"
            :class="{ 'fade-in': task.isNew }"
            @click="showTaskDetail(task)"
          >
            <div class="task-header">
              <span class="task-tag tag-dev">{{ task.tag }}</span>
              <span class="task-priority" :class="`priority-${task.priority}`">{{ task.priority }}</span>
            </div>
            <h4>{{ task.title }}</h4>
            <p>{{ task.description }}</p>
            <div class="task-progress">
              <div class="progress-mini">
                <div class="progress-mini-fill" :style="{ width: task.progress + '%' }"></div>
              </div>
              <span class="progress-text-mini">{{ task.progress }}%</span>
            </div>
            <div class="task-footer">
              <span class="task-time">{{ task.createdAt }}</span>
              <span class="task-assignee">{{ task.assignee }}</span>
            </div>
          </div>
        </div>
        <!-- 测试验收列 -->
        <div class="task-column">
          <h3>🟠 测试验收（AI测试工程师）</h3>
          <div
            v-for="(task, index) in testingTasks"
            :key="task.id"
            class="task-card"
            :class="{ 'fade-in': task.isNew }"
            @click="showTaskDetail(task)"
          >
            <div class="task-header">
              <span class="task-tag tag-test">{{ task.tag }}</span>
              <span class="task-priority" :class="`priority-${task.priority}`">{{ task.priority }}</span>
            </div>
            <h4>{{ task.title }}</h4>
            <p>{{ task.description }}</p>
            <div class="task-footer">
              <span class="task-time">{{ task.createdAt }}</span>
              <span class="task-assignee">{{ task.assignee }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI多智能体实时协作对话面板 -->
    <div class="glass-card">
      <div class="card-head">
        <h2>多AI智能体实时协同对话</h2>
        <div class="chat-controls">
          <button class="btn-small" @click="toggleSimulation" :class="{ active: isSystemActive }">
            {{ isSystemActive ? '⏸ 暂停模拟' : '▶ 开始模拟' }}
          </button>
        </div>
      </div>
      <div class="chat-area" ref="chatArea">
        <div
          v-for="(message, index) in chatMessages"
          :key="message.id"
          class="chat-item"
          :class="{ 'fade-in': message.isNew }"
        >
          <div class="chat-avatar" :class="`avatar-${message.agentType}`">
            {{ message.avatar }}
          </div>
          <div class="chat-bubble">
            <div class="name">{{ message.agentName }}</div>
            <div class="text">{{ message.content }}</div>
            <div class="message-time">{{ message.timestamp }}</div>
          </div>
        </div>
        <div v-if="isTyping" class="typing-indicator">
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
          <span>AI智能体正在输入...</span>
        </div>
      </div>
      <div class="input-row">
        <input
          class="apple-input"
          placeholder="发送指令给全部AI智能体..."
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          :disabled="!isSystemActive"
        >
        <button class="btn btn-primary" @click="sendMessage" :disabled="!isSystemActive || !inputMessage.trim()">
          发送协同指令
        </button>
      </div>
      <div class="quick-actions">
        <button
          v-for="action in quickActions"
          :key="action.text"
          class="quick-action-btn"
          @click="sendQuickAction(action.text)"
          :disabled="!isSystemActive"
        >
          {{ action.text }}
        </button>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, inject } from 'vue'

// 从 App.vue 注入共享状态
const isSystemActive = inject('isSystemActive')
const sharedAgents = inject('agents')

const isTyping = ref(false)
let simulationInterval = null
let messageIdCounter = 0
let taskIdCounter = 0

// 统计数据
const stats = reactive({
  totalTasks: 12,
  completed: 5,
  testing: 4,
  planning: 3
})

// 计算项目整体进度
const projectProgress = computed(() => {
  const total = stats.totalTasks
  const completed = stats.completed
  return total > 0 ? Math.round((completed / total) * 100) : 0
})

// 生成时间戳
const getTimeString = () => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 任务数据
const planningTasks = ref([
  {
    id: taskIdCounter++,
    tag: 'PRD撰写',
    title: '用户登录模块需求文档',
    description: '梳理登录、验证码、找回密码业务逻辑',
    priority: '高',
    assignee: 'AI产品经理',
    createdAt: getTimeString(),
    progress: 0,
    isNew: false
  },
  {
    id: taskIdCounter++,
    tag: '原型设计',
    title: '智能体对话界面原型',
    description: '多角色聊天窗口、消息撤回、@提醒功能',
    priority: '中',
    assignee: 'AI产品经理',
    createdAt: getTimeString(),
    progress: 0,
    isNew: false
  }
])

const developmentTasks = ref([
  {
    id: taskIdCounter++,
    tag: '后端接口',
    title: '多智能体通信API',
    description: '实现角色消息分发、任务状态同步接口',
    priority: '高',
    assignee: 'AI程序员',
    createdAt: getTimeString(),
    progress: 75,
    isNew: false
  },
  {
    id: taskIdCounter++,
    tag: '前端页面',
    title: '苹果风UI页面渲染',
    description: '磨砂玻璃、拖拽看板、实时聊天组件开发',
    priority: '中',
    assignee: 'AI程序员',
    createdAt: getTimeString(),
    progress: 45,
    isNew: false
  }
])

const testingTasks = ref([
  {
    id: taskIdCounter++,
    tag: '功能测试',
    title: '任务拖拽流转测试用例',
    description: '跨列拖拽、状态自动更新边界场景验证',
    priority: '高',
    assignee: 'AI测试工程师',
    createdAt: getTimeString(),
    progress: 100,
    isNew: false
  },
  {
    id: taskIdCounter++,
    tag: '兼容性测试',
    title: '多分辨率界面适配',
    description: '大屏/小窗口下苹果磨砂UI显示校验',
    priority: '中',
    assignee: 'AI测试工程师',
    createdAt: getTimeString(),
    progress: 100,
    isNew: false
  }
])

// 聊天数据
const chatMessages = ref([
  {
    id: messageIdCounter++,
    agentName: 'AI产品经理',
    avatar: '产',
    agentType: 'pm',
    content: '本次模拟项目需要实现多角色AI自动分配任务，程序员完成接口后自动流转到测试，测试完成自动归档。',
    timestamp: getTimeString(),
    isNew: false
  },
  {
    id: messageIdCounter++,
    agentName: 'AI程序员',
    avatar: '开',
    agentType: 'dev',
    content: '已完成任务状态流转接口，支持自动更新看板，需要测试同学验证拖拽交互逻辑。',
    timestamp: getTimeString(),
    isNew: false
  },
  {
    id: messageIdCounter++,
    agentName: 'AI测试工程师',
    avatar: '测',
    agentType: 'test',
    content: '收到，正在编写全量功能测试用例，预计10模拟周期内完成第一轮回归测试。',
    timestamp: getTimeString(),
    isNew: false
  }
])

const inputMessage = ref('')
const chatArea = ref(null)

// 快捷操作
const quickActions = ref([
  { text: '分配新任务' },
  { text: '检查进度' },
  { text: '召开会议' },
  { text: '生成报告' }
])

// AI智能体对话库
const aiResponses = {
  pm: [
    '需求已更新，请各位查看最新PRD文档。',
    '新增功能需求已确认，优先级为高，请开发团队评估工时。',
    '产品原型已完成评审，可以进入开发阶段。',
    '用户反馈的问题已记录，将在下个版本中优化。',
    '市场需求发生变化，需要调整部分功能优先级。'
  ],
  dev: [
    '接口开发完成，已部署到测试环境，请测试同学验证。',
    '前端页面渲染性能已优化，FPS提升40%。',
    '遇到技术难点，需要产品经理确认需求细节。',
    '代码重构完成，减少了30%的重复代码。',
    '新功能已上线，监控数据表现正常。'
  ],
  test: [
    '功能测试完成，发现2个bug，已提交到缺陷跟踪系统。',
    '回归测试通过，所有核心功能正常。',
    '兼容性测试完成，支持主流浏览器和移动设备。',
    '性能测试结果：响应时间<200ms，并发支持1000用户。',
    '自动化测试覆盖率达到85%，建议继续提升。'
  ],
  op: [
    '服务器扩容完成，性能提升50%。',
    '监控系统告警已解除，系统运行正常。',
    '数据库备份完成，数据安全得到保障。',
    'CDN配置优化，页面加载速度提升30%。',
    '安全漏洞已修复，系统安全性提升。'
  ]
}

// 添加聊天消息
const addChatMessage = (agentName, avatar, agentType, content) => {
  const message = {
    id: messageIdCounter++,
    agentName,
    avatar,
    agentType,
    content,
    timestamp: getTimeString(),
    isNew: true
  }
  chatMessages.value.push(message)

  setTimeout(() => {
    message.isNew = false
  }, 1000)

  nextTick(() => {
    if (chatArea.value) {
      chatArea.value.scrollTop = chatArea.value.scrollHeight
    }
  })
}

// 发送消息
const sendMessage = () => {
  if (inputMessage.value.trim()) {
    addChatMessage('系统', '系', 'pm', inputMessage.value)

    setTimeout(() => {
      simulateAIResponse()
    }, 1000)

    inputMessage.value = ''
  }
}

// 发送快捷操作
const sendQuickAction = (actionText) => {
  addChatMessage('系统', '系', 'pm', `执行操作：${actionText}`)

  setTimeout(() => {
    simulateAIResponse()
  }, 800)
}

// 模拟AI响应
const simulateAIResponse = () => {
  if (!isSystemActive.value) return

  const agentTypes = ['pm', 'dev', 'test', 'op']
  const randomType = agentTypes[Math.floor(Math.random() * agentTypes.length)]
  const agent = sharedAgents.value.find(a => a.type === randomType)

  agent.isWorking = true
  agent.status = '正在处理...'

  isTyping.value = true

  setTimeout(() => {
    const responses = aiResponses[randomType]
    const randomResponse = responses[Math.floor(Math.random() * responses.length)]

    addChatMessage(agent.name, agent.avatar, randomType, randomResponse)

    agent.isWorking = false
    agent.status = ''
    isTyping.value = false
  }, 1500)
}

// 切换模拟状态
const toggleSimulation = () => {
  isSystemActive.value = !isSystemActive.value

  if (isSystemActive.value) {
    startSimulation()
  } else {
    stopSimulation()
  }
}

// 开始模拟
const startSimulation = () => {
  if (simulationInterval) return

  simulationInterval = setInterval(() => {
    if (isSystemActive.value && Math.random() > 0.3) {
      simulateAIResponse()
    }
  }, 8000)

  setInterval(() => {
    if (isSystemActive.value) {
      updateTaskProgress()
    }
  }, 15000)
}

// 停止模拟
const stopSimulation = () => {
  if (simulationInterval) {
    clearInterval(simulationInterval)
    simulationInterval = null
  }
}

// 更新任务进度
const updateTaskProgress = () => {
  const devTasks = developmentTasks.value.filter(t => t.progress < 100)
  if (devTasks.length > 0) {
    const randomTask = devTasks[Math.floor(Math.random() * devTasks.length)]
    const progressIncrease = Math.floor(Math.random() * 10) + 5
    randomTask.progress = Math.min(100, randomTask.progress + progressIncrease)

    if (randomTask.progress >= 100) {
      moveTaskToTesting(randomTask)
    }
  }
}

// 移动任务到测试列
const moveTaskToTesting = (task) => {
  const devIndex = developmentTasks.value.findIndex(t => t.id === task.id)
  if (devIndex > -1) {
    developmentTasks.value.splice(devIndex, 1)

    task.tag = '功能测试'
    task.assignee = 'AI测试工程师'
    task.progress = 100
    task.isNew = true
    testingTasks.value.unshift(task)

    stats.testing++

    const devAgent = sharedAgents.value.find(a => a.type === 'dev')
    addChatMessage(devAgent.name, devAgent.avatar, 'dev', `任务"${task.title}"开发完成，已提交测试。`)

    setTimeout(() => {
      task.isNew = false
    }, 1000)
  }
}

// 添加新任务
const addNewTask = () => {
  const newTask = {
    id: taskIdCounter++,
    tag: '新功能',
    title: `新任务 ${taskIdCounter}`,
    description: '这是一个新创建的任务，需要分配给相应的AI智能体处理。',
    priority: '中',
    assignee: 'AI产品经理',
    createdAt: getTimeString(),
    progress: 0,
    isNew: true
  }

  planningTasks.value.unshift(newTask)
  stats.totalTasks++
  stats.planning++

  const pmAgent = sharedAgents.value.find(a => a.type === 'pm')
  addChatMessage(pmAgent.name, pmAgent.avatar, 'pm', `新任务"${newTask.title}"已创建，开始需求分析。`)

  setTimeout(() => {
    newTask.isNew = false
  }, 1000)
}

// 显示任务详情
const showTaskDetail = (task) => {
  const agent = sharedAgents.value.find(a => a.name === task.assignee)
  if (agent) {
    addChatMessage(agent.name, agent.avatar, agent.type, `正在处理任务：${task.title}，当前进度：${task.progress}%`)
  }
}

// 组件挂载时启动模拟
onMounted(() => {
  startSimulation()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopSimulation()
})
</script>

<style scoped>
/* 主内容区域 */
.main-wrap {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: linear-gradient(135deg, #F5F5F7 0%, #E8E8ED 100%);
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-title h1 {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 4px;
}
.page-title span {
  color: #86868B;
  font-size: 14px;
}
.header-actions {
  display: flex;
  gap: 12px;
}
/* Apple 原生按钮 */
.btn {
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary {
  background: #007AFF;
  color: white;
}
.btn-primary:hover {
  background: #0062CC;
}
.btn-primary:disabled {
  background: #86868B;
  cursor: not-allowed;
}
.btn-ghost {
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.1);
}
.btn-ghost:hover {
  background: rgba(255,255,255,0.9);
}
.btn-small {
  padding: 6px 12px;
  font-size: 13px;
  background: rgba(0,122,255,0.1);
  color: #007AFF;
  border: 1px solid rgba(0,122,255,0.3);
  border-radius: 6px;
  transition: all 0.2s;
}
.btn-small:hover {
  background: rgba(0,122,255,0.2);
}
.btn-small.active {
  background: #FF9500;
  color: white;
  border-color: #FF9500;
}

/* 磨砂玻璃卡片容器 */
.glass-card {
  background: rgba(255,255,255,0.72);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  border: 1px solid rgba(255,255,255,0.9);
  padding: 20px;
  margin-bottom: 20px;
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-head h2 {
  font-size: 17px;
  font-weight: 600;
}
.live-indicator {
  font-size: 12px;
  color: #34C759;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 顶部状态统计行 */
.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-item {
  text-align: center;
  padding: 18px;
  background: rgba(255,255,255,0.5);
  border-radius: 12px;
}
.stat-num {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #007AFF;
  transition: all 0.3s ease;
}
.stat-label {
  font-size: 13px;
  color: #86868B;
}

/* 进度条 */
.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(0,0,0,0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-top: 16px;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007AFF 0%, #34C759 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}
.progress-text {
  text-align: center;
  margin-top: 8px;
  font-size: 12px;
  color: #86868B;
  font-weight: 500;
}

/* 项目任务看板 */
.task-board {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}
.task-column h3 {
  font-size: 14px;
  color: #86868B;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.task-card {
  background: rgba(255,255,255,0.85);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 10px;
  border: 1px solid rgba(0,0,0,0.06);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.06);
}
.task-card.fade-in {
  animation: fadeIn 0.5s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.task-tag {
  display: inline-block;
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 6px;
}
.tag-pm { background: rgba(0,122,255,0.12); color: #007AFF; }
.tag-dev { background: rgba(52,199,89,0.12); color: #34C759; }
.tag-test { background: rgba(255,149,0,0.12); color: #FF9500; }
.task-priority {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}
.priority-高 { background: rgba(255,59,48,0.15); color: #FF3B30; }
.priority-中 { background: rgba(255,149,0,0.15); color: #FF9500; }
.priority-低 { background: rgba(52,199,89,0.15); color: #34C759; }
.task-card h4 {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
}
.task-card p {
  font-size: 12px;
  color: #86868B;
  line-height: 1.4;
  margin-bottom: 8px;
}
.task-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.progress-mini {
  flex: 1;
  height: 4px;
  background: rgba(0,0,0,0.1);
  border-radius: 2px;
  overflow: hidden;
}
.progress-mini-fill {
  height: 100%;
  background: linear-gradient(90deg, #34C759 0%, #30D158 100%);
  border-radius: 2px;
  transition: width 0.3s ease;
}
.progress-text-mini {
  font-size: 11px;
  color: #34C759;
  font-weight: 500;
  min-width: 30px;
}
.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0,0,0,0.06);
}
.task-time {
  font-size: 10px;
  color: #86868B;
}
.task-assignee {
  font-size: 10px;
  color: #007AFF;
  font-weight: 500;
}

/* 多智能体实时协作对话面板 */
.chat-controls {
  display: flex;
  gap: 8px;
}
.chat-area {
  height: 320px;
  overflow-y: auto;
  margin-bottom: 16px;
  padding-right: 8px;
}
.chat-item {
  margin-bottom: 14px;
  display: flex;
  gap: 10px;
  transition: all 0.3s ease;
}
.chat-item.fade-in {
  animation: messageSlide 0.3s ease;
}
@keyframes messageSlide {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}
.chat-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}
.avatar-pm { background: #007AFF; }
.avatar-dev { background: #34C759; }
.avatar-test { background: #FF9500; }
.avatar-op { background: #AF52DE; }
.chat-bubble {
  background: rgba(255,255,255,0.8);
  border-radius: 12px;
  padding: 10px 14px;
  max-width: 70%;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.chat-bubble .name {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 4px;
  color: #007AFF;
}
.chat-bubble .text {
  font-size: 13px;
  line-height: 1.5;
}
.chat-bubble .message-time {
  font-size: 10px;
  color: #86868B;
  margin-top: 6px;
}
/* 苹果原生输入框 */
.input-row {
  display: flex;
  gap: 10px;
}
.apple-input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.1);
  background: rgba(255,255,255,0.8);
  font-size: 14px;
  outline: none;
  transition: border 0.2s;
}
.apple-input:focus {
  border-color: #007AFF;
}
.apple-input:disabled {
  background: rgba(0,0,0,0.05);
  cursor: not-allowed;
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.quick-action-btn {
  padding: 6px 12px;
  font-size: 12px;
  background: rgba(0,122,255,0.1);
  color: #007AFF;
  border: 1px solid rgba(0,122,255,0.2);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.quick-action-btn:hover {
  background: rgba(0,122,255,0.2);
  transform: translateY(-1px);
}
.quick-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 正在输入指示器 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(255,255,255,0.6);
  border-radius: 12px;
  margin-bottom: 14px;
  font-size: 12px;
  color: #86868B;
}
.typing-dots {
  display: flex;
  gap: 3px;
}
.typing-dots span {
  width: 6px;
  height: 6px;
  background: #007AFF;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}
.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-4px); }
}
</style>
