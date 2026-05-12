<template>
  <header class="topbar">
    <div class="topbar-left">
      <button class="mobile-menu-btn" @click="$emit('toggle-sidebar')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
      <h1 class="page-title">{{ title }}</h1>
    </div>
    <div class="topbar-right">
      <div class="user-info" @click="showDropdown = !showDropdown">
        <div class="user-avatar">{{ avatarLetter }}</div>
        <span class="user-name">{{ nickname }}</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="chevron" :class="{ open: showDropdown }">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </div>
      <Transition name="dropdown">
        <div v-if="showDropdown" class="dropdown-menu" @click.stop>
          <router-link to="/profile" class="dropdown-item" @click="showDropdown = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            个人中心
          </router-link>
          <button class="dropdown-item danger" @click="handleLogout">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            退出登录
          </button>
        </div>
      </Transition>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/index'
import { logoutApi } from '@/api/auth'

defineEmits(['toggle-sidebar'])

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const showDropdown = ref(false)

const title = computed(() => route.meta?.title || '仪表盘')
const nickname = computed(() => userStore.nickname)
const avatarLetter = computed(() => nickname.value?.charAt(0) || 'U')

function handleClickOutside(e) {
  if (showDropdown.value) showDropdown.value = false
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))

async function handleLogout() {
  try {
    await logoutApi()
  } finally {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.topbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(9, 9, 11, 0.8);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 50;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 4px;
}

.mobile-menu-btn svg {
  width: 22px;
  height: 22px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.topbar-right {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 10px;
  transition: background 0.15s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.04);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.3), rgba(16, 185, 129, 0.3));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.user-name {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.chevron {
  width: 14px;
  height: 14px;
  color: rgba(255, 255, 255, 0.3);
  transition: transform 0.2s;
}

.chevron.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 160px;
  background: #1c1c1f;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 6px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 13px;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  transition: all 0.15s;
}

.dropdown-item svg {
  width: 16px;
  height: 16px;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
}

.dropdown-item.danger:hover {
  background: rgba(239, 68, 68, 0.08);
  color: #ef4444;
}

.dropdown-enter-active, .dropdown-leave-active {
  transition: all 0.2s;
}
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 768px) {
  .mobile-menu-btn { display: flex; }
  .topbar { padding: 0 16px; }
}
</style>
