import service from '@/utils/request'

export function getUserInfo() {
  return service.get('/user/profile')
}

export function updateUserInfo(data) {
  return service.put('/user/profile', data)
}

export function changePassword(data) {
  return service.post('/user/password', {
    oldPassword: data.oldPassword,
    newPassword: data.newPassword
  })
}

export function getUserStats() {
  return service.get('/user/stats')
}

export function getDashboardStats() {
  return service.get('/user/dashboard')
}

export function getHistoryList(params = {}) {
  return service.get('/user/history', { params })
}
