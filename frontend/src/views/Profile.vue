<template>
  <div class="profile-page">
    <!-- Loading -->
    <div v-if="loading" class="loading-wrapper">
      <LoadingSpinner text="加载个人信息..." size="lg" />
    </div>

    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <h1 class="page-title">个人中心</h1>
        <p class="page-subtitle">管理你的账户信息与偏好设置</p>
      </div>

      <!-- Two-column Layout -->
      <div class="profile-layout">
        <!-- Left Column -->
        <div class="profile-left">
          <!-- Profile Card -->
          <GlassCard class="profile-card">
            <div class="profile-avatar">
              <div class="avatar-circle">
                {{ userInitial }}
              </div>
            </div>

            <!-- View Mode -->
            <template v-if="!editing">
              <div class="profile-info">
                <h2 class="profile-username">{{ userStore.user?.username || '--' }}</h2>
                <div class="profile-detail-list">
                  <div class="profile-detail-item">
                    <span class="profile-detail-label">昵称</span>
                    <span class="profile-detail-value">{{ userStore.user?.nickname || '--' }}</span>
                  </div>
                  <div class="profile-detail-item">
                    <span class="profile-detail-label">邮箱</span>
                    <span class="profile-detail-value">{{ userStore.user?.email || '--' }}</span>
                  </div>
                  <div class="profile-detail-item">
                    <span class="profile-detail-label">角色</span>
                    <span class="profile-detail-value role-badge">{{ roleLabel }}</span>
                  </div>
                  <div class="profile-detail-item">
                    <span class="profile-detail-label">注册日期</span>
                    <span class="profile-detail-value">{{ userStore.user?.createdAt || '--' }}</span>
                  </div>
                </div>
              </div>
              <button class="btn btn-primary" @click="startEdit">编辑资料</button>
            </template>

            <!-- Edit Mode -->
            <template v-else>
              <div class="profile-info">
                <h2 class="profile-username">{{ userStore.user?.username || '--' }}</h2>
                <div class="edit-form">
                  <div class="form-group">
                    <label class="form-label">昵称</label>
                    <input
                      v-model="editForm.nickname"
                      type="text"
                      class="form-input"
                      placeholder="请输入昵称"
                    />
                  </div>
                  <div class="form-group">
                    <label class="form-label">邮箱</label>
                    <input
                      v-model="editForm.email"
                      type="email"
                      class="form-input"
                      placeholder="请输入邮箱"
                    />
                  </div>
                </div>
              </div>
              <div class="btn-group">
                <button class="btn btn-primary" :disabled="saving" @click="saveProfile">
                  {{ saving ? '保存中...' : '保存' }}
                </button>
                <button class="btn btn-ghost" @click="cancelEdit">取消</button>
              </div>
            </template>
          </GlassCard>

          <!-- Password Change -->
          <GlassCard class="password-card">
            <template #header>修改密码</template>
            <div class="edit-form">
              <div class="form-group">
                <label class="form-label">当前密码</label>
                <input
                  v-model="passwordForm.oldPassword"
                  type="password"
                  class="form-input"
                  placeholder="请输入当前密码"
                />
              </div>
              <div class="form-group">
                <label class="form-label">新密码</label>
                <input
                  v-model="passwordForm.newPassword"
                  type="password"
                  class="form-input"
                  placeholder="请输入新密码"
                />
              </div>
              <div class="form-group">
                <label class="form-label">确认新密码</label>
                <input
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  class="form-input"
                  placeholder="请再次输入新密码"
                />
              </div>
              <p v-if="passwordError" class="form-error">{{ passwordError }}</p>
              <p v-if="passwordSuccess" class="form-success">{{ passwordSuccess }}</p>
              <button
                class="btn btn-primary"
                :disabled="changingPassword"
                @click="handleChangePassword"
              >
                {{ changingPassword ? '修改中...' : '修改密码' }}
              </button>
            </div>
          </GlassCard>

          <GlassCard class="account-card">
            <div class="account-header">
              <h3 class="account-title">账户操作</h3>
              <p class="account-subtitle">退出当前登录账户，将返回登录页</p>
            </div>
            <button class="btn btn-danger account-logout-btn" @click="handleLogout">
              退出登录
            </button>
          </GlassCard>
        </div>

        <!-- Right Column -->
        <div class="profile-right">
          <!-- Usage Statistics -->
          <GlassCard class="stats-card">
            <template #header>使用统计</template>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-item__number" style="color: #f59e0b">{{ stats.textCount }}</span>
                <span class="stat-item__label">文本数量</span>
              </div>
              <div class="stat-item">
                <span class="stat-item__number" style="color: #10b981">{{ stats.clusterCount }}</span>
                <span class="stat-item__label">聚类任务</span>
              </div>
              <div class="stat-item">
                <span class="stat-item__number" style="color: #ef4444">{{ stats.summaryCount }}</span>
                <span class="stat-item__label">摘要数量</span>
              </div>
              <div class="stat-item">
                <span class="stat-item__number" style="color: #f59e0b">{{ stats.usageDays }}</span>
                <span class="stat-item__label">使用天数</span>
              </div>
            </div>
          </GlassCard>

          <!-- Radar Chart -->
          <GlassCard class="chart-card">
            <template #header>个人使用统计</template>
            <div ref="radarChartRef" class="chart-container"></div>
          </GlassCard>

          <!-- Activity Chart -->
          <GlassCard class="chart-card">
            <template #header>近7天活跃度</template>
            <div ref="activityChartRef" class="chart-container"></div>
          </GlassCard>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import GlassCard from '@/components/Common/GlassCard.vue'
import LoadingSpinner from '@/components/Common/LoadingSpinner.vue'
import { getUserStats, updateUserInfo, changePassword } from '@/api/user'
import { logoutApi } from '@/api/auth'
import { useUserStore } from '@/store/index'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const editing = ref(false)
const saving = ref(false)
const changingPassword = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

const stats = ref({
  textCount: 0,
  clusterCount: 0,
  summaryCount: 0,
  usageDays: 0,
  activityData: []
})

const editForm = ref({ nickname: '', email: '' })

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const radarChartRef = ref(null)
const activityChartRef = ref(null)
let radarChart = null
let activityChart = null

const userInitial = computed(() => {
  const name = userStore.user?.nickname || userStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

const roleLabel = computed(() => {
  const map = { admin: '管理员', user: '普通用户', guest: '访客' }
  return map[userStore.user?.role] || userStore.user?.role || '--'
})

/* ---------- Profile Edit ---------- */

function startEdit() {
  editForm.value.nickname = userStore.user?.nickname || ''
  editForm.value.email = userStore.user?.email || ''
  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

async function saveProfile() {
  saving.value = true
  try {
    const res = await updateUserInfo(editForm.value)
    if (res.data) {
      userStore.updateProfile(res.data)
    }
    editing.value = false
  } catch (e) {
    console.error('Failed to update profile', e)
  } finally {
    saving.value = false
  }
}

/* ---------- Password Change ---------- */

async function handleChangePassword() {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    passwordError.value = '请填写所有密码字段'
    return
  }
  if (passwordForm.value.newPassword === passwordForm.value.oldPassword) {
    passwordError.value = '新密码不能与旧密码相同'
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }

  changingPassword.value = true
  try {
    await changePassword({
      oldPassword: passwordForm.value.oldPassword,
      newPassword: passwordForm.value.newPassword
    })
    passwordSuccess.value = '密码修改成功'
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  } catch (e) {
    passwordError.value = e?.response?.data?.message || '密码修改失败'
  } finally {
    changingPassword.value = false
  }
}

/* ---------- ECharts ---------- */

const chartTextStyle = { color: 'rgba(255,255,255,0.5)', fontSize: 11 }
const axisLineStyle = { lineStyle: { color: 'rgba(255,255,255,0.08)' } }
const splitLineStyle = { lineStyle: { color: 'rgba(255,255,255,0.04)' } }

function initRadarChart() {
  if (!radarChartRef.value) return
  radarChart = echarts.init(radarChartRef.value)
  radarChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: 'rgba(9,9,11,0.9)',
      borderColor: 'rgba(245,158,11,0.3)',
      textStyle: { color: '#fff', fontSize: 12 }
    },
    radar: {
      indicator: [
        { name: '文本上传', max: 100 },
        { name: '聚类分析', max: 100 },
        { name: '摘要生成', max: 100 },
        { name: '系统使用', max: 100 },
        { name: '活跃度', max: 100 }
      ],
      shape: 'polygon',
      axisName: {
        color: 'rgba(255,255,255,0.5)',
        fontSize: 11
      },
      splitArea: {
        areaStyle: { color: ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.04)'] }
      },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [72, 58, 45, 80, 65],
        name: '使用指标',
        areaStyle: {
          color: 'rgba(245,158,11,0.2)'
        },
        lineStyle: {
          color: '#f59e0b',
          width: 2
        },
        itemStyle: {
          color: '#f59e0b'
        },
        symbol: 'circle',
        symbolSize: 6
      }]
    }]
  })
}

function initActivityChart() {
  if (!activityChartRef.value) return
  activityChart = echarts.init(activityChartRef.value)
  const list = stats.value.activityData || []
  const dates = list.map(d => (d.date || '').toString().slice(5))
  const counts = list.map(d => d.count ?? 0)
  activityChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(9,9,11,0.9)',
      borderColor: 'rgba(16,185,129,0.3)',
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
      minInterval: 1,
      axisLabel: chartTextStyle,
      axisLine: { show: false },
      splitLine: splitLineStyle
    },
    series: [{
      type: 'bar',
      data: counts,
      barWidth: 24,
      barMinHeight: 2,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#10b981' },
          { offset: 1, color: 'rgba(16,185,129,0.25)' }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }]
  })
}

function handleResize() {
  radarChart?.resize()
  activityChart?.resize()
}

/* ---------- Logout ---------- */

async function handleLogout() {
  try {
    await logoutApi()
  } finally {
    userStore.logout()
    router.push('/login')
  }
}

/* ---------- Lifecycle ---------- */

onMounted(async () => {
  try {
    const res = await getUserStats()
    if (res.data) {
      stats.value = res.data
    }
  } catch (e) {
    console.error('Failed to load user stats', e)
  } finally {
    loading.value = false
  }

  await nextTick()
  initRadarChart()
  initActivityChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  radarChart?.dispose()
  activityChart?.dispose()
})
</script>

<style scoped>
.profile-page {
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

/* ---- Two-column Layout ---- */
.profile-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

.profile-left,
.profile-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ---- Profile Card ---- */
.profile-card {
  text-align: center;
}

.profile-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-circle {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #10b981);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 700;
  color: #09090b;
  flex-shrink: 0;
}

.profile-username {
  font-size: 22px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 20px;
}

.profile-detail-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
  text-align: left;
}

.profile-detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.profile-detail-item:last-child {
  border-bottom: none;
}

.profile-detail-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

.profile-detail-value {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
}

.role-badge {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

/* ---- Forms ---- */
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: left;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: rgba(245, 158, 11, 0.4);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.form-error {
  font-size: 13px;
  color: #ef4444;
  margin: 0;
}

.form-success {
  font-size: 13px;
  color: #10b981;
  margin: 0;
}

/* ---- Buttons ---- */
.btn {
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1));
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.3), rgba(245, 158, 11, 0.15));
  border-color: rgba(245, 158, 11, 0.5);
}

.btn-ghost {
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-ghost:hover {
  color: rgba(255, 255, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-group {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* ---- Stats Grid ---- */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.stat-item__number {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
}

.stat-item__label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

/* ---- Charts ---- */
.chart-card {
  min-height: 0;
}

.chart-container {
  width: 100%;
  height: 280px;
}

/* ---- Password Card ---- */
.password-card .edit-form {
  margin-bottom: 0;
}

/* ---- Account card ---- */
.account-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.account-header {
  text-align: left;
}

.account-title {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.account-subtitle {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
}

.account-logout-btn {
  align-self: flex-start;
  margin-top: 4px;
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .profile-page {
    padding: 20px 16px;
  }

  .profile-layout {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 22px;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
