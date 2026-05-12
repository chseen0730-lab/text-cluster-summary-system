<template>
  <div class="results-page">
    <!-- Loading -->
    <div v-if="pageLoading" class="loading-wrapper">
      <LoadingSpinner text="加载聚类结果..." size="lg" />
    </div>

    <template v-else-if="detail">
      <!-- Back + Title -->
      <div class="page-header">
        <button class="btn btn-ghost btn-back" @click="$router.push('/cluster-analysis')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M19 12H5" /><polyline points="12 19 5 12 12 5" />
          </svg>
          <span>返回列表</span>
        </button>
        <h1 class="page-title">{{ detail.name }}</h1>
      </div>

      <!-- Task Info -->
      <GlassCard class="info-card">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">任务名称</span>
            <span class="info-value">{{ detail.name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">聚类算法</span>
            <span class="info-value info-value--amber">{{ detail.algorithm }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">任务状态</span>
            <span class="info-value info-value--emerald">{{ statusMap[detail.status] || detail.status }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">创建时间</span>
            <span class="info-value">{{ detail.createdAt }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">完成时间</span>
            <span class="info-value">{{ detail.completedAt || '--' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">轮廓系数</span>
            <span class="info-value info-value--amber">{{ detail.results?.silhouetteScore ?? '--' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">惯性值</span>
            <span class="info-value">{{ detail.results?.inertia ?? '--' }}</span>
          </div>
        </div>
      </GlassCard>

      <!-- Charts Grid -->
      <div v-if="detail.results" class="charts-grid">
        <GlassCard noPadding>
          <template #header>聚类分布饼图</template>
          <div ref="pieChartRef" class="chart-container"></div>
        </GlassCard>

        <GlassCard noPadding>
          <template #header>簇内文本数量条形图</template>
          <div ref="barChartRef" class="chart-container"></div>
        </GlassCard>

        <GlassCard noPadding>
          <template #header>相似度矩阵热力图</template>
          <div ref="heatmapChartRef" class="chart-container"></div>
        </GlassCard>
      </div>

      <!-- Cluster Detail Cards -->
      <div v-if="normalizedClusters.length > 0" class="cluster-details-section">
        <h2 class="section-title">聚类详情</h2>
        <div class="cluster-cards-grid">
          <GlassCard
            v-for="cluster in normalizedClusters"
            :key="cluster.id"
            hoverable
          >
            <div class="cluster-card-header">
              <span class="cluster-label" :style="{ color: clusterColors[cluster.id % clusterColors.length] }">
                {{ cluster.label }}
              </span>
              <span class="cluster-count">{{ cluster.textIds.length }} 篇文本</span>
            </div>
            <div class="cluster-keywords">
              <span
                v-for="kw in cluster.keywords"
                :key="kw"
                class="keyword-tag"
                :style="{
                  background: clusterColors[cluster.id % clusterColors.length] + '15',
                  color: clusterColors[cluster.id % clusterColors.length],
                  borderColor: clusterColors[cluster.id % clusterColors.length] + '30'
                }"
              >
                {{ kw }}
              </span>
            </div>
            <div class="cluster-text-ids">
              <span class="text-ids-label">文本 ID:</span>
              <span
                v-for="tid in cluster.textIds"
                :key="tid"
                class="text-id-badge"
              >
                #{{ tid }}
              </span>
            </div>
          </GlassCard>
        </div>
      </div>
    </template>

    <!-- Error / not found -->
    <div v-else class="error-wrapper">
      <p class="error-text">未找到该聚类任务</p>
      <button class="btn btn-amber" @click="$router.push('/cluster-analysis')">返回列表</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import GlassCard from '@/components/Common/GlassCard.vue'
import LoadingSpinner from '@/components/Common/LoadingSpinner.vue'
import { getClusterDetail } from '@/api/cluster'

const route = useRoute()
const id = route.params.id

/* ---------- constants ---------- */

const statusMap = {
  completed: '已完成',
  running: '运行中',
  pending: '待处理'
}

const clusterColors = [
  '#f59e0b',  // amber
  '#10b981',  // emerald
  '#ef4444',  // coral
  '#fbbf24',  // lighter amber
  '#34d399',  // lighter emerald
  '#f87171'   // lighter coral
]

/* ---------- state ---------- */

const pageLoading = ref(true)
const detail = ref(null)

const pieChartRef = ref(null)
const barChartRef = ref(null)
const heatmapChartRef = ref(null)

// 后端返回的 results 实际是“簇数组”（而非 { clusters: [...] }）
// 这里做兼容与字段规范化，保证图表/卡片都能正常渲染。
const normalizedClusters = computed(() => {
  const results = detail.value?.results
  let list = []
  if (Array.isArray(results)) list = results
  else if (results && Array.isArray(results.clusters)) list = results.clusters

  return list.map((c) => {
    const textIds = Array.isArray(c.textIds) ? c.textIds : []
    const keywords = Array.isArray(c.keywords) ? c.keywords : []
    // label 在当前实现里可能不存在，给一个兜底展示
    const label = c.label || (keywords[0] ? String(keywords[0]) : `簇${c.id ?? ''}`)
    return { ...c, textIds, keywords, label }
  })
})

let pieChart = null
let barChart = null
let heatmapChart = null

/* ---------- fetch ---------- */

async function fetchDetail() {
  try {
    const res = await getClusterDetail(id)
    if (res.data) {
      detail.value = res.data
    }
  } catch (e) {
    console.error('获取聚类结果失败', e)
    detail.value = null
  } finally {
    pageLoading.value = false
  }
}

/* ---------- charts ---------- */

function initCharts() {
  if (!detail.value?.results) return

  const baseClusters = normalizedClusters.value
  const safeClusters = baseClusters.length > 0
    ? baseClusters
    : [{ id: 0, label: '无数据', textIds: [], keywords: [] }]

  const clusters = safeClusters
  const labels = clusters.map(c => c.label)
  const counts = clusters.map(c => (Array.isArray(c.textIds) ? c.textIds.length : 0))

  // Pie chart (doughnut)
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value, null, { renderer: 'canvas' })
    pieChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(24, 24, 27, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: 'rgba(255, 255, 255, 0.85)', fontSize: 13 },
        formatter: '{b}: {c} 篇 ({d}%)'
      },
      legend: {
        bottom: 10,
        textStyle: { color: 'rgba(255, 255, 255, 0.5)', fontSize: 12 }
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '68%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 6,
            borderColor: '#09090b',
            borderWidth: 2
          },
          label: {
            color: 'rgba(255, 255, 255, 0.7)',
            fontSize: 12
          },
          labelLine: {
            lineStyle: { color: 'rgba(255, 255, 255, 0.15)' }
          },
          data: clusters.map((c, i) => ({
            name: c.label,
            value: c.textIds.length,
            itemStyle: { color: clusterColors[i % clusterColors.length] }
          }))
        }
      ]
    })
  }

  // Bar chart (horizontal)
  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value, null, { renderer: 'canvas' })
    barChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(24, 24, 27, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: 'rgba(255, 255, 255, 0.85)', fontSize: 13 },
        formatter: (params) => `${params[0].name}: ${params[0].value} 篇`
      },
      grid: {
        left: 16,
        right: 40,
        top: 16,
        bottom: 16,
        containLabel: true
      },
      xAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.08)' } },
        axisLabel: { color: 'rgba(255, 255, 255, 0.4)', fontSize: 12 },
        splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.04)' } },
        minInterval: 1
      },
      yAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.08)' } },
        axisLabel: { color: 'rgba(255, 255, 255, 0.6)', fontSize: 12 },
        axisTick: { show: false }
      },
      series: [
        {
          type: 'bar',
          data: counts,
          barWidth: 20,
          itemStyle: {
            borderRadius: [0, 4, 4, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: 'rgba(245, 158, 11, 0.6)' },
              { offset: 1, color: '#f59e0b' }
            ])
          }
        }
      ]
    })
  }

  // Heatmap chart
  if (heatmapChartRef.value) {
    heatmapChart = echarts.init(heatmapChartRef.value, null, { renderer: 'canvas' })

    // Generate mock similarity matrix
    const n = labels.length
    const heatData = []
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        let val
        if (i === j) {
          val = 1.0
        } else {
          // Deterministic mock similarity based on indices
          val = parseFloat((0.3 + 0.15 * Math.abs(Math.sin(i * 3 + j * 7))).toFixed(2))
        }
        heatData.push([i, j, val])
      }
    }

    heatmapChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        backgroundColor: 'rgba(24, 24, 27, 0.95)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        textStyle: { color: 'rgba(255, 255, 255, 0.85)', fontSize: 13 },
        formatter: (params) => {
          const [x, y, val] = params.data
          return `${labels[x]} - ${labels[y]}<br/>相似度: ${val}`
        }
      },
      grid: {
        left: 16,
        right: 60,
        top: 16,
        bottom: 16,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.08)' } },
        axisLabel: {
          color: 'rgba(255, 255, 255, 0.5)',
          fontSize: 11,
          rotate: 30,
          overflow: 'truncate',
          width: 80
        },
        axisTick: { show: false }
      },
      yAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.08)' } },
        axisLabel: { color: 'rgba(255, 255, 255, 0.5)', fontSize: 11 },
        axisTick: { show: false }
      },
      visualMap: {
        min: 0,
        max: 1,
        calculable: true,
        orient: 'vertical',
        right: 0,
        top: 'center',
        itemHeight: 120,
        inRange: {
          color: ['#f59e0b', '#10b981']
        },
        textStyle: { color: 'rgba(255, 255, 255, 0.4)', fontSize: 11 }
      },
      series: [
        {
          type: 'heatmap',
          data: heatData,
          label: {
            show: true,
            color: 'rgba(255, 255, 255, 0.85)',
            fontSize: 12,
            formatter: (params) => params.data[2].toFixed(2)
          },
          itemStyle: {
            borderColor: '#09090b',
            borderWidth: 2,
            borderRadius: 4
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(245, 158, 11, 0.3)'
            }
          }
        }
      ]
    })
  }
}

function handleResize() {
  pieChart?.resize()
  barChart?.resize()
  heatmapChart?.resize()
}

/* ---------- lifecycle ---------- */

onMounted(async () => {
  await fetchDetail()
  await nextTick()
  initCharts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  pieChart?.dispose()
  barChart?.dispose()
  heatmapChart?.dispose()
  pieChart = null
  barChart = null
  heatmapChart = null
})
</script>

<style scoped>
.results-page {
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

.error-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 40vh;
  gap: 20px;
}

.error-text {
  color: rgba(255, 255, 255, 0.5);
  font-size: 16px;
}

/* ---- Header ---- */
.page-header {
  margin-bottom: 28px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 16px;
  padding: 8px 16px;
  font-size: 13px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
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

.btn-amber:hover {
  background: rgba(245, 158, 11, 0.25);
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

/* ---- Info Card ---- */
.info-card {
  margin-bottom: 28px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.35);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
}

.info-value--amber {
  color: #f59e0b;
}

.info-value--emerald {
  color: #10b981;
}

/* ---- Charts Grid ---- */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 36px;
}

.chart-container {
  width: 100%;
  height: 360px;
  padding: 8px;
  box-sizing: border-box;
}

/* ---- Section Title ---- */
.section-title {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 20px;
}

/* ---- Cluster Detail Cards ---- */
.cluster-details-section {
  margin-top: 8px;
}

.cluster-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.cluster-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.cluster-label {
  font-size: 16px;
  font-weight: 600;
}

.cluster-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.05);
  padding: 4px 10px;
  border-radius: 6px;
}

.cluster-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.keyword-tag {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
}

.cluster-text-ids {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.text-ids-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  font-weight: 500;
}

.text-id-badge {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 8px;
  border-radius: 4px;
  font-variant-numeric: tabular-nums;
}

/* ---- Responsive ---- */
@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .results-page {
    padding: 20px 16px;
  }

  .page-title {
    font-size: 22px;
  }

  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .chart-container {
    height: 300px;
  }

  .cluster-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
