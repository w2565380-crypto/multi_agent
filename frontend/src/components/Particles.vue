<template>
  <div ref="containerRef" class="particles-container" />
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Renderer, Camera, Geometry, Program, Mesh } from 'ogl'

const props = defineProps({
  particleCount: { type: Number, default: 200 },
  particleSpread: { type: Number, default: 10 },
  speed: { type: Number, default: 0.1 },
  particleColors: { type: Array, default: () => ['#ffffff'] },
  moveParticlesOnHover: { type: Boolean, default: false },
  particleHoverFactor: { type: Number, default: 1 },
  alphaParticles: { type: Boolean, default: false },
  particleBaseSize: { type: Number, default: 100 },
  sizeRandomness: { type: Number, default: 1 },
  cameraDistance: { type: Number, default: 20 },
  disableRotation: { type: Boolean, default: false },
  pixelRatio: { type: Number, default: 1 },
})

const containerRef = ref(null)
const mouseRef = { x: 0, y: 0 }
let renderer = null, camera = null, particles = null, program = null
let animationId = null, lastTime = 0, elapsed = 0

const hexToRgb = (hex) => {
  hex = hex.replace(/^#/, '')
  if (hex.length === 3) hex = hex.split('').map(c => c + c).join('')
  const int = parseInt(hex, 16)
  return [(int >> 16 & 255) / 255, (int >> 8 & 255) / 255, (int & 255) / 255]
}

const VERT = `attribute vec3 position;
attribute vec4 random;
attribute vec3 color;
uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;
uniform float uSpread;
uniform float uBaseSize;
uniform float uSizeRandomness;
varying vec4 vRandom;
varying vec3 vColor;
void main() {
  vRandom = random;
  vColor = color;
  vec3 pos = position * uSpread;
  pos.z *= 10.0;
  vec4 mPos = modelMatrix * vec4(pos, 1.0);
  float t = uTime;
  mPos.x += sin(t * random.z + 6.28 * random.w) * mix(0.1, 1.5, random.x);
  mPos.y += sin(t * random.y + 6.28 * random.x) * mix(0.1, 1.5, random.w);
  mPos.z += sin(t * random.w + 6.28 * random.y) * mix(0.1, 1.5, random.z);
  vec4 mvPos = viewMatrix * mPos;
  gl_PointSize = uSizeRandomness == 0.0
    ? uBaseSize
    : (uBaseSize * (1.0 + uSizeRandomness * (random.x - 0.5))) / length(mvPos.xyz);
  gl_Position = projectionMatrix * mvPos;
}`

const FRAG = `precision highp float;
uniform float uTime;
uniform float uAlphaParticles;
varying vec4 vRandom;
varying vec3 vColor;
void main() {
  vec2 uv = gl_PointCoord.xy;
  float d = length(uv - vec2(0.5));
  if (uAlphaParticles < 0.5) {
    if (d > 0.5) discard;
    gl_FragColor = vec4(vColor + 0.2 * sin(uv.yxx + uTime + vRandom.y * 6.28), 1.0);
  } else {
    float circle = smoothstep(0.5, 0.4, d) * 0.8;
    gl_FragColor = vec4(vColor + 0.2 * sin(uv.yxx + uTime + vRandom.y * 6.28), circle);
  }
}`

const resize = () => {
  if (!containerRef.value || !renderer) return
  const w = containerRef.value.clientWidth
  const h = containerRef.value.clientHeight
  renderer.setSize(w, h)
  camera.perspective({ aspect: renderer.gl.canvas.width / renderer.gl.canvas.height })
}

const handleMouseMove = (e) => {
  const rect = containerRef.value.getBoundingClientRect()
  mouseRef.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
  mouseRef.y = -(((e.clientY - rect.top) / rect.height) * 2 - 1)
}

const init = () => {
  if (!containerRef.value) return
  cleanup()
  const container = containerRef.value
  renderer = new Renderer({ dpr: props.pixelRatio, depth: false, alpha: true })
  const gl = renderer.gl
  gl.clearColor(0, 0, 0, 0)
  container.appendChild(gl.canvas)
  camera = new Camera(gl, { fov: 15 })
  camera.position.set(0, 0, props.cameraDistance)

  window.addEventListener('resize', resize)
  resize()
  if (props.moveParticlesOnHover) container.addEventListener('mousemove', handleMouseMove)

  const count = props.particleCount
  const positions = new Float32Array(count * 3)
  const randoms = new Float32Array(count * 4)
  const colors = new Float32Array(count * 3)
  const palette = props.particleColors.length > 0 ? props.particleColors : ['#ffffff']

  for (let i = 0; i < count; i++) {
    let x, y, z, len
    do { x = Math.random() * 2 - 1; y = Math.random() * 2 - 1; z = Math.random() * 2 - 1; len = x * x + y * y + z * z } while (len > 1 || len === 0)
    const r = Math.cbrt(Math.random())
    positions.set([x * r, y * r, z * r], i * 3)
    randoms.set([Math.random(), Math.random(), Math.random(), Math.random()], i * 4)
    const col = hexToRgb(palette[Math.floor(Math.random() * palette.length)])
    colors.set(col, i * 3)
  }

  const geometry = new Geometry(gl, {
    position: { size: 3, data: positions },
    random: { size: 4, data: randoms },
    color: { size: 3, data: colors }
  })

  program = new Program(gl, {
    vertex: VERT, fragment: FRAG,
    uniforms: {
      uTime: { value: 0 }, uSpread: { value: props.particleSpread },
      uBaseSize: { value: props.particleBaseSize * props.pixelRatio },
      uSizeRandomness: { value: props.sizeRandomness },
      uAlphaParticles: { value: props.alphaParticles ? 1 : 0 }
    },
    transparent: true, depthTest: false
  })

  particles = new Mesh(gl, { mode: gl.POINTS, geometry, program })
  lastTime = performance.now()
  elapsed = 0

  const loop = (t) => {
    animationId = requestAnimationFrame(loop)
    const delta = t - lastTime; lastTime = t; elapsed += delta * props.speed
    program.uniforms.uTime.value = elapsed * 0.001

    if (props.moveParticlesOnHover) {
      particles.position.x = -mouseRef.x * props.particleHoverFactor
      particles.position.y = -mouseRef.y * props.particleHoverFactor
    }

    if (!props.disableRotation) {
      particles.rotation.x = Math.sin(elapsed * 0.0002) * 0.1
      particles.rotation.y = Math.cos(elapsed * 0.0005) * 0.15
      particles.rotation.z += 0.01 * props.speed
    }

    renderer.render({ scene: particles, camera })
  }
  animationId = requestAnimationFrame(loop)
}

const cleanup = () => {
  if (animationId) { cancelAnimationFrame(animationId); animationId = null }
  window.removeEventListener('resize', resize)
  if (containerRef.value) containerRef.value.removeEventListener('mousemove', handleMouseMove)
  if (renderer) {
    try {
      const lose = renderer.gl.getExtension('WEBGL_lose_context')
      if (lose) lose.loseContext()
      const canvas = renderer.gl.canvas
      if (canvas?.parentNode) canvas.parentNode.removeChild(canvas)
    } catch { /* ignore */ }
    renderer = null
  }
}

onMounted(async () => { await nextTick(); requestAnimationFrame(() => init()) })
onUnmounted(() => cleanup())
</script>

<style scoped>
.particles-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
.particles-container canvas {
  position: absolute;
  inset: 0;
}
</style>
