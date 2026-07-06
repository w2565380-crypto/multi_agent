<template>
  <div ref="containerRef" class="side-rays-container" />
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Renderer, Program, Mesh, Triangle } from 'ogl'

const props = defineProps({
  speed: { type: Number, default: 2.5 },
  rayColor1: { type: String, default: '#EAB308' },
  rayColor2: { type: String, default: '#96c8ff' },
  intensity: { type: Number, default: 2 },
  spread: { type: Number, default: 2 },
  origin: { type: String, default: 'top-right' },
  tilt: { type: Number, default: 0 },
  saturation: { type: Number, default: 1.5 },
  blend: { type: Number, default: 0.75 },
  falloff: { type: Number, default: 1.6 },
  opacity: { type: Number, default: 1.0 },
})

const containerRef = ref(null)
let renderer = null
let mesh = null
let uniforms = null
let animationId = null

const hexToRgb = (hex) => {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return m ? [parseInt(m[1], 16) / 255, parseInt(m[2], 16) / 255, parseInt(m[3], 16) / 255] : [1, 1, 1]
}

const originToFlip = (origin) => {
  switch (origin) {
    case 'top-left': return [1, 0]
    case 'bottom-right': return [0, 1]
    case 'bottom-left': return [1, 1]
    default: return [0, 0]
  }
}

const VERT = `attribute vec2 position;
void main() {
  gl_Position = vec4(position, 0.0, 1.0);
}`

const FRAG = `precision highp float;

uniform float iTime;
uniform vec2 iResolution;
uniform float iSpeed;
uniform vec3 iRayColor1;
uniform vec3 iRayColor2;
uniform float iIntensity;
uniform float iSpread;
uniform float iFlipX;
uniform float iFlipY;
uniform float iTilt;
uniform float iSaturation;
uniform float iBlend;
uniform float iFalloff;
uniform float iOpacity;

float rayStrength(vec2 raySource, vec2 rayRefDirection, vec2 coord, float seedA, float seedB, float speed) {
  vec2 sourceToCoord = coord - raySource;
  float cosAngle = dot(normalize(sourceToCoord), rayRefDirection);
  return clamp(
    (0.45 + 0.15 * sin(cosAngle * seedA + iTime * speed)) +
    (0.3 + 0.2 * cos(-cosAngle * seedB + iTime * speed)),
    0.0, 1.0) *
    clamp((iResolution.x - length(sourceToCoord)) / iResolution.x, 0.5, 1.0);
}

void main() {
  vec2 fragCoord = gl_FragCoord.xy;
  if (iFlipX > 0.5) fragCoord.x = iResolution.x - fragCoord.x;
  if (iFlipY > 0.5) fragCoord.y = iResolution.y - fragCoord.y;

  vec2 coord = vec2(fragCoord.x, iResolution.y - fragCoord.y);
  vec2 rayPos = vec2(iResolution.x * 1.1, -0.5 * iResolution.y);

  float tiltRad = iTilt * 3.14159265 / 180.0;
  float cs = cos(tiltRad);
  float sn = sin(tiltRad);
  vec2 rel = coord - rayPos;
  vec2 tiltedCoord = vec2(rel.x * cs - rel.y * sn, rel.x * sn + rel.y * cs) + rayPos;

  float halfSpread = iSpread * 0.275;
  vec2 rayRefDir1 = normalize(vec2(cos(0.785398 + halfSpread), sin(0.785398 + halfSpread)));
  vec2 rayRefDir2 = normalize(vec2(cos(0.785398 - halfSpread), sin(0.785398 - halfSpread)));

  vec4 rays1 = vec4(iRayColor1, 1.0) * rayStrength(rayPos, rayRefDir1, tiltedCoord, 36.2214, 21.11349, iSpeed);
  vec4 rays2 = vec4(iRayColor2, 1.0) * rayStrength(rayPos, rayRefDir2, tiltedCoord, 22.3991, 18.0234, iSpeed * 0.2);

  vec4 color = rays1 * (1.0 - iBlend) * 0.9 + rays2 * iBlend * 0.9;

  float distanceToLight = length(fragCoord.xy - vec2(rayPos.x, iResolution.y - rayPos.y)) / iResolution.y;
  float brightness = iIntensity * 0.4 / pow(max(distanceToLight, 0.001), iFalloff);
  color.rgb *= brightness;

  float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
  color.rgb = mix(vec3(gray), color.rgb, iSaturation);

  color.a = max(color.r, max(color.g, color.b)) * iOpacity;
  gl_FragColor = color;
}`

const updateSize = () => {
  if (!containerRef.value || !renderer) return
  renderer.dpr = Math.min(window.devicePixelRatio, 2)
  const { clientWidth: w, clientHeight: h } = containerRef.value
  renderer.setSize(w, h)
  uniforms.iResolution.value = [w * renderer.dpr, h * renderer.dpr]
}

const init = () => {
  if (!containerRef.value) return
  cleanup()

  renderer = new Renderer({ dpr: Math.min(window.devicePixelRatio, 2), alpha: true })
  const gl = renderer.gl
  gl.canvas.style.width = '100%'
  gl.canvas.style.height = '100%'
  gl.canvas.style.position = 'absolute'
  gl.canvas.style.top = '0'
  gl.canvas.style.left = '0'
  gl.canvas.style.pointerEvents = 'none'

  containerRef.value.appendChild(gl.canvas)

  const [flipX, flipY] = originToFlip(props.origin)
  uniforms = {
    iTime: { value: 0 },
    iResolution: { value: [1, 1] },
    iSpeed: { value: props.speed },
    iRayColor1: { value: hexToRgb(props.rayColor1) },
    iRayColor2: { value: hexToRgb(props.rayColor2) },
    iIntensity: { value: props.intensity },
    iSpread: { value: props.spread },
    iFlipX: { value: flipX },
    iFlipY: { value: flipY },
    iTilt: { value: props.tilt },
    iSaturation: { value: props.saturation },
    iBlend: { value: props.blend },
    iFalloff: { value: props.falloff },
    iOpacity: { value: props.opacity },
  }

  const geometry = new Triangle(gl)
  const program = new Program(gl, { vertex: VERT, fragment: FRAG, uniforms })
  mesh = new Mesh(gl, { geometry, program })

  window.addEventListener('resize', updateSize)
  updateSize()

  const loop = (t) => {
    if (!renderer || !uniforms || !mesh) {
      animationId = requestAnimationFrame(loop)
      return
    }
    uniforms.iTime.value = t * 0.001
    try { renderer.render({ scene: mesh }) } catch { /* ignore */ }
    animationId = requestAnimationFrame(loop)
  }
  animationId = requestAnimationFrame(loop)
}

const cleanup = () => {
  if (animationId) { cancelAnimationFrame(animationId); animationId = null }
  window.removeEventListener('resize', updateSize)
  if (renderer) {
    try {
      const lose = renderer.gl.getExtension('WEBGL_lose_context')
      if (lose) lose.loseContext()
      const canvas = renderer.gl.canvas
      if (canvas?.parentNode) canvas.parentNode.removeChild(canvas)
    } catch { /* ignore */ }
    renderer = null
  }
  uniforms = null
  mesh = null
}

onMounted(async () => {
  await nextTick()
  requestAnimationFrame(() => init())
})

onUnmounted(() => cleanup())

watch(() => [
  props.speed, props.rayColor1, props.rayColor2, props.intensity,
  props.spread, props.origin, props.tilt, props.saturation,
  props.blend, props.falloff, props.opacity,
], () => {
  if (!uniforms) return
  uniforms.iSpeed.value = props.speed
  uniforms.iRayColor1.value = hexToRgb(props.rayColor1)
  uniforms.iRayColor2.value = hexToRgb(props.rayColor2)
  uniforms.iIntensity.value = props.intensity
  uniforms.iSpread.value = props.spread
  const [fx, fy] = originToFlip(props.origin)
  uniforms.iFlipX.value = fx
  uniforms.iFlipY.value = fy
  uniforms.iTilt.value = props.tilt
  uniforms.iSaturation.value = props.saturation
  uniforms.iBlend.value = props.blend
  uniforms.iFalloff.value = props.falloff
  uniforms.iOpacity.value = props.opacity
})
</script>

<style scoped>
.side-rays-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
</style>
