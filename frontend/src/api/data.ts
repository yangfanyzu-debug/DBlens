import http from './http'

export const getTableData = (connId: string, database: string, table: string, params: Record<string, any>) =>
  http.get(`/data/${connId}/${database}/${table}`, { params }).then(r => r.data)

export const previewChanges = (connId: string, database: string, table: string, changes: any[]) =>
  http.post(`/data/${connId}/${database}/${table}/preview`, { changes }).then(r => r.data)

export const applyChanges = (connId: string, database: string, table: string, changes: any[]) =>
  http.put(`/data/${connId}/${database}/${table}/rows`, { changes }).then(r => r.data)

export const exportData = (connId: string, database: string, table: string, format: string) =>
  `/dblens-api/data/${connId}/${database}/${table}/export?format=${format}`
