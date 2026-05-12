<template>
  <div class="loading-spinner" :class="size">
    <div class="spinner-ring">
      <div></div><div></div><div></div>
    </div>
    <p v-if="text" class="spinner-text">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '' },
  size: { type: String, default: 'md' }
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-spinner.sm { padding: 16px; }
.loading-spinner.lg { padding: 60px; }

.spinner-ring {
  position: relative;
  width: 40px;
  height: 40px;
}

.sm .spinner-ring { width: 24px; height: 24px; }
.lg .spinner-ring { width: 56px; height: 56px; }

.spinner-ring div {
  position: absolute;
  inset: 0;
  border: 2px solid transparent;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.spinner-ring div:nth-child(2) {
  border-top-color: #10b981;
  animation-delay: -0.15s;
  inset: 3px;
}

.spinner-ring div:nth-child(3) {
  border-top-color: rgba(255, 255, 255, 0.2);
  animation-delay: -0.3s;
  inset: 6px;
}

.spinner-text {
  margin-top: 16px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
