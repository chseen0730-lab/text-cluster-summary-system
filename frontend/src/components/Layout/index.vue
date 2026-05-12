<template>
  <div class="layout">
    <!-- Global ambient background -->
    <AmbientBackground />
    <ParticleCanvas :count="50" :connect-radius="120" :opacity="0.35" />

    <Sidebar :collapsed="collapsed" @toggle="toggleSidebar" />
    <div class="layout-main" :class="{ 'sidebar-collapsed': collapsed }">
      <Topbar @toggle-sidebar="toggleSidebar" />
      <main class="layout-content">
        <PageTransition />
      </main>
    </div>
    <div v-if="mobileOpen" class="mobile-overlay" @click="mobileOpen = false"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'
import PageTransition from '../Common/PageTransition.vue'
import AmbientBackground from '../Common/AmbientBackground.vue'
import ParticleCanvas from '../Common/ParticleCanvas.vue'
import { useAppStore } from '@/store/index'

const appStore = useAppStore()
const collapsed = ref(false)
const mobileOpen = ref(false)

function toggleSidebar() {
  if (window.innerWidth <= 768) {
    mobileOpen.value = !mobileOpen.value
  } else {
    collapsed.value = !collapsed.value
    appStore.sidebarCollapsed = collapsed.value
  }
}

function handleResize() {
  if (window.innerWidth <= 768) {
    collapsed.value = true
  }
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: #09090b;
  position: relative;
  overflow: hidden;
}

.layout-main {
  flex: 1;
  margin-left: 240px;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.layout-main.sidebar-collapsed {
  margin-left: 72px;
}

.layout-content {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
}

.mobile-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
}

@media (max-width: 768px) {
  .layout-main {
    margin-left: 0 !important;
  }
  .mobile-overlay {
    display: block;
  }
  .layout-content {
    padding: 16px;
  }
}
</style>
