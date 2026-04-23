import http from './http'

export const executeQuery = (connId: string, database: string, sql: string, queryId: string) =>
  http.post<{ query_id: string; status: string }>('/query/execute', {
    conn_id: connId, database, sql, query_id: queryId,
  }).then(r => r.data)

export const killQuery = (queryId: string) =>
  http.delete(`/query/${queryId}`)
