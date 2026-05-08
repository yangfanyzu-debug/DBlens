import http from './http'

export const getTableData = (connId: string, database: string, table: string, params: Record<string, any>) =>
  http.get(`/data/${connId}/${database}/${table}`, { params }).then(r => r.data)

export const previewChanges = (connId: string, database: string, table: string, changes: any[]) =>
  http.post(`/data/${connId}/${database}/${table}/preview`, { changes }).then(r => r.data)

export const applyChanges = (connId: string, database: string, table: string, changes: any[]) =>
  http.put(`/data/${connId}/${database}/${table}/rows`, { changes }).then(r => r.data)

function filenameFromDisposition(disposition: unknown, fallback: string) {
  if (typeof disposition !== 'string') return fallback

  const encodedMatch = disposition.match(/filename\*=UTF-8''([^;]+)/i)
  if (encodedMatch?.[1]) {
    return decodeURIComponent(encodedMatch[1].replace(/^"|"$/g, ''))
  }

  const quotedMatch = disposition.match(/filename="?([^";]+)"?/i)
  return quotedMatch?.[1] || fallback
}

export const exportData = async (connId: string, database: string, table: string, format: string) => {
  const response = await http.get<Blob>(`/data/${connId}/${database}/${table}/export`, {
    params: { format },
    responseType: 'blob',
  })

  return {
    blob: response.data,
    filename: filenameFromDisposition(response.headers['content-disposition'], `${table}.${format}`),
  }
}
