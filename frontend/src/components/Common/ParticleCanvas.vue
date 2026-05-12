<template>
  <canvas ref="canvasRef" class="particle-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  count: { type: Number, default: 60 },
  color: { type: String, default: '245,158,11' },  // RGB string
  colorSecondary: { type: String, default: '16,185,129' },
  maxSpeed: { type: Number, default: 0.35 },
  connectRadius: { type: Number, default: 140 },
  dotRadius: { type: Number, default: 1.5 },
  opacity: { type: Number, default: 0.55 },
})

const canvasRef = ref(null)
let ctx = null
let animId = null
let W = 0, H = 0
let particles = []

class Particle {
  constructor () {
    this.reset(true)
  }
  reset (init = false) {
    this.x = Math.random() * W
    this.y = init ? Math.random() * H : (Math.random() > 0.5 ? -6 : H + 6)
    const angle = Math.random() * Math.PI * 2
    const speed = (0.08 + Math.random() * props.maxSpeed)
    this.vx = Math.cos(angle) * speed
    this.vy = Math.sin(angle) * speed
    // Mix color between primary and secondary
    this.colorIdx = Math.random() > 0.6 ? 1 : 0
    this.alpha = 0.3 + Math.random() * 0.7
    this.r = props.dotRadius * (0.6 + Math.random() * 0.8)
    // Gentle wobble
    this.wobblePhase = Math.random() * Math.PI * 2
    this.wobbleSpeed = 0.005 + Math.random() * 0.01
    this.wobbleAmp = 0.2 + Math.random() * 0.4
  }
  update () {
    this.wobblePhase += this.wobbleSpeed
    this.x += this.vx + Math.sin(this.wobblePhase) * this.wobbleAmp
    this.y += this.vy + Math.cos(this.wobblePhase * 0.7) * this.wobbleAmp * 0.5
    if (this.x < -20 || this.x > W + 20 || this.y < -20 || this.y > H + 20) {
      this.reset()
    }
  }
  draw () {
    const rgb = this.colorIdx === 0 ? props.color : props.colorSecondary
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(${rgb},${this.alpha * props.opacity})`
    ctx.fill()
  }
}

function init () {
  resize()
  particles = Array.from({ length: props.count }, () => new Particle())
}

function resize () {
  const canvas = canvasRef.value
  W = canvas.width = canvas.offsetWidth
  H = canvas.height = canvas.offsetHeight
}

function drawConnections () {
  const r2 = props.connectRadius * props.connectRadius
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x
      const dy = particles[i].y - particles[j].y
      const dist2 = dx * dx + dy * dy
      if (dist2 < r2) {
        const t = 1 - Math.sqrt(dist2) / props.connectRadius
        // Blend colors based on both particle colors
        const rgb = particles[i].colorIdx === 0 ? props.color : props.colorSecondary
        ctx.beginPath()
        ctx.moveTo(particles[i].x, particles[i].y)
        ctx.lineTo(particles[j].x, particles[j].y)
        ctx.strokeStyle = `rgba(${rgb},${t * 0.22 * props.opacity})`
        ctx.lineWidth = t * 0.8
        ctx.stroke()
      }
    }
  }
}

function loop () {
  ctx.clearRect(0, 0, W, H)
  drawConnections()
  particles.forEach(p => { p.update(); p.draw() })
  animId = requestAnimationFrame(loop)
}

let resizeObserver = null

onMounted(() => {
  ctx = canvasRef.value.getContext('2d')
  init()
  loop()
  resizeObserver = new ResizeObserver(() => {
    resize()
    particles.forEach(p => {
      if (p.x > W) p.x = Math.random() * W
      if (p.y > H) p.y = Math.random() * H
    })
  })
  resizeObserver.observe(canvasRef.value)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animId)
  resizeObserver?.disconnect()
})
</script>

<style scoped>
.particle-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>
