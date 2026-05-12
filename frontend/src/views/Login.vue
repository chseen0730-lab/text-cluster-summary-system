<template>
  <div class="login-page">
    <div class="aurora-bg">
      <div class="aurora aurora-1"></div>
      <div class="aurora aurora-2"></div>
      <div class="aurora aurora-3"></div>
      <!-- Particle layer on top of aurora -->
      <ParticleCanvas :count="70" color="245,158,11" color-secondary="16,185,129" :connect-radius="130" :opacity="0.5" />
      <MeteorShower :count="10" />
    </div>

    <div class="glass-card">
      <h1 class="title">登录</h1>
      <p class="subtitle">欢迎回来，请登录您的账户</p>

      <form class="form" @submit.prevent="handleSubmit">
        <div class="field">
          <label class="label" for="username">用户名</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="input"
            placeholder="请输入用户名"
            autocomplete="username"
          />
          <span v-if="errors.username" class="error">{{ errors.username }}</span>
        </div>

        <div class="field">
          <label class="label" for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="input"
            placeholder="请输入密码"
            autocomplete="current-password"
          />
          <span v-if="errors.password" class="error">{{ errors.password }}</span>
        </div>

        <span v-if="submitError" class="error submit-error">{{ submitError }}</span>

        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>登录</span>
        </button>
      </form>

      <p class="link-text">
        还没有账户？
        <router-link class="link" to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginApi } from '@/api/auth'
import { useUserStore } from '@/store/index'
import ParticleCanvas from '@/components/Common/ParticleCanvas.vue'
import MeteorShower from '@/components/Common/MeteorShower.vue'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({
  username: '',
  password: '',
})

const errors = reactive({
  username: '',
  password: '',
})

const submitError = ref('')
const loading = ref(false)

function validate() {
  let valid = true
  errors.username = ''
  errors.password = ''

  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    valid = false
  }
  if (!form.password) {
    errors.password = '请输入密码'
    valid = false
  }
  return valid
}

async function handleSubmit() {
  submitError.value = ''
  if (!validate()) return

  loading.value = true
  try {
    const res = await loginApi({ username: form.username, password: form.password })
    if (res?.code === 200 && res?.data?.user && res?.data?.token) {
      userStore.login(res.data.user)
      router.push('/home')
    } else {
      submitError.value = res?.message || '登录失败，请重试'
    }
  } catch (err) {
    submitError.value = err?.response?.data?.message || err?.message || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #09090b;
  overflow: hidden;
}

/* ---- Aurora background ---- */
.aurora-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.aurora {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.35;
  will-change: transform;
}

.aurora-1 {
  width: 700px;
  height: 700px;
  top: -20%;
  left: -10%;
  background: radial-gradient(circle, #10b981 0%, transparent 70%);
  animation: drift-1 14s ease-in-out infinite alternate;
}

.aurora-2 {
  width: 600px;
  height: 600px;
  bottom: -15%;
  right: -5%;
  background: radial-gradient(circle, #f59e0b 0%, transparent 70%);
  animation: drift-2 18s ease-in-out infinite alternate;
}

.aurora-3 {
  width: 500px;
  height: 500px;
  top: 30%;
  left: 50%;
  background: radial-gradient(circle, #10b98188 0%, #f59e0b44 50%, transparent 70%);
  animation: drift-3 22s ease-in-out infinite alternate;
}

@keyframes drift-1 {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(80px, 60px) scale(1.15); }
}
@keyframes drift-2 {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(-70px, -50px) scale(1.1); }
}
@keyframes drift-3 {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(-60px, 40px) scale(1.2); }
}

/* ---- Glass card ---- */
.glass-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  margin: 0 16px;
  padding: 40px 36px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(245, 158, 11, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  animation: card-appear 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.glass-card::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 21px;
  padding: 1px;
  background: linear-gradient(
    135deg,
    rgba(245, 158, 11, 0.3) 0%,
    rgba(16, 185, 129, 0.15) 50%,
    rgba(245, 158, 11, 0.1) 100%
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: border-rotate 6s linear infinite;
  background-size: 200% 200%;
  pointer-events: none;
}

@keyframes border-rotate {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes card-appear {
  from { opacity: 0; transform: translateY(24px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.title {
  margin: 0 0 6px;
  font-size: 28px;
  font-weight: 700;
  color: #f5f5f5;
  letter-spacing: 0.5px;
}

.subtitle {
  margin: 0 0 32px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.45);
}

/* ---- Form ---- */
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
}

.input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #f5f5f5;
  font-size: 15px;
  outline: none;
  transition: border-color 0.25s, box-shadow 0.25s;
  box-sizing: border-box;
}

.input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.input:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
}

.error {
  font-size: 12px;
  color: #ef4444;
}

.submit-error {
  text-align: center;
  font-size: 13px;
}

/* ---- Button ---- */
.btn-submit {
  width: 100%;
  padding: 13px 0;
  margin-top: 4px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #09090b;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.25s, opacity 0.25s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-submit:hover {
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
}

.btn-submit:active {
  transform: scale(0.97);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(9, 9, 11, 0.3);
  border-top-color: #09090b;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ---- Link ---- */
.link-text {
  margin: 24px 0 0;
  text-align: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

.link {
  color: #f59e0b;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.link:hover {
  color: #fbbf24;
}
</style>
