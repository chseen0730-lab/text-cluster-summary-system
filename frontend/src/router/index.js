import { createRouter, createWebHashHistory } from 'vue-router'
import { isLoggedIn } from '@/utils/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    component: () => import('@/components/Layout/index.vue'),
    redirect: '/home',
    children: [
      { path: 'home', name: 'Home', component: () => import('@/views/Home.vue'), meta: { title: '仪表盘' } },
      { path: 'text-upload', name: 'TextUpload', component: () => import('@/views/TextUpload.vue'), meta: { title: '文本管理' } },
      { path: 'cluster-analysis', name: 'ClusterAnalysis', component: () => import('@/views/ClusterAnalysis.vue'), meta: { title: '聚类分析' } },
      { path: 'cluster-results/:id', name: 'ClusterResults', component: () => import('@/views/ClusterResults.vue'), meta: { title: '聚类结果' } },
      { path: 'summary-generation', name: 'SummaryGeneration', component: () => import('@/views/SummaryGeneration.vue'), meta: { title: '摘要生成' } },
      { path: 'summary-management', name: 'SummaryManagement', component: () => import('@/views/SummaryManagement.vue'), meta: { title: '摘要管理' } },
      { path: 'history', name: 'History', component: () => import('@/views/History.vue'), meta: { title: '操作历史' } },
      { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心' } }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/home' }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.guest) {
    if (isLoggedIn()) {
      next('/home')
    } else {
      next()
    }
  } else {
    if (isLoggedIn()) {
      next()
    } else {
      next('/login')
    }
  }
})

export default router
