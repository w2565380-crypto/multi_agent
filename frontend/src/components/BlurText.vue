<template>
  <p ref="rootRef" :class="className" class="blur-text-wrap">
    <span
      v-for="(segment, i) in segments"
      :key="i"
      class="blur-segment"
    >{{ segment === ' ' ? '\u00A0' : segment }}{{ animateBy === 'words' && i < segments.length - 1 && segment !== ' ' ? '\u00A0' : '' }}</span>
  </p>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  text: { type: String, default: '' },
  className: { type: String, default: '' },
  animateBy: { type: String, default: 'words' },
  direction: { type: String, default: 'top' },
  delay: { type: Number, default: 200 },
  stepDuration: { type: Number, default: 0.35 },
})

const emit = defineEmits(['animationComplete'])

const rootRef = ref(null)

const segments = computed(() =>
  props.animateBy === 'words' ? props.text.split(' ') : props.text.split('')
)

onMounted(async () => {
  await nextTick()
  const el = rootRef.value
  if (!el) return
  const spans = el.querySelectorAll('.blur-segment')
  if (spans.length === 0) return

  gsap.fromTo(
    spans,
    {
      filter: 'blur(10px)',
      opacity: 0,
      y: props.direction === 'top' ? -50 : 50,
    },
    {
      filter: 'blur(0px)',
      opacity: 1,
      y: 0,
      duration: props.stepDuration * 2,
      stagger: props.delay / 1000,
      ease: 'power2.out',
      onComplete: () => {
        emit('animationComplete')
      },
    }
  )
})
</script>

<style scoped>
.blur-text-wrap {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
}
.blur-segment {
  display: inline-block;
  will-change: transform, filter, opacity;
}
</style>
