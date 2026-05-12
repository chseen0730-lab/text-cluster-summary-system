import service from '@/utils/request'

export function getSummaryList(params = {}) {
  return service.get('/summary', { params })
}

export function getSummaryDetail(id) {
  return service.get(`/summary/${id}`)
}

export function generateSummary(data) {
  return service.post('/summary/generate', {
    sourceType: data.sourceType || (data.clusterId != null ? 'cluster' : 'text'),
    sourceId: data.clusterId != null ? data.clusterId : data.textId,
    title: data.title
  })
}

export function deleteSummary(id) {
  return service.delete(`/summary/${id}`)
}
