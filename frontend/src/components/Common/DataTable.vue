<template>
  <div class="data-table-wrap">
    <div class="table-scroll">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="selectable" class="col-check">
              <input type="checkbox" :checked="allSelected" @change="toggleAll" />
            </th>
            <th v-for="col in columns" :key="col.key" :style="{ width: col.width }"
                :class="{ sortable: col.sortable }" @click="col.sortable && toggleSort(col.key)">
              {{ col.title }}
              <span v-if="col.sortable" class="sort-icon">
                <svg v-if="sortKey === col.key" viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                  <path v-if="sortOrder === 'asc'" d="M7 14l5-5 5 5z"/>
                  <path v-else d="M7 10l5 5 5-5z"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="currentColor" width="14" height="14" opacity="0.3">
                  <path d="M7 10l5 5 5-5z"/>
                </svg>
              </span>
            </th>
            <th v-if="$slots.actions" class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in displayData" :key="row.id || idx" class="table-row">
            <td v-if="selectable" class="col-check">
              <input type="checkbox" :checked="selectedIds.includes(row.id)" @change="toggleRow(row.id)" />
            </td>
            <td v-for="col in columns" :key="col.key">
              <slot :name="'col-' + col.key" :row="row" :value="row[col.key]">
                {{ row[col.key] }}
              </slot>
            </td>
            <td v-if="$slots.actions" class="col-actions">
              <slot name="actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="total > pageSize" class="pagination">
      <span class="page-info">共 {{ total }} 条</span>
      <div class="page-btns">
        <button :disabled="currentPage <= 1" @click="changePage(currentPage - 1)">&lsaquo;</button>
        <button v-for="p in pageNumbers" :key="p" :class="{ active: p === currentPage }" @click="changePage(p)">{{ p }}</button>
        <button :disabled="currentPage >= totalPages" @click="changePage(currentPage + 1)">&rsaquo;</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  data: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  pageSize: { type: Number, default: 10 },
  selectable: { type: Boolean, default: false }
})

const emit = defineEmits(['page-change', 'selection-change', 'sort-change'])

const currentPage = ref(1)
const sortKey = ref('')
const sortOrder = ref('asc')
const selectedIds = ref([])

const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

const pageNumbers = computed(() => {
  const pages = []
  const total = totalPages.value
  const cur = currentPage.value
  let start = Math.max(1, cur - 2)
  let end = Math.min(total, cur + 2)
  if (end - start < 4) {
    if (start === 1) end = Math.min(total, 5)
    else start = Math.max(1, end - 4)
  }
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const displayData = computed(() => {
  let list = [...props.data]
  if (sortKey.value) {
    list.sort((a, b) => {
      const va = a[sortKey.value]
      const vb = b[sortKey.value]
      const cmp = typeof va === 'number' ? va - vb : String(va).localeCompare(String(vb))
      return sortOrder.value === 'asc' ? cmp : -cmp
    })
  }
  return list
})

const allSelected = computed(() =>
  props.data.length > 0 && props.data.every(r => selectedIds.value.includes(r.id))
)

function changePage(p) {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  emit('page-change', p)
}

function toggleSort(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  emit('sort-change', { key: sortKey.value, order: sortOrder.value })
}

function toggleRow(id) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
  emit('selection-change', [...selectedIds.value])
}

function toggleAll() {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = props.data.map(r => r.id)
  }
  emit('selection-change', [...selectedIds.value])
}
</script>

<style scoped>
.data-table-wrap {
  width: 100%;
}

.table-scroll {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 500;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  white-space: nowrap;
  user-select: none;
}

.data-table th.sortable {
  cursor: pointer;
}

.data-table th.sortable:hover {
  color: rgba(255, 255, 255, 0.7);
}

.sort-icon {
  display: inline-flex;
  vertical-align: middle;
  margin-left: 4px;
}

.data-table td {
  padding: 14px 16px;
  color: rgba(255, 255, 255, 0.75);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.table-row {
  transition: background 0.15s;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.col-check {
  width: 40px;
}

.col-check input[type="checkbox"] {
  accent-color: #f59e0b;
  cursor: pointer;
}

.col-actions {
  width: 120px;
  text-align: right;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.page-info {
  color: rgba(255, 255, 255, 0.35);
  font-size: 13px;
}

.page-btns {
  display: flex;
  gap: 4px;
}

.page-btns button {
  min-width: 32px;
  height: 32px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}

.page-btns button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
}

.page-btns button.active {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
  color: #f59e0b;
}

.page-btns button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
</style>
