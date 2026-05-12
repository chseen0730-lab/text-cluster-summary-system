import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getUser, setUser, clearAuth, isLoggedIn } from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref(getUser())
  const logged = ref(isLoggedIn())

  const nickname = computed(() => user.value?.nickname || '未登录')
  const role = computed(() => user.value?.role || 'guest')

  function login(userData) {
    user.value = userData
    logged.value = true
    setUser(userData)
  }

  function logout() {
    user.value = null
    logged.value = false
    clearAuth()
  }

  function updateProfile(data) {
    user.value = { ...user.value, ...data }
    setUser(user.value)
  }

  return { user, logged, nickname, role, login, logout, updateProfile }
})

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const loading = ref(false)
  const currentRoute = ref('')

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setLoading(val) {
    loading.value = val
  }

  function setCurrentRoute(name) {
    currentRoute.value = name
  }

  return { sidebarCollapsed, loading, currentRoute, toggleSidebar, setLoading, setCurrentRoute }
})
