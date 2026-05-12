<template>
  <div class="glass-card" :class="[variant, { hoverable, 'no-padding': noPadding }]">
    <div v-if="$slots.header" class="glass-card__header">
      <slot name="header" />
    </div>
    <div class="glass-card__body">
      <slot />
    </div>
    <div v-if="$slots.footer" class="glass-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'default' },
  hoverable: { type: Boolean, default: false },
  noPadding: { type: Boolean, default: false }
})
</script>

<style scoped>
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Top shimmer line */
.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.12) 30%,
    rgba(245, 158, 11, 0.2) 50%,
    rgba(255, 255, 255, 0.12) 70%,
    transparent 100%
  );
  transition: opacity 0.3s;
  pointer-events: none;
}

/* Subtle inner glow when hovered */
.glass-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 16px;
  background: radial-gradient(
    ellipse 60% 50% at 50% 0%,
    rgba(245, 158, 11, 0.04),
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.4s;
  pointer-events: none;
}

.glass-card.hoverable:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.18);
  box-shadow:
    0 12px 40px rgba(0, 0, 0, 0.35),
    0 0 0 1px rgba(245, 158, 11, 0.08),
    0 0 60px rgba(245, 158, 11, 0.04);
}

.glass-card.hoverable:hover::after {
  opacity: 1;
}

.glass-card.accent {
  border-color: rgba(245, 158, 11, 0.15);
  background: rgba(245, 158, 11, 0.03);
}

.glass-card.success {
  border-color: rgba(16, 185, 129, 0.15);
  background: rgba(16, 185, 129, 0.03);
}

.glass-card.success::before {
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(16, 185, 129, 0.2) 50%,
    transparent 100%
  );
}

.glass-card.danger {
  border-color: rgba(239, 68, 68, 0.15);
  background: rgba(239, 68, 68, 0.03);
}

.glass-card__header {
  padding: 20px 24px 0;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.glass-card__body {
  padding: 20px 24px;
}

.glass-card.no-padding .glass-card__body {
  padding: 0;
}

.glass-card__footer {
  padding: 0 24px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 16px;
  margin-top: 0;
}
</style>
