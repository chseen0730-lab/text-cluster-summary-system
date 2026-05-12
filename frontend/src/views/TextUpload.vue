<template>
  <div class="text-manage-page">
    <!-- Loading -->
    <div v-if="pageLoading" class="loading-wrapper">
      <LoadingSpinner text="加载文本数据..." size="lg" />
    </div>

    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <h1 class="page-title">文本管理</h1>
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
              placeholder="搜索关键词..."
              @keydown.enter="fetchList"
            />
          </div>
          <select v-model="filterCategory" class="filter-select" @change="fetchList">
            <option value="">全部分类</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        <div class="toolbar-right">
          <button v-if="selectedIds.length > 0" class="btn btn-danger" @click="showBatchDelete = true">
            批量删除 ({{ selectedIds.length }})
          </button>
          <button class="btn btn-amber" @click="openCreateModal">新建文本</button>
        </div>
      </div>

      <!-- Table -->
      <GlassCard :no-padding="true">
        <DataTable
          :columns="columns"
          :data="textList"
          :total="total"
          :page-size="pageSize"
          :selectable="true"
          @page-change="onPageChange"
          @selection-change="onSelectionChange"
          @sort-change="onSortChange"
        >
          <template #col-status="{ value }">
            <StatusBadge :status="value" />
          </template>
          <template #col-title="{ value }">
            <span class="cell-title">{{ value }}</span>
          </template>
          <template #col-wordCount="{ value }">
            <span class="cell-count">{{ value }}</span>
          </template>
          <template #actions="{ row }">
            <div class="action-btns">
              <button class="btn-action btn-edit" @click="openEditModal(row)">编辑</button>
              <button class="btn-action btn-del" @click="openDeleteDialog(row)">删除</button>
            </div>
          </template>
        </DataTable>
      </GlassCard>
    </template>

    <!-- Create / Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modalVisible" class="modal-overlay" @click.self="closeModal">
          <div class="modal-panel">
            <h3 class="modal-title">{{ isEditing ? '编辑文本' : '新建文本' }}</h3>
            <form @submit.prevent="handleSubmit">
              <div class="form-group">
                <label class="form-label">标题 <span class="required">*</span></label>
                <input
                  v-model="form.title"
                  type="text"
                  class="form-input"
                  placeholder="请输入文本标题"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">内容 <span class="required">*</span></label>
                <textarea
                  v-model="form.content"
                  class="form-input form-textarea"
                  placeholder="请输入文本内容"
                  rows="6"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">分类</label>
                <select v-model="form.category" class="form-input form-select">
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>
              <div class="modal-actions">
                <button type="button" class="btn btn-ghost" @click="closeModal">取消</button>
                <button type="submit" class="btn btn-amber" :disabled="submitting">
                  {{ submitting ? '提交中...' : '确定' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Single Delete Confirm -->
    <ConfirmDialog
      :visible="showDeleteConfirm"
      title="删除文本"
      :message="`确定要删除「${deleteTarget?.title || ''}」吗？此操作不可撤销。`"
      type="danger"
      confirm-text="删除"
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
      @update:visible="showDeleteConfirm = $event"
    />

    <!-- Batch Delete Confirm -->
    <ConfirmDialog
      :visible="showBatchDelete"
      title="批量删除"
      :message="`确定要删除选中的 ${selectedIds.length} 条文本吗？此操作不可撤销。`"
      type="danger"
      confirm-text="全部删除"
      @confirm="handleBatchDelete"
      @cancel="showBatchDelete = false"
      @update:visible="showBatchDelete = $event"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import GlassCard from '@/components/Common/GlassCard.vue'
import DataTable from '@/components/Common/DataTable.vue'
import StatusBadge from '@/components/Common/StatusBadge.vue'
import LoadingSpinner from '@/components/Common/LoadingSpinner.vue'
import ConfirmDialog from '@/components/Common/ConfirmDialog.vue'
import {
  getTextList,
  createText,
  updateText,
  deleteText,
  batchDeleteTexts
} from '@/api/text'

/* ---------- constants ---------- */

const categories = ['科技', '社会', '商业', '环境', '未分类']

const columns = [
  { key: 'id', title: 'ID', width: '60px', sortable: true },
  { key: 'title', title: '标题', sortable: true },
  { key: 'category', title: '分类', width: '100px' },
  { key: 'wordCount', title: '字数', width: '80px', sortable: true },
  { key: 'createdAt', title: '创建时间', width: '160px', sortable: true },
  { key: 'status', title: '状态', width: '100px' }
]

/* ---------- list state ---------- */

const pageLoading = ref(true)
const textList = ref([])
const total = ref(0)
const pageSize = ref(10)
const currentPage = ref(1)
const keyword = ref('')
const filterCategory = ref('')
const selectedIds = ref([])

/* ---------- modal state ---------- */

const modalVisible = ref(false)
const isEditing = ref(false)
const editId = ref(null)
const submitting = ref(false)
const form = ref({
  title: '',
  content: '',
  category: '未分类'
})

/* ---------- delete state ---------- */

const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)
const showBatchDelete = ref(false)

/* ---------- fetch ---------- */

async function fetchList() {
  try {
    const res = await getTextList({
      page: currentPage.value,
      pageSize: pageSize.value,
      keyword: keyword.value || undefined,
      category: filterCategory.value || undefined
    })
    if (res.data) {
      textList.value = res.data.list
      total.value = res.data.total
    }
  } catch (e) {
    console.error('获取文本列表失败', e)
  } finally {
    pageLoading.value = false
  }
}

function onPageChange(page) {
  currentPage.value = page
  fetchList()
}

function onSelectionChange(ids) {
  selectedIds.value = ids
}

function onSortChange() {
  fetchList()
}

/* ---------- create / edit ---------- */

function resetForm() {
  form.value = { title: '', content: '', category: '未分类' }
  editId.value = null
  isEditing.value = false
}

function openCreateModal() {
  resetForm()
  modalVisible.value = true
}

function openEditModal(row) {
  isEditing.value = true
  editId.value = row.id
  form.value = {
    title: row.title,
    content: row.content || '',
    category: row.category || '未分类'
  }
  modalVisible.value = true
}

function closeModal() {
  modalVisible.value = false
  resetForm()
}

async function handleSubmit() {
  if (!form.value.title || !form.value.content) return
  submitting.value = true
  try {
    if (isEditing.value) {
      await updateText(editId.value, { ...form.value })
    } else {
      await createText({ ...form.value })
    }
    closeModal()
    await fetchList()
  } catch (e) {
    console.error('提交失败', e)
  } finally {
    submitting.value = false
  }
}

/* ---------- delete ---------- */

function openDeleteDialog(row) {
  deleteTarget.value = row
  showDeleteConfirm.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteText(deleteTarget.value.id)
    showDeleteConfirm.value = false
    deleteTarget.value = null
    await fetchList()
  } catch (e) {
    console.error('删除失败', e)
  }
}

async function handleBatchDelete() {
  try {
    await batchDeleteTexts([...selectedIds.value])
    showBatchDelete.value = false
    selectedIds.value = []
    await fetchList()
  } catch (e) {
    console.error('批量删除失败', e)
  }
}

/* ---------- lifecycle ---------- */

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.text-manage-page {
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
  margin-bottom: 20px;
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

/* ---- Table cells ---- */
.cell-title {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.cell-count {
  font-variant-numeric: tabular-nums;
}

.action-btns {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-action {
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
}

.btn-edit {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.btn-edit:hover {
  background: rgba(245, 158, 11, 0.2);
}

.btn-del {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.btn-del:hover {
  background: rgba(239, 68, 68, 0.2);
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
  max-width: 540px;
  width: 100%;
  backdrop-filter: blur(16px);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
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
  min-height: 100px;
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
  .text-manage-page {
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

  .modal-panel {
    max-width: none;
    width: 100%;
    margin: 0;
    border-radius: 12px;
  }
}
</style>
