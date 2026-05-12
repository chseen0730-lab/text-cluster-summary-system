<template>
  <div class="summary-gen-page">
    <!-- Loading -->
    <div v-if="pageLoading" class="loading-wrapper">
      <LoadingSpinner text="加载聚类任务..." size="lg" />
    </div>

    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <h1 class="page-title">摘要生成</h1>
      </div>

      <!-- Two-panel layout -->
      <div class="panels">
        <!-- Left Panel: Configuration -->
        <GlassCard class="panel-left">
          <template #header>配置参数</template>
          <form class="gen-form" @submit.prevent="handleGenerate">
            <div class="form-group">
              <label class="form-label">摘要标题 <span class="required">*</span></label>
              <input
                v-model="form.title"
                type="text"
                class="form-input"
                placeholder="请输入摘要标题"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">选择聚类任务 <span class="required">*</span></label>
              <select
                v-model="form.clusterId"
                class="form-input form-select"
                required
                @change="onClusterTaskChange"
              >
                <option value="" disabled>请选择已完成的聚类任务</option>
                <option
                  v-for="task in clusterTasks"
                  :key="task.id"
                  :value="task.id"
                >
                  {{ task.name }}
                </option>
              </select>
            </div>

            <div v-if="clusterLabels.length > 0" class="form-group">
              <label class="form-label">选择聚类簇 <span class="required">*</span></label>
              <select
                v-model="form.clusterIndex"
                class="form-input form-select"
                required
              >
                <option value="" disabled>请选择聚类簇</option>
                <option
                  v-for="cluster in clusterLabels"
                  :key="cluster.id"
                  :value="cluster.id"
                >
                  {{ cluster.label }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">生成模型</label>
              <select v-model="form.model" class="form-input form-select">
                <option value="GPT-4">GPT-4</option>
                <option value="GPT-3.5">GPT-3.5</option>
                <option value="Claude-3">Claude-3</option>
              </select>
            </div>

            <button
              type="submit"
              class="btn btn-amber btn-full"
              :disabled="generating || !canGenerate"
            >
              {{ generating ? '生成中...' : '生成摘要' }}
            </button>
          </form>
        </GlassCard>

        <!-- Right Panel: Result Preview -->
        <GlassCard class="panel-right">
          <template #header>结果预览</template>

          <!-- Empty state -->
          <EmptyState
            v-if="!generating && !result"
            text="请选择聚类任务并生成摘要"
          />

          <!-- Loading state -->
          <LoadingSpinner
            v-else-if="generating"
            text="正在生成摘要..."
            size="lg"
          />

          <!-- Result -->
          <div v-else class="result-content">
            <h2 class="result-title">{{ result.title }}</h2>

            <div class="result-section">
              <h3 class="result-section-title">摘要内容</h3>
              <p class="result-text">{{ result.content }}</p>
            </div>

            <div v-if="result.keyPoints && result.keyPoints.length" class="result-section">
              <h3 class="result-section-title">关键观点</h3>
              <ul class="key-points-list">
                <li v-for="(point, idx) in result.keyPoints" :key="idx" class="key-point-item">
                  <span class="key-point-dot"></span>
                  <span>{{ point }}</span>
                </li>
              </ul>
            </div>

            <div class="result-meta">
              <div class="meta-tag">
                <span class="meta-label">字数</span>
                <span class="meta-value">{{ result.wordCount }}</span>
              </div>
              <div class="meta-tag">
                <span class="meta-label">模型</span>
                <span class="meta-value">{{ result.model }}</span>
              </div>
            </div>

            <router-link to="/summary" class="save-link">
              保存到摘要管理
            </router-link>
          </div>
        </GlassCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import GlassCard from '@/components/Common/GlassCard.vue'
import EmptyState from '@/components/Common/EmptyState.vue'
import LoadingSpinner from '@/components/Common/LoadingSpinner.vue'
import { getClusterList } from '@/api/cluster'
import { generateSummary } from '@/api/summary'

/* ---------- state ---------- */

const pageLoading = ref(true)
const generating = ref(false)
const clusterTasks = ref([])
const clusterLabels = ref([])
const result = ref(null)

const form = ref({
  title: '',
  clusterId: '',
  clusterIndex: '',
  model: 'GPT-4'
})

/* ---------- computed ---------- */

const canGenerate = computed(() => {
  return form.value.title.trim() !== ''
    && form.value.clusterId !== ''
    && (clusterLabels.value.length === 0 || form.value.clusterIndex !== '')
})

/* ---------- fetch clusters ---------- */

async function fetchCompletedClusters() {
  try {
    const res = await getClusterList({ status: 'completed' })
    if (res.data) {
      clusterTasks.value = res.data.list
    }
  } catch (e) {
    console.error('获取聚类任务列表失败', e)
  } finally {
    pageLoading.value = false
  }
}

/* ---------- handlers ---------- */

function onClusterTaskChange() {
  form.value.clusterIndex = ''
  const task = clusterTasks.value.find(t => t.id === form.value.clusterId)

  const rawResults = task?.results
  let list = []
  // 兼容后端返回：results 可能是“簇数组”，或是 { clusters: [...] }
  if (Array.isArray(rawResults)) list = rawResults
  else if (rawResults && Array.isArray(rawResults.clusters)) list = rawResults.clusters

  clusterLabels.value = list.map((c) => {
    const textIds = Array.isArray(c.textIds) ? c.textIds : []
    const keywords = Array.isArray(c.keywords) ? c.keywords : []
    const label = c.label || (keywords[0] ? String(keywords[0]) : `簇${c.id ?? ''}`)
    return { ...c, textIds, keywords, label }
  })
}

async function handleGenerate() {
  if (!canGenerate.value || generating.value) return

  const selectedCluster = clusterLabels.value.find(c => c.id === form.value.clusterIndex)

  generating.value = true
  result.value = null
  try {
    const res = await generateSummary({
      title: form.value.title,
      clusterId: form.value.clusterId,
      clusterLabel: selectedCluster ? selectedCluster.label : '',
      model: form.value.model
    })
    if (res.data) {
      result.value = res.data
    }
  } catch (e) {
    console.error('生成摘要失败', e)
  } finally {
    generating.value = false
  }
}

/* ---------- lifecycle ---------- */

onMounted(() => {
  fetchCompletedClusters()
})
</script>

<style scoped>
.summary-gen-page {
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

/* ---- Two-panel layout ---- */
.panels {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 24px;
  align-items: start;
}

.panel-left {
  position: sticky;
  top: 32px;
}

/* ---- Form ---- */
.gen-form {
  display: flex;
  flex-direction: column;
  gap: 0;
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

.btn-full {
  width: 100%;
  padding: 14px 20px;
  font-size: 15px;
  font-weight: 600;
  margin-top: 4px;
}

/* ---- Result ---- */
.result-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-title {
  font-size: 20px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #f59e0b;
  margin: 0;
  text-transform: none;
}

.result-text {
  font-size: 14px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* ---- Key Points ---- */
.key-points-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.key-point-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

.key-point-dot {
  flex-shrink: 0;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  margin-top: 7px;
}

/* ---- Meta ---- */
.result-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.meta-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
}

.meta-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
}

.meta-value {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

/* ---- Save Link ---- */
.save-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #10b981;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
  align-self: flex-end;
}

.save-link:hover {
  color: #34d399;
}

/* ---- Responsive ---- */
@media (max-width: 900px) {
  .panels {
    grid-template-columns: 1fr;
  }

  .panel-left {
    position: static;
  }
}

@media (max-width: 768px) {
  .summary-gen-page {
    padding: 20px 16px;
  }

  .page-title {
    font-size: 22px;
  }

  .panels {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style>
