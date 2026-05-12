import axios from 'axios'
import { getToken, clearAuth } from './auth'

const MOCK_ENABLED = false

const service = axios.create({
  baseURL: '/api',
  timeout: 15000
})

service.interceptors.request.use(config => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

service.interceptors.response.use(
  res => res.data,
  error => {
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      // 登录/注册接口返回 401 时不重定向，让页面显示“用户名或密码错误”
      if (!url.includes('/auth/login') && !url.includes('/auth/register')) {
        clearAuth()
        window.location.hash = '#/login'
      }
    }
    return Promise.reject(error)
  }
)


function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export async function mockRequest(mockFn, ms) {
  if (!MOCK_ENABLED) return null
  const wait = ms ?? (300 + Math.random() * 500)
  await delay(wait)
  return mockFn()
}

export default service
