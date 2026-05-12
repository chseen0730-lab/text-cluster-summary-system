<template>
  <div class="summary-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">摘要管理</h1>
      <div class="search-bar">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
        </svg>
        <input
          v-model="keyword"
          type="text"
          class="search-input"
          placeholder="搜索摘要标题或内容..."
          @input="onSearch"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-wrapper">
      <LoadingSpinner text="加载摘要列表..." size="lg" />
    </div>

    <!-- Empty State -->
    <EmptyState v-else-if="summaries.length === 0" text="暂无摘要数据" />

    <!-- Summary Cards -->
    <div v-else class="summary-grid">
      <GlassCard
        v-for="item in summaries"
        :key="item.id"
        hoverable
      >
        <!-- Header: title + cluster tag -->
        <div class="card-top">
          <h2 class="card-title">{{ item.title }}</h2>
          <span class="cluster-tag">{{ item.clusterLabel }}</span>
        </div>

        <!-- Content preview or full -->
        <p class="card-content">
          {{ expandedIds.has(item.id) ? item.content : truncate(item.content, 100) }}
        </p>

        <!-- Key points -->
        <ul class="key-points">
          <template v-if="expandedIds.has(item.id)">
            <li v-for="(point, idx) in (item.keyPoints || [])" :key="idx">{{ point }}</li>
          </template>
          <template v-else>
            <li v-for="(point, idx) in (item.keyPoints || []).slice(0, 2)" :key="idx">{{ point }}</li>
          </template>
        </ul>

        <!-- Meta info -->
        <div class="card-meta">
          <span class="meta-item">{{ item.wordCount }} 字</span>
          <span class="meta-divider"></span>
          <span class="meta-item">{{ item.model }}</span>
          <span class="meta-divider"></span>
          <span class="meta-item">{{ item.createdAt }}</span>
        </div>

        <!-- Actions -->
        <template #footer>
          <div class="card-actions">
            <button class="btn btn-ghost" @click="toggleExpand(item.id)">
              {{ expandedIds.has(item.id) ? '收起' : '查看详情' }}
            </button>
            <button class="btn btn-danger" @click="openDelete(item)">删除</button>
          </div>
        </template>
      </GlassCard>
    </div>

    <!-- Delete Confirm Dialog -->
    <ConfirmDialog
      :visible="deleteDialogVisible"
      title="删除摘要"
      :message="`确定要删除「${deleteTarget?.title ?? ''}」吗？此操作不可撤销。`"
      type="danger"
      confirmText="删除"
      cancelText="取消"
      @confirm="handleDelete"
      @cancel="deleteDialogVisible = false"
      @update:visible="deleteDialogVisible = $event"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import GlassCard from '@/components/Common/GlassCard.vue'
import ConfirmDialog from '@/components/Common/ConfirmDialog.vue'
import LoadingSpinner from '@/components/Common/LoadingSpinner.vue'
import EmptyState from '@/components/Common/EmptyState.vue'
import { getSummaryList, deleteSummary } from '@/api/summary'
import { ensureMinLoadingOff, getNowMsSafe } from '@/utils/minLoading'

/* ---------- state ---------- */

const loading = ref(true)
const summaries = ref([])
const keyword = ref('')
const expandedIds = reactive(new Set())

const deleteDialogVisible = ref(false)
const deleteTarget = ref(null)

let searchTimer = null

/* ---------- helpers ---------- */

function truncate(text, len) {
  if (!text) return ''
  return text.length > len ? text.slice(0, len) + '...' : text
}

function toggleExpand(id) {
  if (expandedIds.has(id)) {
    expandedIds.delete(id)
  } else {
    expandedIds.add(id)
  }
}

/* ---------- data fetching ---------- */

async function fetchList() {
  loading.value = true
  const startedAtMs = getNowMsSafe()
  try {
    const params = {}
    if (keyword.value.trim()) {
      params.keyword = keyword.value.trim()
    }
    const res = await getSummaryList(params)
    if (res.data?.list) {
      // 后端返回的摘要列表里可能没有 keyPoints 等字段，做兜底避免模板渲染时报错导致页面空白
      summaries.value = res.data.list.map(item => ({
        ...item,
        keyPoints: Array.isArray(item.keyPoints)
          ? item.keyPoints
          : (Array.isArray(item.keypoints) ? item.keypoints : []),
        wordCount: item.wordCount ?? item.word_count ?? 0,
        model: item.model ?? item.sourceModel ?? ''
      }))
    }
  } catch (e) {
    console.error('获取摘要列表失败', e)
  } finally {
    ensureMinLoadingOff(loading, startedAtMs)
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    fetchList()
  }, 300)
}

/* ---------- delete ---------- */

function openDelete(item) {
  deleteTarget.value = item
  deleteDialogVisible.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteSummary(deleteTarget.value.id)
    summaries.value = summaries.value.filter(s => s.id !== deleteTarget.value.id)
    expandedIds.delete(deleteTarget.value.id)
  } catch (e) {
    console.error('删除摘要失败', e)
  } finally {
    deleteDialogVisible.value = false
    deleteTarget.value = null
  }
}

/* ---------- lifecycle ---------- */

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.summary-page {
  min-height: 100%;
  padding: 32px;
  background: #09090b;
}

/* ---- Page Header ---- */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 28px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
}

/* ---- Search Bar ---- */
.search-bar {
  position: relative;
  width: 320px;
  max-width: 100%;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.3);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 16px 10px 40px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.search-input:focus {
  border-color: rgba(245, 158, 11, 0.4);
}

/* ---- Loading ---- */
.loading-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

/* ---- Summary Grid ---- */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

/* ---- Card Internals ---- */
.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  line-height: 1.4;
}

.cluster-tag {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.2);
  white-space: nowrap;
}

.card-content {
  font-size: 14px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.55);
  margin: 0 0 14px;
}

/* ---- Key Points ---- */
.key-points {
  list-style: none;
  padding: 0;
  margin: 0 0 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.key-points li {
  position: relative;
  padding-left: 18px;
  font-size: 13px;
  line-height: 1.6;
  color: #10b981;
}

.key-points li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

/* ---- Meta Info ---- */
.card-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
}

.meta-divider {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

/* ---- Card Actions ---- */
.card-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 8px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  white-space: nowrap;
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
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.15);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .summary-page {
    padding: 20px 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-title {
    font-size: 22px;
  }

  .search-bar {
    width: 100%;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
