<template>
  <div class="cluster-page">
    <!-- Loading -->
    <div v-if="pageLoading" class="loading-wrapper">
      <LoadingSpinner text="加载聚类任务..." size="lg" />
    </div>

    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <h1 class="page-title">聚类分析</h1>
      </div>

      <!-- Toolbar: search + filter + create -->
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
              placeholder="搜索任务名称..."
              @keydown.enter="fetchList"
            />
          </div>
          <select v-model="filterStatus" class="filter-select" @change="fetchList">
            <option value="">全部</option>
            <option value="completed">已完成</option>
            <option value="running">运行中</option>
            <option value="pending">待处理</option>
          </select>
        </div>
        <div class="toolbar-right">
          <button class="btn btn-amber" @click="openCreateModal">新建任务</button>
        </div>
      </div>

      <!-- Card Grid -->
      <div v-if="clusterList.length > 0" class="card-grid">
        <GlassCard v-for="item in clusterList" :key="item.id" hoverable>
          <div class="card-top">
            <div class="card-title-row">
              <h3 class="card-name">{{ item.name }}</h3>
              <StatusBadge :status="item.status" />
            </div>
            <span class="algorithm-badge">{{ item.algorithm }}</span>
          </div>

          <!-- Progress bar for running tasks -->
          <div v-if="item.status === 'running'" class="progress-wrapper">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: item.progress + '%' }"></div>
            </div>
            <span class="progress-text">{{ item.progress }}%</span>
          </div>

          <div class="card-meta">
            <div class="meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><polyline points="14 2 14 8 20 8" />
              </svg>
              <span>{{ item.textIds.length }} 篇文本</span>
            </div>
            <div class="meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <circle cx="12" cy="12" r="10" /><path d="M8 12h8" /><path d="M12 8v8" />
              </svg>
              <span>{{ item.clusterCount }} 个聚类</span>
            </div>
          </div>

          <div class="card-time">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
              <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
            </svg>
            <span>{{ item.createdAt }}</span>
          </div>

          <div class="card-actions">
            <router-link
              v-if="item.status === 'completed'"
              :to="'/cluster-results/' + item.id"
              class="btn btn-sm btn-emerald"
            >
              查看结果
            </router-link>
            <button class="btn btn-sm btn-danger" @click="openDeleteDialog(item)">删除</button>
          </div>
        </GlassCard>
      </div>

      <!-- Empty State -->
      <EmptyState
        v-else
        text="暂无聚类任务"
        action-text="新建任务"
        @action="openCreateModal"
      />
    </template>

    <!-- Create Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modalVisible" class="modal-overlay" @click.self="closeModal">
          <div class="modal-panel">
            <h3 class="modal-title">新建任务</h3>
            <form @submit.prevent="handleSubmit">
              <div class="form-group">
                <label class="form-label">任务名称 <span class="required">*</span></label>
                <input
                  v-model="form.name"
                  type="text"
                  class="form-input"
                  placeholder="请输入任务名称"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">任务描述</label>
                <textarea
                  v-model="form.description"
                  class="form-input form-textarea"
                  placeholder="请输入任务描述（可选）"
                  rows="3"
                />
              </div>
              <div class="form-row">
                <div class="form-group form-group-half">
                  <label class="form-label">算法选择</label>
                  <select v-model="form.algorithm" class="form-input form-select">
                    <option value="K-Means">K-Means</option>
                    <option value="DBSCAN">DBSCAN</option>
                    <option value="层次聚类">层次聚类</option>
                  </select>
                </div>
                <div class="form-group form-group-half">
                  <label class="form-label">聚类数量</label>
                  <input
                    v-model.number="form.clusterCount"
                    type="number"
                    class="form-input"
                    min="2"
                    max="10"
                  />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">选择文本</label>
                <div class="text-checklist">
                  <label
                    v-for="t in availableTexts"
                    :key="t.id"
                    class="check-item"
                  >
                    <input
                      type="checkbox"
                      :value="t.id"
                      v-model="form.textIds"
                      class="check-input"
                    />
                    <span class="check-label">{{ t.title }}</span>
                  </label>
                </div>
              </div>
              <div class="modal-actions">
                <button type="button" class="btn btn-ghost" @click="closeModal">取消</button>
                <button type="submit" class="btn btn-amber" :disabled="submitting">
                  {{ submitting ? '提交中...' : '创建任务' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Confirm -->
    <ConfirmDialog
      :visible="showDeleteConfirm"
      title="删除任务"
      :message="`确定要删除「${deleteTarget?.name || ''}」吗？此操作不可撤销。`"
      type="danger"
      confirm-text="删除"
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
      @update:visible="showDeleteConfirm = $event"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import GlassCard from '@/components/Common/GlassCard.vue'
import StatusBadge from '@/components/Common/StatusBadge.vue'
import LoadingSpinner from '@/components/Common/LoadingSpinner.vue'
import EmptyState from '@/components/Common/EmptyState.vue'
import ConfirmDialog from '@/components/Common/ConfirmDialog.vue'
import { getClusterList, createCluster, deleteCluster } from '@/api/cluster'

/* ---------- constants ---------- */

const availableTexts = [
  { id: 1, title: '人工智能技术的未来发展趋势' },
  { id: 2, title: '碳中和目标下的能源转型路径' },
  { id: 3, title: '数据隐私保护与个人信息安全' },
  { id: 4, title: '远程办公对企业管理的影响' },
  { id: 5, title: '新能源汽车市场竞争格局分析' },
  { id: 6, title: '社交媒体对青少年心理健康的影响' },
  { id: 7, title: 'AI大模型的商业化应用前景' },
  { id: 8, title: '城市智慧交通系统建设方案' }
]

/* ---------- list state ---------- */

const pageLoading = ref(true)
const clusterList = ref([])
const keyword = ref('')
const filterStatus = ref('')

/* ---------- modal state ---------- */

const modalVisible = ref(false)
const submitting = ref(false)
const form = ref({
  name: '',
  description: '',
  algorithm: 'K-Means',
  clusterCount: 3,
  textIds: []
})

/* ---------- delete state ---------- */

const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)

/* ---------- fetch ---------- */

async function fetchList() {
  try {
    const res = await getClusterList({
      keyword: keyword.value || undefined,
      status: filterStatus.value || undefined
    })
    if (res.data) {
      clusterList.value = res.data.list
    }
  } catch (e) {
    console.error('获取聚类任务列表失败', e)
  } finally {
    pageLoading.value = false
  }
}

/* ---------- create ---------- */

function resetForm() {
  form.value = {
    name: '',
    description: '',
    algorithm: 'K-Means',
    clusterCount: 3,
    textIds: []
  }
}

function openCreateModal() {
  resetForm()
  modalVisible.value = true
}

function closeModal() {
  modalVisible.value = false
  resetForm()
}

async function handleSubmit() {
  if (!form.value.name) return
  submitting.value = true
  try {
    await createCluster({
      name: form.value.name,
      description: form.value.description,
      algorithm: form.value.algorithm,
      clusterCount: form.value.clusterCount,
      textIds: form.value.textIds
    })
    closeModal()
    await fetchList()
  } catch (e) {
    console.error('创建任务失败', e)
  } finally {
    submitting.value = false
  }
}

/* ---------- delete ---------- */

function openDeleteDialog(item) {
  deleteTarget.value = item
  showDeleteConfirm.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteCluster(deleteTarget.value.id)
    showDeleteConfirm.value = false
    deleteTarget.value = null
    await fetchList()
  } catch (e) {
    console.error('删除任务失败', e)
  }
}

/* ---------- lifecycle ---------- */

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.cluster-page {
  min-height: 100%;
  padding: 32px;
  background: #09090b;
}

.loading-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

/* ---- Header ---- */
.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
}

/* ---- Toolbar ---- */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 320px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.25);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 36px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.search-input:focus {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.08);
}

.filter-select {
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.4)' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 32px;
}

.filter-select:focus {
  border-color: rgba(245, 158, 11, 0.4);
}

.filter-select option {
  background: #18181b;
  color: rgba(255, 255, 255, 0.9);
}

/* ---- Buttons ---- */
.btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  white-space: nowrap;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-sm {
  padding: 6px 14px;
  font-size: 12px;
  border-radius: 8px;
}

.btn-amber {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.btn-amber:hover:not(:disabled) {
  background: rgba(245, 158, 11, 0.25);
}

.btn-amber:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-emerald {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.btn-emerald:hover {
  background: rgba(16, 185, 129, 0.25);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.25);
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

/* ---- Card Grid ---- */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.card-title-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.92);
  margin: 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.algorithm-badge {
  flex-shrink: 0;
  padding: 4px 10px;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.15);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  color: #f59e0b;
  white-space: nowrap;
}

/* ---- Progress ---- */
.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.progress-text {
  font-size: 12px;
  font-weight: 500;
  color: #f59e0b;
  font-variant-numeric: tabular-nums;
  min-width: 36px;
  text-align: right;
}

/* ---- Card Meta ---- */
.card-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
}

.meta-item svg {
  color: rgba(255, 255, 255, 0.25);
}

.card-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 16px;
}

.card-time svg {
  color: rgba(255, 255, 255, 0.2);
}

/* ---- Card Actions ---- */
.card-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* ---- Modal ---- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-panel {
  background: rgba(24, 24, 27, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 32px;
  max-width: 560px;
  width: 100%;
  backdrop-filter: blur(16px);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group-half {
  flex: 1;
}

.form-label {
  display: block;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 8px;
}

.required {
  color: #ef4444;
  margin-left: 2px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.form-input:focus {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.08);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.form-select {
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.4)' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 32px;
}

.form-select option {
  background: #18181b;
  color: rgba(255, 255, 255, 0.9);
}

/* ---- Text Checklist ---- */
.text-checklist {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
}

.text-checklist::-webkit-scrollbar {
  width: 4px;
}

.text-checklist::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 4px;
  border-radius: 6px;
  transition: background 0.15s;
}

.check-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.check-input {
  width: 16px;
  height: 16px;
  accent-color: #f59e0b;
  cursor: pointer;
  flex-shrink: 0;
}

.check-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 28px;
}

/* ---- Modal transition ---- */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .modal-panel,
.modal-leave-active .modal-panel {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-panel {
  transform: scale(0.95) translateY(10px);
}

.modal-leave-to .modal-panel {
  transform: scale(0.95) translateY(10px);
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .cluster-page {
    padding: 20px 16px;
  }

  .page-title {
    font-size: 22px;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left {
    flex-direction: column;
  }

  .search-box {
    max-width: none;
  }

  .toolbar-right {
    justify-content: stretch;
  }

  .toolbar-right .btn {
    flex: 1;
    text-align: center;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .modal-panel {
    max-width: none;
    width: 100%;
    margin: 0;
    border-radius: 12px;
  }
}
</style>
