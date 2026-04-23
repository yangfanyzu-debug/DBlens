import http from './http'

export interface Connection {
  id: string
  name: string
  db_type: string
  host?: string
  port?: number
  username?: string
  database?: string
  group_name?: string
  ssh_enabled: boolean
  ssh_host?: string
  ssh_port: number
  ssh_username?: string
  ssl_enabled: boolean
}

export interface ConnectionForm {
  name: string
  db_type: string
  host?: string
  port?: number
  username?: string
  password?: string
  database?: string
  group_name?: string
  ssh_enabled: boolean
  ssh_host?: string
  ssh_port: number
  ssh_username?: string
  ssh_password?: string
  ssh_private_key?: string
  ssl_enabled: boolean
  ssl_ca?: string
  ssl_cert?: string
  ssl_key?: string
}

export const listConnections = () => http.get<Connection[]>('/connections').then(r => r.data)
export const createConnection = (data: ConnectionForm) => http.post<Connection>('/connections', data).then(r => r.data)
export const updateConnection = (id: string, data: ConnectionForm) => http.put<Connection>(`/connections/${id}`, data).then(r => r.data)
export const deleteConnection = (id: string) => http.delete(`/connections/${id}`)
export const testConnection = (id: string) => http.post<{ success: boolean; message: string; latency_ms: number }>(`/connections/${id}/test`).then(r => r.data)
export const openConnection = (id: string) => http.post(`/connections/${id}/connect`)
export const closeConnection = (id: string) => http.delete(`/connections/${id}/disconnect`)
