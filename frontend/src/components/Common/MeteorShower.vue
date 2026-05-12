<template>
  <div class="meteor-shower" aria-hidden="true">
    <span
      v-for="m in meteors"
      :key="m.id"
      class="meteor"
      :style="m.style"
    ></span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  count: { type: Number, default: 12 },
})

const meteors = computed(() => {
  return Array.from({ length: props.count }, (_, i) => {
    const top = Math.random() * 60   // % from top
    const left = 10 + Math.random() * 80  // % from left
    const duration = 2.5 + Math.random() * 3   // seconds
    const delay = Math.random() * 10            // seconds
    const length = 80 + Math.random() * 120     // px tail length
    return {
      id: i,
      style: {
        top: `${top}%`,
        left: `${left}%`,
        '--duration': `${duration}s`,
        '--delay': `${delay}s`,
        '--length': `${length}px`,
      }
    }
  })
})
</script>

<style scoped>
.meteor-shower {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 1;
}

.meteor {
  position: absolute;
  width: 2px;
  height: var(--length, 80px);
  background: linear-gradient(
    180deg,
    rgba(245, 158, 11, 0.8) 0%,
    rgba(245, 158, 11, 0.3) 50%,
    transparent 100%
  );
  border-radius: 9999px;
  transform: rotate(-45deg) translateY(-100%);
  opacity: 0;
  animation: meteor-drop var(--duration, 3s) ease-in var(--delay, 0s) infinite;
}

.meteor::after {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.9);
  box-shadow: 0 0 6px 2px rgba(245, 158, 11, 0.5);
}

@keyframes meteor-drop {
  0% {
    opacity: 0;
    transform: rotate(-45deg) translateY(-20px);
  }
  5% {
    opacity: 1;
  }
  70% {
    opacity: 0.5;
  }
  100% {
    opacity: 0;
    transform: rotate(-45deg) translateY(500px);
  }
}
</style>
