<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="visible" class="dialog-overlay" @click.self="onCancel">
        <div class="dialog-panel">
          <div class="dialog-icon" :class="type">
            <svg v-if="type === 'danger'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            <svg v-else-if="type === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
          </div>
          <h3 class="dialog-title">{{ title }}</h3>
          <p class="dialog-message">{{ message }}</p>
          <div class="dialog-actions">
            <button class="btn btn-ghost" @click="onCancel">{{ cancelText }}</button>
            <button class="btn" :class="'btn-' + type" @click="onConfirm">{{ confirmText }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: '确认操作' },
  message: { type: String, default: '确定要执行此操作吗？' },
  type: { type: String, default: 'danger' },
  confirmText: { type: String, default: '确定' },
  cancelText: { type: String, default: '取消' }
})

const emit = defineEmits(['confirm', 'cancel', 'update:visible'])

function onConfirm() {
  emit('confirm')
  emit('update:visible', false)
}

function onCancel() {
  emit('cancel')
  emit('update:visible', false)
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.dialog-panel {
  background: #18181b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 32px;
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.dialog-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dialog-icon svg {
  width: 24px;
  height: 24px;
}

.dialog-icon.danger {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.dialog-icon.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.dialog-icon.info {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.dialog-title {
  color: rgba(255, 255, 255, 0.95);
  font-size: 18px;
  margin-bottom: 8px;
}

.dialog-message {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  margin-bottom: 24px;
  line-height: 1.6;
}

.dialog-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn {
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.25);
}

.btn-warning {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.btn-warning:hover {
  background: rgba(245, 158, 11, 0.25);
}

.btn-info {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.btn-info:hover {
  background: rgba(16, 185, 129, 0.25);
}

.dialog-enter-active, .dialog-leave-active {
  transition: opacity 0.2s;
}

.dialog-enter-active .dialog-panel, .dialog-leave-active .dialog-panel {
  transition: transform 0.2s;
}

.dialog-enter-from, .dialog-leave-to {
  opacity: 0;
}

.dialog-enter-from .dialog-panel {
  transform: scale(0.95);
}

.dialog-leave-to .dialog-panel {
  transform: scale(0.95);
}
</style>
