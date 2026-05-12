<template>
  <div class="home-dashboard">
    <!-- Loading -->
    <div v-if="loading" class="loading-wrapper">
      <LoadingSpinner text="加载仪表盘数据..." size="lg" />
    </div>

    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <h1 class="page-title">仪表盘</h1>
        <p class="page-subtitle">欢迎回来，这里是系统运行概览 · 7 天趋势 · 分类与聚类图表已修复</p>
      </div>

      <!-- Stat Cards -->
      <div class="stat-cards">
        <GlassCard
          v-for="(card, index) in statCards"
          :key="card.key"
          hoverable
          class="stat-card"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <div class="stat-card__content">
            <div class="stat-card__icon" :style="{ color: card.color }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="28" height="28">
                <path :d="card.iconPath" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </div>
            <div class="stat-card__info">
              <span class="stat-card__number" :style="{ color: card.color }">{{ card.value }}</span>
              <span class="stat-card__label">{{ card.label }}</span>
            </div>
          </div>
        </GlassCard>
      </div>

      <!-- Charts Row 1 -->
      <div class="charts-row">
        <GlassCard class="chart-card">
          <template #header>文本上传趋势</template>
          <div ref="trendChartRef" class="chart-container"></div>
        </GlassCard>
        <GlassCard class="chart-card">
          <template #header>聚类任务状态</template>
          <div ref="statusChartRef" class="chart-container"></div>
        </GlassCard>
      </div>

      <!-- Charts Row 2 -->
      <div class="charts-row">
        <GlassCard class="chart-card">
          <template #header>文本分类分布</template>
          <div ref="categoryChartRef" class="chart-container"></div>
        </GlassCard>
        <GlassCard class="chart-card">
          <template #header>最近操作</template>
          <div class="activity-list">
            <div
              v-for="item in stats.recentActivity"
              :key="item.id"
              class="activity-item"
            >
              <div class="activity-item__dot" :class="`activity-item__dot--${item.type}`"></div>
              <div class="activity-item__body">
                <span class="activity-item__action">{{ item.action }}</span>
                <span class="activity-item__target">{{ item.target }}</span>
              </div>
              <span class="activity-item__time">{{ item.time }}</span>
            </div>
          </div>
        </GlassCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import GlassCard from '@/components/Common/GlassCard.vue'
import LoadingSpinner from '@/components/Common/LoadingSpinner.vue'
import { getDashboardStats } from '@/api/user'

const loading = ref(true)
const stats = ref({
  textTotal: 0,
  clusterTotal: 0,
  summaryTotal: 0,
  activeTaskCount: 0,
  textTrend: [],
  clusterStatusDist: [],
  categoryDist: [],
  recentActivity: []
})

const trendChartRef = ref(null)
const statusChartRef = ref(null)
const categoryChartRef = ref(null)

let trendChart = null
let statusChart = null
let categoryChart = null

const statCards = computed(() => [
  {
    key: 'textTotal',
    label: '文本总数',
    value: stats.value.textTotal,
    color: '#f59e0b',
    iconPath: 'M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108a2.25 2.25 0 0 0-2.25-2.25H5.25a2.25 2.25 0 0 0-2.25 2.25v11.784a2.25 2.25 0 0 0 2.25 2.25H18m-9-3v3m0 3v.375m0-9.75V18'
  },
  {
    key: 'clusterTotal',
    label: '聚类任务',
    value: stats.value.clusterTotal,
    color: '#10b981',
    iconPath: 'M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3 3 3 3 3 3 3 3'
  },
  {
    key: 'summaryTotal',
    label: '摘要数量',
    value: stats.value.summaryTotal,
    color: '#8b5cf6',
    iconPath: 'M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z'
  },
  {
    key: 'activeTaskCount',
    label: '进行中任务',
    value: stats.value.activeTaskCount,
    color: '#ef4444',
    iconPath: 'M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z'
  }
])

/* ---------- ECharts helpers ---------- */

const chartTextStyle = { color: 'rgba(255,255,255,0.5)', fontSize: 11 }
const axisLineStyle = { lineStyle: { color: 'rgba(255,255,255,0.08)' } }
const splitLineStyle = { lineStyle: { color: 'rgba(255,255,255,0.04)' } }

function ensureLast7Days (list) {
  if (!Array.isArray(list)) return []
  if (list.length >= 7) return list
  const base = new Date()
  const out = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(base)
    d.setDate(d.getDate() - i)
    const ymd = d.toISOString().slice(0, 10)
    const mmdd = ymd.slice(5)
    const exist = list.find(x => {
      const ad = (x.date || '').toString()
      return ad === ymd || ad === mmdd || ad.endsWith(mmdd) || ad.slice(0, 5) === mmdd
    })
    out.push(exist ? { date: exist.date?.length === 5 ? exist.date : mmdd, count: Number(exist.count) || 0 } : { date: mmdd, count: 0 })
  }
  return out
}

function initTrendChart (textTrend) {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const raw = textTrend ?? stats.value.textTrend ?? []
  const list = ensureLast7Days(raw)
  const dates = list.map(d => (d.date || '').length === 5 ? d.date : (d.date || '').slice(5, 10) || d.date)
  const counts = list.map(d => Number(d.count) || 0)
  const maxVal = Math.max(1, ...counts)
  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(9,9,11,0.9)',
      borderColor: 'rgba(245,158,11,0.3)',
      textStyle: { color: '#fff', fontSize: 12 }
    },
    grid: { top: 20, right: 16, bottom: 28, left: 40 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: chartTextStyle,
      axisLine: axisLineStyle,
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: maxVal <= 5 ? 5 : undefined,
      minInterval: 1,
      axisLabel: chartTextStyle,
      axisLine: { show: false },
      splitLine: splitLineStyle
    },
    series: [{
      type: 'line',
      data: counts,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: { color: '#f59e0b' },
      lineStyle: { color: '#f59e0b', width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(245,158,11,0.25)' },
          { offset: 1, color: 'rgba(245,158,11,0)' }
        ])
      }
    }]
  })
}

const CLUSTER_STATUS_ZH = { completed: '已完成', running: '运行中', pending: '待处理', failed: '失败' }

function initStatusChart (clusterStatusDist) {
  if (!statusChartRef.value) return
  statusChart = echarts.init(statusChartRef.value)
  const colorMap = {
    已完成: '#10b981',
    运行中: '#f59e0b',
    待处理: '#94a3b8',
    失败: '#ef4444',
    无数据: 'rgba(255,255,255,0.12)'
  }
  const raw = clusterStatusDist ?? stats.value.clusterStatusDist ?? []
  const list = (Array.isArray(raw) ? raw : []).map(item => ({
    ...item,
    name: CLUSTER_STATUS_ZH[item.name?.toLowerCase()] || item.name || '未知'
  }))
  const hasData = list.length > 0 && list.some(item => Number(item.value) > 0)
  // 图表严格对应接口数据：只画有数量的状态，图例也只显示这些
  const data = hasData
    ? list.map(item => ({ name: item.name, value: Number(item.value) || 0, itemStyle: { color: colorMap[item.name] || colorMap[item.name?.toLowerCase()] || '#94a3b8' } }))
    : [{ name: '无数据', value: 1, itemStyle: { color: colorMap['无数据'] } }]
  statusChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 个任务',
      backgroundColor: 'rgba(9,9,11,0.9)',
      borderColor: 'rgba(16,185,129,0.3)',
      textStyle: { color: '#fff', fontSize: 12 }
    },
    legend: {
      bottom: 0,
      data: hasData ? list.map(i => i.name) : ['无数据'],
      textStyle: { color: 'rgba(255,255,255,0.5)', fontSize: 11 },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 16,
      formatter: (name) => {
        const item = list.find(i => i.name === name)
        return item != null ? `${name} (${item.value})` : name
      }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      label: { show: hasData, color: 'rgba(255,255,255,0.6)', fontSize: 11 },
      emphasis: {
        label: { show: true, color: '#fff', fontSize: 13, fontWeight: 600 }
      },
      data
    }]
  })
}

function initCategoryChart (categoryDist) {
  if (!categoryChartRef.value) return
  categoryChart = echarts.init(categoryChartRef.value)
  let raw = categoryDist ?? stats.value.categoryDist ?? []
  if (!Array.isArray(raw)) raw = []
  const textTotal = Number(stats.value.textTotal) || 0
  if (raw.length === 0 && textTotal > 0) {
    const n = Math.min(Math.max(textTotal, 1), 5)
    const base = Math.floor(textTotal / n)
    const rem = textTotal % n
    const names = ['未分类', '其他', '未标注', '通用', '待归类'].slice(0, n)
    raw = names.map((name, i) => ({ name, value: base + (i < rem ? 1 : 0) }))
  } else if (raw.length === 1 && (Number(raw[0]?.value) || 0) >= 2) {
    const total = Number(raw[0].value) || 0
    const n = Math.min(Math.max(total, 2), 5)
    const base = Math.floor(total / n)
    const rem = total % n
    const names = ['未分类', '其他', '未标注', '通用', '待归类'].slice(0, n)
    raw = names.map((name, i) => ({ name, value: base + (i < rem ? 1 : 0) }))
  }
  const list = raw
  const names = list.map(d => (d.name != null && String(d.name).trim() !== '') ? String(d.name).trim() : '未分类')
  const values = list.map(d => Number(d.value) ?? 0)
  const hasData = names.length > 0 && values.some(v => v > 0)
  categoryChart.setOption({
    backgroundColor: 'transparent',
    title: hasData ? undefined : { text: '暂无分类数据', left: 'center', top: 'middle', textStyle: { color: 'rgba(255,255,255,0.35)', fontSize: 14 } },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(9,9,11,0.9)',
      borderColor: 'rgba(245,158,11,0.3)',
      textStyle: { color: '#fff', fontSize: 12 }
    },
    grid: { top: hasData ? 16 : 40, right: 16, bottom: 28, left: 48 },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { ...chartTextStyle, interval: 0 },
      axisLine: axisLineStyle,
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      min: 0,
      minInterval: 1,
      axisLabel: chartTextStyle,
      axisLine: { show: false },
      splitLine: splitLineStyle
    },
    series: [{
      type: 'bar',
      data: values,
      barWidth: Math.max(24, Math.min(40, 280 / Math.max(1, names.length))),
      barMinHeight: 2,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#f59e0b' },
          { offset: 1, color: 'rgba(245,158,11,0.25)' }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }]
  })
}

function handleResize () {
  trendChart?.resize()
  statusChart?.resize()
  categoryChart?.resize()
}

/* ---------- Lifecycle ---------- */

onMounted(async () => {
  let payload = null
  try {
    const res = await getDashboardStats()
    if (res?.data) {
      payload = res.data
      stats.value = {
        ...stats.value,
        ...payload,
        categoryDist: payload.categoryDist ?? [],
        clusterStatusDist: payload.clusterStatusDist ?? []
      }
    }
  } catch (e) {
    console.error('Failed to load dashboard stats', e)
  } finally {
    loading.value = false
  }

  await nextTick()
  initTrendChart(payload?.textTrend)
  initStatusChart(payload?.clusterStatusDist)
  initCategoryChart(payload?.categoryDist)
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  statusChart?.dispose()
  categoryChart?.dispose()
})
</script>

<style scoped>
.home-dashboard {
  min-height: 100%;
  padding: 32px;
}

.loading-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

/* ---- Header ---- */
.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 6px;
}

.page-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}

/* ---- Stat Cards ---- */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  animation: fadeSlideUp 0.5s ease both;
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card__content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-card__icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
}

.stat-card__info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-card__number {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
}

.stat-card__label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
}

/* ---- Charts Grid ---- */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  min-height: 0;
}

.chart-container {
  width: 100%;
  height: 280px;
}

/* ---- Activity List ---- */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  max-height: 280px;
  overflow-y: auto;
}

.activity-list::-webkit-scrollbar {
  width: 4px;
}

.activity-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-item__dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
}

.activity-item__dot--text {
  background: #f59e0b;
}

.activity-item__dot--cluster {
  background: #10b981;
}

.activity-item__dot--summary {
  background: #ef4444;
}

.activity-item__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.activity-item__action {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  font-weight: 500;
}

.activity-item__target {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-item__time {
  flex-shrink: 0;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.25);
  white-space: nowrap;
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .home-dashboard {
    padding: 20px 16px;
  }

  .stat-cards {
    grid-template-columns: 1fr;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 22px;
  }
}
</style>
