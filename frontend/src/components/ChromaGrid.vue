<template>
  <div
    ref="rootRef"
    class="chroma-grid"
    :class="className"
    :style="{ '--r': radius + 'px', '--cols': columns }"
    @pointermove="handleMove"
    @pointerleave="handleLeave"
  >
    <article
      v-for="(item, i) in items"
      :key="i"
      class="chroma-card"
      :style="{
        '--card-border': item.borderColor || '',
        '--card-gradient': item.gradient || '',
      }"
      @mousemove="handleCardMove"
      @click="emit('card-click', { item, index: i })"
    >
      <div class="chroma-card-body">
        <slot name="card" :item="item" :index="i">
          <div class="chroma-img-wrapper">
            <img v-if="item.image" :src="item.image" :alt="item.title" loading="lazy" />
          </div>
          <footer class="chroma-info">
            <h3 class="name">{{ item.title }}</h3>
            <span v-if="item.handle" class="handle">{{ item.handle }}</span>
            <p class="role">{{ item.subtitle }}</p>
          </footer>
        </slot>
      </div>
    </article>
    <div class="chroma-overlay" />
    <div ref="fadeRef" class="chroma-fade" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  items: { type: Array, default: () => [] },
  className: { type: String, default: '' },
  radius: { type: Number, default: 300 },
  columns: { type: Number, default: 2 },
  damping: { type: Number, default: 0.45 },
  fadeOut: { type: Number, default: 0.6 },
  ease: { type: String, default: 'power3.out' },
})

const emit = defineEmits(['card-click'])

const rootRef = ref(null)
const fadeRef = ref(null)
let setX = null
let setY = null
const pos = { x: 0, y: 0 }

onMounted(() => {
  const el = rootRef.value
  if (!el) return
  setX = gsap.quickSetter(el, '--x', 'px')
  setY = gsap.quickSetter(el, '--y', 'px')
  const { width, height } = el.getBoundingClientRect()
  pos.x = width / 2
  pos.y = height / 2
  setX(pos.x)
  setY(pos.y)
})

const moveTo = (x, y) => {
  gsap.to(pos, {
    x, y,
    duration: props.damping,
    ease: props.ease,
    onUpdate: () => {
      setX?.(pos.x)
      setY?.(pos.y)
    },
    overwrite: true,
  })
}

const handleMove = (e) => {
  const r = rootRef.value.getBoundingClientRect()
  moveTo(e.clientX - r.left, e.clientY - r.top)
  gsap.to(fadeRef.value, { opacity: 0, duration: 0.25, overwrite: true })
}

const handleLeave = () => {
  gsap.to(fadeRef.value, { opacity: 1, duration: props.fadeOut, overwrite: true })
}

const handleCardMove = (e) => {
  const card = e.currentTarget
  const rect = card.getBoundingClientRect()
  card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`)
  card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`)
}
</script>

<style scoped>
.chroma-grid {
  position: relative;
  width: 100%;
  display: grid;
  grid-template-columns: repeat(var(--cols, 2), 1fr);
  gap: 1rem;
  box-sizing: border-box;
  --x: 50%;
  --y: 50%;
  --r: 300px;
}

.chroma-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid var(--card-border, #333);
  transition: border-color 0.3s ease;
  background: var(--card-gradient);
  cursor: pointer;
  --mouse-x: 50%;
  --mouse-y: 50%;
  --spotlight-color: rgba(255, 255, 255, 0.15);
}

.chroma-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at var(--mouse-x) var(--mouse-y),
    var(--spotlight-color),
    transparent 70%
  );
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.5s ease;
  z-index: 2;
}

.chroma-card:hover::before {
  opacity: 1;
}

.chroma-card-body {
  position: relative;
  z-index: 1;
}

.chroma-img-wrapper {
  position: relative;
  padding: 10px 10px 0;
}

.chroma-img-wrapper img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 10px;
  display: block;
}

.chroma-info {
  padding: 0.75rem 1rem;
  color: #fff;
  font-family: system-ui, sans-serif;
}

.chroma-info .role,
.chroma-info .handle {
  color: #aaa;
}

.chroma-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 3;
  backdrop-filter: grayscale(1) brightness(0.85);
  -webkit-backdrop-filter: grayscale(1) brightness(0.85);
  background: rgba(0, 0, 0, 0.001);
  mask-image: radial-gradient(
    circle var(--r) at var(--x) var(--y),
    transparent 0%,
    transparent 15%,
    rgba(0, 0, 0, 0.1) 30%,
    rgba(0, 0, 0, 0.22) 45%,
    rgba(0, 0, 0, 0.35) 60%,
    rgba(0, 0, 0, 0.5) 75%,
    rgba(0, 0, 0, 0.68) 88%,
    white 100%
  );
  -webkit-mask-image: radial-gradient(
    circle var(--r) at var(--x) var(--y),
    transparent 0%,
    transparent 15%,
    rgba(0, 0, 0, 0.1) 30%,
    rgba(0, 0, 0, 0.22) 45%,
    rgba(0, 0, 0, 0.35) 60%,
    rgba(0, 0, 0, 0.5) 75%,
    rgba(0, 0, 0, 0.68) 88%,
    white 100%
  );
}

.chroma-fade {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 4;
  backdrop-filter: grayscale(1) brightness(0.85);
  -webkit-backdrop-filter: grayscale(1) brightness(0.85);
  background: rgba(0, 0, 0, 0.001);
  mask-image: radial-gradient(
    circle var(--r) at var(--x) var(--y),
    white 0%,
    white 15%,
    rgba(255, 255, 255, 0.9) 30%,
    rgba(255, 255, 255, 0.78) 45%,
    rgba(255, 255, 255, 0.65) 60%,
    rgba(255, 255, 255, 0.5) 75%,
    rgba(255, 255, 255, 0.32) 88%,
    transparent 100%
  );
  -webkit-mask-image: radial-gradient(
    circle var(--r) at var(--x) var(--y),
    white 0%,
    white 15%,
    rgba(255, 255, 255, 0.9) 30%,
    rgba(255, 255, 255, 0.78) 45%,
    rgba(255, 255, 255, 0.65) 60%,
    rgba(255, 255, 255, 0.5) 75%,
    rgba(255, 255, 255, 0.32) 88%,
    transparent 100%
  );
  opacity: 1;
  transition: opacity 0.25s ease;
}
</style>
