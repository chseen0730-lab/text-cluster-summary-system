import service from '@/utils/request'
import { setToken, setUser } from '@/utils/auth'

export function loginApi(data) {
  return service.post('/auth/login', data).then(res => {
    if (res && res.code === 200 && res.data) {
      setToken(res.data.token)
      setUser(res.data.user)
    }
    return res
  })
}

export function registerApi(data) {
  return service.post('/auth/register', data).then(res => {
    if (res && res.code === 200 && res.data) {
      setToken(res.data.token)
      setUser(res.data.user)
    }
    return res
  })
}

export function logoutApi() {
  return service.post('/auth/logout').then(res => {
    return res
  })
}
