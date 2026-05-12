import service from '@/utils/request'

export function getTextList(params = {}) {
  return service.get('/texts', { params })
}

export function getTextDetail(id) {
  return service.get(`/texts/${id}`)
}

export function createText(data) {
  return service.post('/texts', data)
}

export function updateText(id, data) {
  return service.put(`/texts/${id}`, data)
}

export function deleteText(id) {
  return service.delete(`/texts/${id}`)
}

export function batchDeleteTexts(ids) {
  return service.post('/texts/batch-delete', { ids })
}
