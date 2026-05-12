import service from '@/utils/request'

export function getClusterList(params = {}) {
  return service.get('/cluster', { params })
}

export function getClusterDetail(id) {
  return service.get(`/cluster/${id}`)
}

export function createCluster(data) {
  return service.post('/cluster', {
    name: data.name,
    description: data.description,
    textIds: data.textIds || [],
    clusterCount: data.clusterCount || 3,
    algorithm: data.algorithm || 'K-Means'
  })
}

export function runCluster(id) {
  return service.post(`/cluster/${id}/run`)
}

export function deleteCluster(id) {
  return service.delete(`/cluster/${id}`)
}

export function getClusterStats() {
  return service.get('/cluster/stats')
}
