<template>
  <div ref="containerRef" class="dot-field-container">
    <canvas ref="canvasRef" class="dot-canvas" />
    <svg ref="svgRef" class="dot-svg">
      <defs>
        <radialGradient :id="glowId">
          <stop offset="0%" :stop-color="glowColor" />
          <stop offset="100%" stop-color="transparent" />
        </radialGradient>
      </defs>
      <circle ref="glowRef" cx="-9999" cy="-9999" :r="glowRadius" :fill="`url(#${glowId})`" />
    </svg>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

const TWO_PI = Math.PI * 2

const props = defineProps({
  dotRadius: { type: Number, default: 1.5 },
  dotSpacing: { type: Number, default: 14 },
  cursorRadius: { type: Number, default: 500 },
  cursorForce: { type: Number, default: 0.1 },
  bulgeOnly: { type: Boolean, default: true },
  bulgeStrength: { type: Number, default: 67 },
  glowRadius: { type: Number, default: 160 },
  sparkle: { type: Boolean, default: false },
  waveAmplitude: { type: Number, default: 0 },
  gradientFrom: { type: String, default: 'rgba(168, 85, 247, 0.35)' },
  gradientTo: { type: String, default: 'rgba(180, 151, 207, 0.25)' },
  glowColor: { type: String, default: '#120F17' },
})

const containerRef = ref(null)
const canvasRef = ref(null)
const svgRef = ref(null)
const glowRef = ref(null)
const glowId = `dot-glow-${Math.random().toString(36).slice(2, 9)}`

const dotsRef = []
const mouseRef = { x: -9999, y: -9999, prevX: -9999, prevY: -9999, speed: 0 }
const sizeRef = { w: 0, h: 0, offsetX: 0, offsetY: 0 }
const glowOpacity = { current: 0 }
const engagement = { current: 0 }
let rafId = null
let speedInterval = null
let frameCount = 0
let ctx = null
let dpr = 1

const buildDots = () => {
  const { w, h } = sizeRef
  const step = props.dotRadius + props.dotSpacing
  const cols = Math.floor(w / step)
  const rows = Math.floor(h / step)
  const padX = (w % step) / 2
  const padY = (h % step) / 2
  dotsRef.length = 0
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const ax = padX + col * step + step / 2
      const ay = padY + row * step + step / 2
      dotsRef.push({ ax, ay, sx: ax, sy: ay, vx: 0, vy: 0, x: ax, y: ay })
    }
  }
}

const resize = () => {
  const canvas = canvasRef.value
  const parent = containerRef.value
  if (!canvas || !parent) return
  dpr = Math.min(window.devicePixelRatio || 1, 2)
  const w = parent.offsetWidth
  const h = parent.offsetHeight
  canvas.width = w * dpr
  canvas.height = h * dpr
  canvas.style.width = `${w}px`
  canvas.style.height = `${h}px`
  ctx = canvas.getContext('2d', { alpha: true })
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  const rect = parent.getBoundingClientRect()
  sizeRef.w = w
  sizeRef.h = h
  sizeRef.offsetX = rect.left + window.scrollX
  sizeRef.offsetY = rect.top + window.scrollY
  buildDots()
}

const onMouseMove = (e) => {
  mouseRef.x = e.pageX - sizeRef.offsetX
  mouseRef.y = e.pageY - sizeRef.offsetY
}

const updateMouseSpeed = () => {
  const m = mouseRef
  const dx = m.prevX - m.x
  const dy = m.prevY - m.y
  const dist = Math.sqrt(dx * dx + dy * dy)
  m.speed += (dist - m.speed) * 0.5
  if (m.speed < 0.001) m.speed = 0
  m.prevX = m.x
  m.prevY = m.y
}

const tick = () => {
  frameCount++
  const dots = dotsRef
  const m = mouseRef
  const { w, h } = sizeRef
  const len = dots.length
  const t = frameCount * 0.02

  const targetEngagement = Math.min(m.speed / 5, 1)
  engagement.current += (targetEngagement - engagement.current) * 0.06
  if (engagement.current < 0.001) engagement.current = 0
  const eng = engagement.current

  glowOpacity.current += (eng - glowOpacity.current) * 0.08

  const glowEl = glowRef.value
  if (glowEl) {
    glowEl.setAttribute('cx', m.x)
    glowEl.setAttribute('cy', m.y)
    glowEl.style.opacity = glowOpacity.current
  }

  ctx.clearRect(0, 0, w, h)

  const grad = ctx.createLinearGradient(0, 0, w, h)
  grad.addColorStop(0, props.gradientFrom)
  grad.addColorStop(1, props.gradientTo)
  ctx.fillStyle = grad

  const cr = props.cursorRadius
  const crSq = cr * cr
  const rad = props.dotRadius / 2
  const isBulge = props.bulgeOnly

  ctx.beginPath()
  for (let i = 0; i < len; i++) {
    const d = dots[i]
    const dx = m.x - d.ax
    const dy = m.y - d.ay
    const distSq = dx * dx + dy * dy

    if (distSq < crSq && eng > 0.01) {
      const dist = Math.sqrt(distSq)
      if (isBulge) {
        const t2 = 1 - dist / cr
        const push = t2 * t2 * props.bulgeStrength * eng
        const angle = Math.atan2(dy, dx)
        d.sx += (d.ax - Math.cos(angle) * push - d.sx) * 0.15
        d.sy += (d.ay - Math.sin(angle) * push - d.sy) * 0.15
      } else {
        const angle = Math.atan2(dy, dx)
        const move = (500 / dist) * (m.speed * props.cursorForce)
        d.vx += Math.cos(angle) * -move
        d.vy += Math.sin(angle) * -move
      }
    } else if (isBulge) {
      d.sx += (d.ax - d.sx) * 0.1
      d.sy += (d.ay - d.sy) * 0.1
    }

    if (!isBulge) {
      d.vx *= 0.9
      d.vy *= 0.9
      d.x = d.ax + d.vx
      d.y = d.ay + d.vy
      d.sx += (d.x - d.sx) * 0.1
      d.sy += (d.y - d.sy) * 0.1
    }

    let drawX = d.sx
    let drawY = d.sy
    if (props.waveAmplitude > 0) {
      drawY += Math.sin(d.ax * 0.03 + t) * props.waveAmplitude
      drawX += Math.cos(d.ay * 0.03 + t * 0.7) * props.waveAmplitude * 0.5
    }

    if (props.sparkle) {
      const hash = ((i * 2654435761) ^ (frameCount >> 3)) >>> 0
      if ((hash % 100) < 3) {
        ctx.moveTo(drawX + rad * 1.8, drawY)
        ctx.arc(drawX, drawY, rad * 1.8, 0, TWO_PI)
      } else {
        ctx.moveTo(drawX + rad, drawY)
        ctx.arc(drawX, drawY, rad, 0, TWO_PI)
      }
    } else {
      ctx.moveTo(drawX + rad, drawY)
      ctx.arc(drawX, drawY, rad, 0, TWO_PI)
    }
  }
  ctx.fill()

  rafId = requestAnimationFrame(tick)
}

onMounted(async () => {
  await nextTick()
  // 确保父容器已完成布局，否则 canvas 尺寸为 0
  requestAnimationFrame(() => {
    resize()
    window.addEventListener('resize', resize)
    window.addEventListener('mousemove', onMouseMove, { passive: true })
    speedInterval = setInterval(updateMouseSpeed, 20)
    rafId = requestAnimationFrame(tick)
  })
})

onUnmounted(() => {
  cancelAnimationFrame(rafId)
  clearInterval(speedInterval)
  window.removeEventListener('resize', resize)
  window.removeEventListener('mousemove', onMouseMove)
})

watch(() => [props.dotRadius, props.dotSpacing], buildDots)
</script>

<style scoped>
.dot-field-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
.dot-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.dot-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
