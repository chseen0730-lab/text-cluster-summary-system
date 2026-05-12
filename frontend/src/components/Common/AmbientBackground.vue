<template>
  <div class="ambient-bg">
    <!-- Deep noise mesh gradient orbs -->
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="orb orb-4"></div>
    <!-- Scanline grain overlay -->
    <div class="noise-overlay"></div>
    <!-- Grid lines -->
    <div class="grid-overlay"></div>
    <!-- Vignette -->
    <div class="vignette"></div>
  </div>
</template>

<script setup>
defineProps({
  intensity: { type: String, default: 'normal' } // 'subtle' | 'normal' | 'vivid'
})
</script>

<style scoped>
.ambient-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

/* ---- Orbs ---- */
.orb {
  position: absolute;
  border-radius: 50%;
  will-change: transform, opacity;
  mix-blend-mode: screen;
}

.orb-1 {
  width: 900px;
  height: 900px;
  top: -25%;
  left: -15%;
  background: radial-gradient(ellipse at center,
    rgba(16, 185, 129, 0.12) 0%,
    rgba(16, 185, 129, 0.04) 40%,
    transparent 70%
  );
  animation: orb-drift-1 20s ease-in-out infinite alternate;
  filter: blur(40px);
}

.orb-2 {
  width: 800px;
  height: 800px;
  bottom: -20%;
  right: -10%;
  background: radial-gradient(ellipse at center,
    rgba(245, 158, 11, 0.14) 0%,
    rgba(245, 158, 11, 0.05) 40%,
    transparent 70%
  );
  animation: orb-drift-2 26s ease-in-out infinite alternate;
  filter: blur(50px);
}

.orb-3 {
  width: 600px;
  height: 600px;
  top: 35%;
  left: 30%;
  background: radial-gradient(ellipse at center,
    rgba(245, 158, 11, 0.07) 0%,
    rgba(16, 185, 129, 0.04) 50%,
    transparent 70%
  );
  animation: orb-drift-3 32s ease-in-out infinite alternate;
  filter: blur(60px);
}

.orb-4 {
  width: 400px;
  height: 400px;
  top: 10%;
  right: 20%;
  background: radial-gradient(ellipse at center,
    rgba(239, 68, 68, 0.06) 0%,
    transparent 70%
  );
  animation: orb-drift-4 18s ease-in-out infinite alternate;
  filter: blur(70px);
}

@keyframes orb-drift-1 {
  0%   { transform: translate(0, 0) scale(1); }
  33%  { transform: translate(60px, 40px) scale(1.08); }
  66%  { transform: translate(30px, 80px) scale(0.95); }
  100% { transform: translate(80px, 20px) scale(1.12); }
}
@keyframes orb-drift-2 {
  0%   { transform: translate(0, 0) scale(1); }
  40%  { transform: translate(-50px, -60px) scale(1.1); }
  70%  { transform: translate(-80px, -20px) scale(0.92); }
  100% { transform: translate(-30px, -80px) scale(1.06); }
}
@keyframes orb-drift-3 {
  0%   { transform: translate(0, 0) scale(1) rotate(0deg); }
  50%  { transform: translate(-40px, 50px) scale(1.15) rotate(10deg); }
  100% { transform: translate(60px, -30px) scale(0.9) rotate(-5deg); }
}
@keyframes orb-drift-4 {
  0%   { transform: translate(0, 0) scale(1); opacity: 0.6; }
  50%  { transform: translate(30px, 40px) scale(1.2); opacity: 1; }
  100% { transform: translate(-20px, 60px) scale(0.85); opacity: 0.4; }
}

/* ---- Subtle dot grid ---- */
.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
  -webkit-mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
}

/* ---- Noise grain ---- */
.noise-overlay {
  position: absolute;
  inset: -50%;
  width: 200%;
  height: 200%;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
  opacity: 0.025;
  animation: noise-drift 8s steps(2) infinite;
  pointer-events: none;
}

@keyframes noise-drift {
  0%   { transform: translate(0, 0); }
  20%  { transform: translate(-2%, -3%); }
  40%  { transform: translate(3%, 1%); }
  60%  { transform: translate(-1%, 4%); }
  80%  { transform: translate(4%, -2%); }
  100% { transform: translate(0, 0); }
}

/* ---- Edge vignette ---- */
.vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse 100% 100% at 50% 50%,
    transparent 50%,
    rgba(9, 9, 11, 0.55) 100%
  );
}
</style>
