<template>
  <div class="history-page">
    <!-- Loading -->
    <div v-if="pageLoading" class="loading-wrapper">
      <LoadingSpinner text="加载操作历史..." size="lg" />
    </div>

    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <h1 class="page-title">操作历史</h1>
      </div>

      <!-- Toolbar: search + type filter -->
      <div class="toolbar">
        <div class="toolbar-left">
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
            </svg>
            <input
              v-model="keyword"
              type="text"
              class="search-input"
              placeholder="搜索关键词..."
              @keydown.enter="fetchList"
            />
          </div>
          <select v-model="filterType" class="filter-select" @change="fetchList">
            <option value="">全部</option>
            <option value="text">文本</option>
            <option value="cluster">聚类</option>
            <option value="summary">摘要</option>
          </select>
        </div>
      </div>

      <!-- Empty State -->
      <EmptyState v-if="historyList.length === 0" text="暂无操作历史" />

      <!-- Table -->
      <GlassCard v-else :no-padding="true">
        <DataTable
          :columns="columns"
          :data="historyList"
          :total="total"
          :page-size="pageSize"
          @page-change="onPageChange"
          @sort-change="onSortChange"
        >
          <template #col-type="{ value }">
            <span class="type-cell">
              <span class="type-dot" :class="'dot-' + value"></span>
              {{ typeLabels[value] || value }}
            </span>
          </template>
          <template #col-status="{ value }">
            <StatusBadge :status="value" />
          </template>
        </DataTable>
      </GlassCard>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import GlassCard from '@/components/Common/GlassCard.vue'
import DataTable from '@/components/Common/DataTable.vue'
import StatusBadge from '@/components/Common/StatusBadge.vue'
import LoadingSpinner from '@/components/Common/LoadingSpinner.vue'
import EmptyState from '@/components/Common/EmptyState.vue'
import { getHistoryList } from '@/api/user'

const pageLoading = ref(true)
const keyword = ref('')
const filterType = ref('')
const historyList = ref([])
const total = ref(0)
const pageSize = 10
const currentPage = ref(1)

const typeLabels = {
  text: '文本',
  cluster: '聚类',
  summary: '摘要'
}

const columns = [
  { key: 'id', title: 'ID', width: '60px' },
  { key: 'type', title: '操作类型', width: '120px', sortable: true },
  { key: 'action', title: '操作', width: '140px' },
  { key: 'target', title: '目标' },
  { key: 'user', title: '操作人', width: '100px' },
  { key: 'time', title: '时间', width: '170px', sortable: true },
  { key: 'status', title: '状态', width: '100px' }
]

async function fetchList() {
  try {
    const params = {
      page: currentPage.value,
      pageSize,
      keyword: keyword.value || undefined,
      type: filterType.value || undefined
    }
    const res = await getHistoryList(params)
    if (res.code === 200) {
      historyList.value = res.data.list
      total.value = res.data.total
    }
  } catch (e) {
    console.error('Failed to fetch history:', e)
  } finally {
    pageLoading.value = false
  }
}

function onPageChange(page) {
  currentPage.value = page
  fetchList()
}

function onSortChange() {
  fetchList()
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.history-page {
  padding: 0;
  min-height: 100%;
}

.loading-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: -0.5px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: rgba(255, 255, 255, 0.3);
  pointer-events: none;
}

.search-input {
  padding: 8px 12px 8px 36px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  outline: none;
  width: 220px;
  transition: all 0.2s;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.search-input:focus {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(255, 255, 255, 0.07);
}

.filter-select {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-select:focus {
  border-color: rgba(245, 158, 11, 0.4);
}

.filter-select option {
  background: #09090b;
  color: rgba(255, 255, 255, 0.85);
}

.type-cell {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
}

.type-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-text {
  background: #f59e0b;
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.4);
}

.dot-cluster {
  background: #10b981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.4);
}

.dot-summary {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.4);
}
</style>
