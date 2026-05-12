<template>
  <span class="status-badge" :class="type">
    <span class="badge-dot"></span>
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true }
})

const statusMap = {
  completed: { label: '已完成', type: 'success' },
  running: { label: '运行中', type: 'warning' },
  pending: { label: '待处理', type: 'muted' },
  active: { label: '正常', type: 'success' },
  failed: { label: '失败', type: 'danger' },
  success: { label: '成功', type: 'success' }
}

const label = computed(() => statusMap[props.status]?.label || props.status)
const type = computed(() => statusMap[props.status]?.type || 'muted')
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.success { background: rgba(16, 185, 129, 0.1); color: #10b981; }
.success .badge-dot { background: #10b981; }

.warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.warning .badge-dot { background: #f59e0b; animation: pulse-dot 2s infinite; }

.danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.danger .badge-dot { background: #ef4444; }

.muted { background: rgba(255, 255, 255, 0.05); color: rgba(255, 255, 255, 0.4); }
.muted .badge-dot { background: rgba(255, 255, 255, 0.3); }

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
